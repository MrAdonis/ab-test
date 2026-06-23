/**
 * inventoryDecay 集成测试
 *
 * 微信云 DB 在 CI 不可达，这里用内存版 wx-server-sdk stub（不得已的 mock）
 * 跑真实的 inventoryDecay/index.js 代码路径，验证：
 *   1. 过期批次：置 expired + 写 store_loss + 写「负向」inventory_movements
 *   2. 重复执行幂等（status 过滤 → 第二次扫不到）
 *   3a. dup-id 但账记录完整（batch 已 expired + loss + movement 均在）→ 真幂等跳过
 *   3b. dup-id 但污染/半截（batch 仍 active 或账缺失）→ 计入 failures，不静默吞
 *   4. qty<=0 批次仅置 consumed，不产生损耗账
 *
 * 运行：node --test scripts/test-inventory-decay.js
 *
 * stub 语义刻意贴近云 DB：add 撞 _id 抛 DOCUMENT_EXISTS；
 * runTransaction 失败整体回滚（快照丢弃）。
 */
const test = require('node:test')
const assert = require('node:assert/strict')
const path = require('node:path')
const Module = require('node:module')

const DECAY_PATH = path.join(__dirname, '..', 'miniprogram', 'cloudfunctions', 'inventoryDecay', 'index.js')

function makeDupError() {
  const e = new Error('DOCUMENT_EXISTS: _id already exists')
  e.errCode = 'DATABASE_PRIMARY_KEY_CONFLICT'
  e.code = 'DUPLICATE_KEY'
  return e
}

// 内存数据库：collections[name] = Map(_id -> doc)
function createDb() {
  const collections = {}
  const col = (name) => (collections[name] ||= new Map())

  const INC = Symbol('inc')
  const LT = Symbol('lt')
  const GT = Symbol('gt')

  const command = {
    inc: (n) => ({ [INC]: n }),
    lt: (v) => ({ [LT]: v }),
    gt: (v) => ({ [GT]: v }),
  }

  const applyUpdate = (doc, data) => {
    for (const [k, v] of Object.entries(data)) {
      if (v && typeof v === 'object' && INC in v) doc[k] = (doc[k] || 0) + v[INC]
      else doc[k] = v
    }
  }

  const matches = (doc, cond) => {
    for (const [k, v] of Object.entries(cond)) {
      if (v && typeof v === 'object' && LT in v) {
        if (!(doc[k] < v[LT])) return false
      } else if (v && typeof v === 'object' && GT in v) {
        if (!(doc[k] > v[GT])) return false
      } else if (doc[k] !== v) {
        return false
      }
    }
    return true
  }

  // store 工厂：传入目标 Map（真实 store 或事务快照）
  const collectionApi = (store) => (name) => {
    const m = store(name)
    return {
      doc: (id) => ({
        get: async () => ({ data: m.has(id) ? { ...m.get(id) } : null }),
        update: async ({ data }) => {
          if (!m.has(id)) throw new Error('UPDATE_MISSING')
          const d = { ...m.get(id) }
          applyUpdate(d, data)
          m.set(id, d)
        },
        set: async ({ data }) => m.set(id, { _id: id, ...data }),
      }),
      add: async ({ data }) => {
        const id = data._id != null ? data._id : `auto_${Math.random().toString(36).slice(2)}`
        if (m.has(id)) throw makeDupError()
        m.set(id, { ...data, _id: id })
        return { _id: id }
      },
      where: (cond) => {
        const build = (orders, lim) => ({
          orderBy: (f, dir) => build([...orders, [f, dir]], lim),
          limit: (n) => build(orders, n),
          get: async () => {
            let rows = [...m.values()].filter((d) => matches(d, cond))
            for (const [f, dir] of orders) {
              rows.sort((a, b) => (a[f] < b[f] ? -1 : a[f] > b[f] ? 1 : 0) * (dir === 'desc' ? -1 : 1))
            }
            if (lim != null) rows = rows.slice(0, lim)
            return { data: rows.map((d) => ({ ...d })) }
          },
          count: async () => ({ total: [...m.values()].filter((d) => matches(d, cond)).length }),
        })
        return build([], null)
      },
    }
  }

  const db = {
    command,
    serverDate: () => new Date(),
    collection: collectionApi((n) => col(n)),
    runTransaction: async (fn) => {
      // 快照所有集合；失败丢弃，成功提交
      const snap = {}
      for (const [n, m] of Object.entries(collections)) snap[n] = new Map([...m].map(([k, v]) => [k, { ...v }]))
      const txStore = (n) => (snap[n] ||= new Map())
      const tx = { collection: collectionApi(txStore) }
      try {
        const r = await fn(tx)
        for (const [n, m] of Object.entries(snap)) collections[n] = m
        return r
      } catch (err) {
        throw err // 回滚：snap 不提交
      }
    },
  }
  return { db, collections, col }
}

