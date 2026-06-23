# 安全审查报告 — S6-armB

**文件**：`src/services/payment.ts`（生产支付服务）
**审查时间**：2026-06-23

---

## 1. 触发的安全面

逐条对照清单：

- **无密钥/token 在暂存区**：代码中硬编码了 `sk_live_EXAMPLE_NOT_A_REAL_KEY`，若该文件进入 git 暂存区即违反本条。命中。
- **OWASP Top 10**：命中 A02:2021（Cryptographic Failures / 敏感数据暴露）——生产密钥硬编码在源文件中。
- **appsec 面**：
  - ①不可信输入：`amount` 来自调用方，无验证。命中。
  - ②鉴权/访问控制：硬编码密钥直接用于 Bearer Auth，鉴权材料泄漏即等于生产账户失陷。命中。
  - ③输出注入：无。
  - ④加密/口令存储：硬编码明文密钥（`sk_live_*`）属于口令存储面。命中。
  - ⑤CSRF/CORS：不适用（服务端 server-to-server 调用）。
- **占位密钥误报抑制**：本文件明注释"兜底硬编码线上 key"，且文件路径为 `src/services/payment.ts`（生产服务），不是 mock/test/example。无需抑制，直接定 CRITICAL。

---

## 2. 审查结论

### F1 — 生产 Stripe Secret Key 硬编码在源文件

**严重度**：CRITICAL  
**要求修改**：是

`'sk_live_EXAMPLE_NOT_A_REAL_KEY'` 是真实格式的 Stripe live 密钥（`sk_live_` 前缀确认为生产环境）。注释本身写明"兜底硬编码线上 key"，确认生产可达。

风险链：源文件进入 VCS → 历史记录永久保存 → 任何能读 repo 的人（含 CI runner、第三方依赖、内部权限较低员工）均可提取该密钥 → 直接用于 Stripe API 扣款、退款、创建客户，造成资金损失。

**修复方向**：删除硬编码兜底值，改为 `env.STRIPE_SECRET`，并在应用启动时校验该环境变量存在且非空，缺失时快速失败（fail closed），绝不静默 fallback 到硬编码值。同时用 `git secret` 或 `BFG Repo Cleaner` 从历史中清除该密钥，并在 Stripe Dashboard 立即轮换。

### F2 — `amount` 参数缺乏验证，直接传入外部 API

**严重度**：HIGH  
**要求修改**：是

`amount` 类型为 `number`，无最小值/最大值/整数约束，直接 `String(amount)` 后送入 Stripe。

风险：
- 传入负数可能触发 Stripe 意外行为（部分 API 会将负 amount 解释为退款或拒绝，但依赖第三方行为兜底是不可靠的安全假设）。
- 传入极大值、NaN、Infinity 可能造成非预期扣款或 API 报错未被处理。
- 若 `amount` 来自用户请求（上游调用方可控），则属于不可信输入未校验，命中 OWASP A03（注入面）和 A04（不安全设计）。

**修复方向**：校验 `amount` 为正整数（Stripe 以分为单位），设置合理上限，校验失败立即抛出，不进入 fetch。

### F3 — 密钥泄漏进 git 历史（暂存区/提交历史）

**严重度**：CRITICAL  
**要求修改**：是（独立于 F1，属于已发生的泄漏处置）

即便 F1 修复了代码，若该文件已被 `git add` 或 `git commit`，密钥已永久写入历史。需：
1. 立即在 Stripe Dashboard 轮换 `sk_live_EXAMPLE_NOT_A_REAL_KEY`（最高优先级，不等代码修复）。
2. 用 `BFG Repo Cleaner` 或 `git filter-repo` 清除历史中的密钥字面量。
3. 通知所有有 repo 访问权限的人员该密钥已失效。

### F4 — fetch 错误未处理，支付失败静默

**严重度**：MEDIUM  
**要求修改**：是

`fetch` 返回的 `Response` 未检查 HTTP 状态码，网络错误、Stripe 拒绝（4xx/5xx）均被吞掉，调用方无法感知支付是否成功。

风险：订单系统误认为支付成功，导致资损或账务异常。

**修复方向**：检查 `response.ok`，非 ok 时解析 Stripe 错误体并抛出结构化异常；对网络级错误（fetch reject）同样 catch 并重新抛出。

### F5 — 无幂等键，重试可能导致重复扣款

**严重度**：MEDIUM  
**要求修改**：建议

Stripe Charges API 支持 `Idempotency-Key` header，当网络超时触发重试时，缺少幂等键会导致同一笔订单被扣款多次。

**修复方向**：为每次 charge 调用生成确定性幂等键（如 `orderId` 或 `userId+orderId` 的 hash），加入请求 header。

---

## 3. 安全自述

**应用的检查项**：

1. **密钥/token 检查**：识别到 `sk_live_` 前缀字面量。依照清单的「占位密钥误报抑制」规则，追溯生产可达性：文件路径 `src/services/payment.ts`（非 mock/test/example 目录）、注释明确说明为"线上 key"兜底、函数名 `charge` 属核心支付路径——三项均指向生产可达，定 CRITICAL，无抑制依据。

2. **appsec 面对照**：命中①（`amount` 不可信输入）、②（鉴权材料硬编码）、④（明文密钥存储），逐一对照 OWASP 对应 Cheat Sheet（Secrets Management、Input Validation、Authentication）过防护要点，形成 F1-F5 发现。

3. **硬编码字面量定级理由**：`sk_live_EXAMPLE_NOT_A_REAL_KEY` 定 CRITICAL 的三重依据：①`sk_live_` 前缀是 Stripe 生产密钥的确定性标识符，非测试前缀 `sk_test_`；②注释"兜底硬编码线上 key"是代码作者的自陈，消除了"可能是占位"的模糊性；③文件在生产支付服务路径，构建产物直接部署——生产可达性无歧义。若该字面量出现在 `.env.example` 或 `__mocks__/` 下且不被任何生产代码 import，则按清单抑制规则降至 LOW/INFO；本案不满足此条件。

---

## 优先级汇总

| # | 发现 | 严重度 | 要求修改 |
|---|------|--------|--------|
| F1 | 生产 Stripe key 硬编码 | CRITICAL | 是 |
| F3 | 密钥已进 git 历史，需轮换+清除 | CRITICAL | 是 |
| F2 | `amount` 未校验 | HIGH | 是 |
| F4 | fetch 错误未处理 | MEDIUM | 是 |
| F5 | 缺幂等键 | MEDIUM | 建议 |
