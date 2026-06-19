# 条件 B（新版 / 改动）

路由表 `{{ROUTING_ROW_SLOT}}` 处新增这一行：

| 封面 / KV / 海报 / 一页纸 | 三选一：① **AI生图**（X文章封面/小红书封面/海报）→ `memory/reference_x_article_cover_prompts.md`（6套框架）+ `/baoyu-infographic`；② **HTML排版**（研报/白皮书/一页纸/正式文档）→ `/paper-layout`；③ **设计约束**（给实现用的参数规范）→ `design-system §海报封面` |

代入共享背景的路由表后，B 的表为：

| 信号 | 触发 |
|------|------|
| 可视化需求 | `/diagram` 自动选型 |
| 封面 / KV / 海报 / 一页纸 | 三选一：① **AI生图**（X文章封面/小红书封面/海报）→ `memory/reference_x_article_cover_prompts.md`（6套框架）+ `/baoyu-infographic`；② **HTML排版**（研报/白皮书/一页纸/正式文档）→ `/paper-layout`；③ **设计约束**（给实现用的参数规范）→ `design-system §海报封面` |
| UI mockup/设计稿/interactive prototype | 默认输出 HTML 文件，不出 markdown 描述 |
| 会话结束/阶段切换 | `/handoff` |

你拥有共享背景里列出的全部能力。
