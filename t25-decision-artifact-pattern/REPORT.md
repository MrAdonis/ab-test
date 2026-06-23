# t25 REPORT — 「选择型任务的产物设计」模式 13 入 skill-design-patterns.md

**日期**：2026-06-21
**判定**：❌ **ROLLBACK**（B 49 vs A 51.5，不入配）
**来源**：用户分享 joeseesun/qiaomu-icon-generator，对照 `~/.claude/references/skill-design-patterns.md` 12 模式找真缺口。

## 假设

现有 12 模式无一条管「skill 产出是**一组供人选择的候选**（封面/配色/命名/方案）时该生成什么」。qiaomu 的三件套（校准候选数 6-12 默认 10 + 对照稿 contact sheet + 压力测试稿 favicon-readability-sheet）+ 人在回路（选定前不覆盖生产）可泛化为新模式 13。

## 方法（t24 严测）

- **单变量**：arm A 读真实 12 模式框架，arm B 读 `/tmp/t25-framework-B.md`（12 + 模式 13），两 arm 同一元指令「先判断哪些模式适用本 skill 再写 SKILL.md」，唯一差异 = 模式 13。
- **6 场景含灰区 + 跳过**（不 cherry-pick B 主场）：S1 hero配色 / S2 命名（clear-hit）；S3 MD→PDF / S4 天气API（clear-skip，noise 测试）；S5 信息图（gray-单产出）；S6 重构方案（gray-文本）。
- **盲评**：每场景独立 Opus 评分员，只看两方案（标甲/乙，A/B 打乱、不告知哪个加了模式 13），先独立列「该 skill 应包含什么」再打分；clear-skip/gray 场景显式 noise penalty。

## 打乱映射（解码用）

S1/S3/S5：甲=B，乙=A ｜ S2/S4/S6：甲=A，乙=B

## 结果

| 场景 | 类型 | A | B | 胜 | 关键发现 |
|---|---|---|---|---|---|
| S1 hero配色 | clear-hit | **8.5** | 7.0 | A | B「压力测试稿」被独立判为给挑色任务过度工程 |
| S2 命名 | clear-hit | **9.0** | 8.5 | A | B stress-test + emoji + 学术引用 = 轻度堆料 |
| S3 MD→PDF | clear-skip | 8.5 | **9.0** | B | 两方无 noise；B 恰好多引擎 fallback 链（与模式13无关）|
| S4 天气API | clear-skip | **9.0** | 8.0 | A | B 给 schema 塞 humidity/wind 噪声（与模式13无关）|
| S5 信息图 | gray-单产出 | 8.0 | **8.5** | B | B 边际堆料但有跳过门兜住，净质量略高 |
| S6 重构方案 | gray-文本 | **8.5** | 8.0 | A | B 生搬 contact-sheet/候选数硬下界到文本建议 = noise |
| **合计** | | **51.5** | **49.0** | **A** | |

A 胜 4 场，B 胜 2 场（均为与模式 13 无关的旁支差异）。

## 为什么回滚（不是噪声，是真信号）

1. **模式 13 在它本该发力的 clear-hit 场景（S1/S2）反而拖累 B**。盲评员（不知道哪个加了模式）独立判定：模式 13 推着生成器给「挑配色 / 挑名字」这种本就轻量的选择流程硬加**压力测试稿**和**对照机制**，属过度工程。即三件套对「真·候选集」任务都偏重。
2. **跳过门不可靠**。S5 跳过门兜住了（B 标注「可选」+ 显式跳过），但 S6 失效——B 仍把视觉素材的 contact-sheet / 候选数硬下界生搬到文本重构建议上，正是跳过门设计目标却没拦住。
3. **B 的两场胜出都与模式 13 无关**（S3 引擎 fallback、S5 边际）——不能归功于补丁。

结论：模式 13 **过度规定**（三件套对轻量选择任务都太重）+ **跳过门不可靠**（文本场景生搬），净负向。框架现有 12 模式已隐含覆盖「人在回路」（模式 8 触发 + coding-dod 破坏性操作安全），不需要专门一节。

## 回滚动作

真实改动只在 `/tmp/t25-framework-B.md`，真实配置 `~/.claude/references/skill-design-patterns.md` 全程未动。回滚 = 不应用模式 13，无需还原。

## 派生（仍开放，需各自单独测）

对照分析时识别的另两个微调（**未进本次单变量测试**）：
- Gap 2：模式 1「硬停 fallback」补一句「有合理降级链时走 graceful degradation 而非硬停」——qiaomu 的 PNG 失败回退 SVG 是好例子。
- Gap 3：模式 10a「阈值要引用」补「来自交付规范/平台硬性约束的阈值免引用」——如 favicon 32px 是平台事实非主观品味。

二者方向更窄、更像真缺口，但本次为单变量隔离未测。若日后要做，各起一个 tN 单独验证，**不与模式 13 捆绑**（模式 13 已否决）。

## 沉淀

负反馈记入 `~/.claude/projects/-Users-edon/memory/feedback_decision_artifact_pattern_rejected.md`（confidence: high）。
