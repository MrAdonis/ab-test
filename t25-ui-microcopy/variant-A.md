---
name: design-system
description: 设计美学准则——反 AI 审美、量化维度、设计原则、执行标准、组件规范。做前端设计/UI/落地页/组件时触发。
version: "1.0.0"
metadata:
  pattern: reference
paths: ["**/*.css", "**/*.scss", "**/*.tsx", "**/*.jsx", "**/*.vue", "**/*.svelte", "**/*.astro", "**/DESIGN.md", "**/tailwind.config.*"]
---

# 设计美学准则

## 项目 DESIGN.md 集成

做前端设计、UI、落地页、组件、仪表盘、图表、营销页时，先检查当前项目根目录是否存在 `./DESIGN.md`。

如果存在：
- 先读 `./DESIGN.md`，再开始方案和代码
- `./DESIGN.md` 是项目级设计事实来源，优先用于颜色、字体、间距、组件模式、品牌语气、视觉约束
- 本 skill 负责补充反 AI 审美、质量门槛、排版判断、动效克制、可用性与一致性
- 如果本 skill 与 `./DESIGN.md` 冲突，`./DESIGN.md` 优先；增量改动时，已存在代码实现优先于抽象规则
- 如果 `./DESIGN.md` 很长，先读目录和 Quick Rules，只加载与当前任务相关的章节

优先级：当前代码库已存在的实现 > `./DESIGN.md` > 本 skill > 模型默认审美

未找到 `./DESIGN.md` 时，按本 skill 执行。

## 开工前的 Design Read（一句话强制声明）

**适用范围**：新设计 / 重设计 / 完整 landing / portfolio / 多 section 营销页任务。token 级修改（颜色 / padding / 字号微调）、bug 修复、纯文案调整、单组件小改不触发本规则。

任何在适用范围内的前端任务开工前，**必须**先在响应里写一句"Design Read"，结构固定：

> Reading this as: **<页面类型>** for **<目标读者>**, with a **<vibe 关键词>** language, leaning toward **<设计系统或美学家族>**。

四个槽位都不能省：

- **页面类型**：landing（SaaS / 消费 / agency / 活动）、portfolio（开发者 / 设计师 / 工作室）、editorial / blog、redesign（preserve / overhaul）、product UI、教学/文档站
- **目标读者**：技术 buyer / 设计敏感的 C 端 / 招聘官扫 portfolio / 散户教学等具体身份，不写"用户"这种空词
- **vibe 关键词**：minimalist / Linear-style / Awwwards / premium consumer / 粗野主义 / 编辑风 / 玻璃质感 / dark tech 等
- **设计系统或美学家族**：shadcn/ui + Tailwind / Radix Themes / GOV.UK Frontend / 原生 CSS + 编辑型字体 / Bootstrap 等

示例：

> Reading this as: 散户期权教学 landing for 中文非专业投资者, with a 编辑型 + 数据可信 language, leaning toward 原生 CSS + 衬线副标 + 等宽数字。

> Reading this as: 美股小报订阅页 for 已订阅老用户回访, with a Linear-style 克制 language, leaning toward Tailwind + Geist + 单色调。

**brief 模糊时**：只问一个澄清问题，不发问题清单。能从 vault / 项目 DESIGN.md / 上下文推断的不问。

**目的**：强制模型先做语境分类再选规则，避免直接跳到默认审美（AI 紫 / Inter / 三列卡片）。这套负向约束对抗的是 distributional convergence——无约束时模型采样会塌向训练数据的概率中心（Inter/紫渐变/三栏卡片是高频项），强约束把它从"安全中心"推到"风格边缘"。Design Read 写完，下一步直接走"量化维度"确定 dial。

## 量化维度（开工前必须确定）

每个项目开工前，根据场景确定三个维度的值，用这组值驱动后续所有设计决策：

| 维度 | 范围 | 说明 |
|------|------|------|
| **VARIANCE** | 1-10 | 布局破格程度。1=严格对称网格，5=有节奏的不对称，10=实验性构图 |
| **MOTION** | 1-10 | 动效强度。1=纯静态，5=CSS 过渡+入场动画，10=滚动编排+物理弹簧 |
| **DENSITY** | 1-10 | 信息密度。1=画廊级留白，5=标准 web app，10=数据驾驶舱 |

