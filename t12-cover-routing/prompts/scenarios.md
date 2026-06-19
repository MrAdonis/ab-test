# 5 个评测场景（A/B 相同）

1. **clear-aigen** — 「帮我做一张 X 文章封面，文章讲期权策略。」
2. **clear-html** — 「帮我做个一页纸的投资备忘，A4 能打印的那种。」
3. **clear-constraint** — 「我要给前端同学海报区块的设计参数规范，让他在代码里实现。」
4. **ambiguous-bare** — 「帮我做一张封面。」（无任何限定）
5. **overlap-poster** — 「做个海报。」（无任何限定）

## 期望路由（评分用，agent 不可见）

1. clear-aigen → ① AI生图（`reference_x_article_cover_prompts.md` + `/baoyu-infographic`）
2. clear-html → ② `/paper-layout`
3. clear-constraint → ③ `design-system §海报封面`
4. ambiguous-bare → 先澄清（问是 AI生图 / HTML排版 / 设计约束 哪种）
5. overlap-poster → 先澄清 或 给默认（成品图默认 ①，但需点明可切 ③）
