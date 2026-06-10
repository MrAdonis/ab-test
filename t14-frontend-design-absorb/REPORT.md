# t14: frontend-design 增量吸收进 design-system — AB Test 报告

**日期**: 2026-06-11
**结论**: **不吸收**（总分平手 A 8.07 vs B 8.03，按「无提升则回滚」），frontend-design 插件卸载

## 背景

配置体检发现 frontend-design 插件（claude-plugins-official）于 2026-06-03 被复装启用，与 2026-05-28「随 example-skills 整包禁用」决策冲突，且与自有 design-system skill 双重触发。对比两者全文后提炼出 frontend-design 的 4 点真实增量，做成 variant B 测试是否值得吸收。

## 设置

- **Variant A**: design-system SKILL.md 原版
- **Variant B**: A + 4 处增量：
  1. Space Grotesk 跨代收敛禁令（与 Inter 同列，不同项目必须换字体）
  2. 风格池刻意拉宽（organic / art deco / soft pastel / industrial / retro-futuristic / playful / maximalist 都是合法方向）
  3. 「一个记忆点」差异化追问（开工前回答"这个页面唯一会被记住的是什么"；dashboard/后台不适用）
  4. 实现复杂度匹配美学愿景（maximalist 配足动效代码，minimalist 靠克制与字排细节）
- **生成**: 6 个 Sonnet 子代理（3 场景 × A/B），各自只读对应 variant
- **评审**: 3 个 Sonnet 盲评 judge，双盲（设计稿 1/2，顺序每场景随机）
- **评分维度**: 场景适配 30% / 反 AI 审美 30% / 设计完成度与记忆点 25% / 可用性硬指标 15%

## 结果

| 场景 | A | B | 胜者 | 关键证据 |
|------|-----|-----|------|---------|
| S1 中文 landing（Driftnote 笔记工具） | **8.0** | 6.3 | A | B 落入 hacker green + emoji icon + radial glow 的典型 AI Tell；A 用暖纸色 + `//` `[[` 文字符号 icon + CTA 大字水印 |
| S2 英文 portfolio（建筑摄影师） | 8.0 | **8.8** | B | B 的无缝拼接网格（border 代 gap）+ hero-index 信息条复刻画廊图册语言，记忆点真实落地 |
| S3 dashboard（反向场景） | 8.2 | **9.0** | B | B 赢在信息密度（p99/5xx/节点状态色语义），双方都克制——与 B 增量无关 |
| **均分** | **8.07** | **8.03** | **平手** | |

## 分析

1. **B 胜 2/3 场景但被 S1 大败（-1.7）完全抵消**。S1 里 B 的生成代理无视了 variant B 自己新增的「风格池拉宽」规则，缩回 hacker green 安全区——增量 prose 没有可靠改变生成行为。这本身就是证据：加这 4 段文字付出 context 成本，却不产生稳定效果。
2. **S2 的胜利可部分归因于「一个记忆点」规则**（hero-index + 无缝网格正是对该追问的回答），但同一规则在 S1 没救场。n=1/场景，方差大于规则效应。
3. **S3 验证了增量不产生噪音**（B 的 dashboard 同样克制），排除了"吸收会污染克制场景"的担忧——但"无害"不等于"有益"。
4. 与 t-distill（Impeccable detector 蒸馏）结论同族：**往 design-system prose 里加规则文字，AB 测不出提升**。品味规则的瓶颈不在条目数量，在生成时是否被执行——确定性问题走 lint 脚本，不走 prose。

## 落地

- ✅ frontend-design 插件卸载，cache 归档 `~/.claude/archive/plugins/frontend-design`
- ✅ 决策回写 `~/.claude/rules/skill-tiers.md`（example-skills 节）
- ✅ 负反馈追加 memory `feedback_design_system_distill_rejected.md`（rejected-edit buffer）
- ❌ variant B 4 点增量不合入 design-system

## 文件

- `variant-A.md` / `variant-B.md` — 两版规范
- `prompts/scenarios.md` — 场景与评分定义
- `outputs/s{1,2,3}-{A,B}.html` — 6 份产出
- `source-frontend-design.md` — 插件原文存档