let dbCtx
let currentOpenid = '' // cron/控制台运维触发为空；前端登录态调用非空
const stub = {
  init: () => {},
  get DYNAMIC_CURRENT_ENV() { return 'test-env' },
  database: () => dbCtx.db,
  getWXContext: () => ({ OPENID: currentOpenid }),
}

// 拦截 require('wx-server-sdk')
const origLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'wx-server-sdk') return stub
  return origLoad.apply(this, arguments)
}

function loadDecayFresh() {
  delete require.cache[require.resolve(DECAY_PATH)]
  return require(DECAY_PATH)
}

const past = new Date(Date.now() - 86400000) // 昨天，已过期
const future = new Date(Date.now() + 86400000)

test('cron-only: 前端带 OPENID 直调 → 403，过期批次不被处理', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('g1', {
    _id: 'g1', storeId: 's1', sku: 'SKU1', qty: 7, status: 'active', expiryDate: past,
  })
  currentOpenid = 'op_attacker' // 模拟前端登录态直调
  try {
    const r = await loadDecayFresh().main()
    assert.equal(r.errCode, 403, '非空 OPENID 被 cron-only 守卫拦截')
    assert.equal(dbCtx.col('store_inventory_batch').get('g1').status, 'active', '守卫先于业务返回，过期批次未被置 expired')
  } finally {
    currentOpenid = '' // 恢复 cron 上下文，不污染后续测试
  }
})

test('过期批次：expired + store_loss + 负向 movement', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('b1', {
    _id: 'b1', storeId: 's1', sku: 'SKU1', qty: 7, status: 'active', expiryDate: past,
  })
  dbCtx.col('store_inventory_batch').set('b2', {
    _id: 'b2', storeId: 's1', sku: 'SKU2', qty: 3, status: 'active', expiryDate: future,
  })

  const r = await loadDecayFresh().main()

  assert.equal(r.errCode, 0)
  assert.equal(r.expired, 1)
  assert.equal(r.lossQty, 7)
  assert.equal(r.failed, 0)

  const b1 = dbCtx.col('store_inventory_batch').get('b1')
  assert.equal(b1.status, 'expired')
  assert.equal(dbCtx.col('store_inventory_batch').get('b2').status, 'active') // 未过期不动

  const loss = dbCtx.col('store_loss').get('expiry_b1')
  assert.ok(loss, 'store_loss 确定性 _id 必须写入')
  assert.equal(loss.qty, 7)
  assert.equal(loss.reason, 'expired')
  assert.equal(loss.autoGenerated, true)

  const mv = dbCtx.col('inventory_movements').get('decay_b1')
  assert.ok(mv, 'inventory_movements 确定性 _id 必须写入')
  assert.equal(mv.qtyDelta, -7, 'P2-2 对账依赖负向 qtyDelta')
  assert.equal(mv.movementType, 'loss')
  assert.equal(mv.reason, 'expired')
  assert.equal(mv.lossId, 'expiry_b1')
})

test('重复执行幂等：第二次扫不到 active', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('b1', {
    _id: 'b1', storeId: 's1', sku: 'SKU1', qty: 5, status: 'active', expiryDate: past,
  })

  await loadDecayFresh().main()
  const lossCount1 = dbCtx.col('store_loss').size
  const mvCount1 = dbCtx.col('inventory_movements').size

  const r2 = await loadDecayFresh().main()

  assert.equal(r2.expired, 0)
  assert.equal(dbCtx.col('store_loss').size, lossCount1, '不得重复写 store_loss')
  assert.equal(dbCtx.col('inventory_movements').size, mvCount1, '不得重复写 movement')
})

