---
description: Skill 分级索引——日常默认优先用 Daily Core，专项用 Specialist，低频库存按需取用
---

# Skill 分级

**入口优先级**：选层级更高、粒度更粗的入口。商务始终从 `/biz` 开始。

> **重要：两类 skill**
> - **User-invocable（可 `/xxx` 触发）**：frontmatter 无 `paths:` 字段
> - **Auto-trigger only（不能 `/xxx`，只在文件路径匹配时自动加载）**：frontmatter 有 `paths:` 字段
>
> Claude Code 产品层行为，两者互斥。下表已区分。

## Daily Core（可 `/xxx` 触发）

| Skill | 场景 |
|-------|------|
| `/biz` | 商务全流程（analyze / scope / quote / prep / review） |
| `/cross-review` | 设计/代码/debug 交叉验证 |
| `/handoff` | 会话结束或阶段切换记录进度 |
| `/write-review` | 内容写完后去 AI 味检查 |
| `/github-quality` | 评估外部 GitHub 仓库 |
| `/web-access` | 联网兜底（登录态/交互/动态渲染） |
| `/caveman` | 响应太冗长时切换精简模式（持续到 "stop caveman"），token -75%，技术信息不减 |
| `/grill-me` | 逐问题压力测试方案——每题带推荐答案，问完才动手；比「批量假设前置」更适合复杂设计探索 |

## Specialist（可 `/xxx` 触发）

