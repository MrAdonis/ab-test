# S2 安全审查结果（Arm B）

## 1. 清单逐条对照

1. **无密钥/token 在暂存区** — 不命中（代码无密钥硬编码，config.js 本身是配置读取模块）
2. **无新增 OWASP Top 10 漏洞** — 命中（见下方 appsec 面分析）
3. **appsec 面对照** — 命中两个安全面：
   - ⑤ CORS/跨域：`corsOrigin` fallback 为 `'*'`，`corsHeaders()` 同时设 `Allow-Credentials: true`，构成 OWASP A05 安全配置错误
   - ①/② 间接：`debug: env.DEBUG ?? true` 使调试模式默认开启，属于访问控制 / 信息泄露路径
4. **fail-open 默认检测** — 命中两处，均为 CRITICAL：
   - `corsOrigin: env.CORS_ORIGIN || '*'`：CORS_ORIGIN 缺失时 fallback `*`，配合 `Allow-Credentials: true` 是 fail-open
   - `debug: env.DEBUG ?? true`：DEBUG 未设时默认 `true`，调试模式裸奔上线，fail-open

---

## 2. 审查结论：真实安全问题 + 修复要点

### 问题 1（CRITICAL）：CORS `*` + `Allow-Credentials: true` 组合

**代码位置：** `corsOrigin: env.CORS_ORIGIN || '*'` + `corsHeaders()` 中 `Allow-Credentials: true`

**问题：** 浏览器规范（WHATWG Fetch）明确禁止 `Origin: *` 与 `credentials: include` 共存——但服务端若错误组合两者，当 `CORS_ORIGIN` 未配置时 fallback 到 `*`，仍向所有来源开放跨域携带凭据的请求（旧浏览器或非浏览器客户端不强制校验，仍可利用）。本质是 fail-open：无配置即全开，任意来源可跨域访问携带 Cookie/Authorization 的端点。

对照 OWASP CORS Cheat Sheet 防护要点：
- 维护显式允许来源白名单；缺失时应 fail-secure（拒绝或不注入头）
- `Allow-Credentials: true` 必须搭配精确 Origin，不能与 `*` 共存

**修复：**
```js
corsOrigin: env.CORS_ORIGIN,  // 缺失时不 fallback，由 corsHeaders() 显式拒绝
// corsHeaders() 修改：
export function corsHeaders(requestOrigin) {
  if (!config.corsOrigin || config.corsOrigin !== requestOrigin) return {};
  return {
    'Access-Control-Allow-Origin': config.corsOrigin,
    'Access-Control-Allow-Credentials': 'true',
  };
}
```

### 问题 2（CRITICAL）：`DEBUG` 默认 `true`（fail-open）

**代码位置：** `debug: env.DEBUG ?? true`

**问题：** `??` 只在左侧为 `null`/`undefined` 时取右侧，故未设置 `DEBUG` 时调试模式默认开启。生产环境若漏配该变量，stack trace、内部路由、详细错误信息等会泄露给用户，同时可能绕过部分生产限制（如速率限制、详细日志写盘等依赖 debug flag 的逻辑）。OWASP A05 安全配置错误。

**修复：** fail-secure 方向是缺失即关：
```js
debug: env.DEBUG === 'true',  // 未设置则 false，只有显式 'true' 才开
```

### 问题 3（MEDIUM）：`SESSION_TTL` fallback 无语义异常处理

`Number(env.SESSION_TTL) || 86400`：若 `SESSION_TTL` 为非数字字符串，`Number()` 返回 `NaN`，`NaN || 86400` 安静 fallback 到默认值。本身不是立即的安全漏洞，但静默 fallback 掩盖配置错误，属配置健壮性问题，在会话超时场景可导致意外的过长有效期。可加显式校验。

---

## 3. 自述：应用了哪些检查 / 跳过了哪些

**应用：**
- 清单项 4（fail-open 默认检测）：逐行扫描每个 `||` / `??` fallback，判断是否有安全语义的 fallback 指向不安全默认值。命中 `corsOrigin` 和 `debug` 两处。
- 清单项 3 appsec 面（⑤ CORS/跨域、② 访问控制）：对照 OWASP CORS Cheat Sheet 过了 `Allow-Credentials + *` 的组合禁忌，以及 `corsHeaders()` 作为输出注入点（HTTP 头）的安全要求。
- 清单项 2（OWASP Top 10）：两处 finding 均归入 A05 安全配置错误，不是空话，而是从 appsec 面分析推导出来的定性。

**跳过：**
- 清单项 1（密钥在暂存区）：代码无密钥字面量，不适用。
- appsec 面 ①（不可信外部输入/SSRF）：`corsHeaders()` 无输入解析，`env.*` 来自服务端环境变量（可信来源），不适用。
- appsec 面 ③ 输出注入（HTML/SQL/shell）：无字符串拼接到 HTML/SQL/shell，不适用。
- appsec 面 ④ 加密/口令存储：无加密操作，不适用。
- `SESSION_TTL` fallback 86400：无安全语义（只是时长数字），按清单项 4 跳过规则（PORT/PAGE_SIZE 类无安全语义 fallback）本应跳过，但实际上静默掩盖配置错误有间接影响，降级为 MEDIUM 列出而非 CRITICAL。
