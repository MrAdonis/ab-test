## 设计说明

**Design Read**

Reading this as: **redesign (overhaul)** for **企业行政采购决策者（HR/行政主管）**, with a **trust-first + 现代餐饮品牌** language, leaning toward **原生 CSS + 中性色系 + 编辑型字体栈**。

---

**澄清判断（客户不在场）**

客户说"视觉推倒重来，做成现代的"——判定为 **Overhaul** 类型：视觉当 greenfield 做，内容和信息架构严格保留。

需要判断的模糊点：
- 「现代」对于 B2B 团餐场景 = trust-first + 专业感，而非 Awwwards 型实验布局。目标读者是企业行政，转化动作是填订餐表单，信任比酷更重要。我的判断：选 trust-first 方向，偏编辑型克制，不做 Dribbble 风。
- 原站有导航链接（/about.html、/caidan.html 等）——这是多页站的单页 HTML，我保留导航结构但不生成跳转页面，URL 保持原样（不改 slug）。
- 原站有图片（images/hongshaorou.jpg 等）——图片路径保留，用 aspect-ratio 容器保留位置避免布局跳动。

**量化维度**

- VARIANCE: 5（有节奏的不对称，但不破格——B2B 企业采购不需要实验布局）
- MOTION: 3（CSS 过渡为主，入场 fade-up，无滚动编排）
- DENSITY: 5（标准 web，信息全部保留，节制留白）

**美学关键词**：克制、专业、可信

**色彩决策**
- 主色：深墨绿 `#1a3c2e`（60-70%）——延续原站绿色品牌色，去掉饱和度，专业感
- 中性色：暖白 `#f9f7f4`、浅灰 `#f2efe9`、边框 `#e8e3db`（30%）
- 强调色：暖橙 `#c85a1e`（≤10%）——替代原站刺眼红色，保留食欲感，饱和度降低
- 不选紫色渐变（AI审美标志）；不选纯黑（用 `#1a1a18` 代替）

**字体决策**
- 标题：`"Noto Serif SC"` / `"Songti SC"` 系列——餐饮/食品场景衬线字体有温度感，比 Gothic 更有品质感；不选 Inter/Roboto（AI Tell）
- 正文：`-apple-system, "PingFang SC", "Noto Sans SC", sans-serif`——可读性优先
- 数字：`tabular-nums` + 等宽数字字体处理价格

**布局**
- Hero：不对称分屏（左文字 + 右快速订餐表单），VARIANCE 5 下的实用分屏，不是纯装饰性破格
- 菜单：3 列卡片（但每张卡片有真实层次感，非等宽平铺 AI 版本）
- 服务说明：full-width 编辑区块，数字高亮
- Section eyebrow 交替使用

**保留内容清单（全部保留）**
- ✅ 公告内容（低脂套餐活动）
- ✅ 三款菜单（名称、价格、描述、图片路径）
- ✅ 订餐表单（4个字段 + select + button，form action 不变）
- ✅ 订餐须知（10:30前下单、10份起送、免配送费）
- ✅ 服务说明（成立年份、37家企业、食品证号、冷链、月结发票）
- ✅ 导航链接（URL保持原样）
- ✅ 页脚（公司名、版权年份、热线、ICP、食品证号）
- ✅ marquee 公告（改为静态通知栏，内容不变）

**未改内容**
- URL slug / 表单字段名和顺序 / form action / 法务文案 / ICP备案号 / 食品经营许可证号

---