| Skill | 场景 | 触发条件 |
|-------|------|----------|
| `/diagram` | 可视化（结构图/统计图） | 流程图、架构图、ER、时序图、柱线饼雷达等——SVG 确定性渲染，中文不乱码 |
| `/baoyu-infographic` | 信息图/文章配图 | 信息图、infographic、高密度信息大图、小红书图文、科普长图——AI 生图路径 |
| `/cover-styles` | 封面/海报 prompt 编译 | X文章封面、小红书/公众号封面、海报KV、封面诊断——8 风格原子（META/STYLE）+ blueprint 编译成单条 prompt，后端走 seedream/codex-imagen；架构随上游 github.com/adrianpunk/Punk-Skill，改库后跑 `cover-styles-verify.py` |
| 本地 Z-Image Turbo（命令非 slash） | 临时配图/mockup/插画，**不要求中文文字**（t2i） | mockup、配图、插画、草图、头图、随手出张图、占位图——且无中文文字准确需求时 → `mflux-generate-z-image-turbo --model /Users/edon/Developer/models/z-image-turbo-mflux-q8`（本地 6B q8，**零 key 零联网免费**，44s/张 1024²，2026-08-05 实测）。**先于 baoyu-imagine（付费 seedream）考虑**；原 codex-imagen.sh 失效停用（memory `reference_codex_imagen_broken_0144`），完整命令与边界见 `references/image-base.md` 决策门 |
| `/persona-ip` | 个人 IP 角色包（照片→三视图→character-spec） | 建个人 IP 形象、角色三视图、character sheet、多张配图人物长相漂移——只管「画的是谁」，产物落 `~/.claude/personas/<ip-id>/`，供 article-illustration / cover-styles 引用 |
| `/article-illustration` | 长文正文配图（一组，非单张） | 长文配图、公众号/X 文章插图、把观点画成一组图、带个人 IP 出镜的正文插图——画风从 `cover-styles/styles/` 选（不自建风格库），人物从 `personas/` 读（只读不写） |
| `video-shotcraft` | 产品宣传片/演示视频（Remotion 确定性渲染） | 把网页/前端项目做成宣传片、产品发布视频、功能演示视频，或单个镜头动效——真实页面截图 + 2.5D 运镜 + 卡点 + SFX，104 镜头卡在线画廊可挑。**只做「网页→视频成片」**：带音轨的已有视频素材剪辑不归它；网页内动效归 gsap-*；录屏路线（歸藏 demo-video）被本 skill 上位替代。2026-08-08 装，Apache-2.0 |
| `/baoyu-youtube-transcript` | YouTube 转录 | YouTube URL |
| `/obsidian` | Obsidian vault | vault 操作/笔记语法 |
| `/generative-ui` | claude.ai widget 设计系统 | 用 show_widget 输出时 |
| `/x-article-publisher` | X Articles 发布 | 发布 Markdown 到 X |
| `/cloudflare` | CF 平台操作（Pages/Workers/D1/R2/AI） | edonspace、客户H 反代等 CF 资源 |
| `/wrangler` | wrangler 部署管理 | CF 部署/配置 |
| `/web-perf` | Core Web Vitals 审计 | edonspace 等站点性能审计 |
| `/content-audit` | 内容日更对抗式审核 | stock-daily-report / newsnow-publisher 当天 output 稿件对照 research 核事实，出 P0-P3 + 评级 |
| `/xiaohongshu` | 小红书账号自动化风控规范 | 做小红书发帖/评论/私信/关注/投流的自动化或批量脚本、设计账号状态机、排查封号限流——频控基线表/风控状态机/合规红线/拟人化调度。**只管账号操作风控**，抓取走 routing.md，文案走 content-profiles.md |
| `/diagnose` | 硬 bug / 性能回归的纪律化调试循环（Phase 1 = 先建可跑反馈环） | 用户说 "diagnose" / 报了 bug / 性能回归；与 `/cross-review debug` 互补（diagnose = 系统方法论，cross-review = 跨模型外部视角） |
| `/apple-design` | Apple WWDC 交互物理原则（Emil Kowalski，17 条） | 做手势驱动 UI / spring 动效 / drag·swipe·sheet·可中断过渡 / 材质分层时触发。与 design-system 正交：那个管反 AI 审美与验收，本 skill 管动效物理对不对。**动效四件套分工**：apple-design 管原则、gsap-* 管库实现、improve/review-animations 管审计与 review、design-lint.sh 管确定性反模式。**冲突以 design-system 为准**：tracking 条款 / display 字体 vs 系统字体 / B2B 禁毛玻璃——产品 UI 场景才让 apple-design 赢。简单 CSS transition 不触发 |
| `/improve-animations` `/review-animations` | 动效专项审计 / diff 级动效 review | improve = 全库动效审计出优先级清单 + 自包含实现计划（只读不改码，计划交便宜模型执行）；review = 单 diff 动效 review（default to flagging；上游 `disable-model-invocation` 已本地摘除并 frozen，模型可自动触发）。触发：动效 diff/组件 review、动效重的交付前检查，或用户说「audit the motion / 改进动效 / review 这段动效」——两个都靠 description 自动触发，不需点名。非动效代码 review 走 `/cross-review code`；同仓 emil-design-eng / animation-vocabulary 已评估不装（与 design-system 重叠 + 课程导流） |

> **`/diagram` vs `/baoyu-infographic` 边界**：前者做"工程图"（SVG DOM 精确渲染，可编辑、可 diff、文字不乱码），后者做"海报图"（AI 生图，视觉感强但整张位图、改只能重出）。数据/结构要准走 diagram，视觉/传播要酷走 infographic。

> **AI 生图三选一决策门（每次"画张图"先过）**：中文文字/生产管线 → seedream（`/baoyu-infographic`）；临时配图无中文文字 → 免费 codex-imagen（默认省钱档）；结构图 → `/diagram`。完整三档逻辑 + auto-trigger 改道见 `references/image-base.md`。

> **`/web-perf` 增量场景**：主 skill 五 Phase 覆盖 CWV/trace/网络/a11y/codebase；遇到①部署前完整质量门（Lighthouse 一次出 a11y/SEO/best-practices）②跨视口响应式 / Slow 3G + CPU throttle 模拟③登录态后台 perf 调优（auto-connect 接管已登录 Chrome）④SPA 内存泄漏（heap snapshot），先读 `references/web-perf-extras.md` 取对应节方法（DevTools for Agents 1.0 新增四块，按需加载）。auto-connect 走前先看 §3 安全边界——agent 接管时拥有 profile 全部数据。

