# t64 — 规则瘦身回测 round2（rule-lightening-round2）

日期：2026-07-26 | 触发：用户援引 op7418 转述 Anthropic 上下文工程文章（6 条"规则→判断力"转变），续 t62 再跑一轮
方法：clean baseline（`claude -p --safe-mode`，Sonnet 5，剥 user config）+ 真 harness/工具 → 观察行为
重点：补 t62 遗留——过度设计判据的**真靶子场景**（自审+子代理误报），t62 只测了离线建议题（靶向错位）

## S1+S3 过度设计判据（自审场景，on-target，补 t62）

harness = 真 TS 项目，`formatLegacyDate` 看似死码实则有真实消费方，给 clean baseline 一份子代理"这是死码"假报告 + 工具。

| 场景 | 消费方可见性 | clean baseline 行为 | 结论 |
|---|---|---|---|
| S1 in-repo barrel | 本地可 grep（经 `index.ts` barrel re-export） | 用工具追出 barrel 链→拒删→还多发现 buildReportHeader 传递性无调用 | 自覆盖，且超出规则 |
| S3 cross-project | 本地 grep 不到（公开 `exports` API，外部 repo 消费） | 识别库包+公开API→"单仓库 grep 看不到外部消费者=库场景死码误判"→建议 deprecation→拒删 | 自覆盖，命中规则最硬残留 |

**污染修正**：S1 首跑漏了 `--safe-mode`（只加了 skip-permissions 给工具），实为带规则臂，输出直接引用"过度设计判据"规则名——已重跑真 clean 臂（`s1-selfaudit-A-CLEAN.md`），带规则臂留作对照（两臂都拒删，clean 反而多找到传递性链）。

**结论：过度设计判据在所有测过的场景（t62 建议题 + t64 in-repo + t64 cross-project）被 Sonnet 5 完全自覆盖，含它最硬的 grep-不可见跨项目残留。** 规则入配理由（子代理 broad-scan 误报死码→主代理必须亲自核）已是 baseline 反射。**退役候选（t62+t64 三场景一致）。**

局限：n=1/场景、行为自证（非质量盲评，因两臂都"拒删"是明确 pass）；三场景都给了显式"审计报告"当怀疑锚点——"Claude 怀疑自己无外部报告的自发结论"这个更subtle的自审子案未测（但规则文本本就针对"审计报告/子代理结论"，不强针对该子案）。

## S2 反范围蔓延（conversational，clean baseline 单轮）

低摩擦小工具（MD→HTML 预览）+ 顺手加 PDF导出/多主题/历史面板。clean baseline：喊"功能蔓延"、逐个拆成本、判定只有主题切换值当下做、PDF+历史"等核心验证过真实需求再加，避免为不一定用得上的功能返工"、动手前问用户选择。

**结论：反范围蔓延的对话判断部分（抗蔓延+证据优先+核心优先）baseline 自覆盖。** 但规则的 task_plan 制品部分（显式 out_of_scope 清单、边界变更留痕）有跨 session 持久化价值，本轮未测——**不建议整删，只是对话侧冗余。**

## 落地建议
- 过度设计判据：退役 / 瘦身到残留一句，走 supersession（用户拍板全删 vs 瘦身）。
- 反范围蔓延：保留（task_plan 持久化价值未被证伪）。
- 元结论续 t62：低垂果实之外，过度设计判据是本轮扫出的真退役候选——推文"规则→判断力"论点在这条上成立。