**默认基线 (5, 4, 5)**——多数 web 项目适用。根据场景类型选行，按"规则节"列跳到对应规则：

| 场景 | 信号关键词 | VARIANCE | MOTION | DENSITY | 规则节 |
|------|---------|----------|--------|---------|-------|
| 品牌 / 营销落地页 | "landing""营销页""官网" | 7-9 | 6-8 | 2-4 | §布局硬规则 + §反AI审美 |
| 作品集 / 个人品牌 | "portfolio""个人站""品牌站" | 8-10 | 7-9 | 2-4 | §布局硬规则 + §设计原则 |
| SaaS 产品 UI | "产品""工具""SaaS app" | 3-5 | 3-5 | 6-8 | §组件状态 + §技术护栏 |
| B2B 工具 / 后台 | "后台""管理""ERP""admin""表格" | 2-3 | 1-2 | 8-10 | §B2B工具规范 |
| 数据面板 / 监控 | "数据""chart""指标""看板" | 2-3 | 2-3 | 8-10 | §B2B工具规范（DENSITY≥8）|
| 电商 / Shopify | "电商""Shopify""商品页""产品卡" | 6-7 | 4-5 | 4-6 | 项目 DESIGN.md + §组件状态 |
| 海报 / 封面 / KV | "海报""封面""小红书封面""KV" | 6 | 0 | 3 | §海报封面（拨盘固定值）|
| 内容 / 编辑站 | "博客""editorial""阅读为主" | 5-6 | 3-4 | 3-4 | §设计原则（typography 优先）|

**Vibe word → dial 映射**（用户用关键词描述风格时直接查）：

| vibe 关键词 | VARIANCE | MOTION | DENSITY | 说明 |
|----------|----------|--------|---------|------|
| minimalist / clean / calm / 极简 / Linear-style | 5-6 | 3-4 | 2-3 | 中规中矩破格 + 弱动效 + 大留白 |
| premium consumer / Apple-y / luxury / 高端 / 质感 | 7-8 | 5-7 | 3-4 | 显著破格 + 中度动效 + 中等密度 |
| Awwwards / Dribbble / playful / 实验 / 粗野主义 | 9-10 | 8-10 | 3-4 | 满级破格 + 满级动效 + 中等密度 |
| editorial / 编辑风 / 排版优先 / 杂志感 | 6 | 4 | 3 | 不对称但克制 + 弱动效 + 大留白 |
| trust-first / 公共服务 / 合规 / 政务 | 3-4 | 2-3 | 4-5 | 严格对称 + 几乎无动效 + 标准密度 |
| dark tech / hacker / 极客 | 6-7 | 5-6 | 5-6 | 中度破格 + 中度动效 + 中等密度 |
| 教学 / 文档 / 内容优先 | 4-5 | 3-4 | 4-5 | 标准布局 + 内容为主 + 适度密度 |

两个表的关系：
- 用户给项目类型时（"做一个 SaaS landing"）→ 查项目类型表
- 用户给 vibe word 时（"想要 Linear 那种感觉"）→ 查 vibe 表
- 两者都没给时 → 默认基线 (5, 4, 5)，并主动问一次 vibe 关键词
- 两者冲突时（"SaaS landing 但想要 Awwwards 感"）→ 取 vibe 表的值（vibe 比项目类型更具体、更强表达意图）

维度值影响具体规则：
- VARIANCE ≥ 6 时，**禁止居中 hero**，必须用不对称/分屏/错位布局
- MOTION ≥ 6 时，**至少 3 个有意图的动效**：一个入场序列、一个滚动联动、一个交互反馈
- DENSITY ≥ 8 时，**禁止卡片容器**，用 border-t / divide-y / 纯间距分组；数字用等宽字体

## 反 AI 审美