## Auto-trigger only（无法 `/xxx`，靠文件路径自动加载）

frontmatter 带 `paths:` 的 skill，**不能当 slash command 用**；能否被 Skill 工具按名调，取决于是否已被路径触发加载：编辑或 `Read` 任一匹配 `paths` 的文件即触发加载，加载后 `Skill(name)` 可按名调用；未触发时不在列表、按名调直接报 `Unknown skill`。**最轻用法**：想用其知识但 cwd 没碰相关文件时，直接 `Read` 对应 `SKILL.md`——Read 本身即触发加载。

| Skill | 自动加载条件 | 语义提示 |
|-------|-----------|---------|
| seo | `**/*.html`, `**/*.astro`, `**/sitemap.*`, `**/next.config.*` 等 | SEO 统一入口（内部路由 seo-* 子 skill） |
| convergent-execution | `**/task_plan.md`, `**/PLAN.md` | 收敛执行（有 task_plan 时自动） |
| design-system | `**/*.css`, `**/*.tsx`, `**/DESIGN.md` 等 | 前端设计规范 |
| yfinance-data | `**/*.py`, `**/*.ipynb` | 股票/财报数据 |
| stock-daily | `**/stock-daily-report/**`, `**/generate.py` | 美股小报管线 |
| stock-correlation | `**/*.py`, `**/*.ipynb` | 股票相关性分析 |
| options-payoff | `**/*.py`, `**/*.ipynb` | 期权收益曲线 |
| frontend-slides | `**/slides/**`, `**/deck(s)/**`, `**/presentation(s)/**`, `**/*.slides.{astro,html}`, `**/*.pptx`, `**/*.ppt` | 演示稿源文件（Astro/HTML/PPT），不触通用站点 |
| workers-best-practices | Worker 代码文件 | CF Worker 代码 auto-load，context 成本低 |
| wxapp | `**/*.wxml`, `**/*.wxss`, `**/*.wxs`, `**/project.config.json` | 原生微信小程序开发规范（生命周期/setData/列表分页四态） |

想当 slash command 用 → 要么删掉 `paths:`（丢失 auto-trigger），要么在 `~/.claude/commands/` 建同名 wrapper（叠加入口，不改 SKILL.md）。

## Cloudflare 套件（cloudflare/skills 官方）

已安装并结清（2026-05-17），整包 8 skills + 5 MCP，skill 已并入上方 Specialist / Auto-trigger 表。安装命令、踩坑、重装路径见 `~/.claude/references/skill-install-history.md`（重装必须在新会话开始前做——MCP schema 变更炸缓存）。下表是"主用 / 无视"分类，不是安装开关——不想用的 skill 挂着不触发即可；不想要的 MCP 需显式禁用。

| 组件 | 类型 | 用法 |
|------|------|------|
| `cloudflare` `wrangler` `web-perf` | skill | 主用（已入 Specialist 表） |
| `workers-best-practices` | skill | 主用（已入 Auto-trigger 表） |
| `cloudflare-docs` MCP | MCP | 主用——CF 文档查询，比 WebFetch 干净有索引（routing.md 已加规则） |
| `cloudflare-observability` MCP | MCP | 主用——调 Pages/Workers 日志比 dashboard 快 |
| `cloudflare-bindings` MCP | MCP | 主用——写 wrangler.toml bindings 自动补全 |
| `cloudflare-builds` MCP | MCP | 按需——build 状态查询 |
| `cloudflare-api` MCP | MCP | 🔴 **默认禁用**（已于 2026-05-17 在 `/mcp` 里 disconnect）。真实写账户资源（DNS / Pages / Workers / R2 含 aloud-releases / zone 设置），全不可逆，归 `rules/hard-gates.md`。常态保持禁用；仅当有明确批量写需求（如批量改 DNS）时临时 `/mcp` 授权，用完立即 disconnect。授权前必须确认 token scope + 能否碰生产 zone |
| 其余 skill（agents-sdk / durable-objects / sandbox-sdk / cloudflare-email-service 等） | skill | 无视——无需求，不主动触发即可 |

