---
description: Skill 协作约束——原则和触发条件。具体流程步骤见 /chain 和 /plan 命令。
---

# Skill 协作约束

## 按需加载资源
- 写新 skill 或改 skill 规则时，先读 `~/.claude/references/skill-design-patterns.md`
- **自有 skill 执行失败并定位根因后**：回写一条到该 skill 的 `## Gotchas` 段（格式/进 skill vs 留 rules 的判据见 skill-design-patterns.md 模式 11）。专属坑直接写，领域坑用指针引权威 rules，第三方/vendor 包不碰其 SKILL.md
- 系统性想减少长命令输出对 context 的浪费、单次 tool_result > P95（约 6K 字符）、写新 hook/包装命令时，先读 `~/.claude/references/llm-context-filtering-strategies.md`（12 类过滤策略判断手册，借自 rtk-ai/rtk）

## 原则
- 上游输出 = 下游输入，不让用户手动搬运
- 闭环：做完 → 审 → 改 → 再审
- 每步完成后提示下一步（不自动执行）
- **单一源真理（Single Source of Truth）**：同一条规则/阈值/触发条件只在一处写权威版本，其他文件只放指针（"详见 X"）。新规则进来时先 grep 现有 rules/ 和 references/，命中已有概念 → 在已有文件扩展，不另起新段。判定"是否权威所在地"按一条标准：**谁负责该领域的边界判断**（如代码 DoD 在 coding-dod.md，审核框架在 review-base.md，过滤策略在 llm-context-filtering-strategies.md）。同一规则在 2+ 文件出现 = drift 起点，下次维护必有一处过时

## 职责分离（Command / Agent / Skill）
- **Command**（`~/.claude/commands/`）：用户入口 + 工作流编排，按需加载
- **Agent**（`~/.claude/agents/`）：独立 context 执行者，预加载 skills 作为领域知识
- **Skill**（`~/.claude/skills/`）：可复用知识单元，可被 Command 调用或 Agent 预加载
- 编排流程放 Command（`/plan`、`/chain`），约束和触发条件放 Rules（本文件）

## 触发条件速查

