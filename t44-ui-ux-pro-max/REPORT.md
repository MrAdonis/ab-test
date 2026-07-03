# t44 — ui-ux-pro-max-skill 叠加价值 AB 测试

- 日期：2026-07-03
- 被测：nextlevelbuilder/ui-ux-pro-max-skill（agentskillshub Top Rated，★99k 营销位）叠加在自有 design-system 基线上是否产生可测提升
- Variant A = design-system SKILL.md 原版（基线）；Variant B = A + ui-ux-pro-max 全文 + BM25 检索脚本（search.py，离线可用，生成代理实际调用了）
- 协议：3 场景 × A/B = 6 个 Sonnet 生成代理（互相隔离）；每场景 3 个 Sonnet 盲评（中性文件名 `blind/s{N}-d{1,2}.html`，A/B 顺序随机）；权重 场景适配30/反AI审美30/完成度与记忆点25/可用性15；单场景差 <0.3 判平手；判定规则 = B 均分未超 A 则不装（沿 t14）

## 结论：REJECT，不装

**A（基线）总均分 8.18，B（叠加）7.96。** B 赢 S1（+0.50），大输 S2（−1.28），S3 平手（+0.12 <0.3）。叠加后整体不升反降，且 S2 的失败模式可归因到该 skill 本身的检索产出。

## 分数矩阵（加权总分，judge 独立）

| 场景 | 盲评 key | A 三票 | A 均 | B 三票 | B 均 | 差（B−A） | 判 |
|------|---------|--------|------|--------|------|-----------|-----|
| S1 中文 SaaS landing「潮汐」 | 稿1=B 稿2=A | 7.93 / 7.70 / 7.79 | 7.81 | 8.26 / 8.11 / 8.56 | 8.31 | **+0.50** | B 胜 |
| S2 英文陶艺作品集 Kiln & Tide | 稿1=A 稿2=B | 8.62 / 8.56 / 8.65 | 8.61 | 7.11 / 7.43 / 7.44 | 7.33 | **−1.28** | A 胜 |
| S3 车队监控 dashboard（反向场景） | 稿1=B 稿2=A | 8.58 / 7.82 / 7.94 | 8.11 | 7.82 / 8.68 / 8.20 | 8.23 | +0.12 | 平手（<0.3） |
| **总均** | | | **8.18** | | **7.96** | **−0.22** | **A** |

## 各场景证据要点（来自盲评原话）

**S1（B 胜 +0.50）**：B 的 teal+珊瑚非对称 bento、功能卡内嵌带真实任务名的迷你看板、真交互定价切换获三票一致好评；A 反而撞了 radial glow 红线（`.hero-glow` radial-gradient，三票都点名）+ 汉堡按钮只切 aria 无菜单内容的伪交互。此场景 ui-ux-pro-max 的风格检索方向正确。

**S2（A 胜 −1.28，决定性）**：B 撞上 brief 明确警示的 **cream+terracotta 工艺站陈词** + hero/about 双 radial glow，画廊 7 件作品复用同一个同心圆 "rings" SVG——与"件件独一无二"文案自相矛盾，三票反 AI 维度 5.0/5.8/5.8（A 为 8.8/8.5/8.8）。A 的 JS 实测高度 masonry「陶架」+ 7 种不同器型轮廓 + 钴蓝釉冷色系三票全部点赞。**关键归因：B 生成代理调 search.py 检索 pottery/craft 风格，拿回的正是这套 terracotta 配色和"手工感=同心圆纹样"的通用答案——检索库把最高频的品类套路端上来，恰好就是评审 rubric 里的 AI 俗套。检索型风格库在需要「唯一记忆点」的创意场景里系统性输出中位数审美。**

**S3（平手）**：B 的暗色控制室克制感、状态色-文字双载体被认可，但被抓到筛选 chip 无 JS 绑定、"156 辆"只渲染 12 行无提示、深色控制台里用彩色 emoji 当状态图标；A 筛选/搜索真实联动但"已完成"状态色与品牌蓝撞色。各有硬伤，净差 0.12 在噪声内。担心的「装饰规则错误泛化到工具界面」未发生（B 的 DENSITY 9 参数反而对路）——该 skill 在反向场景无害，但也无增量。

## 决策与留痕

1. **不装** ui-ux-pro-max（判定规则触发：B 总均分未超 A）。/tmp/uipro 评估副本随 /tmp 自然清理，不进 ~/.agents/skills/。
2. 负反馈已记入 playground memory（`feedback_uiuxpromax_rejected.md`）：检索型设计知识库（BM25 → 风格/配色 CSV）在创意差异化场景输出品类中位数套路，与 design-system 的反 AI 审美原则直接冲突；S1 类结构化 landing 场景它有小幅正贡献，但一正一负一平不构成安装理由。
3. 诚实边界：n=3 场景 × 单次生成，S2 的失败理论上含生成代理个体方差；但失败模式（terracotta+rings 图标）与该 skill 检索库的品类高频答案存在直接因果链，非随机噪声形态。若未来复测，建议 S2 类创意场景加做第二次独立生成再判。

## 复现

- 场景与评分定义：`prompts/scenarios.md`
- 产出：`outputs/s{1,2,3}-{A,B}.html`；盲评副本 `outputs/blind/`
- 被测 skill 来源：github.com/nextlevelbuilder/ui-ux-pro-max-skill（MIT，评估时 tarball 于 /tmp/uipro，安全审查通过：无 postinstall、无外传、危险模式命中均良性）
