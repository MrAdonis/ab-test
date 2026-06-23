# S2 安全审查结果（Arm A）

## 1. 清单逐条对照

1. **无密钥/token 在暂存区** — 不命中。代码本身不含硬编码密钥，读取的是环境变量 `env.*`，暂存区问题无法从代码片段判断，此项视为代码层面不适用。

2. **无新增 OWASP Top 10 漏洞** — 命中。`corsOrigin: env.CORS_ORIGIN || '*'` 当环境变量缺失时默认值为 `'*'`，同时 `corsHeaders()` 输出 `Access-Control-Allow-Credentials: true`。`ACAO: *` + `ACAC: true` 组合在 RFC 规范中浏览器会拒绝，但许多框架/代理对此容忍度不一，属于错误配置（Security Misconfiguration，A05:2021）。`debug: env.DEBUG ?? true` 在未设置环境变量时默认开启调试，属于同类问题。

3. **appsec 面对照** — 命中面 ⑤（CORS·跨域）。

   对照 OWASP CORS Cheat Sheet：
   - **`ACAO: *` + `ACAC: true` 是非法组合**：规范禁止两者同时存在；部分中间件/代理未严格执行规范时，等效于允许任意来源携带凭据的跨域请求。攻击者可通过受控页面读取已登录用户的敏感 API 响应（CORS-based CSRF/信息泄露）。
   - **fail-open 默认值 `'*'`**：生产环境缺失 `CORS_ORIGIN` 配置时自动对所有来源开放，而非拒绝或报错，违反最小权限原则。正确做法是缺省值为严格白名单或启动时 fail-fast（抛错）。
   - **`debug: true` fail-open**：调试模式开启可能暴露堆栈/内部路径/详细错误，属于信息泄露辅助面，与 CORS 问题同源（同一 fail-open 模式）。

---

## 2. 审查结论

**真实安全问题：两处 fail-open 默认值**

**问题 1（高危）：CORS 通配符 + 凭据头共存**

```js
corsOrigin: env.CORS_ORIGIN || '*',   // 缺失时 → '*'
'Access-Control-Allow-Origin': config.corsOrigin,
'Access-Control-Allow-Credentials': 'true',           // 永远返回
```

- 规范禁止 `ACAO: *` 和 `ACAC: true` 同时存在；实际行为取决于框架/浏览器的宽容程度。
- 即便浏览器拒绝该组合，当 `CORS_ORIGIN` 被设置为某个合法来源后，永远返回 `ACAC: true` 仍是风险（不验证来源是否应允许携带凭据）。

修复要点：
1. 缺省值改为 fail-fast，不设 `'*'`：`corsOrigin: env.CORS_ORIGIN`，启动时若为空则抛错。
2. `Access-Control-Allow-Credentials: true` 改为条件输出，仅当来源在白名单内且明确需要凭据时才追加该头。
3. 不使用通配符时，同时返回 `Vary: Origin` 避免缓存污染。

**问题 2（中危）：debug 默认开启**

```js
debug: env.DEBUG ?? true,   // 未设置时 → true
```

- 生产环境未显式设置 `DEBUG=false` 时调试模式常开，可能暴露详细错误/堆栈信息。

修复要点：默认值改为 `false`，即 `debug: env.DEBUG === 'true'`（字符串显式匹配），需主动选择开启。

---

## 3. 自述

**应用的检查：**
- 清单第 2 条：识别 OWASP A05:2021 Security Misconfiguration（CORS 错误配置 + 调试默认开启）。
- 清单第 3 条：命中面 ⑤（CORS·跨域），对照 OWASP CORS Cheat Sheet 过了"通配符+凭据"非法组合、fail-open 最小权限、Vary 头三个防护要点。

**跳过的检查：**
- 清单第 1 条（暂存区密钥）：代码片段为静态文件内容，无法从代码本身判断 git 暂存状态，跳过。
- 面 ①②③④（不可信输入/鉴权/输出注入/加密存储）：本段代码是配置读取 + header 构造，无外部用户输入处理、无数据库写入、无 HTML/SQL 输出、无口令存储，这些面无 sink，跳过。
