实现之前有一个关键决策点必须先说清楚，因为它决定了整个方案的架构和风险敞口。

## 先定architecture：这个"退款"按钮到底退款权在谁手里

"后台一键退款"字面上看是标配功能，但本质是给系统开了一个**能直接把钱打出去、且不可逆**的接口。任何越权、状态机漏洞、重放，损失都是真实资金，不是脏数据。业内对这类功能的默认档是：

- **方案 A（推荐默认）**：管理员在微信商户平台人工发起退款（真实打款这一步完全不经过我们的代码，天然有微信侧的风控和对账）。后台的「退款」按钮只做**状态同步**：管理员输入微信给的退款流水号作为凭证，云函数校验权限+幂等+状态机后，把订单标记为已退款、库存加回去。
- **方案 B（程序化一键退款）**：云函数直接调微信支付退款 API 自动打钱。只有在人工退款量大到扛不住时才值得建，且必须同时具备：审批流（发起≠执行）、单笔/日累计限额、幂等令牌、审计留痕、与商户平台的定期对账——这些不是可选项，少一条这个接口就是一个可被滥用/误操作的资金漏洞。

下面按**方案 A** 给完整可落地代码（如果你确认走方案 B，我再补审批流+限额+微信退款 API 签名那部分，工作量和测试要求都高不少）。

## 数据库改动

`orders` 集合新增字段（不新建集合，展开字段方便建索引）：

```
status          — 状态机新增终态 REFUNDED
refundNo        — 管理员登记的微信退款流水号（字符串，必填才允许提交）
refundOperator  — 操作管理员的 openid
refundOperatorName — 冗余展示用
refundAmount    — 退款金额，直接取 order.totalAmount，不重新计算（价目表可能已变，退款金额只能是订单当时的权威快照）
refundReason    — 可选，管理员填写
refundTime      — db.serverDate()
```

`orders.items[]` 本身已有 `productId` + `quantity`，退库存直接用这个快照，**不查当前商品表的 SKU 结构重算**（商品可能已下架/改过规格）。

新增（若项目还没有）`audit_logs` 集合，记录谁在什么时候对哪个订单做了退款登记。

**集合权限**（上线前逐集合手动锁，代码建不了）：`orders` 客户端不可写；`products` 客户端不可写；`audit_logs` 客户端不可读写。全部写入走云函数（云函数天然不受集合客户端权限约束）。

## 云函数 orderRefund

```js
// cloudfunctions/orderRefund/index.js
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const _ = db.command

// 只有这些状态允许发起退款登记，按项目实际状态机调整
const REFUNDABLE_STATUS = ['PAID', 'PENDING_SHIPMENT', 'PENDING_RECEIPT']

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const { orderId, refundNo, refundReason } = event

  if (!orderId || typeof orderId !== 'string') {
    return { ok: false, code: 'INVALID_PARAM', msg: '缺少 orderId' }
  }
  if (!refundNo || typeof refundNo !== 'string' || !refundNo.trim()) {
    return { ok: false, code: 'INVALID_PARAM', msg: '缺少微信退款流水号，请先在商户平台完成退款' }
  }

  // 权限闸：role 一律由服务端查表判定，不信任前端传来的任何身份字段
  const adminSnap = await db.collection('admins').where({ _openid: OPENID }).limit(1).get()
  const operator = adminSnap.data[0]
  if (!operator || operator.role !== 'admin') {
    return { ok: false, code: 'FORBIDDEN', msg: '无权限执行退款操作' }
  }

  let txResult
  try {
    txResult = await db.runTransaction(async (transaction) => {
      const orderDoc = await transaction.collection('orders').doc(orderId).get()
      const order = orderDoc.data
      if (!order) return { ok: false, code: 'NOT_FOUND', msg: '订单不存在' }

      // 幂等短路必须排在业务状态校验之前——重复点击/请求重放时直接返回已处理结果，
      // 不再往下走状态机校验和库存回滚等有副作用的分支
      if (order.status === 'REFUNDED') {
        return { ok: true, idempotent: true, data: { orderId, status: 'REFUNDED' } }
      }

      if (!REFUNDABLE_STATUS.includes(order.status)) {
        return { ok: false, code: 'INVALID_STATUS', msg: `当前状态[${order.status}]不允许退款` }
      }

      await transaction.collection('orders').doc(orderId).update({
        data: {
          status: 'REFUNDED',
          refundNo: refundNo.trim(),
          refundOperator: OPENID,
          refundOperatorName: operator.nickName || '',
          refundAmount: order.totalAmount,
          refundReason: refundReason || '',
          refundTime: db.serverDate(),
        },
      })

      // 库存回滚：按订单快照的 items 逐条加回
      for (const item of order.items || []) {
        await transaction.collection('products').doc(item.productId).update({
          data: { stock: _.inc(item.quantity) },
        })
      }

      return { ok: true, idempotent: false, data: { orderId, status: 'REFUNDED', refundAmount: order.totalAmount } }
    })
  } catch (e) {
    console.error('[orderRefund] transaction failed', e)
    return { ok: false, code: 'TX_FAILED', msg: '退款登记失败，请重试' }
  }

  // 审计日志——fire-and-forget，失败只 warn，不回滚已成功的业务结果
  if (txResult.ok && !txResult.idempotent) {
    db.collection('audit_logs').add({
      data: {
        operatorId: OPENID,
        operatorRole: 'admin',
        action: 'order.refund',
        targetId: orderId,
        detail: { refundNo: refundNo.trim(), refundAmount: txResult.data.refundAmount, refundReason: refundReason || '' },
        createdAt: db.serverDate(),
      },
    }).catch((e) => console.warn('[orderRefund] audit log failed', e))
  }

  return txResult
}
```

