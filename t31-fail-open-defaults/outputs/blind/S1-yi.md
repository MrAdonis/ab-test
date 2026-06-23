# S1 安全审查 — Arm A

## 1. 清单逐条对照

1. **无密钥/token 在暂存区** — 不命中（代码审查，非 git 暂存区检查；但见条目 3 中 JWT_SECRET 的 fail-open 问题）
2. **无新增 OWASP Top 10 漏洞** — 命中（存在 fail-open 默认密钥，属 A02 Cryptographic Failures）
3. **appsec 面对照** — 命中多个安全面，触发详细审查（见下）：
   - ① 不可信输入：`req.json()` 无验证，外部来源直接解构
   - ② 鉴权/session：JWT 签发逻辑，直接处理认证令牌
   - ③ 输出注入：无（Response.json 无下游注入 sink）
   - ④ 加密/口令存储：JWT_SECRET 有 fail-open 默认值；`verifyHash` 实现不可见但存在口令校验路径
   - ⑤ CSRF/CORS：不命中（Workers 无内置 CORS 设置，但无浏览器交互 context）

## 2. 审查结论

**真实安全问题 2 个：**

**P0 — Fail-open JWT_SECRET 默认值**

```js
const secret = env.JWT_SECRET || 'dev-secret-change-me'
```

`env.JWT_SECRET` 未配置时静默降级为硬编码字符串 `'dev-secret-change-me'`，Worker 仍正常运行、签发 JWT，攻击者知道默认值即可伪造任意令牌。这是典型的 fail-open：系统在密钥缺失（配置错误、部署疏漏）时不拒绝服务，而是用已知弱密钥继续工作。

OWASP 对照：[Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) — 密钥必须来自安全配置，不得有可预测 fallback。

**修复：** 移除 `|| 'dev-secret-change-me'`，缺失时抛异常终止请求：
```js
const secret = env.JWT_SECRET
if (!secret) return new Response('Server misconfiguration', { status: 500 })
```

**P1 — 缺少请求体输入校验**

`await req.json()` 无 try/catch，且解构后的 `email`/`password` 未做类型/格式验证。若请求体非 JSON 或字段缺失，会产生未处理异常（500）或以 `undefined` 查库。`email` 作为参数化查询的绑定值是安全的（无 SQL 注入风险），但 `password` 传入 `verifyHash` 时若值为 `undefined`/`null`，行为取决于 `verifyHash` 实现，有潜在 bypass 风险。

OWASP 对照：[Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) — 所有外部输入必须在业务逻辑前验证类型和格式。

**修复：**
```js
let email, password
try {
  ({ email, password } = await req.json())
} catch {
  return new Response('Bad request', { status: 400 })
}
if (typeof email !== 'string' || typeof password !== 'string' || !email || !password) {
  return new Response('Bad request', { status: 400 })
}
```

**无问题项：**
- SQL 注入：D1 参数化绑定 (`bind(email)`) 正确，不命中
- 认证逻辑：`verifyHash` + 401 的失败处理结构正确，无 timing oracle 可见问题（取决于 verifyHash 实现）
- 响应内容：不泄露用户是否存在（`!user || !verifyHash(...)` 合并为同一 401）

## 3. 自述

**应用的检查：**
- 清单条目 2：扫描已知 OWASP Top 10 类别，命中 A02（弱/可预测密钥）
- 清单条目 3：触发 appsec 面对照——识别到①不可信输入（req.json 外部来源）和④加密/口令存储（JWT_SECRET 路径），对照对应 OWASP Cheat Sheet 过防护要点

**跳过的检查：**
- 清单条目 1（暂存区密钥扫描）：仅代码片段，无 git context，无法执行
- appsec 面③输出注入/⑤CSRF·CORS：③ Response.json 无 HTML/SQL/shell sink；⑤ 登录接口为 API endpoint，无状态 Cookie session，CSRF 不适用；两者均满足跳过条件（无对应 sink 或不适用场景）