**禁止清单（AI Tells）**：
- 字体：Inter / Roboto / Arial / 系统默认 sans-serif 一把梭 / Fraunces（被 AI 滥用的 display 字体，2024 年后慎用）
- 配色：紫色渐变白底（「AI 紫」）、纯黑 #000000（用 Zinc-950 或 Charcoal 替代）、过饱和强调色（饱和度 < 80%）
- 布局：对称居中万能布局、三列等宽卡片网格、圆角卡片堆叠、圆角卡片 + 左边框 accent color（典型 dashboard AI slop）
- 装饰：标题下方装饰线、emoji 作为图标、neon 外发光 box-shadow、用 SVG 画 logo / 插画 / 复杂图标（用 placeholder，让用户提供真素材）
- 内容：「Jane Doe」占位名、99.99% 假数据、Acme/Nexus 假品牌名、「Elevate」「Seamless」「Unleash」营销套话
- 一致性：每个输出都长一个样——不同项目必须有不同的美学方向

**Production Tell（具体到文案/装饰的禁用清单，来自真实 AI 测试观察）**：

**适用范围**：landing / marketing / portfolio / 内容站。dashboard / 后台 UI / 数据面板 / 工具型应用不受此清单约束（dashboard 反而欢迎真实状态 dot、紧凑数据展示、status pill）。

- **section numbering eyebrow**：`00 / INDEX`、`001 · Capabilities`、`06 · how it works`、`Stage 1 / Stage 2 / Stage 3` 类编号——禁用。section 用主题名（"how it works"）就够，不需要编号
- **装饰文字条**：hero 底部 `BRAND. MOTION. SPATIAL.` / `DESIGN · BUILD · SHIP` / `ESTD. 2018 · LISBON` 之类的小号大写散字符串——禁用。除非是真实导航条/cookie 横幅/真实状态信息
- **scroll cue**：`Scroll`、`↓ scroll`、`Scroll to explore` + 动画鼠标轮 icon——禁用。用户看到 hero 就知道往下滑，hero 底部不需要标签
- **诗化社会证明标签**：`Quietly trusted by` / `Field notes` / `From the field` / `On our desks` / `Currently on the bench`——禁用。用 `Trusted by` / `Customers include` / `Latest writing` / `Now working on` 这种功能化标签
- **floating 角落小字**：section 大标题左对齐，标题右上角飘一段小字解释——禁用。要么放标题正下方，要么做 2 列正交布局，不要"飘着"
- **`border-t` + `border-b` 双边框 spec 表**：长 spec 表每行都画上下分隔线——禁用。换成 2 列卡片 / scroll-snap pills / 分组 chunks
- **micro-meta 小字段落**：eyebrow 下面再加一句小字"each of these is..."——禁用。eyebrow + 标题 + 正文就够，多一行就是 AI 在凑细节
- **fake live counter**：`Reservation 412 of 800` / `last sync 4s ago` 这种装饰性"实时感"数据——禁用，除非是真实库存/真实时间戳
- **photo-credit 装饰**：`Field study no. 12 · Ines Caetano` / `Plate 03 · House archive` 在 picsum/stock 图下面——禁用。真实有摄影师才标
- **version footer**：marketing 页脚 `v1.4.2 · build 0048`——禁用。这是 devtool/CLI 装饰，不是 landing 内容

## 设计原则

**must**（不可违背）：
- 先确定美学方向再动手——用 3 个关键词概括（如「粗野、单色、高对比」），并确定量化维度值
- 色彩有主次：一个主色 60-70%，1-2 个辅助色，一个强调色（≤10%）。每种颜色标明精确占比和使用场景。全项目同一色温，不在冷暖灰之间摇摆
- 字体有性格：标题用 display 字体（Geist / Outfit / Cabinet Grotesk / Satoshi 等有辨识度的），正文用高可读性字体，二者反差明显。数据面板禁用 serif
- 设计决策要有排除逻辑：不只说「选了 X」，要说「没选 Y 因为 Z」
- **感觉空 ≠ 填内容**：如果某个 section 看起来空，那是布局/构图问题，不是内容问题。禁止用占位文本、假 stats、装饰性 icon 填空。删到剩核心 + 重新构图，而不是加内容
- **多方向变体用页内控制，禁止多文件**：多个设计方向用 variant selector / CSS 变量切换，或并排 artboard 展示。禁止创建 N 个独立 HTML 各存一个方向——用户需要对比时打开 N 个链接，不如页内 toggle。版本迭代保留旧版：`My Design.html` → `My Design v2.html`（复制后编辑副本）

