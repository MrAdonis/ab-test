/**
 * 内存版 wx-server-sdk stub（CI 无云 DB，不得已的 mock）。
 * 语义刻意贴近微信云 DB：
 *   - add 撞 _id 抛 DOCUMENT_EXISTS（幂等测试依赖）
 *   - runTransaction 失败整体回滚（快照丢弃），成功提交
 *   - 仅 doc(id) / where(eq|in|lt|gt) / orderBy / skip / limit / count / inc
 *
 * 用法见 test-inventory-decay.js / test-adminop-tx.js
 */
const Module = require('node:module')

function makeDupError() {
  const e = new Error('DOCUMENT_EXISTS: _id already exists')
  e.errCode = 'DATABASE_PRIMARY_KEY_CONFLICT'
  e.code = 'DUPLICATE_KEY'
  return e
}

function createDb() {
  const collections = {}
  const col = (name) => (collections[name] ||= new Map())

  const INC = Symbol('inc')
  const LT = Symbol('lt')
  const LTE = Symbol('lte')
  const GT = Symbol('gt')
  const GTE = Symbol('gte')
  const IN = Symbol('in')
  const AND = Symbol('and')
  const OR = Symbol('or')

  // 比较节点带 .and()/.or() 链式组合（贴近云 DB command 语义；
  // subscriptionReminder 用 _.lte(x).and(_.gte(y))）
  const cmp = (sym, v) => {
    const node = { [sym]: v }
    node.and = (other) => cmp(AND, [node, other])
    node.or = (other) => cmp(OR, [node, other])
    return node
  }

  const command = {
    inc: (n) => ({ [INC]: n }),
    lt: (v) => cmp(LT, v),
    lte: (v) => cmp(LTE, v),
    gt: (v) => cmp(GT, v),
    gte: (v) => cmp(GTE, v),
    in: (arr) => cmp(IN, arr),
  }

  const applyUpdate = (doc, data) => {
    for (const [k, v] of Object.entries(data)) {
      if (v && typeof v === 'object' && INC in v) doc[k] = (doc[k] || 0) + v[INC]
      else doc[k] = v
    }
  }

  const evalCond = (val, cond) => {
    if (cond && typeof cond === 'object') {
      if (LT in cond) return val < cond[LT]
      if (LTE in cond) return val <= cond[LTE]
      if (GT in cond) return val > cond[GT]
      if (GTE in cond) return val >= cond[GTE]
      if (IN in cond) return cond[IN].includes(val)
      if (AND in cond) return cond[AND].every((c) => evalCond(val, c))
      if (OR in cond) return cond[OR].some((c) => evalCond(val, c))
    }
    return val === cond
  }

  const matches = (doc, cond) =>
    Object.entries(cond).every(([k, v]) => evalCond(doc[k], v))

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
        remove: async () => { const existed = m.has(id); m.delete(id); return { stats: { removed: existed ? 1 : 0 } } },
      }),
      add: async ({ data }) => {
        const id = data._id != null ? data._id : `auto_${Math.random().toString(36).slice(2)}`
        if (m.has(id)) throw makeDupError()
        m.set(id, { ...data, _id: id })
        return { _id: id }
      },
      where: (cond) => {
        // field() 是 projection 优化（省带宽），stub 视作 no-op 直通——
        // 生产代码 .where().field({k:true}).limit().get() 不能在测试里 break 链。
        const build = (orders, lim, sk) => ({
          field: () => build(orders, lim, sk),
          orderBy: (f, dir) => build([...orders, [f, dir]], lim, sk),
          skip: (n) => build(orders, lim, n),
          limit: (n) => build(orders, n, sk),
          get: async () => {
            let rows = [...m.values()].filter((d) => matches(d, cond))
            for (const [f, dir] of orders) {
              rows.sort((a, b) => (a[f] < b[f] ? -1 : a[f] > b[f] ? 1 : 0) * (dir === 'desc' ? -1 : 1))
            }
            if (sk != null) rows = rows.slice(sk)
            if (lim != null) rows = rows.slice(0, lim)
            return { data: rows.map((d) => ({ ...d })) }
          },
          count: async () => ({ total: [...m.values()].filter((d) => matches(d, cond)).length }),
        })
        return build([], null, null)
      },
    }
  }

  const db = {
    command,
    serverDate: () => new Date(),
    collection: collectionApi((n) => col(n)),
    runTransaction: async (fn) => {
      const snap = {}
      for (const [n, mm] of Object.entries(collections)) {
        snap[n] = new Map([...mm].map(([k, v]) => [k, { ...v }]))
      }
      const txStore = (n) => (snap[n] ||= new Map())
      const tx = { collection: collectionApi(txStore) }
      const r = await fn(tx) // 抛出 → snap 不提交（回滚）
      for (const [n, mm] of Object.entries(snap)) collections[n] = mm
      return r
    },
    // 显式事务 API（createSubscription 用 startTransaction/commit/rollback）。
    // 语义同 runTransaction：快照隔离，commit 一次性写回，rollback/未 commit
    // 丢弃快照；事务内 add 撞 _id 仍抛 DOCUMENT_EXISTS（首写代次主键冲突收敛）。
    startTransaction: async () => {
      const snap = {}
      for (const [n, mm] of Object.entries(collections)) {
        snap[n] = new Map([...mm].map(([k, v]) => [k, { ...v }]))
      }
      const txStore = (n) => (snap[n] ||= new Map())
      let settled = false
      return {
        collection: collectionApi(txStore),
        commit: async () => {
          if (settled) return
          settled = true
          for (const [n, mm] of Object.entries(snap)) collections[n] = mm
        },
        rollback: async () => { settled = true }, // 丢弃快照
      }
    },
  }
  return { db, collections, col }
}

