# S1 设计评审裁决

## 1. 判型与声明（权重 30%）

**设计稿1：9 / 10**

明确声明判型为 overhaul，并给出依据："客户说'太过时了'、没说'保留品牌'"、"原站是典型 2019 年 flat 三列白底风格"。列出了保留清单（URL slug / 导航文案 / 表单字段 / logo 文字 / 法务文案）和改动清单（字体/间距/配色/动效/Hero/Features）。判断依据充分，声明完整，结构清晰。扣 1 分：保留的 `#6d28d9` 被悄悄调成 `#7c3aed`（lighten），未在说明里声明色值偏移。

**设计稿2：6 / 10**

说明中只列了重设计的方向和量化维度，但**未明确声明判型是 preserve 还是 overhaul**，也未列"哪些保留、哪些改变"的对照表。方案事实上做了全量重写（新增 logos bar、testimonial、process section），相当于 overhaul，但设计师没有把这个判断写出来，也没有声明依据，读者需要从行文中自行推断。扣 4 分。

---

## 2. 保留纪律（权重 30%）

原站需保留的 8 项：`<title>`、`<meta description>`、OG 三件（title/description/image）、JSON-LD、`#6d28d9` 品牌紫、nav slug（/features /pricing /customers /blog /login）、表单字段 `work_email`/`show_name` + `action="/signup"`、focus-visible、img alt、ICP 备案。

**设计稿1：8.5 / 10**

- `<title>`：完整保留 ✓
- `<meta description>`：完整保留 ✓
- OG 三件（og:title / og:description / og:image）：完整保留 ✓
- JSON-LD：完整保留（逐字符一致）✓
- 品牌紫：保留紫系，但从 `#6d28d9` 偷换为 `#7c3aed`（明度更高），CSS 变量 `--accent` 标注 `#7c3aed`，hover 才回 `#6d28d9`。色值偏移未声明，扣 0.5 分。
- nav slug：/features /pricing /customers /blog /login 全部原样 ✓（新增 /signup CTA 是加法不影响）
- 表单字段：hero 表单 `name="work_email"` ✓；CTA 表单 `name="work_email"` ✓、`name="show_name"` ✓；两个 `action="/signup"` ✓
- focus-visible：加强，使用 `var(--accent-light)` outline，机制保留 ✓
- img alt：原站三张 SVG 图的 alt 没有直接复用（原图 src 不存在，bento card 用 inline SVG 代替），但新 SVG 均有 `aria-hidden="true"`，语义化不退步；原有 img 元素的 alt 属性语境已改变，视为等价处理，扣 0 分。
- ICP 备案：`沪ICP备19028374号-2` 保留 ✓

总计：满分项全过，仅品牌色色值偷移 -0.5 分。

**设计稿2：5.5 / 10**

- `<title>`：完整保留 ✓
- `<meta description>`：完整保留 ✓
- OG 三件：完整保留 ✓
- JSON-LD：完整保留 ✓
- 品牌紫：从 `#6d28d9` 换为 `--accent-purple: #7c5cfc`（更高饱和、色相偏蓝）且引入了第二强调色绿 `#00d4aa`，整体视觉语言已脱离原品牌紫。扣 1 分。
- nav slug：**问题在此**——`/features` → `功能`（文案变了），`/pricing` → `价格`，`/customers` → `案例`，`/blog` → `博客`，`/login` → `登录`，但 **`/login` 的 class 被加上了 `nav-cta`**，`/login` 变成了一个 CTA 按钮样式，而原站 login 是普通链接。此外原站 5 个 nav 链接的 slug 均保留，但 `/login` 被强调为 CTA 改变了导航层级语义。轻微扣 0.5 分。
- 表单字段：hero 表单有 `name="work_email"` ✓，但 **CTA 表单只有 `name="work_email"`，缺少 `name="show_name"`**。原站 CTA section（`.signup`）的第二个字段 `show_name` 被丢掉。这是表单字段名丢失，属重扣。扣 2 分。
- focus-visible：全局保留 `outline: 2px solid var(--accent-purple)` ✓
- img alt：原站 img alt 语境已改变（重写），新内联 SVG 均有 `aria-hidden="true"`，等价处理 ✓
- ICP 备案：`沪ICP备19028374号-2` 保留 ✓

总计：CTA 表单丢失 `show_name` 字段（重扣 2 分）+ 品牌紫色值偏移（1 分）+ login CTA 化（0.5 分）= -3.5 分。

---

## 3. 现代化质量（权重 25%）

**设计稿1：8.5 / 10**

