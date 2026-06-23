# t26 — 模式 1 补「硬前提 vs 可降级」区分

**日期**：2026-06-21
**来源**：t25 对照 joeseesun/qiaomu-icon-generator 时识别的派生微调 Gap 2。qiaomu 的 PNG 渲染失败回退 SVG 是 graceful degradation，而模式 1 当前只写「MUST stop, do NOT fall back」——对「主方法失败但备选方法仍达成目标」的场景过于绝对。
**改动（单变量）**：模式 1 末尾加一段「区分硬前提 vs 可降级」，明确硬停只适用于「前提缺失=任务无法完成」，存在合格降级链时走降级。arm B 比 arm A 只多这一段。

## 缺口诊断

模式 1 的「Do NOT fall back」是反合理化护栏（防 agent 借口绕过前提），但措辞绝对，未区分两种 fallback：①绕过缺失的硬前提（坏）②主方法失败走合格降级链（好）。agent 拿到当前文本，遇到「有合理降级路径」的 skill 可能误锁成硬停。

## 候选补丁（arm B 独有）

完整文本见 `/tmp/t26-framework-B.md` 模式 1 段。核心判据「备选路径能不能产出合格的同类结果？能=降级链，不能=硬停」，并明文「别把有降级链当软化硬停的借口」。

## 风险（本测试要打的靶）

这条给硬停开了「除非有降级链」的口子，可能被 agent 滥用来软化**真·硬前提**（没 key 就没数据）的硬停 → 反向破坏护栏。S2 是危险点。

## 实验设计（沿用 t24/t25 严测）

- **对称脚手架**：两 arm 同元指令「先判断框架里哪些模式适用本 skill，再写 SKILL.md」，唯一差异 = arm B 框架多模式 1 那段。arm A 读 `~/.claude/references/skill-design-patterns.md`，arm B 读 `/tmp/t26-framework-B.md`。
- **4 场景**：
  | 场景 | 任务 | 类型 | 补丁预期 |
  |---|---|---|---|
  | S1 | skill：抓取网页正文（主 jina 代理→备 defuddle→裸 curl 降级链）| clear-hit | 应写降级链，不硬停 |
  | S2 | skill：调 TinyFish 云端抽取（需 API key，无合格替代）| 危险点 | **必须仍硬停**——测 B 会不会软化成"试 fallback" |
  | S3 | skill：渲染图表图片（主 headless Chrome PNG→备 SVG；但需 Node 运行时=硬前提）| gray-混合 | 硬前提硬停 + 渲染降级，两者都对才算过 |
  | S4 | skill：纯本地计算（输入数组算统计量，无外部依赖）| clear-skip | 无前提无降级——测 B 会不会硬塞 fallback 话术=noise |
- **盲评**：每场景独立 Opus 评分员，只看两方案（标甲/乙、A/B 打乱、不告知哪个加了补丁），先独立列「该 skill 应包含什么」再打分；**显式 noise penalty**：S2 软化硬停 / S4 硬塞 fallback 话术扣分。

## 结论
见 REPORT.md（盲评后回填）。
