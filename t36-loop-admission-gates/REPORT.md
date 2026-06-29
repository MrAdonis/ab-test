# t36 — Loop 准入四闸 / 搭建顺序 / cost 杀闸

**日期**：2026-06-25
**来源**：X @Cander_zhu 推荐的「Loop Engineering」三篇（Addy Osmani `addyosmani.com/blog/loop-engineering/` + Anatoli Kopadze X Article《Loops explained: Claude, GPT, Mira》+ Peter Steinberger / steipete 博客与演讲）
**落点**：memory `reference_incontext_loop`（loop 选型单一源真理），不另起文件

## 假设

外部「Loop Engineering」框架里，相对现有配置真正新的三条——准入四闸（何时建）/ 搭建顺序（怎么分阶段）/ cost 杀闸（何时停）——并进 loop 选型规则能提升 loop-design 判断质量。已覆盖部分（五部件的 Sub-agents 分工、Verifier 确定性验收、Connectors/MCP、Comprehension 防认知投降）不重复吸收。

## 方法

- A = 现有 loop 选型规则（四类 loop + 五字段 + 退出闸 + 「一次性脚本不套 loop」）
- B = A + 候选三条
- 5 个区分性场景（含 1 个「好候选不该被误杀」对照组），Sonnet 生成 + Sonnet 裁判，四维度（判断正确性/推理质量/不过度/可执行性）每场景折算满分 10、总分 50

场景设计锚点：S1 一次性任务伪装 loop（应拒）/ S2 主观质量自动发布（应拒或强警告）/ S3 好候选但想直接挂 cron（应强制搭建顺序）/ S4 接受率约半（应杀不应继续调 prompt）/ S5 四闸全过（对照，应建）。

## 结果

| 场景 | A | B | 胜方 |
|------|---|---|------|
| S1 一次性任务 | 9.25 | 9.50 | B |
| S2 主观质量任务 | 9.25 | 9.75 | B |
| S3 好候选强制顺序 | 8.50 | 9.75 | **B +1.25** |
| S4 接受率低杀闸 | 8.75 | 9.75 | **B +1.0** |
| S5 对照组防误杀 | 9.50 | 9.75 | B |
| **总分** | **45.25** | **48.50** | **B +3.25** |

两组核心判断 5/5 全对——baseline 并不蠢，「一次性脚本不套 loop」已让 A 在 S1/S2 判对该不该建。B 的增量集中在：
- **S3 搭建顺序**（+1.25）：B 给出 Manual→Skill→Loop→Schedule 四步，A 缺「先手工跑一次」这个先手。
- **S4 cost 杀闸**（+1.0）：B 挖到「Verifier gate 设计缺陷 + agent 钻空子」根因并建议停掉退回手动，A 只到「Exit when 不够严格」表层、仍倾向继续调。
- **准入四闸（S1/S2）仅 +0.25~0.5**：与现有规则高度重叠，边际价值低。

## 决策：KEEP（trim 版）

按 Edit Discipline「少而准、能说出删了什么」，**不全量照搬**：
- 入配：搭建顺序 + cost 杀闸（真正增量）；准入四闸**压成一行框架**而非全量枚举（barely moved 但 S3/S4 挂在它上）。
- **未吸收**：五部件解剖、Connectors——与 `coding.md` 子代理分工 + MCP 实践重叠，加即堆料（记入 rejected-edit 思路）。

## 教训

baseline 在「该不该建 loop」上已不蠢（t31 同源教训），外部框架的真正增量往往不在最显眼的「准入清单」，而在配置真空地带的**过程纪律**（分阶段搭建）和**止损信号**（接受率杀闸）。吸收时按场景 margin 拆解，只留 discriminating 的部分。
