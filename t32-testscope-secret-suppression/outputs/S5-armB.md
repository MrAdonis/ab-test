# 安全审查报告 — S5-armB

**被审查文件：** `src/components/Button.stories.tsx`  
**审查时间：** 2026-06-23  
**审查员：** Arm B（含占位密钥误报抑制清单）

---

## 第一步：清单触及判断

| 清单项 | 是否触及 | 依据 |
|--------|---------|------|
| 无密钥/token 在暂存区 | **触及** | `apiToken: 'demo-token-123'` 是硬编码字面量 |
| 无新增 OWASP Top 10 漏洞 | 不触及 | 纯 Storybook 故事文件，无 HTTP 请求、无后端逻辑、无输入处理 |
| appsec 面对照（①不可信输入 ②鉴权·session ③输出注入 ④加密·口令 ⑤CSRF·CORS） | 不触及 | 代码只声明组件故事，无外部输入来源，无下游 sink；5 个安全面全不命中，按跳过规则处理 |
| 占位密钥误报抑制 | **触及** | 需判断 `demo-token-123` 是否生产可达 |

---

## 第二步：审查结论

### 发现 F1：`apiToken: 'demo-token-123'` 硬编码字面量

**严重度：LOW**  
**是否要求修改：否（建议/非强制）**

**生产可达性判断：**

- 文件为 `.stories.tsx`，是 Storybook 专用格式，通过 `export default { component: Button }` 注册故事，不被应用主入口 import。
- Storybook 构建产物（`storybook-static/`）与应用生产构建（`dist/`）是独立流水线，正常配置下不会打包进生产 bundle。
- `args` 对象是 Storybook Controls 的 prop 注入机制，只在 Storybook iframe 运行时生效，不会被 Button 组件以外的生产代码消费。
- 字面量 `demo-token-123` 前缀 `demo-` 和后缀 `-123` 均为典型占位风格，不具备真实 API token 的熵特征（无 Base64/UUID/长随机串）。

**综合判定：** 该值是 Storybook 演示用占位 token，生产可达性低。按清单"占位密钥误报抑制"规则，定级 LOW，不强制修改。

**可选改进建议（不阻塞）：** 若希望进一步降低误报风险，可将值改为更明确的占位形式（如 `__STORYBOOK_DEMO_TOKEN__` 或 `YOUR_API_TOKEN_HERE`），便于扫描工具识别并静默。

---

### 发现 F2：`apiToken` prop 设计——潜在架构信息点

**严重度：INFO**  
**是否要求修改：否**

`Button` 组件接受 `apiToken` 作为 prop，说明该组件可能在运行时持有 token 并直接使用（如在 `onClick` 里发起 fetch）。这是一个架构信息点：将 token 作为组件 prop 传入通常意味着 token 会暴露在 React DevTools、组件树和潜在的日志中，建议在 `Button` 组件实现层（非本文件范围）确认 token 处理方式符合最小暴露原则。本故事文件本身不引入此问题，仅作 INFO 标记供实现层参考。

---

## 第三步：安全自述

**应用的检查：**

1. **密钥/token 字面量扫描**：识别到 `apiToken: 'demo-token-123'`，触发占位密钥误报抑制规则。
2. **生产可达性追踪**：分析该文件在构建流水线中的位置——`.stories.tsx` 仅被 Storybook 消费，不进入应用生产 bundle，判定生产不可达。
3. **OWASP appsec 面扫描**：逐一核对 5 个安全面（不可信输入、鉴权/session、输出注入、加密/口令存储、CSRF/CORS），代码无外部输入来源，无 HTTP、无 DOM 操作、无状态管理，5 面全不命中，按"输入无外部来源且输出无下游 sink"跳过规则处理，未做 OWASP Cheat Sheet 展开——这是正确的跳过，不是遗漏。

**硬编码字面量定级理由：**

`demo-token-123` 定 LOW 而非 CRITICAL 的依据是**生产可达性**，而非文件名。判断链：① `.stories.tsx` 扩展名表明是 Storybook 文件，但不足以单独定级；② 追踪 import 链——该文件没有被非 Storybook 路径 import 的迹象；③ Storybook `args` 机制不会将值传入生产运行时；④ 字面量本身无高熵特征，符合占位值特征。四条合并判定生产不可达，降为 LOW。若任一条件反转（例如该文件被 `src/App.tsx` import，或 token 值呈现高熵 UUID 格式），则应升为 CRITICAL。
