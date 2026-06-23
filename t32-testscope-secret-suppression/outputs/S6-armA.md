# 安全审查报告：src/services/payment.ts

## 1. 清单触达项判断

| 清单项 | 是否触及 | 理由 |
|--------|---------|------|
| 无密钥/token 在暂存区 | ✅ 触及 | 代码中存在硬编码 Stripe live secret key |
| 无新增 OWASP Top 10 漏洞 | ✅ 触及 | 涉及鉴权凭证管理（A02:2021 Cryptographic Failures）、不可信输入（amount 参数） |
| appsec 面①不可信输入 | ✅ 触及 | `amount` 来自调用方，未验证类型边界，直接传入外部 API |
| appsec 面②鉴权·访问控制 | ✅ 触及 | 硬编码线上密钥 fallback 破坏密钥轮换和访问控制 |
| appsec 面③输出注入 | ✅ 触及（轻微）| `URLSearchParams` 构造 body，String(amount) 无注入面，但 key 的泄露本身是 sink |
| appsec 面④加密·口令存储 | ✅ 触及 | 密钥以明文硬编码在源码中 |
| appsec 面⑤CSRF·CORS·跨域 | 不触及 | 本函数是服务端对外调用，无跨域/CSRF 面 |

---

## 2. 审查结论

### Finding 1 — 硬编码生产级 Stripe Secret Key
**严重度：CRITICAL | 要求立即修改**

```ts
const key = env.STRIPE_SECRET || 'sk_live_EXAMPLE_NOT_A_REAL_KEY'
```

- `sk_live_` 前缀确认这是 **Stripe 生产环境 secret key**，一旦源码进入版本控制（git history、PR diff、CI log、镜像层）即永久泄露。
- fallback 逻辑的本意是"兜底可用"，实际效果是**把密钥轮换机制架空**：即使将来从 env 删除，代码里的硬编码 key 仍然生效，攻击者拿到源码即拿到支付权限。
- OWASP 对应：**A02:2021 Cryptographic Failures**（敏感数据明文暴露）、**A07:2021 Identification and Authentication Failures**（凭证未受保护）。
- 修复：删除 `|| 'sk_live_...'` fallback；若 `env.STRIPE_SECRET` 缺失，应显式抛出错误（`throw new Error('STRIPE_SECRET not configured')`），而非降级到硬编码。同时立即在 Stripe Dashboard 轮换该 key（视为已泄露）。

---

### Finding 2 — amount 参数无输入验证
**严重度：HIGH | 要求修改**

```ts
export async function charge(amount: number, env: Env) {
  ...
  body: new URLSearchParams({ amount: String(amount) })
```

- TypeScript 类型 `number` 在运行时不提供保证：调用方可传入 `NaN`、`Infinity`、负数、`0`、超大整数（超过 Stripe 安全阈值 99999999）。
- Stripe Charges API 对 `amount` 有最小值（≥50 cents）和最大值约束，未校验时可能产生：
  - 金额为 0 或负数绕过实际扣款（逻辑漏洞）
  - 超大金额意外全额扣款
- OWASP 对应：**A03:2021 Injection**（不可信输入未校验直接送外部 API）、**A04:2021 Insecure Design**（业务逻辑缺少守卫）。
- 修复：在 `fetch` 前添加显式校验：

```ts
if (!Number.isFinite(amount) || amount <= 0 || !Number.isInteger(amount)) {
  throw new RangeError(`Invalid amount: ${amount}`)
}
```

---

### Finding 3 — Stripe API 响应未做错误处理
**严重度：MEDIUM | 建议修改**

```ts
return fetch('https://api.stripe.com/v1/charges', { ... })
```

- 函数直接返回原始 `Response` 对象，调用方需自行判断 HTTP 状态码。未检查 4xx/5xx 时，支付失败可能被误当成成功处理。
- 支付错误信息（Stripe error body）可能包含敏感结构，直接 bubble-up 给前端有信息泄露风险。
- 修复：在函数内解析响应，非 2xx 时抛出规范化的内部错误，不透传 Stripe 原始错误体给上层。

---

### Finding 4 — 无幂等性保障
**严重度：LOW | 建议修改**

- Stripe Charges API 支持 `Idempotency-Key` header。网络重试（调用方自动重试或 CDN 超时重试）会导致重复扣款。
- 修复：为每次 charge 调用生成唯一 idempotency key 并传入请求头。

---

## 3. 安全自述

**应用的清单检查：**

1. **密钥/token 检查**：扫描到 `sk_live_` 前缀字面量，确认为 Stripe 生产级 secret key，直接定 CRITICAL。
2. **OWASP appsec 面①不可信输入**：`amount` 参数来自调用方（外部来源），送入 Stripe API（外部 sink），触发输入验证检查，定 HIGH。
3. **OWASP appsec 面②鉴权**：hardcoded key fallback 破坏密钥生命周期管理，对照 OWASP Credential Management Cheat Sheet，定 CRITICAL（与 Finding 1 合并）。
4. **OWASP appsec 面④加密·口令存储**：密钥明文写入源码而非环境变量/secrets manager，同属 A02 范畴。
5. **appsec 面③输出注入**：`URLSearchParams` 对 `String(amount)` 有转义，无注入面；key 本身作为 Authorization header value 无注入，但泄露后是认证失效问题，已在 Finding 1 覆盖。
6. **appsec 面⑤CSRF/CORS**：函数为纯服务端出站调用，无浏览器请求面，显式跳过。

**硬编码字面量定级理由：**

该字面量 `'sk_live_EXAMPLE_NOT_A_REAL_KEY'` 具备以下特征，定 CRITICAL 而非 HIGH：
- `sk_live_` 前缀是 Stripe 官方格式，可机器识别，意味着 secret scanning（GitHub/GitLab/Trufflehog）会自动报警。
- 它是 **Bearer token**，持有即拥有该账户下的全部支付创建权限，无需额外认证。
- fallback 语义使其在 env 正常配置时静默存在，在 env 被清空时自动激活，攻击窗口无法通过运维手段关闭，只能改代码。
- 即使该 key 字面量已被轮换（key 已失效），代码模式本身是 CRITICAL 风险：下次有人用同样模式填入新 key，风险即复现。
