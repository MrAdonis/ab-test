# S5 审查结果 — tests/auth.test.ts

## 1. 清单逐条对照

1. **无密钥/token 在暂存区**：不命中（审查对象是文件内容本身，暂存区状态无法从代码片段判断；但文件内含硬编码字符串 `TEST_SECRET = 'test-key-123'`，属于代码层面的明文 secret，与此条相关）
2. **无新增 OWASP Top 10 漏洞**：不命中（测试文件本身无直接的 Top 10 漏洞引入，但 `TEST_SECRET` 硬编码在源文件中会被 git 跟踪，属于 A02:2021 Cryptographic Failures 的边界情况）
3. **appsec 面对照**：命中 ④ 加密·口令存储（`sign`/`verify` 是加密相关函数，`TEST_SECRET` 是测试用密钥）；其余面（①不可信输入 ②鉴权/IDOR ③输出注入 ⑤CSRF/CORS）在此文件中均无外部输入来源，也无下游 sink，跳过。

## 2. 审查结论

**问题：硬编码 secret 进入版本控制**

`TEST_SECRET = 'test-key-123'` 直接写在测试文件里，会被 git 跟踪到历史记录。若该值与真实环境密钥相同或相似（弱 secret 复用），攻击者拿到仓库历史即可伪造 token。

**修复要点：**
- 测试用 secret 应通过环境变量注入，例如 `process.env.TEST_SECRET ?? 'test-key-123'`，并在 CI 中设置随机强密钥，使测试环境与生产环境密钥体系隔离
- 若 `'test-key-123'` 仅用于单元测试且与生产 secret 无关联，风险较低，但仍建议加注释说明"仅用于测试，不得用于生产"，防止后续复用
- 对照 OWASP Cryptographic Storage Cheat Sheet：密钥不应存储在源代码中，即使是测试代码

**无其他安全问题。** 这是一个纯测试文件，无外部输入处理、无真实 I/O sink，逻辑面窄。

## 3. 自述

**应用的检查：**
- 清单条 1（secret 暂存区）：扩展到源文件内硬编码 secret，因为硬编码进 git 是同类风险的源头
- 清单条 3 appsec 面 ④（加密·口令存储）：`sign`/`verify` + `TEST_SECRET` 明确触发此面，对照 OWASP Cryptographic Storage Cheat Sheet 检查密钥管理

**跳过的检查：**
- appsec 面 ①②③⑤：此文件无外部输入（无 HTTP 请求/用户表单/URL 参数），无鉴权访问控制逻辑，无 HTML/SQL/shell 输出，无跨域操作；输入无外部来源且输出无下游 sink，符合跳过条件
- OWASP Top 10 全面扫描：清单要求"不靠空话兜底"，本文件触发安全面唯一是 ④，已单独对照处理