test('已完整入账：batch 已 expired → main 的 status 过滤直接跳过，零副作用', async () => {
  dbCtx = createDb()
  // 上次已完整入账的最常见幂等路径：batch 非 active，被 main 的 where(status:'active') 过滤
  dbCtx.col('store_inventory_batch').set('b1', {
    _id: 'b1', storeId: 's1', sku: 'SKU1', qty: 9, status: 'expired', expiryDate: past,
  })
  dbCtx.col('store_loss').set('expiry_b1', { _id: 'expiry_b1', batchId: 'b1', qty: 9 })
  dbCtx.col('inventory_movements').set('decay_b1', { _id: 'decay_b1', batchId: 'b1', qtyDelta: -9 })

  const r = await loadDecayFresh().main()

  assert.equal(r.expired, 0, '已 expired 不再处理')
  assert.equal(r.failed, 0, '完整入账不算失败')
  assert.equal(dbCtx.col('store_loss').size, 1, 'loss 不被重复写')
  assert.equal(dbCtx.col('inventory_movements').size, 1, 'movement 不被重复写')
})

test('dup-id 但污染/半截：batch 仍 active + 账缺失 → 计入 failures 不静默吞', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('b1', {
    _id: 'b1', storeId: 's1', sku: 'SKU1', qty: 9, status: 'active', expiryDate: past,
  })
  // 预置一条孤立 / 被污染的 loss（无对应 movement），事务内 loss.add 撞 dup → 回滚
  dbCtx.col('store_loss').set('expiry_b1', { _id: 'expiry_b1', batchId: 'b1', qty: 9 })

  const r = await loadDecayFresh().main()

  assert.equal(r.idempotentSkipped, 0, '污染场景绝不能算幂等跳过')
  assert.equal(r.expired, 0)
  assert.equal(r.failed, 1, 'batch 仍 active + 账不完整 → 必须可见失败')
  assert.match(r.failures[0].err, /DECAY_DUP_INCONSISTENT/)
  assert.equal(dbCtx.col('inventory_movements').size, 0, 'movement 随事务回滚不写')
  assert.equal(dbCtx.col('store_inventory_batch').get('b1').status, 'active', '事务回滚 → batch 不变（但已计入 failures，运维可见）')
})

test('qty<=0 批次仅置 consumed，无损耗账', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('b0', {
    _id: 'b0', storeId: 's1', sku: 'SKU0', qty: 0, status: 'active', expiryDate: past,
  })

  const r = await loadDecayFresh().main()

  assert.equal(r.expired, 0)
  assert.equal(r.lossQty, 0)
  assert.equal(dbCtx.col('store_inventory_batch').get('b0').status, 'consumed')
  assert.equal(dbCtx.col('store_loss').size, 0)
  assert.equal(dbCtx.col('inventory_movements').size, 0)
})

test('小数 qty 脏批次 fail-closed：计入 failures，不写小数损耗账/movement，批次留 active (codex-e2e round4 P2)', async () => {
  dbCtx = createDb()
  dbCtx.col('store_inventory_batch').set('bfrac', {
    _id: 'bfrac', storeId: 's1', sku: 'SKU1', qty: 1.5, status: 'active', expiryDate: past,
  })

  const r = await loadDecayFresh().main()

  assert.equal(r.errCode, 0)
  assert.equal(r.expired, 0, '小数批次不计入正常过期')
  assert.equal(r.lossQty, 0, '不累计小数损耗')
  assert.equal(r.failed, 1, '小数批次计入 failures 供运维排查')
  assert.match(r.failures[0].err, /DECAY_NONINTEGER_QTY/)
  assert.equal(dbCtx.col('store_inventory_batch').get('bfrac').status, 'active', '批次保持 active，不被误 expired')
  assert.equal(dbCtx.col('store_loss').size, 0, '无小数 store_loss')
  assert.equal(dbCtx.col('inventory_movements').size, 0, '无小数 movement')
})
