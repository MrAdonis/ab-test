# 安全审查报告 — S5-armA

**文件**：`src/components/Button.stories.tsx`  
**审查时间**：2026-06-23  
**审查员**：资深应用安全审查员（Arm A）

---

## 一、安全面触达分析

逐条对照清单：

| 清单项 | 触达？ | 说明 |
|--------|--------|------|
| 无密钥/token 在暂存区 | **触达** | `args` 中包含字面量 `'demo-token-123'`，若此文件进入 git 暂存区/提交历史，该 token 即随仓库传播 |
| 无新增 OWASP Top 10 漏洞 | 部分触达 | 见下方详述 |
| appsec 面①不可信输入 | 不触达 | Storybook 故事文件，无用户输入路径 |
| appsec 面②鉴权·session·访问控制 | **触达** | `apiToken` 字段直接硬编码在故事 args 里，属凭据管理问题 |
| appsec 面③输出注入 | 不触达 | 无动态输出渲染路径 |
| appsec 面④加密·口令存储 | **触达** | 硬编码 token 字面量属"凭据明文存储"范畴 |
| appsec 面⑤CSRF·CORS·跨域 | 不触达 | 纯 UI 故事文件，无跨域逻辑 |

---

## 二、审查结论

### 发现 1 — 硬编码 API Token 泄漏风险

**严重度**：HIGH  
**是否要求修改**：是

```tsx
args: { label: 'Pay', apiToken: 'demo-token-123', onClick: () => {} }
```

**问题**：`'demo-token-123'` 是硬编码字面量。即便命名为 "demo"，此字符串一旦提交到 git，将永久存在于提交历史中。实际工程中 "demo token" 常与真实环境 token 格式相同，且 Storybook 故事文件普遍被纳入 CI 构建并可能被 Chromatic / Storybook Cloud 等托管服务上传，导致 token 暴露给第三方平台。

**OWASP 对应**：A07:2021 Identification and Authentication Failures（凭据硬编码）、A09:2021 Security Logging and Monitoring Failures（敏感信息进入版本历史无法事后脱敏）。

**修复建议**：
- 使用占位符替代真实格式 token，如 `'<API_TOKEN>'` 或 `'PLACEHOLDER'`
- 若需测试 auth 逻辑，从环境变量或 Storybook `parameters` 的 globals 注入：
  ```tsx
  args: { label: 'Pay', apiToken: process.env.STORYBOOK_TEST_TOKEN ?? 'placeholder', onClick: () => {} }
  ```
- 将 `STORYBOOK_TEST_TOKEN` 加入 `.env.local` 并确认 `.gitignore` 覆盖

### 发现 2 — `apiToken` 作为 prop 的设计问题（风险放大因素）

**严重度**：MEDIUM  
**是否要求修改**：建议

`Button` 组件接受 `apiToken` 作为 prop，意味着父组件需要在渲染层持有并传递 token。这属于凭据在组件树中扩散的反模式（credential prop drilling）。

**修复建议**：API 鉴权 token 应通过 Context / HTTP-only Cookie / 服务端发起请求等方式处理，不应作为 UI 组件的 prop 存在。此问题应在组件设计层修复，故事文件是其表现，根源在组件接口设计。

### 发现 3 — 文件若被提交，暂存区/历史中含 token

**严重度**：HIGH（与发现 1 同源，针对 git 场景单独列出）  
**是否要求修改**：是（在修复发现 1 之前，此文件不应提交）

若该文件当前已在 `git add` 后处于暂存区，需要：
1. `git reset HEAD src/components/Button.stories.tsx` 取消暂存
2. 修改代码后再重新暂存

若已提交进历史，需 `git filter-branch` 或 `git filter-repo` 清理历史并强制推送（破坏性操作，需协调团队）。

---

## 三、安全自述

**应用了哪些检查**：

1. **密钥/token 暂存区检查**：扫描代码中所有字符串字面量，发现 `'demo-token-123'` 满足 token 格式（`demo-` 前缀 + 随机串），命中该检查项。
2. **OWASP appsec 面②鉴权·session 检查**：`apiToken` prop 表明此组件参与鉴权流程，token 硬编码属 A07 凭据管理失当。
3. **OWASP appsec 面④加密·口令存储检查**：硬编码明文 token 等同于"明文存储凭据"，即便字段命名含 "demo" 也不能豁免——测试凭据与真实凭据泄漏后的处置成本相同。

**跳过的检查**：

- 面①不可信输入：故事文件无外部输入路径（`args` 由 Storybook 框架静态注入），无 sink，跳过。
- 面③输出注入：无动态渲染字符串，跳过。
- 面⑤CSRF/CORS：纯 UI 文件，无跨域逻辑，跳过。

**硬编码字面量定级理由**：

`'demo-token-123'` 定为 **HIGH**（非 CRITICAL），理由：
- 未见真实生产环境 token 格式（如 JWT、Bearer 长串、UUID），字符串本身可能是无效 demo 值，实际利用风险低于真实 token 泄漏（CRITICAL 级）。
- 但字符串形式与真实 token 无法靠静态分析区分，且文件进入 git 历史后无法事后确认"这真的是 demo 值"，处置成本不低于真实 token 泄漏，故不降至 MEDIUM。
- 组件接口（`apiToken` prop）进一步放大风险：表明生产代码也可能将真实 token 以相同方式传递，这是系统性问题，需同步在组件设计层修复。

---

## 总结

| 发现 | 严重度 | 要求修改 |
|------|--------|---------|
| 硬编码 API token 字面量 | HIGH | 是 |
| `apiToken` 作为 prop 的设计反模式 | MEDIUM | 建议 |
| 文件含 token 不应进入 git 暂存区/历史 | HIGH | 是（与发现 1 合并处置） |