**should**（建议遵守，可根据场景灵活调整）：
- 排版有节奏：不对称、留白、层叠、对角线流动。网格是基础但可以打破
- 动效有克制：一个精心编排的入场动画 > 满屏散落的微交互
- 间距用 4px 倍数（4/8/12/16/24/32/48/64），保持节奏一致
- 首屏当海报做：品牌/产品名最响亮，hero 需要真实视觉锚点（不是装饰纹理）
- 如果删掉 30% 的 copy 后页面更好，继续删

## 布局硬规则（Landing/Marketing 场景）

以下三条对 landing / marketing / portfolio / 教学落地页生效，dashboard / 产品 UI / 后台不强制。

### 规则 1：Hero 文字栈最多 4 个元素

Hero 是单一时刻，不是 feature 列表。允许的文字元素，**整个 hero 最多 4 个**：

1. eyebrow（小号大写标签）**或** brand strip **或** 二选零
2. 标题（最多 2 行）
3. 副文案（最多 20 词，最多 4 行）
4. CTA（1 个主 + 最多 1 个次）

**禁止塞进 hero 的**：
- CTA 下方的微 tagline（"Works with GitHub, GitLab..."）
- "Used by" 信任 logo 条（应在 hero **下方**独立 section）
- 价格预告（"Free for solo, $10/user"）
- feature 列表
- 头像信任墙

如果你有 eyebrow + CTA 下小字 tagline，删掉 tagline。一个 hero 一个小字元素，封顶。

### 规则 2：Section 布局家族不复用

整页 section 之间，同一种布局家族（3-column-image-cards / full-width-quote / split-text-image / bento-grid / sticky-stack）**最多出现 1 次**。

8 section 的 landing 至少用 4 种不同布局家族。一页 6 个左图右文的 "selected work" 各自重复布局 = AI 反复犯的 Tell。

例：
- ✅ Hero 不对称分屏 + Features 3-up bento + Process 编号横列 + Quote pinned + Pricing 2x2 + FAQ 折叠 + CTA 居中
- ❌ Hero 居中 + Features 3 等列卡片 + Showcase 3 等列卡片 + Testimonials 3 等列卡片

### 规则 3：Section eyebrow 限额

"小号大写带 tracking 的 eyebrow 在每个 section 标题之上" 是模板节奏的 AI Tell。

**规则**：除 hero 外，最多每隔一个 section 用 eyebrow。**交替**：有 eyebrow / 无 eyebrow / 有 eyebrow / 无 eyebrow。

如果你在一个项目里写了 6 个以上 `text-[11px] uppercase tracking-[0.18em]` 风格的 eyebrow，违反此规则——重新审视哪些 section 真的需要 eyebrow，哪些只是为了"看起来像设计"。

## Redesign 协议（改版已有站点）

**适用范围**：对已上线/已有代码的站点做视觉改版。greenfield 新建不触发。误判模式是 redesign 翻车的最大来源——Design Read 里 redesign 必须标注 preserve 或 overhaul，含糊时只问一次："保留现有品牌演进，还是视觉推倒重来？"

- **Preserve**：品牌不变，现代化执行。dial 起点 = 先给旧站打一组 VARIANCE/MOTION/DENSITY 读数，从那里演进，不用默认基线
- **Overhaul**：视觉当 greenfield 做，但内容和信息架构（IA）照搬保留

**动手前先审计**（写进响应，不在脑子里）：品牌 token（主/强调色、字栈、logo 处理、圆角）、IA（页面树、主导航、转化路径）、值得保留的招牌交互、该退役的 AI Tell 和坏布局、**SEO 基线（在排名的页面、meta、结构化数据、OG 卡）——SEO 迁移是 redesign 第一风险**。

**现代化杠杆按序使用，满足 brief 即停**：① 字体刷新（风险最小、视觉提升最大）→ ② 间距与节奏 → ③ 配色再校准（降饱和、统一中性色、保留品牌强调色）→ ④ 动效层 → ⑤ Hero/关键 section 重组 → ⑥ 整块替换（仅当旧块无可救药）。

