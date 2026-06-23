# t25 — 「选择型任务的产物设计」新模式入 skill-design-patterns.md

**日期**：2026-06-21
**来源**：用户分享 joeseesun/qiaomu-icon-generator（一句话生成 App 图标的 skill），对照 `~/.claude/references/skill-design-patterns.md` 12 模式找真缺口。
**改动**：新增「模式 13. 选择型任务的产物设计（候选集 + 对照稿 + 校准数量）」+ 一条自检清单项。**单变量**——arm B 比 arm A 只多模式 13，不含其它微调。

## 缺口诊断

现有 12 模式全在管「指令质量 / context 加载 / 失败处理」，无一条管「当 skill 产出是**一组供人选择的候选**（而非单一确定结果）时该生成什么」。qiaomu 的答案是三件套：校准候选数（6-12 默认 10，带上下界理由）+ 对照稿（contact sheet）+ 压力测试稿（favicon-readability-sheet 专测 32px）+ 人在回路（选定前不覆盖生产）。可泛化到任何「发散给用户选」的 skill：封面候选 / 配色 / 命名 / 方案。

## 候选补丁（arm B 独有）

完整文本见 `/tmp/t25-framework-B.md` 的「## 13.」段。核心三件套 + 跳过门「产出是'一个答案'还是'一组待选项'？只有'一组待选项'才触发」。

## 实验设计（吸收 t24 对抗审核的三条教训）

1. **对称脚手架**：两 arm 用同一元指令「先判断框架里哪些模式适用本 skill，再写 SKILL.md」，唯一差异 = arm B 的框架文件多模式 13。消除「只有 B 被要求先分类」的 confound。
   - arm A 读 `~/.claude/references/skill-design-patterns.md`（12 模式）
   - arm B 读 `/tmp/t25-framework-B.md`（12 + 模式 13）
2. **6 场景含灰区 + 跳过**（不 cherry-pick B 主场）：
   | 场景 | 任务 | 类型 | 模式 13 预期 |
   |---|---|---|---|
   | S1 | skill：为落地页生成多个 hero 配色方案供选 | clear-hit | 应触发（配色候选集）|
   | S2 | skill：为新产品生成多个命名候选供选 | clear-hit | 应触发（命名候选集）|
   | S3 | skill：把 Markdown 文件转成 PDF | clear-skip | 应跳过（单一确定产出）= noise 测试 |
   | S4 | skill：调用天气 API 抓数据返回 JSON | clear-skip | 应跳过（单一确定产出）= noise 测试 |
   | S5 | skill：根据一段文字生成一张信息图 | gray-单产出 | 倾向跳过（默认出一张，非候选集）——测 B 会不会过度把它扭成候选集 |
   | S6 | skill：分析代码库给出重构方案建议 | gray-文本推荐 | 部分触发（文本对照思路，但不强求视觉对照稿/候选数下界）——测 B 是否正确降级 |
3. **盲评**：每场景一个独立 Opus 评分员，只看该场景两方案（标甲/乙，A/B 已打乱、不告知哪个加了模式 13），先独立列「这个 skill 该包含什么」再打分；**显式 noise penalty**：对 clear-skip/gray 场景硬塞候选集机制（contact sheet / 候选数下界）扣分。

## 评分维度（各 /10）
SKILL.md 整体质量：是否抓住该 skill 真正的设计要点、是否过度/不足、是否有堆料。模式 13 只是其中一个观察点，不单独给分（避免产出形态对齐评分偏好的 t24 confound）。

## 结论
见 REPORT.md（生成 + 盲评后回填）。
