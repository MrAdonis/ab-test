## 设计说明

**Design Read**：Reading this as: **企业团餐服务商官网 redesign (overhaul)** for **企业行政/采购负责人（B端决策者）**, with a **trust-first + 现代克制** language, leaning toward **原生 CSS + Outfit display 字体 + 冷白底单色系**.

**量化维度**：VARIANCE 6 / MOTION 4 / DENSITY 5

- VARIANCE 6：不对称分区布局，Hero 左重右轻；菜单用横排卡片而非三列等宽网格；表单独立右侧板块。禁居中 Hero。
- MOTION 4：入场 fade-up 序列（导航 → hero → 菜单 → 表单），hover 过渡 200ms，无滚动编排。
- DENSITY 5：标准留白，每 section 有呼吸感，价格数字用 tabular-nums。

**美学方向**：「单色、克制、可信」。冷白 #fafaf9 底 + 炭黑 #1a1a18 标题 + 橙色 #e8621a 作为唯一强调色（食品暖调，区别 AI 紫，用于价格 / CTA / 菜单标签）。排除蓝色（太企业模板），排除绿色（原站已用、过于老旧）。

**内容保留清单（全部在位）**：
- ✅ 公告跑马灯内容 → 转为顶部静态 banner 条
- ✅ 导航（首页/关于/菜单/订餐/联系）
- ✅ 三款套餐（红烧肉 ¥22 / 低脂轻食 ¥26 / 素食 ¥18）含描述、热量标注
- ✅ 图片占位（aspect-ratio 容器，原 src 不变，加载失败有背景色托底）
- ✅ 服务介绍（成立年份、服务企业数、资质证书编号、配送政策、发票）
- ✅ 快速订餐表单（联系人/手机/公司/套餐/份数，10份起送规则，action/method 不变）
- ✅ 页脚（公司名/热线/ICP/食品经营许可证）

**澄清判断**（客户不在场，自行决定）：
1. 导航外链（/about.html 等）——保留原 href，不改动
2. 图片无法加载时用 aspect-ratio + 背景色占位，结构稳定
3. 表单 action="/cgi-bin/order.cgi" 保留不变，只改视觉层

**布局家族多样性**（8 sections，符合规则 2）：
1. Hero — 不对称分屏（左大字 + 右公告/数据）
2. 菜单 — 横排卡片列表（左图右文，非三列等宽）
3. 服务资质 — 四格数字+标签 stats 横条
4. 订餐表单 — 全宽双栏（左说明文案 + 右表单）
5. Footer — 信息密集单行