判型：IA、内容、SEO 都健康 → 只用杠杆 ①-④（约 40% 风险拿 70% 价值）；结构性视觉债（IA 烂/无设计系统/移动端坏）→ 全量重设计但内容严格保留；品牌本身在换 → 按 greenfield 走。

**未经用户明确批准永不改**：URL slug / 主导航文案 / 表单字段名和顺序（炸 analytics + autofill）/ logo / 法务与 cookie 文案。已有的 a11y 成果（focus 态、alt、键盘导航、对比度）只能更好不能回退；品牌已经是某个"被禁"色（如紫色）就保持——品牌事实优先于反 AI 默认色规则。

## 海报 / 封面：极简黑白编辑风（确定性渲染）

**适用范围**：单图传播物——小红书封面、X 文章封面、朋友圈/社群引流海报、活动 KV、公众号头图。这类是"一张图传播"，不是 landing/UI，走**确定性 HTML/CSS/SVG 渲染**（中文字准、二维码占位可控、可复现），不用 AI 生图。量化维度固定 **VARIANCE 6 / MOTION 0 / DENSITY 3**。

**默认风格 = 极简黑白编辑风**（Edon 的封面审美，像设计杂志封面，不像促销传单）。六条铁律：

1. **单强调色铁律**：黑白灰纸感基底（浅 `#f4f0e7`/墨 `#16130d`，暗 `#100f0d`/墨 `#f3efe6`）+ **唯一一个强调色，只点在一处**（最该被记住的那个词）。第二处彩色即破功。
2. **三层文字系统**：① eyebrow 全大写英文标签 + 年份/场次（10px、字距 2px、下方 1.5px 实线，右挂地点小字）→ ② A 层巨型中文主视觉词（70–80px、weight 900、line-height .92，占上半屏）→ ③ B 层完整短句（30–36px，强调色落在此层某一个词）+ C 层 stamp 印章（带框微旋转 `rotate(-2deg)` 小标签）。字号断崖式拉开。
3. **模块网格 + 数字优先**：卖点拆成「大数字 + 小标签」三栏网格（27px 数字 + 11px mute 标签，上方 1.5px 主墨实线）。能用数字（尺寸/数量/时间/¥0）就不用形容词。
4. **抽象隐喻，不用实物**：线描 SVG 图形做背景大水印（`opacity:.09`，只描边不填充）。不放实拍照、不放彩色插画。隐喻 > 写实。
5. **印刷颗粒 + 英文 slogan + 强留白**：`::after` 叠 SVG `feTurbulence` 噪点（浅 multiply .45 / 暗 screen .06）去塑料感；底部全大写英文 slogan 上下细线夹住做节奏（纯装饰）；`margin-top:auto` 把网格推到下半屏，中段大面积空。宁空勿满。
6. **成套出浅 + 深两版**：同骨架换配色，交替发。暗色版专门承载"夜场/反差"叙事。

**禁区（一眼出戏的通用 promo 痕迹）**：右上角促销角标 ribbon ❌ / 渐变·礼花·霓虹光晕 hero 底 ❌ / 多强调色或彩色 emoji 主视觉 ❌ / 实物堆叠一锅烩 ❌ / 居中「标题—副标—按钮」传单三段式 ❌ / 形容词卖点 ❌。

**合规**：公域图（小红书/抖音封面）不出现二维码/电话/微信号/价格优惠（限流）；私域图（朋友圈/群海报）可留二维码占位，但领券/折扣文案只在私域。

**AI 生图版封面**（需要质感强、非确定性、无精确中文文字要求时）：六套封面提示词框架（弥散风/巨型透视字/极简黑白/麦肯锡/学术科研/时装手稿）见 memory `reference_x_article_cover_prompts.md`（@AdrianPunk115）。本节是其中「极简黑白编辑风」的**确定性 HTML 落地版**——要中文字准走本节，要 AI 质感走 memory。

**落地参考实现**：`~/Developer/worldcup-posters/flyer.html`（纸白 + 暗色成套，class 结构 `.eyebrow/.headline/.big/.big2/.stamp/.specs/.slogan/.qr` 可直接复用）。注意该文件含**项目级主题破例**（世界杯绿茵：绿色球场背景层，红仅落文字）——通用纯编辑风看本节规则，主题扩展看项目 `DESIGN.md`。

