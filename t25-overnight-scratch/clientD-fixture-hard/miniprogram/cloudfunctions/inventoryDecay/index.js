/**
 * 库存自然损耗定时云函数
 * 扫描所有 active 批次，把 expiryDate < now 的置为 expired，
 * 并在「单批次事务」内原子写 store_loss + 负向 inventory_movements。
 *
 * 触发：建议配定时触发器每日 03:00 执行
 * 手动调用：仅限云开发控制台「云端测试」入口（OPENID 为空，通过 cron-only 守卫）。
 *   前端 wx.cloud.callFunction 携登录态 OPENID 会被守卫拒为 403（安全审查 P1）。
 *
 * 幂等：store_loss / inventory_movements 用确定性 _id（基于 batchId，
 * 一个批次只会过期一次），重复执行 / 部分失败重跑都不会重复扣账。
 *
 * ⚠️ SYNC-WITH: cloudfunctions/adminOp/index.js 的
 *   computeBusinessDate / isDuplicateId / isTxConflict / runWithRetry(runChunkWithRetry)
 *   与 inventory_movements / store_loss 记录字段结构。
 *   云函数部署边界独立无法 require，两处必须人工保持语义一致。
 */
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const _ = db.command

const TX_MAX_RETRIES = 3

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

// 业务日：Asia/Shanghai(UTC+8) 的 YYYY-MM-DD
function computeBusinessDate(date = new Date()) {
  const shanghaiMs = date.getTime() + 8 * 60 * 60 * 1000
  return new Date(shanghaiMs).toISOString().slice(0, 10)
}

function _errText(err) {
  return `${err?.errCode ?? ''} ${err?.code ?? ''} ${err?.errMsg ?? ''} ${err?.message ?? ''}`
}

function isTxConflict(err) {
  const code = `${err?.code ?? ''} ${err?.errCode ?? ''}`
  if (/TRANSACTION_CONFLICT|TRANSACTION_TIMEOUT|TRANSACTION_RETRY|TRANSACTION_ROLLBACK/i.test(code)) return true
  return /TRANSACTION.*CONFLICT|TRANSACTION_TIMEOUT|TRANSACTION_RETRY|TRANSACTION.*ROLLBACK/i.test(_errText(err))
}

function isDuplicateId(err) {
  const code = `${err?.code ?? ''} ${err?.errCode ?? ''}`
  if (/DOCUMENT_EXISTS|DUPLICATE_KEY|DATABASE_PRIMARY_KEY_CONFLICT/i.test(code)) return true
  return /DUPLICATE|already exists|E11000|DOCUMENT.*EXISTS|PRIMARY_KEY_CONFLICT/i.test(_errText(err))
}

// 仅对事务冲突指数退避重试；dup-id / 其它错误立即抛出由调用方判定
async function runWithRetry(runFn) {
  let lastErr
  for (let attempt = 0; attempt <= TX_MAX_RETRIES; attempt++) {
    try {
      return await runFn()
    } catch (err) {
      lastErr = err
      if (!isTxConflict(err) || attempt === TX_MAX_RETRIES) throw err
      await sleep(50 * Math.pow(2, attempt))
    }
  }
  throw lastErr
}

/**
 * 单批次过期入账（事务）：复核 → 置 expired → 写 store_loss → 写负向 movement。
 * 确定性 _id 保证重复执行幂等。返回 { processed, idempotent }。
 */
async function expireBatchTxn(b, businessDate) {
  // TODO(decay): 整个过期入账事务被清空，只剩最朴素的「置 expired」。
  // 需根据 scripts/test-inventory-decay.js 反推并补全：
  //   复核当前状态 / qty<=0→consumed / 非整数 qty fail-closed /
  //   写 store_loss + 负向 inventory_movements（确定性 _id 保证幂等）/
  //   dup-id 时事务外三方复核区分「已完整入账(判幂等)」vs「污染半截(计 failures 抛出)」/
  //   事务冲突指数退避重试。返回 { processed, idempotent, qty }。
  const batchId = b._id
  await db.collection('store_inventory_batch').doc(batchId).update({
    data: { status: 'expired', updatedAt: new Date() },
  })
  return { processed: true, idempotent: false, qty: b.qty || 0 }
}

exports.main = async () => {
  // cron-only 守卫（安全审查 P1）：定时触发器 / 控制台运维触发（头部注释「手动调用」）OPENID 为空；
  // 前端 wx.cloud.callFunction 携带登录态 OPENID → 拒绝。inventoryDecay 幂等无群发，守卫主要为统一
  // 三个定时任务的调用面纪律（控制台「云端测试」OPENID 仍为空，不影响运维手动触发）。
  if (cloud.getWXContext().OPENID) {
    return { errCode: 403, errMsg: 'cron only：此函数仅供定时触发器调用' }
  }
  const now = new Date()
  const businessDate = computeBusinessDate(now)
  const res = await db.collection('store_inventory_batch')
    .where({
      status: 'active',
      expiryDate: _.lt(now),
    })
    .limit(500)
    .get()

  let expired = 0
  let lossQty = 0
  let idempotentSkipped = 0
  const failures = []

  for (const b of res.data) {
    try {
      const r = await expireBatchTxn(b, businessDate)
      if (r.idempotent) {
        idempotentSkipped++
      } else if (r.processed && r.qty > 0) {
        expired++
        lossQty += r.qty
      }
    } catch (err) {
      // 单批次失败不阻塞其余批次；status 仍为 active，下次 cron 重试
      failures.push({ batchId: b._id, err: _errText(err) })
      console.error('inventoryDecay: batch failed', b._id, _errText(err))
    }
  }

  return {
    errCode: 0,
    expired,
    lossQty,
    idempotentSkipped,
    failed: failures.length,
    failures,
    scannedAt: now,
  }
}