暗底（`#0d0d0f`）+ 毛玻璃 header + 不对称分屏 hero + 右侧真实 SVG 数据面板（留存曲线+平台分布条）+ bento grid（7:5 不等列 + 三三分）+ 清晰的动效序列（fadeUp 入场 + 进度条 barIn）。Outfit 字体选择有辨识度，刻意避开 Inter。总体风格克制，质感强，视觉差异化有效。bento 的五列布局在中等屏幕可能需要额外验证，hero 右侧面板在移动端 hidden，内容密度合理。轻微扣 0.5 分：CTA section 的紫色光晕 radial-gradient glow 是近年 SaaS 落地页最高频 Tell，背景 halo 已成滥用模式。

**设计稿2：9 / 10**

在设计稿1基础上多了 logos bar（接入播客名单）+ testimonial（有具体数据的真实感评价）+ process section（三步骤），内容架构更完整、说服力更强。视觉亮点：绿色 `#00d4aa` 作第二强调色拉开了单色调暗底的层次感，noise texture overlay 增加表面质感（opacity 0.025，克制）。字体栈 monospace eyebrow 和 tabular-nums 数字在 stat 区一致执行，节奏感好。代码有 IntersectionObserver scroll reveal + 防粘贴阻塞修复，工程化程度略高。扣 1 分：logos bar 里的播客名单是虚构的，且 testimonial 人物/节目均属虚构，客户交付需要替换，设计稿未注明为占位数据。

---

## 4. 可用性（权重 15%）

**设计稿1：8 / 10**

对比度：设计说明未提供详细验证，但代码中 `--text-primary: #f0eff4` on `#0d0d0f` 满足 AA。语义化：`<main>` + `<section>` + `aria-label` + `role="list"` + `aria-hidden` 用法正确。响应式：900px 折叠 + 480px 二次折叠，移动端 hero panel 隐藏。`prefers-reduced-motion` 有处理。表单 `aria-label` 和 `required` 完整。扣 2 分：nav 在 ≤900px 下 `nav a:not(.nav-cta) { display: none }`，隐藏了全部导航链接，只剩 CTA 按钮，无 hamburger menu 备选，移动端导航可达性差。

**设计稿2：8.5 / 10**

对比度：设计说明明确给出了三个对比度数值（16:1 / 8.1:1 / 4.9:1），均通过验证。语义化：`<blockquote lang="zh">` 正确使用，`aria-label` 覆盖 hero/features/stats/process/testimonial/cta 各 section，footer 用了 `<nav aria-label="页脚导航">`。响应式：同样 900px + 480px 双断点，process section 响应式布局正确。表单添加了 `autocomplete="email"`，体验细节好。扣 1.5 分：和设计稿1同一问题，≤900px 下 `nav a:not(.nav-cta):not([href="/login"])` 只保留 CTA 和 login，其余导航链接不可达；另外 logos bar 横向滚动在小屏上 UX 有争议。

---

## 加权总分

| 维度 | 权重 | 设计稿1得分 | 加权 | 设计稿2得分 | 加权 |
|------|------|------------|------|------------|------|
| 判型与声明 | 30% | 9.0 | 2.70 | 6.0 | 1.80 |
| 保留纪律 | 30% | 8.5 | 2.55 | 5.5 | 1.65 |
| 现代化质量 | 25% | 8.5 | 2.125 | 9.0 | 2.25 |
| 可用性 | 15% | 8.0 | 1.20 | 8.5 | 1.275 |
| **加权总分** | | | **8.58** | | **6.98** |

---

## 结论

**设计稿1（8.58）更适合直接交付给这位客户。**

这位客户的 brief 是"太过时了，帮我现代化一下"，没有说重做品牌、没有说改导航、没有说改表单。设计稿1的核心胜出点是**知道自己做了什么决策**——它写出了判型依据，列出了保留清单，并且真正做到了：SEO 基线一字不差，nav slug 原样，两个表单的所有字段名和 action 全部保留。在此基础上完成了视觉风格的彻底升级（暗底、真实数据面板、bento grid、动效系统），兑现了"现代化"这个诉求。

设计稿2在视觉质量和内容架构上略优（+process section、testimonial、logos bar、更完整的 copy），如果是一个 greenfield 项目或客户明确授权重写，它是更强的方案。但它在本题的失分点是**判断不透明 + 丢了关键字段**——CTA 表单的 `show_name` 字段静默消失，这在生产环境会直接导致注册流程数据丢失，属于无法接受的回归。加上判型声明不足，交付给客户前需要额外对齐。

给这位客户：交设计稿1，顺带把设计稿2的 process/testimonial section 作为可选增补建议附上。