## B2B 工具 / 后台 UI 规范

适用：ERP、管理后台、数据面板、内部工具。不适用 landing/marketing（走§布局硬规则）。密度优先，操作响应 ≤150ms，平面化。

**Typography（与 landing 最大差异）**：正文 **13px / 行高 1.4**（不是 web 默认 16px/1.6），副字段 12px，区块标题 16px。数字列用 `tabular-nums`，禁 serif。

**四必备状态（任何组件实现前先定好）**：
1. Loading → 行级 skeleton（表格）/ spinner + 禁用（按钮）
2. Empty → 居中 + 64×64 icon + 12px 说明 + CTA 按钮（必须有 next action）
3. Error → 行级红色背景 + 重试按钮 / 右下 toast 4s 自动消失。**错误文案格式：陈述事实 + 给行动**，禁卖萌（"哎呀出错" → "同步失败：返回 429，正在重试 3/5…"）
4. Success → 右下 toast 绿色 1.5s，无 confetti

**禁忌**：毛玻璃 `backdrop-filter` / 暗色卡片 / 弹簧 bounce 动画 / ≥16px 正文 / 圆角 >12px（Dialog 例外用 12px）/ hover 常驻阴影（仅 hover 时才显）/ eyebrow 装饰标签

## Do / Don't 对照

| Do | Don't | 严重度 |
|---|---|---|
| 开工前写出 VARIANCE/MOTION/DENSITY 三个值和美学关键词 | 不定方向直接动手 | HIGH |
| 标题用 display 字体，正文用高可读性字体，二者反差明显 | 全站一个 sans-serif 字体走到底 | HIGH |
| 主色占大面积，强调色只在 CTA 和关键元素上出现 | 五六种颜色平均分配 | HIGH |
| 留白是设计元素，刻意为之 | 用元素填满每一寸空间 | MEDIUM |
| 用一个精准的动画引导注意力 | 每个元素都加 hover 动效 | MEDIUM |
| 选色/选字体时写出「不选 X 因为 Y」的排除理由 | 只列结论不解释取舍 | HIGH |
| 强调色 WCAG 对比度 ≥ 3:1（文字 ≥ 4.5:1），选色时标注验证结果 | 只凭视觉感觉选色，不验证对比度 | CRITICAL |
| 动效按场景分档（详见下方"Animation 补充"），exit 比 enter 短 30-40% | 动效超过 1s，或入场退场同时长 | LOW |
| 占位数据用有机数字（47.2%、+1 (312) 847-1928） | 99.99%、1234567 等假数据 | MEDIUM |

## 组件状态规范

交互组件（按钮、输入框、卡片、导航项等）**must** 定义以下 7 种状态：

1. **default** — 默认静止态
2. **hover** — 鼠标悬停
3. **focus-visible** — 键盘聚焦（必须可见，不能去掉 outline 又不给替代）
4. **active** — 按下瞬间（-translate-y-[1px] 或 scale-[0.98] 模拟物理按压）
5. **disabled** — 不可用态（视觉上明确降低对比度）
6. **loading** — 加载中（骨架屏匹配布局尺寸，不用通用圆形 spinner）
7. **error** — 错误态（配合错误信息展示）

不需要全部 7 种的场景（如纯展示卡片），至少覆盖 default + hover + focus-visible。

**hover-only 显示的次要操作**（如行级编辑/删除按钮）：用 `opacity-0 group-hover:opacity-100 focus-within:opacity-100` 双触发，让键盘 Tab 能让按钮显示出来。只挂 `group-hover` 会让键盘用户永远看不到按钮。

## 技术护栏

- 全高 section 用 `min-h-[100dvh]`，不用 `h-screen`（iOS Safari 布局跳动）
- 多列布局用 CSS Grid，不用 flexbox 百分比计算（`w-[calc(33%-1rem)]` → `grid grid-cols-3 gap-6`）
- 动画只用 transform + opacity，不动 top/left/width/height
- 噪点/纹理滤镜加在 fixed + pointer-events-none 伪元素上，不加在滚动容器
- 阴影用背景色调色（tinted shadow），不用默认灰色 box-shadow

