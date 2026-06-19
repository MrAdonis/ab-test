# t9 — mattpocock/skills 吸收前后 AB test

**日期**：2026-06-08  
**目标**：量化 /caveman、/grill-me、/diagnose 三个新 skill 对响应质量的实际提升  
**方法**：Sonnet 生成 A/B 产出，Sonnet 独立评分，3 维度各 0-5 分

---

## 评分矩阵

| 场景 | 维度 | A（baseline） | B（新 skill） |
|------|------|:---:|:---:|
| S1 caveman | 信息完整度 | 5 | 4 |
| S1 caveman | 废话密度 | 3 | **5** |
| S1 caveman | 可执行性 | 4 | 4 |
| **S1 小计** | | **12** | **13** |
| S2 grill-me | 需求覆盖深度 | 3 | **5** |
| S2 grill-me | 可执行性 | 4 | 3 |
| S2 grill-me | 交互体验 | 2 | **5** |
| **S2 小计** | | **9** | **13** |
| S3 diagnose | 反馈环建设 | 3 | **5** |
| S3 diagnose | 假设多样性 | **5** | 3 |
| S3 diagnose | 可操作性 | 4 | 4 |
| **S3 小计** | | **12** | **12** |
| **总计** | | **33** | **38** |

**Winner：B 总分领先 5 分（+15%），S1/S2 胜，S3 平**

---

## 逐场景结论

### S1 caveman — B 胜（13 vs 12）

评委 key insight：  
> caveman 场景下 B 用更少篇幅传递了等价信息，废话密度优势决定胜负。A 的格式开销（分隔线、粗体标签、嵌套列表）在高密度问答里是净负担。

- B 唯一失分：漏了"AOF 可手动编辑修复误操作"这个实用细节（-1 信息完整度）
- 核心收益：同等信息量，格式噪音砍掉约 40%
- **结论：收，适合在长技术对话中主动触发**

### S2 grill-me — B 大胜（13 vs 9）

评委 key insight：  
> grill-me 的核心是决策树遍历而非清单轰炸。B 识别出根节点（发什么内容）并一次只问一个；A 批量抛 9 个假设，既违反了 one at a time 规则，又绕过了影响所有后续决策的前置问题。

- A 的「Assumptions 前置」在这里反而暴露了弱点：根节点未厘清，9 条假设建立在错误的前提上
- B 主动利用已知上下文（Supabase、Resend、三语路由）做了 codebase exploration，这正是 skill 要求的 "explore instead of ask"
- A 可执行性小胜（确认 9 条后信息更全），但根节点未锁会导致方案走偏
- **结论：强收，对复杂需求探索有明显提升；对简单 3 条以内的假设核对仍用 Assumptions 前置**

### S3 diagnose — 平局（12 vs 12）

评委 key insight：  
> A 的结构化假设分析（H1-H4 各带 Supports/Conflicts/Test）是 B 的短板；B 的主动触发 feedback loop（replay-500.sh、k6 压测）是 A 的短板。两者互补而非一方碾压。

- 理想答案：B 的 feedback loop → A 的假设框架，串起来跑
- **结论：diagnose skill 不替代假设驱动调试，而是在 Phase 1 补了一层"先让 bug 可重现"的前置步骤。两者叠用**

---

## 配置层面决策

| 结论 | 动作 |
|------|------|
| /caveman 有效，格式噪音问题真实存在 | 保留在 Daily Core，触发信号已入 skill-chains.md |
| /grill-me 对复杂需求显著优于批量假设 | 保留在 Daily Core；简单假设（≤3条）仍走 Assumptions 前置 |
| /diagnose 是 Phase 1 补充，非替代 | 调整触发条件：先建 feedback loop → 再跑假设驱动调试；两者顺序叠用 |
| S3 平局揭示了 coding.md 的一个真实缺口 | **待做**：在 coding.md 假设驱动调试的 OBSERVE 阶段前加一步"先建可跑 feedback loop"，将 diagnose skill 的核心吸收进规则 |

---

## 原始产出

见 `outputs/` 目录：A1/B1（caveman）、A2/B2（grill-me）、A3/B3（diagnose）
