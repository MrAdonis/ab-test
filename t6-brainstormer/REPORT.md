# t6 — Brainstormer Agent AB Test

**测试问题**：在 RBPI 流程里插入 `brainstormer` agent（先发散选项，再 Plan），是否提升最终 task_plan 质量？

**方法**：3 个场景 × A（直接 Plan）/ B（Brainstorm + Plan），独立 Sonnet 评分员盲测，四维打分（方向明确性/功能完整性/量化约束/范围控制），满分 40。S3 额外 +1 奖励正确 skip 判断。生成与评分全 Sonnet。

---

## 汇总

| 场景 | A | B | 胜者 |
|------|---|---|------|
| S1 email digest（应触发） | **35** | 32 | A +3 |
| S2 多平台分发（应触发） | **34** | 31 | A +3 |
| S3 dark mode bugfix（应跳过） | 29 | **34** | B +5 |
| **总计** | **98** | **97** | A 微胜 1 分 |

---

## 分场景分析

### S1 — email digest（brainstorm 已触发）

| 维度 | A1 | B1 |
|------|----|----|
| D1 方向明确性 | 9 | 8 |
| D2 功能完整性 | 8 | 9 |
| D3 量化约束 | 9 | 7 |
| D4 范围控制 | 9 | 8 |
| **Total** | **35** | **32** |

A1 优势：HTML 模板参数写死到色值/字号/行高/列名；F5 有 idempotency 保护（已发返回 already_sent_today）；所有 acceptance 均为可复制 wrangler 命令。

B1 优势：D2 +1（F2 加了「先 SELECT * FROM signals LIMIT 1 确认列名」的防御步骤；F6 把 DNS 部署文档单独 feature 化，写死 SPF/DMARC 值）；out_of_scope 含成本理由（ESP 不 justify）。

A1 弱点：缺 DNS 配置文档 feature，新机器上手路径不在 DoD 里。

B1 弱点：HTML 模板零量化参数（zero dependency 但形态完全开放）；F3 acceptance 依赖「浏览器打开」主观验证。

---

### S2 — 多平台分发（brainstorm 已触发）

| 维度 | A2 | B2 |
|------|----|----|
| D1 方向明确性 | 9 | 7 |
| D2 功能完整性 | 8 | 9 |
| D3 量化约束 | 9 | 6 |
| D4 范围控制 | 8 | 9 |
| **Total** | **34** | **31** |

A2 优势：TypeScript + zod 类型系统写死，字符限制精确到数字（X=280/t.co=23，TG=4096，XHS=1000），nock 拦截 12 矩阵测试覆盖完整。

B2 优势：D2/D4 各 +1。out_of_scope 含「自动发布」「消息队列」并给动机说明（5-15 条/天不需要）；F7 文档先于实践，明确触发时机；MCP 扩展保持向下兼容，小红书频控 warning 阈值量化（≥5 条）。

B2 弱点：D3 -3（格式转换无字符上限数字，tags 映射硬编码无完整清单，content_type fallback 未说明）。

---

### S3 — dark mode bugfix（brainstorm 应跳过）

| 维度 | A3 | B3 |
|------|----|----|
| D1 方向明确性 | 7 | 9 |
| D2 功能完整性 | 8 | 6 |
| D3 量化约束 | 7 | 9 |
| D4 范围控制 | 7 | 8 |
| b5 skip 判断奖励 | - | +1 |
| **Total** | **29** | **34** |

B3 正确触发了跳过逻辑，并在 brainstorm 字段写明理由（「根因已知，改动仅 2 文件」），获 +1 奖励。技术选型写死（github-dark、#0d1117、!important 兜底），acceptance 全为可执行/可观测命令。

A3 弱点：试图解决全站 dark mode 切换（双主题方案），超出 bug 修复范围；F2 acceptance 只检查 CSS 文件内容存在，不是运行时验证；对 darkMode 策略的「先查再写」隐含在 notes 而非 acceptance。

B3 弱点：D2 -2（将站点定性为 light-only 是单方面假设；若站点有 dark mode 切换，单 github-dark 方案会锁死代码块颜色）；!important 兜底是 workaround，未说明可移除条件。

---

## 核心发现

### 发现 1：brainstormer 的价值在「方向选择」，不在「文档质量」

S1/S2 中 A 以 D3（量化约束）压过 B：直接 Plan 把所有 token 投进 plan 文档，能写更细的参数；B 先花 token 发散，剩余 token 做 plan，量化精度略降。

但 B 的选择实质上更适合项目：
- **B2 选 Python**（existing stack），A2 引入 TypeScript + zod —— 对 Node.js + SQLite 的小项目是额外技术债
- **B1 明确排除 ESP**（Resend/Postmark），给出成本理由 —— A1 也没选 ESP，但没说「为什么不」，out_of_scope 较空洞
- **Wildcard 的「两步确认节点」** 被 B2 吸收进 `--preview` flag，这是 brainstorm 特有的发现

**当前 4 维评分衡量的是文档精度，不是架构适配度。** 两者不同：精度可以补（写清楚），适配度出错后修改成本高（换语言 > 加参数）。

### 发现 2：skip 判断正确且有价值（B3 +5）

B3 准确识别了「根因已知的 2 文件改动不需要 brainstorm」，在 brainstorm 字段写明跳过原因，而不是静默执行。这是我们设计的正确行为：

- brainstorm 条件门设计是对的
- B3 还在 task 字段写出了更精准的问题描述（inline style 优先级），而 A3 的 task 描述停留在症状层（「白底黑字」）

### 发现 3：B2 出了更合理的 out_of_scope

「自动发布（发布时机人工决定）」和「消息队列（5-15 条/天不需要）」这两条来自 brainstorm 的 Wildcard 分析，A2 完全没有这两条边界，未来更容易蔓延。D4 上 B 多得 1 分反映了这一点。

---

## 结论与裁定

**原始方案「brainstormer 插入 RBPI 流程」= 保留，但不以 task_plan 分数为主要评估轴。**

核心发现：

1. **触发场景（S1/S2）**：brainstormer 对 task_plan 文档质量无显著提升（A+6），但产出了更合适的架构方向（Python vs TypeScript，无 ESP，有 --preview 节点）——这部分价值在现有 4 维评分里不可见
2. **跳过场景（S3）**：B 明显优于 A（+5），brainstorm 的条件门正在正确工作
3. **总分接近平手**（A=98, B=97），说明 brainstormer 不拖累计划质量，不构成纯 cost

**结论**：保留 `brainstormer`，接受两个已知权衡：

| 权衡 | 说明 |
|------|------|
| D3 量化精度略降 | 触发场景 B 的 HTML 参数、字符限制不如 A 精确，需要 Plan agent 在接收 options.md 时意识到补量化 |
| 架构适配度提升 | brainstorm 帮助避免了 A2 引入 TypeScript 的技术债，以及 B1/B2 更精准的 out_of_scope 边界 |

**落地调整**（一条，不大改）：Plan agent 在 options.md 选定方向后，应在 notes 字段补全关键量化参数（字符数/颜色值等），弥补 brainstorm 消耗 token 导致的精度损失。

---

## 产出留痕

- `prompts/`：scenarios.md、system-A.md、system-B.md、scoring.md
- `outputs/`：A1/B1/A2/B2/A3/B3 各一份 task_plan JSON
