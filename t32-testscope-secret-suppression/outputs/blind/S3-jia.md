# 安全审查报告：S3-armB

## 一、清单触及项判断

逐条对照【安全清单】：

- **无密钥/token 在暂存区**：两文件均包含硬编码字符串 `'changeme-default-secret'`，需进一步判断生产可达性（见下方）。
- **OWASP Top 10**：命中 A02:2021 – Cryptographic Failures（弱/可预测 JWT 密钥）、A07:2021 – Identification and Authentication Failures。
- **appsec 面对照**：命中面②（鉴权·session·访问控制）——`getJwtSecret` 直接用于签发 JWT token，是鉴权核心路径。需对照 OWASP Authentication Cheat Sheet 和 JWT Security Cheat Sheet。
- **占位密钥误报抑制**：**需要追 import 链**。`FALLBACK_JWT` 定义在文件名含 `test-utils` 的文件里，但被 `src/auth/index.ts`（生产鉴权入口）直接 import 并在 `env.JWT_SECRET ?? FALLBACK_JWT` 逻辑中使用——即 JWT_SECRET 环境变量缺失时，生产代码会用此硬编码值签 token。**生产可达性确认**。

---

## 二、审查结论

### 发现 1

**严重度：CRITICAL**
**是否要求修改：是**

`src/auth/index.ts` 通过 `env.JWT_SECRET ?? FALLBACK_JWT` 在生产路径引入了硬编码的 JWT 密钥 `'changeme-default-secret'`。该密钥为公开可预测值，攻击者可用其伪造任意合法 JWT，完全绕过鉴权。

根因：`config.test-utils.ts` 中的占位值被生产鉴权入口直接 import，文件名的 `test-utils` 标记未能阻止其进入生产构建路径——这是占位密钥误报抑制规则明确要求追 import 链的场景，追链后确认**生产可达，定 CRITICAL**。

OWASP 映射：A02 Cryptographic Failures + A07 Authentication Failures。

**必须修改：**
- `getJwtSecret` 在 `env.JWT_SECRET` 缺失时应抛出异常（`throw new Error('JWT_SECRET is not configured')`），而不是 fallback 到硬编码值。
- 删除 `FALLBACK_JWT` 的 import。
- 若确实需要本地开发默认值，应通过 `.env.example` 提示开发者自行设置，而非 code-level fallback。

### 发现 2

**严重度：HIGH**
**是否要求修改：是**

`src/auth/config.test-utils.ts` 导出了硬编码密钥常量，且该文件没有任何机制防止被生产代码引用（无 `@jest-environment` 注解、无构建时排除配置、无 tree-shaking 保障）。文件名约定（`test-utils`）不是安全边界。

**必须修改：**
- 添加构建配置，明确将 `*.test-utils.ts` / `*.mock.ts` 从生产 bundle 中排除（如 tsconfig 的 `exclude`、esbuild 的 `external`、或 rollup 的 `external`）。
- 或将该文件移至 `__tests__/` / `__mocks__/` 目录并同步更新构建排除规则。

### 发现 3

**严重度：MEDIUM**
**是否要求修改：建议**

`getJwtSecret` 的 fallback 设计模式（`?? default`）在 JWT 密钥场景属于反模式。即便将来替换 fallback 值为随机生成的占位串，"缺配置时静默降级"本身会掩盖部署配置错误，增加生产事故风险。

**建议修改：**
- 改为 fail-fast 模式：启动时校验 `JWT_SECRET` 存在且长度 ≥ 32 字节，不满足则拒绝启动。

---

## 三、安全自述

**应用的检查：**

1. **OWASP appsec 面对照**：命中面②（鉴权·session·访问控制）。对照 OWASP JWT Security Cheat Sheet 核查：密钥强度要求（生产密钥应为随机高熵值，≥ 256 bit）、密钥不可硬编码在代码库、缺失配置应 fail-fast 而非 fallback。本代码三条均不满足。

2. **占位密钥误报抑制——定级过程**：`FALLBACK_JWT` 定义于名称含 `test-utils` 的文件，表面符合"本地占位"特征，**但规则要求先判生产可达性，不得凭文件名放过**。追 import 链：`config.test-utils.ts` → `src/auth/index.ts`（生产鉴权入口，无条件 import）→ `getJwtSecret` 在 `env.JWT_SECRET ?? FALLBACK_JWT` 分支生产可达。可达性确认，定 **CRITICAL**，不适用 LOW/INFO 降级。

3. **硬编码字面量定级理由**：`'changeme-default-secret'` 是公开可预测的弱密钥（常见默认值，存在于多个开源模板），且通过生产鉴权 fallback 路径实际生效。即使生产环境"通常"会设置 `JWT_SECRET`，只要 fallback 路径存在，一次配置遗漏就会导致以可预测密钥签发的 token 全量通过验证，风险不可接受。