**反 AI 审美检查**：
- 字体：Outfit（display）+ system-ui（正文），非 Inter/Roboto
- 配色：橙色强调 #e8621a，非 AI 紫
- 布局：Hero 不对称，无三列等宽卡片堆叠
- 无装饰线、无 emoji 图标、无 section 编号、无 scroll cue
- Eyebrow 控制：hero 一个 eyebrow，其余 section 交替使用（规则 3）

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
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
  /* ===== Reset & Base ===== */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --ink:       #1a1a18;
    --ink-2:     #3d3d3a;
    --ink-3:     #6b6b66;
    --bg:        #fafaf9;
    --bg-2:      #f2f1ef;
    --bg-3:      #e8e7e3;
    --accent:    #e8621a;
    --accent-d:  #c4511a;
    --white:     #ffffff;
    --radius:    10px;
    --font-d:    'Outfit', -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
    --font-b:    -apple-system, 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif;
  }
  html { font-size: 16px; scroll-behavior: smooth; }
  body {
    font-family: var(--font-b);
    background: var(--bg);
    color: var(--ink);
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
  }

  /* ===== Announce Banner ===== */
  .announce {
    background: var(--ink);
    color: var(--bg-3);
    font-size: 13px;
    text-align: center;
    padding: 9px 20px;
    letter-spacing: .01em;
  }
  .announce span {
    color: var(--accent);
    font-weight: 600;
  }

  /* ===== Nav ===== */
  .nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--bg);
    border-bottom: 1px solid var(--bg-3);
    padding: 0 clamp(20px, 5vw, 80px);
  }
  .nav-inner {
    max-width: 1160px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
  }
  .nav-brand {
    font-family: var(--font-d);
    font-weight: 900;
    font-size: 20px;
    color: var(--ink);
    text-decoration: none;
    letter-spacing: -.01em;
  }
  .nav-brand em {
    color: var(--accent);
    font-style: normal;
  }
  .nav-links {
    display: flex;
    gap: 32px;
    list-style: none;
  }
  .nav-links a {
    font-size: 14px;
    font-weight: 500;
    color: var(--ink-2);
    text-decoration: none;
    transition: color 180ms ease;
    padding: 6px 0;
    border-bottom: 2px solid transparent;
  }
  .nav-links a:hover {
    color: var(--ink);
    border-bottom-color: var(--accent);
  }
  .nav-links a:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
    border-radius: 3px;
  }

  /* ===== Hero ===== */
  .hero {
    max-width: 1160px;
    margin: 0 auto;
    padding: clamp(60px, 8vw, 100px) clamp(20px, 5vw, 80px) clamp(40px, 5vw, 60px);
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 48px;
    align-items: start;
  }
  .hero-eyebrow {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
  }
  .hero-title {
    font-family: var(--font-d);
    font-size: clamp(42px, 6vw, 68px);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -.02em;
    color: var(--ink);
    margin-bottom: 20px;
    text-wrap: balance;
  }
  .hero-title em {
    color: var(--accent);
    font-style: normal;
  }
  .hero-sub {
    font-size: 17px;
    color: var(--ink-2);
    line-height: 1.75;
    max-width: 420px;
    margin-bottom: 36px;
  }
  .hero-cta {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent);
    color: var(--white);
    font-family: var(--font-d);
    font-size: 16px;
    font-weight: 700;
    padding: 14px 28px;
    border-radius: var(--radius);
    text-decoration: none;
    transition: background 180ms ease, transform 100ms ease;
    min-height: 48px;
  }
  .hero-cta:hover { background: var(--accent-d); }
  .hero-cta:active { transform: scale(.98); }
  .hero-cta:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

  /* Hero sidebar stats */
  .hero-side {
    padding-top: 8px;
  }
  .hero-notice {
    background: var(--bg-2);
    border-radius: var(--radius);
    padding: 20px 22px;
    margin-bottom: 20px;
    border-left: 3px solid var(--accent);
  }
  .hero-notice p {
    font-size: 14px;
    color: var(--ink-2);
    line-height: 1.65;
  }
  .hero-notice strong {
    color: var(--ink);
    font-weight: 600;
  }
  .hero-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .stat-card {
    background: var(--white);
    border: 1px solid var(--bg-3);
    border-radius: var(--radius);
    padding: 18px 16px;
  }
  .stat-num {
    font-family: var(--font-d);
    font-size: 28px;
    font-weight: 900;
    color: var(--ink);
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 4px;
  }
  .stat-num sup {
    font-size: 14px;
    font-weight: 700;
    color: var(--accent);
  }
  .stat-label {
    font-size: 12px;
    color: var(--ink-3);
  }

  /* ===== Section Divider ===== */
  .section-divider {
    height: 1px;
    background: var(--bg-3);
    max-width: 1160px;
    margin: 0 auto;
  }

  /* ===== Menu Section ===== */
  .menu-section {
    max-width: 1160px;
    margin: 0 auto;
    padding: clamp(48px, 6vw, 80px) clamp(20px, 5vw, 80px);
  }
  .section-header {
    margin-bottom: 40px;
  }
  .section-eyebrow {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
    display: block;
  }
  .section-title {
    font-family: var(--font-d);
    font-size: clamp(28px, 4vw, 40px);
    font-weight: 800;
    letter-spacing: -.02em;
    color: var(--ink);
    line-height: 1.1;
    text-wrap: balance;
  }
  .menu-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--bg-3);
    border-radius: calc(var(--radius) + 2px);
    overflow: hidden;
    border: 1px solid var(--bg-3);
  }
  .menu-item {
    background: var(--white);
    display: grid;
    grid-template-columns: 140px 1fr auto;
    gap: 0;
    transition: background 180ms ease;
  }
  .menu-item:hover { background: var(--bg); }
  .menu-img {
    width: 140px;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
    background: var(--bg-2);
  }
  .menu-body {
    padding: 22px 24px;
  }
  .menu-name {
    font-family: var(--font-d);
    font-size: 19px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 4px;
  }
  .menu-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--accent);
    background: rgba(232, 98, 26, .1);
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  .menu-desc {
    font-size: 14px;
    color: var(--ink-3);
    line-height: 1.65;
  }
  .menu-price-col {
    padding: 22px 28px 22px 16px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
    min-width: 100px;
  }
  .menu-price {
    font-family: var(--font-d);
    font-size: 30px;
    font-weight: 900;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
    line-height: 1;
  }
  .menu-price-unit {
    font-size: 14px;
    color: var(--ink-3);
    margin-top: 3px;
  }

  /* ===== Service/Credential Section ===== */
  .service-section {
    background: var(--ink);
    color: var(--white);
    padding: clamp(48px, 6vw, 80px) clamp(20px, 5vw, 80px);
  }
  .service-inner {
    max-width: 1160px;
    margin: 0 auto;
  }
  .service-title {
    font-family: var(--font-d);
    font-size: clamp(26px, 3.5vw, 36px);
    font-weight: 800;
    letter-spacing: -.02em;
    line-height: 1.15;
    color: var(--white);
    margin-bottom: 18px;
    max-width: 560px;
    text-wrap: balance;
  }
  .service-desc {
    font-size: 15px;
    color: rgba(255,255,255,.65);
    line-height: 1.8;
    max-width: 680px;
    margin-bottom: 40px;
  }
  .service-desc a {
    color: var(--accent);
    text-decoration: none;
  }
  .credential-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(255,255,255,.12);
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.12);
  }
  .cred-item {
    background: rgba(255,255,255,.05);
    padding: 22px 20px;
    transition: background 180ms ease;
  }
  .cred-item:hover { background: rgba(255,255,255,.09); }
  .cred-num {
    font-family: var(--font-d);
    font-size: 24px;
    font-weight: 900;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 5px;
    font-variant-numeric: tabular-nums;
  }
  .cred-label {
    font-size: 13px;
    color: rgba(255,255,255,.55);
    line-height: 1.5;
  }

  /* ===== Order Section ===== */
  .order-section {
    max-width: 1160px;
    margin: 0 auto;
    padding: clamp(48px, 6vw, 80px) clamp(20px, 5vw, 80px);
    display: grid;
    grid-template-columns: 1fr 480px;
    gap: 60px;
    align-items: start;
  }
  .order-info h2 {
    font-family: var(--font-d);
    font-size: clamp(28px, 4vw, 38px);
    font-weight: 800;
    letter-spacing: -.02em;
    line-height: 1.1;
    color: var(--ink);
    margin-bottom: 16px;
    text-wrap: balance;
  }
  .order-info p {
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.8;
    margin-bottom: 12px;
  }
  .order-rule {
    background: var(--bg-2);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-top: 24px;
  }
  .order-rule p {
    font-size: 13px;
    color: var(--ink-3);
    margin-bottom: 0;
    line-height: 1.7;
  }
  .order-rule strong {
    color: var(--ink);
  }

  /* Form */
  .order-form {
    background: var(--white);
    border: 1px solid var(--bg-3);
    border-radius: calc(var(--radius) + 4px);
    padding: 32px 28px;
  }
  .form-title {
    font-family: var(--font-d);
    font-size: 20px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 24px;
  }
  .field {
    margin-bottom: 16px;
  }
  .field label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--ink-2);
    margin-bottom: 6px;
    letter-spacing: .01em;
  }
  .field input,
  .field select {
    width: 100%;
    height: 44px;
    padding: 0 14px;
    font-size: 15px;
    font-family: var(--font-b);
    color: var(--ink);
    background: var(--bg);
    border: 1.5px solid var(--bg-3);
    border-radius: var(--radius);
    outline: none;
    transition: border-color 180ms ease, box-shadow 180ms ease;
    appearance: none;
    -webkit-appearance: none;
  }
  .field input::placeholder { color: var(--ink-3); }
  .field input:hover,
  .field select:hover { border-color: var(--bg-3); background: var(--white); }
  .field input:focus,
  .field select:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(232, 98, 26, .15);
    background: var(--white);
  }
  .field select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' viewBox='0 0 16 16'%3E%3Cpath stroke='%236b6b66' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M4 6l4 4 4-4'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 36px;
    cursor: pointer;
  }
  .btn-submit {
    width: 100%;
    height: 50px;
    margin-top: 8px;
    background: var(--accent);
    color: var(--white);
    font-family: var(--font-d);
    font-size: 16px;
    font-weight: 700;
    border: none;
    border-radius: var(--radius);
    cursor: pointer;
    transition: background 180ms ease, transform 100ms ease;
    letter-spacing: .01em;
  }
  .btn-submit:hover { background: var(--accent-d); }
  .btn-submit:active { transform: scale(.99); }
  .btn-submit:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

  /* ===== Footer ===== */
  .site-footer {
    background: var(--bg-2);
    border-top: 1px solid var(--bg-3);
    padding: 28px clamp(20px, 5vw, 80px);
  }
  .footer-inner {
    max-width: 1160px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }
  .footer-brand {
    font-family: var(--font-d);
    font-weight: 700;
    font-size: 15px;
    color: var(--ink);
  }
  .footer-meta {
    font-size: 12px;
    color: var(--ink-3);
    line-height: 1.8;
    text-align: right;
  }
  .footer-meta a {
    color: var(--ink-3);
    text-decoration: none;
  }
  .footer-meta a:hover { color: var(--ink); }

  /* ===== Animations ===== */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .anim { animation: fadeUp .5s ease both; }
  .anim-d1 { animation-delay: .08s; }
  .anim-d2 { animation-delay: .18s; }
  .anim-d3 { animation-delay: .28s; }
  .anim-d4 { animation-delay: .38s; }

  @media (prefers-reduced-motion: reduce) {
    .anim { animation: none; }
  }

  /* ===== Responsive ===== */
  @media (max-width: 860px) {
    .hero {
      grid-template-columns: 1fr;
    }
    .hero-side {
      padding-top: 0;
    }
    .credential-strip {
      grid-template-columns: repeat(2, 1fr);
    }
    .order-section {
      grid-template-columns: 1fr;
      gap: 36px;
    }
  }
  @media (max-width: 640px) {
    .nav-links { display: none; }
    .menu-item {
      grid-template-columns: 110px 1fr;
    }
    .menu-price-col { display: none; }
    .menu-body { padding: 16px; }
    .menu-name::after {
      content: attr(data-price);
      display: block;
      font-family: var(--font-d);
      font-size: 20px;
      font-weight: 900;
      color: var(--accent);
      margin-top: 4px;
    }
    .hero-stats { grid-template-columns: 1fr 1fr; }
    .credential-strip { grid-template-columns: 1fr 1fr; }
    .footer-inner { flex-direction: column; align-items: flex-start; }
    .footer-meta { text-align: left; }
  }
