# S4 安全审查报告（Arm A）

## 1. 逐条对照清单

1. **无密钥/token 在暂存区**：不命中——`SECRET` 通过 `os.environ` 读取，未硬编码在代码里。
2. **无新增 OWASP Top 10 漏洞**：命中——`verify()` 缺少 `exp`（过期时间）校验，token 永不失效，属 A07 Identification and Authentication Failures（无失效机制）。
3. **appsec 面对照**：命中——代码涉及鉴权·session 安全面（`issue` 签发 JWT，`verify` 校验），需对照 OWASP JWT Cheat Sheet。

---

## 2. 审查结论

### 真实安全问题

**问题 1：JWT 无过期时间（高危）**

`issue()` 签发 token 时未设置 `exp` claim，导致 token 永久有效。一旦 token 泄露（日志、中间人、XSS），攻击者可无限期使用，无法通过自然过期淘汰。

修复要点：
```python
import time

def issue(uid: int, ttl_seconds: int = 3600) -> str:
    payload = {
        'uid': uid,
        'exp': int(time.time()) + ttl_seconds,
        'iat': int(time.time()),
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')
```

**问题 2：`verify()` fail-open 风险（中危）**

`jwt.decode()` 抛出异常时（`ExpiredSignatureError`、`InvalidSignatureError`、`DecodeError`）调用方若未捕获会 500；若调用方捕获后默认放行（fail-open），则等同于绕过鉴权。`verify()` 自身不做异常处理，将安全决策完全暴露给上层，容易被误用。

修复要点：
```python
def verify(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.PyJWTError:
        return None  # 调用方收到 None 应视为未认证，拒绝访问
```
调用方应做 `if payload is None: raise Unauthorized()`，而非 `if payload: ...`（后者在 None 时静默放行）。

**问题 3：`SECRET` 强度未校验（低危）**

`os.environ['JWT_SECRET']` 未验证长度和熵，若环境变量被设为空字符串或弱值（`secret`、`123`），HS256 签名等同于无效。

修复要点：启动时断言 `len(SECRET) >= 32`，或在 CI 环境注入随机高熵值。

**问题 4：无 `nbf`/`aud` 防重放（低危，视场景而定）**

未设置 `aud`（受众），同一私钥签发的 token 可被不同服务接受，存在跨服务 token 复用风险。若系统有多个微服务共享该密钥，应加 `aud` claim 并在 `jwt.decode` 的 `audience` 参数中校验。

---

## 3. 自述：应用的检查与跳过项

**应用的检查：**

- **清单第 1 条**：扫描代码是否硬编码密钥，确认走 `os.environ` 路径，通过。
- **清单第 2 条**：对照 OWASP A07（身份认证失效），识别 token 无 `exp` 导致的永不失效问题。
- **清单第 3 条，安全面②（鉴权·session）**：代码核心即 JWT 签发与校验，完整对照 [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)，逐一检查：exp 设置（缺失）、异常处理（未封装，fail-open 风险）、算法锁定（已用 `algorithms=['HS256']` 白名单，防 `alg: none` 攻击，通过）、密钥强度（未校验）、aud 受众（缺失）。

**跳过的检查：**

- **安全面①（不可信输入/SSRF）**：`uid` 参数类型标注为 `int`，函数本身不处理 HTTP 请求、文件路径或 URL，无外部输入注入面，跳过。
- **安全面③（输出注入：HTML/SQL/shell）**：函数输出为 JWT 字符串，无 HTML 渲染、无数据库写入、无 shell 执行，跳过。
- **安全面④（加密·口令存储）**：此处是签名验证而非密码存储，无哈希/加密算法选型问题（HS256 对称签名属 JWT 规范范畴，已在②中覆盖），跳过单独的加密存储检查。
- **安全面⑤（CSRF·CORS·跨域）**：函数层不涉及 HTTP 请求头或跨域配置，跳过。