| 信号 | 触发 |
|------|------|
| 新客户/新行业 | `/biz analyze` |
| 接交付型客户项目（为客户交付/收款/有验收） | `references/delivery-sop.md`（Gate0 起逐闸；与 `/biz` 不互斥，叠加 Gate0 检查；指针段已并入 CLAUDE.md「按需加载方法库」） |
| 接微信小程序云开发项目（原生 WXML/WXSS/JS + 云开发） | `references/wechat-miniapp-cloud-sop.md`（六闸的技术栈落地层：dev/test/release 专属坑 + 9 条跨项目经验，叠加 delivery-sop 用；项目内落地见 `<project>/DELIVERY.md`）；**代码层规范（生命周期/setData/分页四态/本地测试）**走 `wxapp` skill（编辑 `.wxml`/`.wxss` 自动加载） |
| 写文章/内容完成 | `/write-review`（评分制为 X/10：≥8 通过，<8 改后再审，最多 2 轮） |
| 3+ 文件的工程任务 | `/plan`（RBPI 流程） |
| 新功能/需求模糊/跨 3+ 模块（Plan 前） | `brainstormer` agent → `options.md`，⏸ 用户选方向后再 Plan |
| 跨模块架构/新技术/schema 变更 | plan 后先 `/cross-review design` |
| 第 2 次修复失败 | `/cross-review debug` |
| 联网/数据获取 | `rules/routing.md` 四层路由 |
| 可视化需求 | `/diagram` 自动选型 |
| 封面 / KV / 海报 / 一页纸 | 按意图选（裸请求先认意图，认不出就问一句，别硬挑）：① **AI生图成品**（X文章封面/小红书封面/海报/KV——裸"做张封面/海报"默认归此）→ `/cover-styles`（8 风格原子库，META/STYLE 编译，2026-07-08 起替代 memory 6套框架）；高密度信息图整图仍走 `/baoyu-infographic`；② **HTML排版**（研报/白皮书/一页纸/正式可打印文档）→ `/paper-layout`；③ **设计约束**（仅当明说"给开发参数规范/在代码里实现"才走）→ `design-system §海报封面`。既要成品图又要实现参数 = ①+③ 组合路由。AI 生图三档决策门（seedream/codex-imagen/diagram 分流）权威版在 `references/image-base.md`，本行只管封面/海报意图识别，不复制决策表 |
| 给一篇长文配一组正文插图 / 让固定的个人形象在配图里出镜 | 先分清是**一组**还是**一张**：一组正文插图 → `/article-illustration`（按信息密度定图数，不按章节平均分）；单张封面海报 → `/cover-styles`；高密度信息图整图 → `/baoyu-infographic`。要人物长期一致先用 `/persona-ip` 建角色包，只建一次，之后复用。三者解耦：画风在 `cover-styles/styles/` 原子库（单一源），人物在 `~/.claude/personas/`，输出形状各归各的 skill |
| 拿一张照片来要「做成」点什么（手绘化/艺术化/海报化，非修图），或点名 zine/CRT/喜茶风 | 照片驱动生图档：`photo-revival` / `photo-abstract-editorial` / `heytea-style`；点名风格 → `gc-minimal-zine-poster` / `tait-crt-interface-skill`。分流权威版 + 版权边界在 `references/image-base.md`「路由首选·照片驱动档」，本行只管意图识别；裸"做张海报/封面"仍走 `/cover-styles`（上两行规则不变） |
| UI mockup/设计稿/interactive prototype | 前期出 PNG 静态视觉稿，HTML 仅演示场景（详见下节） |
| 含 HTML 页面的项目，用户说「上线前/交付前/部署前/准备好了/web 检查/quality check」 | `/web-quality`（跳过 print-only 页；file:// 跳过 Lighthouse，部署后补跑）|
| 减少长命令输出 / tool_result > P95 / 写新 hook | `references/llm-context-filtering-strategies.md` 挑策略 |
| 评估第三方 repo/skill（质量判断 / 要不要用） | repo 质量走 `/github-quality`；**拉取前先过 `references/llm-context-filtering-strategies.md` 截断**——别 `gh api …recursive=1` / `cat` 整个 transcript 全量灌 context（实测单条 dump 达 33K token）。要结构用 `gh api … \| jq` 只取键，要正文 `\| head -c` 截断 |
| 想看自己 session 哪些命令在浪费 token | `~/.claude/scripts/session-stats.sh` |
| 想看自己 session 哪些命令反复失败 | `~/.claude/scripts/session-fail-pairs.sh` |
| 想看哪些 skill/命令总连着用、挖组合工作流候选 | `~/.claude/scripts/session-cooccur.sh`（共现对+lift+先后序→提案清单，人工拍板后才建 command/路由行，不自动写配置；借自 opensquilla meta-skill-creator 的 auto-propose）。月度自动跑：launchd `com.edon.claude-session-cooccur`（每月 1 号，提案追加 `~/.claude/proposals/cooccur-proposals.md` + 弹通知）；拍板时连续两个月度窗口复现的 pair 才动手 |
| 发现 skill/路由 misroute（用户纠正「不该用这个/该走 X」，或自察触发错了、该触发没触发） | 纠正完当下顺手记一条：`python3 ~/.claude/scripts/misroute-log.py log --type overtrigger\|undertrigger\|wrong_pick --expected <对的> --actual <错的> --source user\|self --note "<一句话现场>"`——生产 misroute 唯一留痕点，不记就永久丢失。消费口：月度整理跑 `misroute-log.py stats`，`fix_candidates`（同 pair ≥2 次）= 该 skill description 修复候选，走 skill-design-patterns.md 模式 13（eval query + near-miss 负例）修，修完在 note 里标已消费；同次顺手把当月 misroute + session-fail-pairs 记录按**失败机制**手工归组（同表象可能不同根因），同机制 ≥2 条才算 pattern、才动 rules，单月记录 >15 条再考虑给脚本加机制字段——现在样本量撑不起自动聚类，不先建管线。 |
| 会话结束/阶段切换 | `/handoff` + wiki 蒸馏检查 |
| 用户改稿 | 提示 `/playbook-learner` |
| 响应太冗长 / token 太多 / 简洁点 / "caveman" | `/caveman`（持续有效直到 "stop caveman"） |
| 压力测试方案 / 想清楚再动手 / "grill me" | `/grill-me`（逐题 Socratic 问答，比批量假设前置更适合复杂设计探索） |
| 用户说 "diagnose" / 报 bug / 性能回归 / 第 2 次以上修复失败 | `/diagnose`（Phase 1 先建可跑反馈环）或 `/cross-review debug`（跨模型外部视角）；两者互补可叠用 |
| 审整个后端/代码库安全（有鉴权/API，白盒有源码，要报告）/ 客户后端交付前 / 自有后端上公网前 | `/security-audit <项目>`（全库 SAST 分组并行出 P0-P3，何时用/不用见 `references/security-audit-sast.md`；客户项目并入 delivery-sop Gate 2 sign-off） |

## UI 前期视觉稿优先，HTML 仅演示场景