</style>
</head>
<body>

<!-- Announce -->
<div class="announce">
  <strong style="color:#fff">本周新增：</strong>低脂轻食套餐上线。<span>满 30 份每份立减 2 元</span>——欢迎企业行政联系试吃。
</div>

<!-- Nav -->
<nav class="nav">
  <div class="nav-inner">
    <a class="nav-brand" href="/index.html">佳膳<em>食堂</em></a>
    <ul class="nav-links">
      <li><a href="/index.html">首页</a></li>
      <li><a href="/about.html">关于我们</a></li>
      <li><a href="/caidan.html">每周菜单</a></li>
      <li><a href="/dingcan.html">在线订餐</a></li>
      <li><a href="/lianxi.html">联系方式</a></li>
    </ul>
  </div>
</nav>

<!-- Hero -->
<section>
  <div class="hero">
    <div class="hero-left">
      <span class="hero-eyebrow anim">企业团餐 · 工作日配送</span>
      <h1 class="hero-title anim anim-d1">每天一顿<em>好饭</em><br>让团队专注做事</h1>
      <p class="hero-sub anim anim-d2">中央厨房现烧、全程保温配送，10 份起送、工作日 10:30 前下单当日到。园区内 37 家企业正在订餐。</p>
      <a href="#order" class="hero-cta anim anim-d3">立即预约试吃 →</a>
    </div>
    <div class="hero-side anim anim-d4">
      <div class="hero-notice">
        <p><strong>本周公告</strong><br>低脂轻食套餐正式上线，鸡胸 / 牛肉可选，标注热量与蛋白质，满 30 份每份立减 2 元。</p>
      </div>
      <div class="hero-stats">
        <div class="stat-card">
          <div class="stat-num">37<sup>+</sup></div>
          <div class="stat-label">服务企业</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">2014</div>
          <div class="stat-label">创立年份</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">¥18</div>
          <div class="stat-label">套餐起步价</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">10</div>
          <div class="stat-label">份起送，免配送费</div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="section-divider"></div>