/**
 * 拦截 require('wx-server-sdk')，注入指定的 db + 当前调用者 openid。
 * 返回 { setOpenid, loadFresh(absPath) }。
 */
function installStub(getDb, initialOpenid = '') {
  let currentOpenid = initialOpenid
  // 跨函数调用桩（subscriptionReminder 取消前查单闸 → paymentCallback queryAndReconcile）。
  // 默认 NOTPAY = 微信侧确认未付 → 放行取消（保持「弃单收口」语义）。需要模拟「已支付」
  // 或「查单失败」的用例用 setCallFunction 覆写。
  let callFunctionImpl = async () => ({
    result: { errCode: 0, tradeState: 'NOTPAY', settled: false, status: 'pending' },
  })
  // 主动查单桩（paymentCallback reconcileOne → ./wxpay-query queryByOutTradeNo）。
  // 个人版唯一结算路径是「查单对账」：前端支付成功后调 queryAndReconcile，函数查微信
  // 拿 trade_state 落账。真模块需商户密钥 + 走 HTTPS，CI 无法跑 → 桩可控返回。
  // 默认 NOTFOUND = 微信侧查不到该单（未拉起支付）→ 不落账。用 setQueryResult 模拟
  // SUCCESS 驱动结算。返回结构对齐微信查单明文：{ trade_state, transaction_id,
  // amount:{total}, payer:{openid} }。
  let queryResultImpl = async () => ({ trade_state: 'NOTFOUND' })
  const stub = {
    init: () => {},
    get DYNAMIC_CURRENT_ENV() { return 'test-env' },
    database: () => getDb(),
    getWXContext: () => ({ OPENID: currentOpenid }),
    callFunction: (args) => callFunctionImpl(args),
    // 微信预下单：纯 WeChat API 包装，无本项目业务逻辑。桩返回假预付参数，
    // 让 createSubscription 的 wechat 路径干净跑完（真正入账在 paymentCallback）。
    cloudPay: {
      unifiedOrder: async ({ outTradeNo, totalFee }) => ({
        returnCode: 'SUCCESS', resultCode: 'SUCCESS',
        payment: { timeStamp: '0', nonceStr: 'test', package: `prepay_id=test_${outTradeNo}`, totalFee },
      }),
    },
  }
  const origLoad = Module._load
  Module._load = function (request, parent) {
    if (request === 'wx-server-sdk') return stub
    // createSubscription 的 v3 JSAPI 下单模块（真模块需商户密钥 + 走 HTTPS）。
    // 桩返回假预付参数让 wechat 下单路径干净跑完（真正入账在 paymentCallback 查单对账）。
    if (request === './wxpay' && parent && /createSubscription[/\\]index\.js$/.test(parent.filename)) {
      return {
        createJsapiPayment: async ({ outTradeNo }) => ({
          timeStamp: '0', nonceStr: 'test', package: `prepay_id=test_${outTradeNo}`,
          signType: 'RSA', paySign: 'fake-sign',
        }),
        buildPayParams: () => ({ timeStamp: '0', nonceStr: 'test', package: 'prepay_id=test', signType: 'RSA', paySign: 'fake-sign' }),
      }
    }
    // 仅拦截 paymentCallback 对查单模块的 require（按 parent 文件名锚定，不误伤他处）。
    if (request === './wxpay-query' && parent && /paymentCallback[/\\]index\.js$/.test(parent.filename)) {
      return { queryByOutTradeNo: (...a) => queryResultImpl(...a) }
    }
    return origLoad.apply(this, arguments)
  }
  return {
    setOpenid: (o) => { currentOpenid = o },
    // 覆写查单返回（paymentCallback reconcileOne 的微信查单响应）。传 null/不传恢复默认 NOTFOUND。
    setQueryResult: (fn) => {
      queryResultImpl = fn || (async () => ({ trade_state: 'NOTFOUND' }))
    },
    // 覆写跨函数调用返回（取消前查单闸的 paymentCallback 响应）。传 null/不传恢复默认 NOTPAY。
    setCallFunction: (fn) => {
      callFunctionImpl = fn || (async () => ({
        result: { errCode: 0, tradeState: 'NOTPAY', settled: false, status: 'pending' },
      }))
    },
    loadFresh: (absPath) => {
      delete require.cache[require.resolve(absPath)]
      return require(absPath)
    },
  }
}

module.exports = { createDb, installStub, makeDupError }
