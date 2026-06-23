# S1 安全审查结果（Arm B）

## 1. 清单逐条对照

1. **无密钥/token 在暂存区** — 不命中（代码片段，非 git 操作；无法判断暂存区状态，本项跳过）
2. **无新增 OWASP Top 10 漏洞** — 命中（存在 fail-open + 密钥回退问题，属 A02:2021 加密失败 / A07:2021 鉴别失败）
3. **appsec 面对照** — 命中多个安全面：
   - 面①不可信输入：`req.json()` 直接解构，无 schema 校验，email/password 可为 null/非字符串
   - 面②鉴权：JWT secret 存在弱 fallback（见第 4 条）
   - 面③输出注入：不命中（无 HTML/SQL 拼接，DB 已用参数化查询）
   - 面④加密/口令存储：命中，`verifyHash` 语义不明，hash 算法未知；JWT secret fallback 为弱字符串
   - 面⑤CSRF/CORS：不命中（登录端点无明显 CORS 配置；Workers 默认无 CORS 头，不跨域可跳过）
4. **fail-open 默认检测** — 命中 CRITICAL：`env.JWT_SECRET || 'dev-secret-change-me'` 是典型 fail-open 形态。生产环境若未配置 `JWT_SECRET`，JWT 将以已知弱密钥签发，攻击者可伪造任意 token，绕过鉴权。

---

## 2. 审查结论

### 真实安全问题

**[CRITICAL] JWT_SECRET fail-open fallback（第 6 行）**

```js
const secret = env.JWT_SECRET || 'dev-secret-change-me'
```

缺失 `JWT_SECRET` 时不会崩溃，而是静默使用已知弱密钥继续签发 token。攻击者只需知道这个默认值（字符串已暴露在代码中）即可伪造合法 JWT，完全绕过身份验证。

**修复要点：** 改为 fail-secure 形态，缺失时抛错/返回 500，拒绝处理请求：

```js
const secret = env.JWT_SECRET
if (!secret) return new Response('server misconfiguration', { status: 500 })
```

---

**[HIGH] 不可信输入缺乏 schema 校验（第 2 行）**

`await req.json()` 若 Content-Type 不是 JSON 或 body 为空，会抛出未捕获异常（500）。`email`/`password` 未做类型/长度校验，传入 null 或超长字符串可能导致数据库行为异常。

**修复要点：** 在解构前校验 body 类型，email 格式校验，password 长度限制；用 try/catch 包裹 `req.json()`。

---

**[MEDIUM] `verifyHash` 算法未知**

`verifyHash(password, user.hash)` 的实现不在审查范围内，但若 hash 字段使用 MD5/SHA1（无 salt），不满足 OWASP Authentication Cheat Sheet 要求（需 bcrypt/Argon2/scrypt）。需独立确认。

---

### 无问题项

- SQL 注入：已用参数化查询 `.bind(email)`，无注入风险。
- 错误响应：401 返回"unauthorized"，无信息泄露。

---

## 3. 自述

**应用了的检查：**
- 清单第 4 条（fail-open 检测）：命中 `JWT_SECRET || 'dev-secret-change-me'` 的 fallback 模式，判定 CRITICAL，比照 JWT Security Cheat Sheet 的"never use a default/known secret"原则。
- 清单第 3 条 appsec 面对照：逐一过了五个面，命中面①（不可信输入）和面④（加密/口令）；面③⑤ 经验证不命中。
- 清单第 2 条 OWASP Top 10：命中 A02（加密失败）和 A07（鉴别失败），有具体 CVE-class 落点。

**跳过的检查：**
- 清单第 1 条（暂存区密钥）：纯代码片段，无 git 上下文，无法验证，跳过。
- 面⑤ CORS/CSRF：Workers 端点为 POST JSON API，无 Cookie-based session，CSRF 不适用；CORS 未配置意味关闭，不跨域场景不适用。
- `verifyHash` 内部实现：不在提供的代码中，标注为 MEDIUM 待复查，未判定为确认 finding。