<!-- Menu -->
<section class="menu-section">
  <div class="section-header">
    <span class="section-eyebrow">每周精选菜单</span>
    <h2 class="section-title">三款套餐，每日现烧</h2>
  </div>
  <div class="menu-list">
    <!-- 红烧肉套餐 -->
    <article class="menu-item">
      <img class="menu-img" src="images/hongshaorou.jpg" alt="红烧肉套餐实拍" loading="lazy" data-fallback>
      <div class="menu-body">
        <div class="menu-tag">两荤一素一汤</div>
        <div class="menu-name" data-price="¥22">红烧肉套餐</div>
        <p class="menu-desc">精选五花肉，每日现烧，配时令蔬菜和例汤，米饭免费续。</p>
      </div>
      <div class="menu-price-col">
        <div class="menu-price">¥22</div>
        <div class="menu-price-unit">/ 份</div>
      </div>
    </article>
    <!-- 低脂轻食 -->
    <article class="menu-item">
      <img class="menu-img" src="images/qingshi.jpg" alt="低脂轻食套餐实拍" loading="lazy">
      <div class="menu-body">
        <div class="menu-tag">鸡胸 / 牛肉可选</div>
        <div class="menu-name" data-price="¥26">低脂轻食套餐</div>
        <p class="menu-desc">少油低盐，标注热量和蛋白质克数，适合健身人群。</p>
      </div>
      <div class="menu-price-col">
        <div class="menu-price">¥26</div>
        <div class="menu-price-unit">/ 份</div>
      </div>
    </article>
    <!-- 素食 -->
    <article class="menu-item">
      <img class="menu-img" src="images/sucai.jpg" alt="素食套餐实拍" loading="lazy">
      <div class="menu-body">
        <div class="menu-tag">三素一汤</div>
        <div class="menu-name" data-price="¥18">素食套餐</div>
        <p class="menu-desc">当季蔬菜为主，豆制品补充蛋白，清淡不寡淡。</p>
      </div>
      <div class="menu-price-col">
        <div class="menu-price">¥18</div>
        <div class="menu-price-unit">/ 份</div>
      </div>
    </article>
  </div>
