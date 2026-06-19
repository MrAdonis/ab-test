# t15 — pm-skills 偷优化点 AB 测试报告

> 日期：2026-06-11
> 来源：拆 phuryn/pm-skills（14k+ stars）对照自有 skill，挑出 2 个真优化点跑 AB。
> 方法：Sonnet 生成 A（基线）/ B（注入方法论）8 份输出，Sonnet 盲评委按 5 维打分。
> 纪律：B>A 才落地 live config，否则回滚（feedback_skill_ab_testing / feedback_ab_test_on_integration）。

## 测的两个点

| # | 偷自 | 注入目标 | 内容 |
|---|------|----------|------|
| 1 | `strategy-red-team` | cross-review 新增 `redteam` 子模式 | 承重假设 → steelman → 攻成「Fails if」→ 按影响×概率×测试便宜度排序 → 每条给四件套（Fails if / 本周证据 / Kill 阈值 / 最便宜测试）→ self-refute 不捏造 |
| 2 | `competitive-analysis` | biz/competitor-scan.md | ① 矩阵维度打标 table-stakes vs differentiator ② 收尾强制三桶 All in / 补平 / 明确不追(Ignore) |

## 场景

- **RT-1**：AI 会议纪要 SaaS 计划（承重假设弱，测能否找到+给 kill 标准）
- **RT-2**：代码片段工具加团队共享库（大体扎实，测是否捏造怀疑 / 承认扎实）
- **CP-1**：社区维修 O2O（与 competitor-scan 示例同域）
- **CP-2**：咖啡馆库存排班 SaaS（跨域测泛化）

## 评分矩阵（满分 50/场景）

### Track 1 Red-Team

| 场景 | A | B | margin |
|------|---|---|--------|
| RT-1 | 30 | **44** | **B +14** |
| RT-2 | 36 | **45** | **B +9** |
| 合计 | 66 | **89** | **B +23** |

B 两点系统性领先：① 把"风险描述"转成"可证伪测试"（kill 阈值 + 本周最便宜测试，操作员当天能开始）；② 诚实度——两场景都有"站得住的部分"独立区块，具体承认扎实点（"月留存 92% 是真实护城河""转录 API 选择合理"）而非客套。A 在 RT-1 几乎全程唱衰、结论埋在最后五点之后。

### Track 2 Competitor

| 场景 | A | B | margin |
|------|---|---|--------|
| CP-1 | 35 | **42** | **B +7** |
| CP-2 | **43** | 40 | A +3 |
| 合计 | 78 | **82** | **B +4** |

B 净胜但 margin 小，CP-2 反输。评委核心诊断（本次测试最关键的发现）：

> 三桶/打标的价值取决于 **Ignore 条目有没有带经济/战略理由**。CP-1 里 Ignore 每条都附了理由（"陪跑烧钱""贴牌打工利润薄""师傅固定成本下亏损"）= 新判断，胜。CP-2 里 A 的"过度竞争区+功能蔓延"已覆盖同等取舍信息，B 的三桶只换标签没加判断 = 形式增量；且 B 缺了 A 的"先 30 家内测验证付费意愿"行动序列，所以反输。

**结论：三桶不是银弹。Ignore 带理由则提升决策密度，不带则堆料；三桶不替代"下一步具体行动"。**

## 裁决：两个都 keep，#2 带边界落地

| # | 裁决 | 落地文件 |
|---|------|----------|
| 1 | **Keep**（B +23 大胜） | 新建 `~/.claude/skills/cross-review/references/redteam-checklist.md` + `cross-review/SKILL.md` 增模式 D（redteam 子模式，单模型不调外部脚本） |
| 2 | **Keep + 堆料边界**（B +4 净胜，CP-2 暴露堆料风险） | `~/.claude/skills/biz/references/competitor-scan.md` 注入打标 + 三桶，并写死两条约束：① Ignore 必须带理由 ② 三桶不替代具体行动 |

把 CP-2 反输的教训直接写进 skill 的"堆料边界"段——这正是 edit-discipline §1（少而准、带触发门，不无条件套）的落地：不是无脑加框架，而是加了框架同时加了"什么时候它是 noise"的判断。

## 没采纳的（拆 pm-skills 时排除）

- **pre-mortem 独立 skill / 风险分类法**：与 redteam 重叠，堆料风险，不新建。
- **brainstorm 多视角（PM/Designer/Engineer 三镜）**：自有 brainstormer 的硬 Wildcard + no-ranking 已更强。
- **/discover 7-step 全链编排**：仪式过重，自有 /plan RBPI 已覆盖。
- **Further Reading 外链漏斗 / 68-skill 细粒度切分**：纯结构噪音。