关键设计点：状态迁移和库存回滚在同一个 `runTransaction` 里完成，文档级读写天然序列化，两个管理员同时点/网络重试不会导致库存被回滚两次；幂等检查在事务内、且排在状态机校验之前，这是支付回调同款的强制顺序，退款登记同样会被重放（用户手抖双击、前端断网重试）。

## 后台前端接入（小程序管理端）

```js
// packages/admin/pages/order-detail/index.js
Page({
  data: { order: null, submitting: false },

  onRefundTap() {
    if (this.data.submitting) return
    const { orderId } = this.data.order

    wx.showModal({
      title: '登记退款',
      editable: true,
      placeholderText: '请输入微信支付退款单号',
      success: async (res) => {
        if (!res.confirm) return
        const refundNo = (res.content || '').trim()
        if (!refundNo) {
          wx.showToast({ title: '请输入退款单号', icon: 'none' })
          return
        }
        this.setData({ submitting: true })
        const result = await cloud.call('orderRefund', { orderId, refundNo }).finally(() => {
          this.setData({ submitting: false })
        })
        if (!result.ok) {
          wx.showToast({ title: result.msg || '操作失败', icon: 'none' })
          return
        }
        wx.showToast({ title: result.data.idempotent ? '该订单已退款' : '退款登记成功', icon: 'success' })
        this.loadOrder(orderId)
      },
    })
  },
})
```

```xml
<button wx:if="{{['PAID','PENDING_SHIPMENT','PENDING_RECEIPT'].indexOf(order.status) > -1}}"
        disabled="{{submitting}}" bindtap="onRefundTap">退款</button>
<text wx:if="{{order.status === 'REFUNDED'}}">已退款 · 单号 {{order.refundNo}}</text>
```

`cloud.call` 是项目里统一封装的 `{ok:true,data} / {ok:false,code,msg}` 调用契约，按你项目现有的 `utils/cloud.js` 对齐即可。

## 三个可调整的假设

我按常见结构给了默认实现，落地时按实际项目改：

1. 权限查表：假设有独立 `admins` 集合按 `_openid` 存 role。如果你项目是 `users` 集合带 `role` 字段，云函数里改一行查询即可。
2. 管理后台形态：假设是小程序管理端（走 `wx.cloud.callFunction`，身份靠 `wxContext.OPENID`）。如果是独立 Web 后台调 HTTP 触发云函数，鉴权要换成后台账号体系，不能再靠 OPENID。
3. 全额退款：按订单整体一次性退款设计，状态直接终态化。如果要支持部分退款（订单里只退某几件商品），需要重新设计成"一订单多退款记录"，复杂度和测试量都上一个台阶，建议先按全额上线。

方案 B（全自动打款）要补的东西，如果后续确认要走：拆成 `orderRefundApply`（校验+调微信退款 API，不改库存）+ `refundNotify`（微信异步回调，验签解密后才真正改状态回库存，同一套幂等优先于状态校验的顺序）两个云函数，外加审批流、单笔/日限额、幂等令牌、定时对账任务——这部分我需要先确认你们支付走的是云调用 `cloud.cloudPay` 还是自建商户号 APIv3 直连,才能给出准确的签名/证书细节。