做 UI mockup / 设计稿分两拍（HTML 只留给演示，不是所有阶段的默认交付物）：

1. **前期探索/定方向 → 静态视觉稿（PNG）**：内部仍用 HTML 排版（inline CSS），headless Chrome 渲染截图，**交付物是 PNG 图**；多方案时并排出 2-3 张对比。用户看图给反馈定方向，改稿只改 HTML 重截，不把半成品 HTML 文件当交付物丢给用户
2. **演示场景 → 交互 HTML 单文件**：需要点着看交互、parametric 调参（sliders+knobs 参数闭环）、spec 文档带可视化、给客户/同事发可直接打开的预览时，才交付 HTML 文件
3. **方向确认后 → 组件代码**：会被持续迭代的进项目框架组件化（见下方不适用第 1 条，分界不变）

两拍都不出"描述设计的 markdown"——文字描述设计稿对方读完仍想象不出来。

**不适用**（仍走原工具）：
- 真实组件代码 / 会被反复迭代的设计稿 / 数据驱动动态变更 UI 的交互稿 → 项目框架（React/Vue/Astro）组件化，不是 HTML 单文件。**分界不只是「throwaway 预览 vs 真实代码」，还有「改一次的上下文代价」**：巨型 HTML 改一个按钮要整文件塞进 context，组件树只加载要改的那块——会被 coding agent 持续改的（即使简单）早组件化，一次性预览（即使复杂）用 HTML——数据绑定交互、复杂 UI 拆分、设计↔代码可映射这三种场景 HTML 单文件都吃亏
- 结构化工程图（流程/架构/ER/时序/甘特等）→ `/diagram`（SVG 确定性渲染）
- 数据/统计图表 → `/diagram`（精确）或 `/baoyu-infographic`（视觉强）
- 设计 tokens / CSS variables → 项目 design system，不是临时 HTML
- 引擎食粮（`task_plan.md` / `HANDOFF.md` / `MEMORY.md` / `rules/`）→ 保持 markdown（要 grep/diff/AI 全文读）

## 共享方法层（内容项目）

内容项目共性方法在 `~/.claude/references/`，项目 CLAUDE.md 引用而非复制：

| 共享文件 | 覆盖 | 位置 |
|----------|------|------|
| `references/review-base.md` | P0-P3 审核框架、禁词、输出格式 | references/ |
| `references/publish-base.md` | 生成→审核→发布→记账→验证闭环 | references/ |
| `references/image-base.md` | AI 图片生成规范、文字防护、比例检查 | references/ |
| `rules/coding-dod.md` | 代码项目 DoD 模板 | rules/（正文） |
| `references/delivery-sop.md` | 交付型客户项目六闸标准（签约前→移交收口） | references/ |
| `references/content-profiles.md` | 平台写作参数（x-shortform/market-longform/blog-en/vlog-short） | references/ |
| `references/two-step-pattern.md` | 分析→生成两步处理模式（Wiki / `/biz analyze` / 写作）| references/ |
| `rules/writing.md` | 写作基础规则 | rules/（正文）|
| `rules/routing.md` | 抓取/联网路由 | rules/（正文）|

项目 CLAUDE.md 只写：项目身份 + 本地约束 + 入口命令 + 指向共享方法的引用。

## 跨链路规则

| 场景 | 路由 |
|------|------|
| 分析中需联网 | routing.md |
| 写作需数据 | routing.md（金融优先 yfinance） |
| 项目交付需内容 | 工程链 → 内容链 |
| 任何链路需可视化 | 插入 `/diagram` |
| 任意链路有新认知 | wiki 蒸馏（rules/wiki-lifecycle.md） |

## 子代理选择

派子代理时，优先用 `~/.claude/agents/` 中的预定义 agent：
- `researcher` — 搜索+提取事实，预加载 markdown-proxy skill
- `brainstormer` — 方案发散，输出 ≥3 方向 + wildcard，⏸ 等用户选定后再 Plan（Opus）
- `code-reviewer` — 独立代码审查，预加载 cross-review skill
- `frontend-builder` — UI 实现，预加载 design-system + diagram skill
- `grok-implementer` — 跨厂商「会写代码」实现 lane，driver=Grok 4.5（grok CLI，acceptEdits 真写文件）。例行、spec 已完全确定的实现活路由到这里，要非 Anthropic 家族低成本敲码时用；区别于 Codex R/E lane（只读审查/分析）。model=sonnet 监工 + 独立复核。网络前提见 agent 内「网络前提」节（grok wrapper 走住宅代理，节点细节以 agent 为准）
- 无匹配时 fork（省 context，继承缓存）
