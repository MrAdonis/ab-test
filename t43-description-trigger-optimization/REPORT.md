# t43 — Description 触发优化（train/test 分离防过拟合）AB Test

**日期**：2026-07-02
**来源**：Claude Science skill-creator（`TTTPOB/extract-claude-science-skills` 从 Linux binary 抽取，Apache-2.0）逆向出的 description 优化闭环，蒸馏为 `skill-design-patterns.md` 模式 13。
**验证目标**：模式 13 作为"给 skill 写/改 description 时"的方法增量，是否真让产出更好——按 `feedback_skill_ab_testing`「外部改动必须 AB，无提升则回滚」。

## 设计

- **A 臂（baseline）**：只有现有模式 8（触发条件=可观测特征）+ 模式 9（progressive disclosure / description 唯一触发 / 对抗 undertrigger 写 pushy）。
- **B 臂（increment）**：A 的全部 + 模式 13（造 20 条 eval query、一半 near-miss 负例、60/40 train/test、每条跑 3 次取稳定触发率、按 test 分选版；关键认知—简单单步 query 不触发）。
- 两个场景，各出 A/B：
  - **S1**：修一个触发混乱的真实 skill（`xiaohongshu`）description——既误触发（抓取公开内容该走 routing.md）又漏触发（限流恢复/安全频率）。要求「说明用什么方法确认它真改好了，不是凭感觉」。
  - **S2**：给新 skill（`changelog-gen`）写并优化 description，不能在 commit message / PR 总结 / release notes 三个相邻任务上误触发。
- generator + judge 均 Sonnet、fresh context（按 AB baseline 惯例）。裁判盲评、匿名甲乙、**每场景位置对调跑两个裁判**防位置偏差。评分三维：description 设计质量 40 / 验证严谨度 40 / 诚实度 20。

## 结果

| 场景 | 裁判 | A（baseline）| B（increment）| 胜方 |
|------|------|:---:|:---:|:---:|
| S1 | order1 | 67 | 90 | **B** |
| S1 | order2（对调）| 68 | 89 | **B** |
| S2 | order1 | 54 | 89 | **B** |
| S2 | order2（对调）| 57 | 88 | **B** |

**4/4 一致 B 胜，位置对调后结论不翻转，平均 B 89.0 vs A 61.5（+27.5），dominant。**

## 差距来自哪里（不是运气）

拉开分差的是「验证严谨度」这一维，恰好是模式 13 直接作用的地方：

- **B 臂真去构造了正负例并拿到可量化对比**。S1-B 起了 3 个独立 Haiku 子代理做隔离盲判，20 条带 ground-truth 的 query（负例专挑"抓取小红书内容""纯文案"两类共享关键词的 near-miss），A/B 版各跑 3 次，实测出旧 description recall 8/10（#4 封号申诉稳定漏触发、#6 养号预热判定抖动 N,Y,N），新版 recall 10/10、60 次判定零抖动。S2-B 造 20 条 eval query 逐条 near-miss 推演，**据此真的改写了 description 结构**（从纯正例列举改成正例 + 显式 Do NOT）。
- **A 臂停在字面/人工层面**。S1-A 自认"静态字面匹配审计"——自己写词、自己核自己的用例是否覆盖，裁判点名"循环论证"。S2-A 只用表格归纳三个结构性锚点，没造任何 eval query。
- **诚实度也顺带拉开**：B 臂因为真做了验证，才有具体局限可交代（"单 skill 隔离判定无法复现多 skill 竞争"）；S2-A 没做验证=无局限可报，被判为"沉默掩盖方法论边界"（7/20）。

值得注意：模式 13 的价值不止"结论更可信"，而是**验证动作本身反过来改进了产物**——S2-B 是因为逐条推演 near-miss 负例才发现三处真实误触发风险并修掉的。方法不是事后打分，是设计回路的一部分。

## 裁决

**KEEP。** 摘掉 `skill-design-patterns.md` 模式 13 的「未 AB，属待验证方法」标记，改为已验证（t43，B 89.0 vs A 61.5，4/4 一致，2026-07-02）。自检清单对应项的「待验证」也摘掉。

## 局限（如实）

- generator 和 judge 都是 Sonnet，测的是"有没有模式 13 引导"下同一底模的产出差，不是不同底模。
- 两场景各 1 样本、裁判 Sonnet。分差足够大（+27.5 且 4/4 无翻转）故结论稳，但样本量小。
- 底模大版本跳变时按 `wiki-lifecycle.md §④` 回测——不过本条 margin 很大，退役压力低，优先回测 margin 小的规则。