## CJK 多语言排版

UI 中混合中日韩与拉丁文字时：
- **字体栈**：Latin 前置，CJK 后补，保证各字符得到正确 glyph：`font-family: -apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif;`
- **行高**：CJK 正文 `line-height ≥ 1.7`（汉字字符密，默认 1.5 不够）
- **lang 属性**：混合内容块加 `lang="zh"` / `lang="en"`，浏览器选对字体和断行规则
- **serif 阅读模式**：必须配 CJK serif fallback——`"Newsreader", "Songti SC", "Noto Serif SC", serif`；否则 serif 切换后中文静默回退 sans，视觉不一致

## Tailwind + React 硬约束

来源：[baseline-ui](https://www.ui-skills.com/skills/ibelick/baseline-ui) (Ibelick)。Tailwind + React 项目的 stack-level 清单，跟"技术护栏"互补，不重复已有规则。

**应用前提（先于清单本身）**

硬约束清单不是"全部必须套"，是"用到时按这个标准"。先按量化维度做 trade-off：

- MOTION ≤ 3：纯 Tailwind `transition-*` 足够，**不必引** `motion/react`（多 ~15kb 依赖换 hover 微动不划算）
- 没有 Dialog / Popover / Combobox / Menu 等真复杂交互：**不必拉** Base UI / Radix
- DENSITY < 5：`tabular-nums` 仅用于真正的数据列，不是所有数字

用到的工具按下面标准；用不到的别为了套规则强引依赖。

**Stack 选型**
- 动画库用 `motion/react`（旧名 `framer-motion`），不自造
- Tailwind 入场/微动画用 `tw-animate-css`
- 类名合并必须用 `cn`（`clsx` + `tailwind-merge`）
- 组件 primitive 优先 Base UI，其次 React Aria / Radix；同一交互面不混搭多套

**A11y 与组件**
- icon-only 按钮必须 `aria-label`
- 永不手写键盘/焦点行为，用 primitive
- 破坏性/不可逆操作用 `AlertDialog` 而非普通 `Dialog`
- 错误信息显示在动作发生处，不集中堆顶或堆底
- `input` / `textarea` 不阻止粘贴

**Layout 补充**
- 正方形元素用 `size-*`，不用 `w-* + h-*`
- z-index 用固定 scale（如 `z-modal` / `z-popover`），禁任意 `z-[123]`
- 固定/吸边元素必须 `safe-area-inset-*`

**Typography 补充**
- 标题加 `text-balance`，正文加 `text-pretty`
- 数据/数字必须 `tabular-nums`
- 密集 UI 用 `truncate` 或 `line-clamp-*`
- 不改 `tracking-*` 除非显式要求

**Animation 补充**

时长按场景分档（不是一刀切上限）：

| 场景 | 时长 | 说明 |
|------|------|------|
| 直接反馈（按钮 `:active` / hover / tooltip / icon 切换） | 100-200ms 硬上限 | 用户期待"跟手"，超过感觉迟钝 |
| 展开/收起（dropdown / select / popover / accordion） | 150-250ms | 需要从触发点流畅展开，<150ms 没有展开感 |
| 空间转换（modal / drawer / sheet / page） | 200-500ms | 空间感切换，太短读不到方向 |
| 营销/解释性（onboarding / 首屏演示） | 可更长 | 不在交互链路上 |

- exit 比 enter 短 30-40%（所有类别共用）
- 入场默认 `ease-out`，**永不用 `ease-in`** 做 UI 动画（起步慢让界面感觉迟钝）
- paint props（`background` / `color`）只在小范围 UI（图标、文字）动画
- 离屏循环动画必须暂停
- `prefers-reduced-motion` 必须降级
- 不动画大 `blur()` / `backdrop-filter` 区域
- `will-change` 只在动画激活期间，结束立即移除

**Design 补充**
- 空状态必须给一个明确 next action，不能只是空白展示
- accent color 一个 view 只用一种
- 优先用现有 token / Tailwind 默认 shadow scale，不轻易引入新值

**性能反模式**
- `useEffect` 不做能在 render 阶段表达的事

**React + Babel 多文件原型专项约束**（来源：baoyu-design 逆向分析，已实测为真实坑）

- **`const styles` 必崩**：多 Babel 文件里同名 styles 对象互相覆盖。每个组件用唯一名：`const terminalStyles = {}` / `const sidebarStyles = {}`；或全走 CSS 变量 + className（推荐，顺便解决 dark mode）
- **Babel script 不共享 scope**：跨文件共享组件必须显式导出：`Object.assign(window, { Terminal, Sidebar, ... })`；不能依赖 import
- **永远走 HTTP，禁 `file://`**：`<script type="text/babel" src="xxx.jsx">` 在 `file://` 下浏览器静默拒绝加载。预览命令：`python3 -m http.server 4311 --directory designs`
- **拆文件按耦合度，不按行数**：抽出 data/icons/纯展示组件；保持合并有状态 App + 强耦合 modal/panel。典型加载顺序：`data.jsx → icons.jsx → panes.jsx → app.jsx`
- **CDN 锁版本 + integrity**：`<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous">`（防版本漂移）

## 交付检查清单

按优先级从高到低检查，CRITICAL 不过不交付。

**自动扫一遍（有真 CSS 产物时）**：`~/.claude/scripts/design-lint.sh <构建产物.html>`——确定性检测 34 条 AI 设计反模式（cream 背景/icon-tile 堆叠/低对比/弹层被裁/排版可读性阈值/重复 CTA intent/eyebrow 超额/beige+brass 高端套色等），比人肉对照下面清单可靠。exit 2 = 检出问题，逐条核。注意：扫 Tailwind 项目要用编译后 dist（真 CSS），不是 CDN 开发态。

**CRITICAL（无障碍 & 可用性）**
- [ ] focus-visible 可见：键盘 Tab 遍历所有交互元素，每个都有清晰的聚焦指示
- [ ] 触摸目标 ≥ 44px：按钮、链接、输入框的最小点击区域
- [ ] 强调色对比度 ≥ 3:1，正文对比度 ≥ 4.5:1（用工具验证，不目测）
- [ ] 移动端适配：最小 375px 宽度无横向滚动，内容不溢出

**HIGH（布局 & 内容）**
- [ ] 量化维度值已声明，设计决策与维度值一致
- [ ] 长文本溢出：标题超长时截断/换行策略明确
- [ ] 空状态：列表无数据时有明确展示（不是空白页面）
- [ ] 单项 vs 多项：只有 1 条数据时布局不崩
- [ ] 异步内容预留空间：图片/动态内容加载前不导致布局跳动（用 aspect-ratio 或固定高度）

**MEDIUM（体验 & 细节）**
- [ ] reduced-motion：`prefers-reduced-motion` 下动效关闭或降级
- [ ] 暗色模式（如适用）：独立验证对比度，不假设亮色模式的值能直接复用
- [ ] 加载状态：所有异步操作有视觉反馈，不是无响应

## 参考网站时的提取流程

需要参考某个网站风格时，**不目测，用数据**：

1. **提取精确 token**：用 `getComputedStyle()` 遍历目标页面 DOM（深度 ≤4），批量取 CSS 计算值（字体、颜色、间距、阴影、圆角、transition），过滤掉默认值。截图用于整体感觉参照，数值负责精确度
2. **写组件 spec**：每个组件 dispatch 前先写 spec，覆盖 DOM 结构、精确 CSS 值、交互模型（scroll/click/hover/static）、状态 diff、真实文本、资产路径、响应式断点变化。**spec inline 进 prompt**，不让 builder 自己读文件
3. **并行施工**：每个 section 提取完立刻 dispatch builder agent（worktree 隔离），不等全部提取完再开工。orchestrator 继续提取下一个
4. **视觉 QA**：原站和克隆站 1440px / 390px 截图对比，差异溯源（spec 错 → 重新提取；builder 错 → 修组件）

**spec 上限 150 行**，超了就拆分。不允许用「逻辑相关」绕过。

## 执行标准
- 做完第一版就检查，假设有问题（因为大概率有）
- 视觉内容转图片后让子代理用新鲜眼睛审查
- 至少完成一轮「修复→重新检查」循环才能交付
