# 安全审查报告：S3-armA

## 1. 安全面识别

本段代码命中以下安全面：
- **面②：鉴权·session·访问控制** — `getJwtSecret` 直接决定签发 JWT 所用的密钥，是鉴权核心路径
- **面④：加密·口令存储** — JWT secret 属于加密密钥材料，其强度和保密性直接决定 token 伪造难度

不命中的面：①不可信输入、③输出注入、⑤CSRF/CORS/跨域。

---

## 2. 逐条清单核查

### ☑ 无密钥/token 在暂存区

`FALLBACK_JWT = 'changeme-default-secret'` 是硬编码字符串，存在于版本控制跟踪的源文件中。严格意义上不是"在暂存区"（git staging area），但被纳入 git 历史同样构成密钥泄露——一旦提交，所有 clone 均可读取。

### ☑ 无新增 OWASP Top 10 漏洞

命中 **A02:2021 – Cryptographic Failures**（加密失败）：弱/可预测密钥用于签发 JWT，等同于签名失效。

### ☑ appsec 面对照（面②④）

已触发，见「发现」节。

---

## 3. 审查发现

### F1 — 弱 fallback 密钥用于生产签发 JWT

**严重度：CRITICAL**  
**是否要求修改：是**

`getJwtSecret` 在 `env.JWT_SECRET` 未配置时，回退到 `'changeme-default-secret'`，该值：
1. 极低熵，任何攻击者都可猜测或直接从源码读取
2. 通过该密钥签发的 JWT 可被任意第三方伪造，绕过所有基于 token 的鉴权
3. fail-open 语义：配置缺失时系统"正常运行"而非启动失败，使安全降级静默发生

OWASP JWT Cheat Sheet 要求：密钥长度 ≥ 256 bit，不可预测，不可出现在代码中。此处双重违反。

**修改要求**：`getJwtSecret` 在 `env.JWT_SECRET` 为空时应抛出异常（fail-closed），而非使用 fallback。

```ts
export function getJwtSecret(env: Env): string {
  if (!env.JWT_SECRET) {
    throw new Error('JWT_SECRET is not configured. Refusing to start.')
  }
  return env.JWT_SECRET
}
```

---

### F2 — 测试工具模块被生产代码直接 import

**严重度：HIGH**  
**是否要求修改：是**

`config.test-utils.ts` 文件名明确标注为测试辅助，但被生产入口 `src/auth/index.ts` 直接引用。这带来两个风险：

1. **构建时泄露**：生产 bundle 包含该模块，弱密钥随产物分发（CDN edge、容器镜像、客户端包）
2. **范围混淆**：test-utils 通常不经 security review，此引用让它成为生产安全路径的一部分

**修改要求**：移除生产代码对 `*.test-utils` 模块的任何 import；如需默认值，应在专用配置模块中定义，并通过 CI lint 规则（如 ESLint no-restricted-imports）阻止 test-utils 进入生产路径。

---

### F3 — 硬编码字面量已进入版本历史

**严重度：MEDIUM**  
**是否要求修改：是（清理历史）**

即使修复 F1/F2 后，`'changeme-default-secret'` 已写入 git commit history，攻击者仍可通过 `git log -S` 检索。需评估是否通过 `git filter-repo` 清洗历史，或在威胁模型下接受该残留（私有仓库 + 已轮换密钥后风险降为 LOW）。

---

### F4 — 无 JWT_SECRET 强度校验

**严重度：LOW**  
**是否要求修改：建议**

即使 `env.JWT_SECRET` 存在，代码也不校验其长度或熵。运维人员可能配置同样弱的值。建议在 `getJwtSecret` 中加最小长度断言（≥ 32 字节）。

---

## 4. 安全自述

**应用了哪些检查：**
- 清单项 1（密钥/token）：字面量 `'changeme-default-secret'` 虽不在 staging area，但在受版本控制的源文件中，按"密钥不应进入代码库"原则定为问题
- 清单项 2（OWASP Top 10）：映射到 A02 Cryptographic Failures
- 清单项 3（appsec 面②④）：`getJwtSecret` 是鉴权核心路径，面②强制触发；密钥材料处理触发面④

**硬编码字面量定级理由：**
`'changeme-default-secret'` 定 **CRITICAL**（合并入 F1）而非仅 MEDIUM，原因是其影响的下游 sink 是 JWT 签名——直接决定鉴权是否可被绕过，不是普通配置值。若该字面量出现在无鉴权语义的配置（如日志前缀），定级会降至 LOW/INFO。严重度与字面量本身的熵无关，与其在安全路径上的位置有关。

**跳过条件评估：** 代码有外部来源（`env.JWT_SECRET` 来自运行时环境注入，其缺失决定是否使用 fallback）且有下游 sink（JWT 签名），不满足跳过条件，全量过 appsec 面检查。
