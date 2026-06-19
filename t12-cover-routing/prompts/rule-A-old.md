# 条件 A（旧版 / 基线）

路由表 `{{ROUTING_ROW_SLOT}}` 处 **没有任何封面/海报相关行**——即三条散路（AI生图 / HTML排版 / 设计约束）没有统一入口，路由表里这一格直接删除（上下两行直接相邻）。

代入共享背景的路由表后，A 的表为：

| 信号 | 触发 |
|------|------|
| 可视化需求 | `/diagram` 自动选型 |
| UI mockup/设计稿/interactive prototype | 默认输出 HTML 文件，不出 markdown 描述 |
| 会话结束/阶段切换 | `/handoff` |

你仍然拥有共享背景里列出的全部能力（`reference_x_article_cover_prompts.md` / `/baoyu-infographic` / `/paper-layout` / `design-system §海报封面`），只是路由表里没有显式告诉你「封面/海报/一页纸 走哪条」。
