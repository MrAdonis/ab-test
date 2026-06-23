# S6 安全审查结果（Arm A）

## 步骤 1：逐条清单对照

1. **无密钥/token 在暂存区**：不命中——代码仅读取 `env.PAGE_SIZE` / `env.PORT`，无 API key、密码、token 字面量。
2. **无新增 OWASP Top 10 漏洞**：命中（见步骤 2 详析）——`page` 参数来自外部，存在注入/滥用路径。
3. **appsec 面对照**：命中——`paginate(rows, page)` 的 `page` 属于①不可信输入，`rows.slice` 的结果输出到下游调用方（下游 sink 存在）；触发 appsec 面精查。

## 步骤 2：审查结论

**问题 1：`page` 未验证，整数溢出 / 负数 slice**

`page` 直接参与 `(page - 1) * PAGE_SIZE` 运算，无类型转换也无范围校验。

- `page = 0` → `start = -PAGE_SIZE`，`rows.slice(-20, 0)` 在 JS 中返回空数组，行为静默且令人困惑。
- `page = -1` → `start = -2 * PAGE_SIZE`，`slice` 同上，静默空结果。
- `page = Infinity` → `start = Infinity`，`slice(Infinity, Infinity + 20)` 返回空数组，不报错。
- `page = "1; DROP TABLE"` 等字符串 → `Number("1; DROP...")` = `NaN`，`NaN - 1 = NaN`，`NaN * 20 = NaN`，`slice(NaN, NaN)` 返回空数组——行为静默不报错，调用方无法区分"第 1 页有数据"和"参数非法"。

**修复要点：**
```js
export function paginate(rows, page) {
  const p = Number(page)
  if (!Number.isInteger(p) || p < 1) throw new Error('page must be a positive integer')
  const start = (p - 1) * PAGE_SIZE
  return rows.slice(start, start + PAGE_SIZE)
}
```

**问题 2：`PAGE_SIZE` 无上界，DoS 风险**

`Number(env.PAGE_SIZE) || 20` 若环境变量被设为超大值（或攻击者控制配置来源），单次分页可返回无限行，导致内存/响应体膨胀。建议加上界：

```js
const PAGE_SIZE = Math.min(Math.max(Number(env.PAGE_SIZE) || 20, 1), 200)
```

**其余无问题：**
- `PORT` 仅用于监听，无注入路径。
- `startServer` 无鉴权/加密/跨域逻辑，不在本次代码范围内。
- 无口令存储、无 SQL/HTML/Shell 输出 sink。

## 步骤 3：自述

**应用的检查：**
- 清单第 1 条（密钥扫描）：确认无字面量密钥，通过。
- 清单第 3 条 appsec 面①（不可信输入）：`page` 参数来源不受约束，触发精查；对照 OWASP Input Validation Cheat Sheet，识别整数溢出、NaN 静默、负数 slice 三个路径。
- 清单第 3 条 appsec 面对 `PAGE_SIZE` 的配置来源校验：环境变量属于半可信输入，识别无上界 DoS 风险。

**跳过的检查：**
- 清单第 3 条 appsec 面②（鉴权/IDOR）：本段无 session、用户 ID、权限判断逻辑，跳过。
- 清单第 3 条 appsec 面③（输出注入：HTML/SQL/shell/模板）：`paginate` 返回数组切片，无 HTML 渲染、无 SQL 拼接、无 shell exec、无模板引擎，跳过。
- 清单第 3 条 appsec 面④（加密/口令存储）：无口令、无加密操作，跳过。
- 清单第 3 条 appsec 面⑤（CSRF/CORS/跨域）：`startServer` 仅调用 `app.listen`，CORS 配置在 `app` 中间件层，不在本段代码内，跳过。