## 最终 HTML

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>佳膳食堂 — 企业团餐订餐</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* ─── Reset & Base ─── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --ink:       #1a1a18;
    --ink-muted: #5a5750;
    --ink-faint: #8a857c;
    --bg:        #f9f7f4;
    --bg-subtle: #f2efe9;
    --border:    #e8e3db;
    --green:     #1a3c2e;
    --green-mid: #2a5a44;
    --green-light: #e8f2ec;
    --accent:    #c85a1e;
    --accent-bg: #fdf1eb;
    --white:     #ffffff;

    --font-serif: "Noto Serif SC", "Songti SC", "Noto Serif", Georgia, serif;
    --font-sans:  "Noto Sans SC", -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;

    --radius-sm: 6px;
    --radius:    10px;
    --radius-lg: 16px;

    --shadow-sm: 0 1px 3px rgba(26,26,24,.06), 0 1px 2px rgba(26,26,24,.04);
    --shadow:    0 4px 16px rgba(26,26,24,.08), 0 1px 3px rgba(26,26,24,.05);
    --shadow-lg: 0 12px 32px rgba(26,26,24,.12), 0 4px 8px rgba(26,26,24,.06);
  }

  html { font-size: 16px; scroll-behavior: smooth; }
  body {
    font-family: var(--font-sans);
    background: var(--bg);
    color: var(--ink);
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
  }

  /* ─── Accessibility ─── */
  :focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
    border-radius: 3px;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }

  /* ─── Utility ─── */
  .container {
    max-width: 1120px;
    margin: 0 auto;
    padding: 0 24px;
  }

  /* ─── Notice Bar ─── */
  .notice-bar {
    background: var(--green);
    color: #b8d9c6;
    font-size: 13px;
    font-family: var(--font-sans);
    padding: 9px 24px;
    text-align: center;
    letter-spacing: .01em;
  }
  .notice-bar strong {
    color: #ffffff;
    font-weight: 500;
  }

  /* ─── Navigation ─── */
  .nav {
    background: var(--white);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    max-width: 1120px;
    margin: 0 auto;
    padding: 0 24px;
  }
  .nav-brand {
    font-family: var(--font-serif);
    font-size: 20px;
    font-weight: 700;
    color: var(--green);
    text-decoration: none;
    letter-spacing: .02em;
    transition: color 150ms ease-out;
  }
  .nav-brand:hover { color: var(--green-mid); }
  .nav-links {
    display: flex;
    gap: 32px;
    list-style: none;
  }
  .nav-links a {
    font-size: 14px;
    font-weight: 500;
    color: var(--ink-muted);
    text-decoration: none;
    transition: color 150ms ease-out;
  }
  .nav-links a:hover { color: var(--ink); }

  /* ─── Hero / Split Layout ─── */
  .hero {
    padding: 72px 0 80px;
  }
  .hero-grid {
    display: grid;
    grid-template-columns: 1fr 420px;
    gap: 64px;
    align-items: start;
  }

  .hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--green-mid);
    margin-bottom: 20px;
  }
  .hero-eyebrow::before {
    content: '';
    display: block;
    width: 24px;
    height: 1.5px;
    background: var(--green-mid);
    flex-shrink: 0;
  }

  .hero-title {
    font-family: var(--font-serif);
    font-size: clamp(36px, 5vw, 54px);
    font-weight: 700;
    line-height: 1.2;
    color: var(--ink);
    margin-bottom: 20px;
    text-wrap: balance;
  }
  .hero-title em {
    font-style: normal;
    color: var(--green);
  }

  .hero-sub {
    font-size: 16px;
    color: var(--ink-muted);
    line-height: 1.75;
    max-width: 480px;
    margin-bottom: 32px;
    text-wrap: pretty;
  }

  .hero-stats {
    display: flex;
    gap: 32px;
    padding-top: 32px;
    border-top: 1px solid var(--border);
  }
  .stat-item {}
  .stat-num {
    display: block;
    font-family: var(--font-serif);
    font-size: 28px;
    font-weight: 700;
    color: var(--ink);
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 4px;
  }
  .stat-label {
    font-size: 12px;
    color: var(--ink-faint);
  }

  /* ─── Order Form Card ─── */
  .order-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 32px;
    box-shadow: var(--shadow-lg);
    position: sticky;
    top: 80px;
  }
  .order-card-title {
    font-family: var(--font-serif);
    font-size: 20px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 6px;
  }
  .order-card-sub {
    font-size: 13px;
    color: var(--ink-faint);
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
  }

  .form-group {
    margin-bottom: 14px;
  }
  .form-label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--ink-muted);
    margin-bottom: 6px;
    letter-spacing: .02em;
  }
  .form-input,
  .form-select {
    width: 100%;
    height: 42px;
    padding: 0 14px;
    font-size: 14px;
    font-family: var(--font-sans);
    color: var(--ink);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    transition: border-color 150ms ease-out, box-shadow 150ms ease-out;
    appearance: none;
    -webkit-appearance: none;
  }
  .form-input::placeholder { color: var(--ink-faint); }
  .form-input:hover, .form-select:hover { border-color: #c8c0b4; }
  .form-input:focus-visible, .form-select:focus-visible {
    outline: none;
    border-color: var(--green);
    box-shadow: 0 0 0 3px rgba(26,60,46,.12);
  }

  .form-select-wrap {
    position: relative;
  }
  .form-select-wrap::after {
    content: '';
    position: absolute;
    right: 14px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid var(--ink-faint);
    pointer-events: none;
  }

  .btn-submit {
    width: 100%;
    height: 48px;
    margin-top: 20px;
    background: var(--green);
    color: #ffffff;
    font-family: var(--font-sans);
    font-size: 15px;
    font-weight: 500;
    letter-spacing: .02em;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 150ms ease-out, transform 100ms ease-out;
  }
  .btn-submit:hover { background: var(--green-mid); }
  .btn-submit:active { transform: scale(0.98); }
  .btn-submit:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
  }

  .form-note {
    font-size: 12px;
    color: var(--ink-faint);
    text-align: center;
    margin-top: 12px;
    line-height: 1.6;
  }

  /* ─── Menu Section ─── */
  .section-menu {
    padding: 80px 0;
    background: var(--bg-subtle);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }

  .section-header {
    margin-bottom: 48px;
  }
  .section-title {
    font-family: var(--font-serif);
    font-size: clamp(26px, 3.5vw, 36px);
    font-weight: 700;
    color: var(--ink);
    line-height: 1.25;
    text-wrap: balance;
  }
  .section-lead {
    font-size: 15px;
    color: var(--ink-muted);
    margin-top: 10px;
    max-width: 540px;
  }

  .menu-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }

  .menu-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    transition: box-shadow 200ms ease-out, transform 200ms ease-out;
  }
  .menu-card:hover {
    box-shadow: var(--shadow);
    transform: translateY(-2px);
  }

  .menu-card-img {
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
    background: var(--bg-subtle);
  }

  .menu-card-body {
    padding: 20px;
  }

  .menu-card-name {
    font-family: var(--font-serif);
    font-size: 18px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 4px;
  }

  .menu-card-tag {
    font-size: 12px;
    color: var(--green-mid);
    font-weight: 500;
    margin-bottom: 10px;
  }

  .menu-card-desc {
    font-size: 13.5px;
    color: var(--ink-muted);
    line-height: 1.65;
    margin-bottom: 16px;
  }

  .menu-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 14px;
    border-top: 1px solid var(--border);
  }

  .menu-price {
    font-family: var(--font-serif);
    font-size: 24px;
    font-weight: 700;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
  }

  .menu-label {
    font-size: 11px;
    color: var(--ink-faint);
    background: var(--bg-subtle);
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid var(--border);
  }

  /* ─── About / Service Section ─── */
  .section-about {
    padding: 80px 0;
  }

  .about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    align-items: start;
  }

  .about-body p {
    font-size: 15px;
    color: var(--ink-muted);
    line-height: 1.85;
    text-wrap: pretty;
  }

  .credential-block {
    margin-top: 28px;
    padding: 20px 24px;
    background: var(--green-light);
    border-left: 3px solid var(--green);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  }
  .credential-block p {
    font-size: 13px !important;
    color: var(--green) !important;
    line-height: 1.7 !important;
    margin-bottom: 4px;
  }
  .credential-block p:last-child { margin-bottom: 0; }

  .service-highlights {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .highlight-item {
    padding: 20px;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
  }
  .highlight-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
  }
  .highlight-title {
    font-family: var(--font-serif);
    font-size: 15px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 4px;
  }
  .highlight-desc {
    font-size: 12.5px;
    color: var(--ink-faint);
    line-height: 1.6;
  }

  /* ─── Footer ─── */
  .footer {
    background: var(--green);
    color: #8ab8a0;
    padding: 40px 0;
  }
  .footer-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }
  .footer-brand {
    font-family: var(--font-serif);
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
  }
  .footer-info {
    font-size: 12.5px;
    line-height: 1.9;
    text-align: right;
  }
  .footer-info a {
    color: #8ab8a0;
    text-decoration: none;
  }
  .footer-info a:hover { color: #ffffff; }

  /* ─── Enter Animations ─── */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .anim-fade-up {
    animation: fadeUp 480ms ease-out both;
  }
  .anim-delay-1 { animation-delay: 80ms; }
  .anim-delay-2 { animation-delay: 160ms; }
  .anim-delay-3 { animation-delay: 240ms; }
  .anim-delay-4 { animation-delay: 320ms; }

  /* ─── Responsive ─── */
  @media (max-width: 900px) {
    .hero-grid {
      grid-template-columns: 1fr;
      gap: 48px;
    }
    .order-card {
      position: static;
    }
    .about-grid {
      grid-template-columns: 1fr;
      gap: 40px;
    }
    .menu-grid {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 600px) {
    .container { padding: 0 16px; }
    .hero { padding: 48px 0 56px; }
    .hero-stats { gap: 20px; }
    .menu-grid { grid-template-columns: 1fr; }
    .service-highlights { grid-template-columns: 1fr; }
    .nav-links { display: none; }
    .footer-inner { flex-direction: column; text-align: center; }
    .footer-info { text-align: center; }
  }
</style>
</head>
<body>

<!-- Notice Bar -->
<div class="notice-bar">
  <strong>本周公告：</strong>新增低脂轻食套餐！满 30 份每份立减 2 元，欢迎企业行政联系试吃。
</div>

<!-- Navigation -->
<nav class="nav" aria-label="主导航">
  <div class="nav-inner">
    <a href="/index.html" class="nav-brand">佳膳食堂</a>
    <ul class="nav-links">
      <li><a href="/index.html">首页</a></li>
      <li><a href="/about.html">关于我们</a></li>
      <li><a href="/caidan.html">每周菜单</a></li>
      <li><a href="/dingcan.html">在线订餐</a></li>
      <li><a href="/lianxi.html">联系方式</a></li>
    </ul>
  </div>
</nav>

<!-- Hero + Order Form -->
<main>
  <section class="hero">
    <div class="container">
      <div class="hero-grid">

        <!-- Left: Copy -->
        <div>
          <div class="hero-eyebrow anim-fade-up">企业团餐 · 一站式服务</div>
          <h1 class="hero-title anim-fade-up anim-delay-1">
            每日新鲜现烧<br><em>送达您的办公室</em>
          </h1>
          <p class="hero-sub anim-fade-up anim-delay-2">
            成立于 2014 年，服务园区内 37 家企业。中央厨房统一制备，全程冷链保温配送，工作日 10:30 前下单当日送达。
          </p>
          <div class="hero-stats anim-fade-up anim-delay-3">
            <div class="stat-item">
              <span class="stat-num">37</span>
              <span class="stat-label">合作企业</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">12</span>
              <span class="stat-label">年运营经验</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">10</span>
              <span class="stat-label">份起送免配送费</span>
            </div>
          </div>
        </div>

        <!-- Right: Order Form -->
        <div class="anim-fade-up anim-delay-2">
          <div class="order-card">
            <h2 class="order-card-title">快速订餐</h2>
            <p class="order-card-sub">工作日 10:30 前下单，当日午餐送达</p>
            <form action="/cgi-bin/order.cgi" method="post">
              <div class="form-group">
                <label class="form-label" for="name">联系人姓名</label>
                <input class="form-input" id="name" type="text" name="name" placeholder="请输入姓名" required autocomplete="name">
              </div>
              <div class="form-group">
                <label class="form-label" for="phone">手机号</label>
                <input class="form-input" id="phone" type="tel" name="phone" placeholder="请输入手机号" required autocomplete="tel">
              </div>
              <div class="form-group">
                <label class="form-label" for="company">公司名称</label>
                <input class="form-input" id="company" type="text" name="company" placeholder="请输入公司名称" required autocomplete="organization">
              </div>
              <div class="form-group">
                <label class="form-label" for="meal_plan">选择套餐</label>
                <div class="form-select-wrap">
                  <select class="form-select" id="meal_plan" name="meal_plan" required>
                    <option value="hongshao">红烧肉套餐 ¥22</option>
                    <option value="qingshi">低脂轻食套餐 ¥26</option>
                    <option value="sushi">素食套餐 ¥18</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label" for="quantity">份数</label>
                <input class="form-input" id="quantity" type="number" name="quantity" placeholder="最少 10 份" min="10" required>
              </div>
              <button class="btn-submit" type="submit">提交订单</button>
            </form>
            <p class="form-note">园区内免配送费 · 支持月结 · 可开增值税专用发票</p>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- Menu Section -->
  <section class="section-menu" aria-labelledby="menu-heading">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title" id="menu-heading">每周精选菜单</h2>
        <p class="section-lead">每日现烧，食材当日采购，标注热量信息，满足不同饮食需求。</p>
      </div>
      <div class="menu-grid">

        <article class="menu-card">
          <img class="menu-card-img" src="images/hongshaorou.jpg" alt="红烧肉套餐实拍" width="400" height="300">
          <div class="menu-card-body">
            <h3 class="menu-card-name">红烧肉套餐</h3>
            <p class="menu-card-tag">两荤一素一汤 · 米饭免费续</p>
            <p class="menu-card-desc">精选五花肉，每日现烧，配时令蔬菜和例汤，米饭免费续。</p>
            <div class="menu-card-footer">
              <span class="menu-price">¥22</span>
              <span class="menu-label">每人份</span>
            </div>
          </div>
        </article>

        <article class="menu-card">
          <img class="menu-card-img" src="images/qingshi.jpg" alt="低脂轻食套餐实拍" width="400" height="300">
          <div class="menu-card-body">
            <h3 class="menu-card-name">低脂轻食套餐</h3>
            <p class="menu-card-tag">鸡胸 / 牛肉可选 · 标注热量</p>
            <p class="menu-card-desc">少油低盐，标注热量和蛋白质克数，适合健身人群。</p>
            <div class="menu-card-footer">
              <span class="menu-price">¥26</span>
              <span class="menu-label">每人份</span>
            </div>
          </div>
        </article>

        <article class="menu-card">
          <img class="menu-card-img" src="images/sucai.jpg" alt="素食套餐实拍" width="400" height="300">
          <div class="menu-card-body">
            <h3 class="menu-card-name">素食套餐</h3>
            <p class="menu-card-tag">三素一汤 · 当季蔬菜</p>
            <p class="menu-card-desc">当季蔬菜为主，豆制品补充蛋白，清淡不寡淡。</p>
            <div class="menu-card-footer">
              <span class="menu-price">¥18</span>
              <span class="menu-label">每人份</span>
            </div>
          </div>
        </article>

      </div>
    </div>
  </section>

  <!-- About / Service Section -->
  <section class="section-about" aria-labelledby="about-heading">
    <div class="container">
      <div class="about-grid">

        <div class="about-body">
          <h2 class="section-title" id="about-heading">我们的服务</h2>
          <p style="margin-top: 20px;">
            成立于 2014 年，目前为园区内 37 家企业提供工作日午餐配送。中央厨房持有食品经营许可证，全程冷链/保温配送，餐损包赔。支持月结，提供增值税专用发票。
          </p>
          <div class="credential-block">
            <p>食品经营许可证：沪食证字 2014 第 310115 号</p>
            <p>全程冷链 / 保温配送 · 餐损包赔</p>
            <p>支持月结 · 开具增值税专用发票</p>
          </div>
        </div>

        <div class="service-highlights">
          <div class="highlight-item">
            <span class="highlight-icon" aria-hidden="true">🕙</span>
            <div class="highlight-title">当日送达</div>
            <p class="highlight-desc">工作日 10:30 前下单，午餐时间准时送达。</p>
          </div>
          <div class="highlight-item">
            <span class="highlight-icon" aria-hidden="true">📦</span>
            <div class="highlight-title">10 份起送</div>
            <p class="highlight-desc">园区内 10 份起送，免收配送费。</p>
          </div>
          <div class="highlight-item">
            <span class="highlight-icon" aria-hidden="true">🧾</span>
            <div class="highlight-title">月结发票</div>
            <p class="highlight-desc">支持月结账期，提供增值税专用发票。</p>
          </div>
          <div class="highlight-item">
            <span class="highlight-icon" aria-hidden="true">🔒</span>
            <div class="highlight-title">持证经营</div>
            <p class="highlight-desc">食品经营许可证正规资质，全程合规操作。</p>
          </div>
        </div>

      </div>
    </div>
  </section>
</main>

<!-- Footer -->
<footer class="footer" role="contentinfo">
  <div class="container">
    <div class="footer-inner">
      <div class="footer-brand">佳膳餐饮管理有限公司</div>
      <div class="footer-info">
        <div>订餐热线 <a href="tel:02158372210">021-5837-2210</a></div>
        <div>© 2014–2026 · <a href="#">沪ICP备14037856号-1</a></div>
        <div>食品经营许可证：沪食证字 2014 第 310115 号</div>
      </div>
    </div>
  </div>
</footer>

</body>
</html>
```