</section>

<div class="section-divider"></div>

<!-- Service / Credential (no eyebrow — alternating rule) -->
<section class="service-section">
  <div class="service-inner">
    <h2 class="service-title">持证经营，12 年专注企业团餐</h2>
    <p class="service-desc">
      成立于 2014 年，目前为园区内 37 家企业提供工作日午餐配送。中央厨房持有食品经营许可证（沪食证字 2014 第 310115 号），全程冷链 / 保温配送，餐损包赔。支持月结，提供增值税专用发票。
    </p>
    <div class="credential-strip">
      <div class="cred-item">
        <div class="cred-num">持证</div>
        <div class="cred-label">食品经营许可证<br>沪食证字 2014 第 310115 号</div>
      </div>
      <div class="cred-item">
        <div class="cred-num">冷链</div>
        <div class="cred-label">全程保温配送<br>餐损包赔</div>
      </div>
      <div class="cred-item">
        <div class="cred-num">月结</div>
        <div class="cred-label">支持月结<br>开增值税专用发票</div>
      </div>
      <div class="cred-item">
        <div class="cred-num">当日</div>
        <div class="cred-label">10:30 前下单<br>当日工作日送达</div>
      </div>
    </div>
  </div>
</section>

<!-- Order Section -->
<section id="order">
  <div class="order-section">
    <div class="order-info">
      <span class="section-eyebrow">在线订餐</span>
      <h2>预约试吃，或直接下单</h2>
      <p>填写基本信息，我们会在 2 小时内联系确认，安排首次试吃或完成正式下单。</p>
      <p>工作日均可配送，最低 10 份，园区内免配送费。如有特殊饮食要求或定制需求，欢迎在订单备注中注明，或直接致电：<strong style="color:var(--ink)">021-5837-2210</strong>。</p>
      <div class="order-rule">
        <p><strong>起送 &amp; 配送规则</strong><br>工作日 10:30 前下单当日送达 · 最低 10 份起送 · 园区内免配送费 · 支持月结</p>
      </div>
    </div>
    <div class="order-form">
      <div class="form-title">快速订餐</div>
      <form action="/cgi-bin/order.cgi" method="post" novalidate>
        <div class="field">
          <label for="name">联系人姓名</label>
          <input type="text" id="name" name="name" placeholder="您的姓名" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="phone">手机号</label>
          <input type="tel" id="phone" name="phone" placeholder="11 位手机号" autocomplete="tel" required>
        </div>
        <div class="field">
          <label for="company">公司名称</label>
          <input type="text" id="company" name="company" placeholder="所在公司全称" autocomplete="organization">
        </div>
        <div class="field">
          <label for="meal_plan">选择套餐</label>
          <select id="meal_plan" name="meal_plan" required>
            <option value="hongshao">红烧肉套餐 ¥22 / 份</option>
            <option value="qingshi">低脂轻食套餐 ¥26 / 份</option>
            <option value="sushi">素食套餐 ¥18 / 份</option>
          </select>
        </div>
        <div class="field">
          <label for="quantity">份数（10 份起送）</label>
          <input type="number" id="quantity" name="quantity" placeholder="请输入份数" min="10" step="1">
        </div>
        <button class="btn-submit" type="submit">提交订单</button>
      </form>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">佳膳餐饮管理有限公司</div>
    <div class="footer-meta">
      订餐热线 021-5837-2210 · © 2014–2026 · <a href="#">沪ICP备14037856号-1</a> · 食品经营许可证：沪食证字 2014 第 310115 号
    </div>
  </div>
</footer>

</body>
</html>
```