**当前状态**：`cloudflare-docs` connected 常用；`cloudflare-api` 默认禁用（见上表 🔴 行）；`cloudflare-bindings`/`builds`/`observability` 保持 needs-auth，用到再临时授权。skill 仅由插件缓存单一提供（单一源原则见「Skill 拓扑契约」）。归档史、误诊更正、账单参考见 `references/skill-install-history.md` §Cloudflare。

## example-skills 套件（anthropic/skills 官方）

已彻底卸载（2026-05-28）：17 skill 中仅 `pdf` `docx` `xlsx` `pptx` 有真实价值，已复制为自有 skill（slash + 自动触发不变，接入 routing.md 文件处理表），其余噪音/重叠随插件禁用。逐条去向、卸载细节、重装路径见 `references/skill-install-history.md` §example-skills。

**frontend-design 别再装**：t14 AB 吸收否决（并入 design-system 总分平手，按「无提升则回滚」不吸收），双注册还抢触发。详见 `references/skill-install-history.md` §frontend-design。

## GSAP 动效套件（greensock/gsap-skills 官方）

2026-06-23 装（官方插件，scope:user）。补的缺口 = design-system 不覆盖的复杂 web 动效（timeline 编排 / ScrollTrigger 滚动驱动 / SVG·物理）。非 slash 非 `paths:`——8 个 skill 由 Skill 工具按名调用。**触发**：做带动效的落地页 / 滚动叙事 / 复杂交互时先 `Skill(gsap-core)`。**边界**：结构图→`/diagram`，设计 token→design-system，简单 CSS transition 不上 GSAP——只有真需要时间轴/滚动/缓动物理才用。

同批否决（防重复评估）：**Lottie 不装**（无需求）、**Three.js 3D 地图 REJECT**（GPL-3.0 copyleft 污染客户交付）。安装审查与否决细节见 `references/skill-install-history.md` §GSAP。

## Inventory（按需调用，不主动推荐）

低频工具（可 `/xxx`）：`/playbook-learner` `/new-project` `/env-sweep` `/self-improving-agent` `/freeze` `/skill-vetter` `/markdown-proxy` `/baoyu-imagine`（AI 生图执行端，被 `/baoyu-infographic` 的 Step 6 调用；首次用需配 `~/.baoyu-skills/baoyu-imagine/EXTEND.md` 指定 provider + API key）

mattpocock/skills（低频）。**保留**：`/prototype`（设计验证原型） `/zoom-out`（陌生代码模块地图） `/grill-with-docs`（对照 CONTEXT.md/ADR 压测方案） `/improve-codebase-architecture`（代码库体检） `/design-an-interface`（并行接口设计） `/review`（双轴 review：repo 标准 × 原始 spec，与 `/cross-review` 互补） `/git-guardrails-claude-code` `/setup-pre-commit` `/write-a-skill` `/tdd`（Matt 版，与 rules/coding.md TDD 规则互补）。

**冻结旧版**（lock `frozen: true`，上游重同步不覆盖）：`caveman` `zoom-out` `grill-me` `grill-with-docs` `improve-codebase-architecture` `write-a-skill`；`handoff` 本地中文重写版（`localFork: true`）永不覆盖。重同步史、冻结理由、已解软链清单（11 个，`ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>` 即复活）、回滚快照见 `references/skill-install-history.md` §mattpocock。

已归档（移出 `skills/` 发现范围，存 `~/.claude/archive/skills/`）：`competitor-scan`（→`/biz analyze` 内部 reference）

SEO 子 skill（已迁入 `seo/subskills/`，不再独立注册）：seo-audit, seo-page, seo-technical, seo-content, seo-schema, seo-sitemap, seo-geo, seo-hreflang, seo-images, seo-plan, seo-programmatic, seo-competitor-pages

## Skill 拓扑契约（单一源 + 健康检查）

