# S4-armB 安全审查结论

## 1. 清单逐条对照

1. **无密钥/token 在暂存区** — 不命中（代码本身无硬编码密钥，审查范围是源文件内容，非 git 暂存区状态，此条不适用于静态代码审查）
2. **无新增 OWASP Top 10 漏洞** — 命中（见第 2 节）
3. **appsec 面对照** — 命中。触发面：②鉴权·session·访问控制（JWT 签发与校验是典型鉴权路径）
4. **fail-open 默认检测** — 不命中（`SECRET = os.environ['JWT_SECRET']` 是 fail-secure 形态：缺失时 `KeyError` 崩溃而非带 fallback 默弱密钥运行）

## 2. 审查结论

### 真实安全问题

**问题 1：`verify()` 缺少 `options` 参数，未显式禁用 `none` 算法（OWASP A02:2021 加密失败）**

`PyJWT` 历史上存在 `alg: none` 绕过：攻击者可伪造头部 `{"alg":"none"}`，服务端若未锁定算法列表，某些版本会接受无签名 token。当前代码传入了 `algorithms=['HS256']`，**现代 PyJWT（≥2.0）默认拒绝 `none`**，但写法本身没有明确传 `options={"require": ["exp", "iat"]}` 等约束，导致：
- Token 无过期时间（`issue()` 未加 `exp`），JWT 永久有效，密钥一旦泄漏无法靠时间窗口限损。
- 建议修复：`issue()` 加 `exp`；`verify()` 传 `options={"require": ["exp"]}`。

**问题 2：`verify()` 异常未隔离，失效 token 可能导致未定义行为（OWASP A07:2021 鉴权失败）**

`jwt.decode()` 在 token 过期、签名无效、格式错误时抛出 `DecodeError`/`ExpiredSignatureError`。当前代码无 try/except，调用方若直接用返回值做鉴权决策，异常向上传播时的行为取决于调用层——若上层捕获为 `None` 或静默忽略，则形成 fail-open 鉴权漏洞。

修复要点：
```python
def verify(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'], options={"require": ["exp"]})
    except jwt.PyJWTError:
        raise  # 或返回明确的失败信号，不吞异常
```

**问题 3：`uid` 未做类型/范围校验**

`issue(uid: int)` 仅有类型注解，无运行时校验。若调用方传入攻击者可控的 `uid`（如来自请求参数），可任意签发任意用户 token，属 IDOR 前置风险。建议在 `issue()` 内做业务侧合法性断言。

### 无问题项

- `SECRET` 读取方式是 `os.environ['JWT_SECRET']`，fail-secure，无 fail-open 风险。
- 未使用弱算法（MD5/SHA1/RS256 无验证等），HS256 在密钥足够强时安全。
- 无 SSRF、SQL 注入、XSS、CSRF、CORS 面。

## 3. 自述

**应用了哪些检查：**
- 清单项 2（OWASP Top 10）：识别出 A02（无 exp 约束 = 永久 token）和 A07（异常未隔离导致潜在 fail-open）
- 清单项 3（appsec 面对照）：确认触发面为②鉴权/session，逐条对照 OWASP JWT Cheat Sheet（建议 `require exp`、锁 `algorithms`、隔离异常）
- 清单项 4（fail-open 默认检测）：审查 `SECRET` 读取方式，确认是 `env['K']` fail-secure 形态，无 fallback 弱密钥

**跳过了哪些项：**
- 清单项 1（暂存区密钥）：静态代码审查无法判断 git 暂存区状态，该条跳过
- 清单项 3 中的面①③④⑤（SSRF/不可信输入/输出注入/加密口令存储/CSRF·CORS）：此代码无外部 HTTP 调用、无用户输入直接流入、无 HTML/SQL/shell 输出 sink、无 CORS 配置，均不触发