三方 agent（Claude / Codex）共用一套 skill 本体，靠软链不靠拷贝。核心一句：**任何 skill 本体只存一份，其余位置一律软链指过去；插件 skill 只由插件缓存提供，绝不在 `~/.claude/skills/` 留 realdir 副本**。

- **共享池 = `~/.agents/skills/`**：第三方 skill 本体 + `skills-lock.json`（记 upstream github 源 + hash）。Claude 逐 skill 软链引用，Codex 启动直接扫，更新跟 git pull 走。
- **自有 skill = `~/.claude/skills/` 的 realdir**：授权地就在这，无 upstream，realdir 合法。
- **插件 skill = `~/.claude/plugins/cache/`**：影子 realdir 是 bug（cloudflare 套件犯过两轮，归档史见 install-history）。
- **codex 约束**：Codex 扫 `~/.agents/skills` + `~/.codex/skills`，SKILL.md `description` >1024 字符会启动报错（Claude 侧无此限）。

**健康检查（只读，不改文件）**：`bash ~/.claude/scripts/skill-topology-health.sh`——检测悬空软链 / 共享池影子 dup / 插件影子 dup / codex desc 超限，exit 0 干净 / exit 2 有漂移。完整拓扑见脚本头注释（单一源）。**何时跑**：装/删第三方 skill 或插件后（接 `hard-gates.md` 安装闸末尾），以及怀疑 skill 重复触发/找不到时。

## 装着未路由（候选清理 / 休眠）

第三方 skill（symlink → `~/.agents/skills/`），出现在 `ls ~/.claude/skills/` 里但**本表的 Daily Core / Specialist / Auto-trigger / Inventory 都未引用，且 rules/ 各文件零提及**。装着没用过 ≠ 该删，但要看得见。

已清理批次（源/归档未删，`ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>` 或从 archive 移回即复活）：lark-* 飞书全家桶 25 个、HyperFrames+动画库 13 个（均 2026-05-26）、planning-with-files 多语言变体 5 skill + 4 command（2026-06-26，归档 `~/.claude/archive/plugin-skills/planning-with-files-multilang-2026-06-26/`，插件升级可能重建变体，重扫即再现）。

判定"装着未路由"的两个**结构信号**（任一）：
1. `grep -r "skill-name" ~/.claude/rules/ ~/.claude/commands/` 零命中
2. memory（`~/.claude/projects/*/memory/`）零相关使用记录

补一条**行为信号**（结构信号管"有没有被引用"，行为信号管"有没有被真触发"，两者交叉才决断）：`bash ~/.claude/scripts/skill-usage-audit.sh`——扫所有 JSONL transcript 统计每个已装 skill 的真实触发频率（Skill 工具调用 + `<command-name>` 标签）+ 最后使用日期，并自动与路由信号交叉分桶：**PURGE**（0 触发 AND 未路由 = 强删除候选）/ **SITUATIONAL**（0 触发但被引用 = 情境性低频，留）/ **STALE**（触发过但 >60 天没用）/ **ACTIVE** / **auto-trigger 测不准**（走路径注入、本方法系统性低估，不据此删）。只读、只产事实，清理动作人工拍板。**何时跑**：定期清理或怀疑 skill 膨胀时；与 `skill-topology-health.sh`（管拓扑健康）正交。**坑**：套件类（gsap/omm/planning-*）常整体引用、子技能名不单独出现，会误入 PURGE——删套件成员前先确认套件本身去留，多语言变体（-ar/-de/…）才是稳 dupe。

清理工具：`unlink ~/.claude/skills/<name>`（只解 symlink，不删 `~/.agents/skills/` 源）。批量解前先确认未在 `~/.claude/CLAUDE.md` 或 `rules/` 任何位置被引用。

## 路由关系

商务→`/biz` | Obsidian→`/obsidian` | 联网→`routing.md` | SEO→auto-load（编辑/Read 匹配文件即触发，加载后亦可 Skill 按名调）| 设计→auto-load（编辑/Read CSS/组件即触发）；widget 输出用 `/generative-ui`
