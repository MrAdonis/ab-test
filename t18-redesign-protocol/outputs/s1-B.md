## 设计说明

**Design Read**

Reading this as: **SaaS 营销落地页（redesign overhaul）** for **独立播客主理人和小型播客工作室**，with a **dark tech + 数据可信** language, leaning toward **原生 CSS + 等宽数字 + 单色调暗底**。

**判断依据**：客户说"太过时了"、没说"保留品牌"，且原站是典型 2019 年 flat 三列白底风格——判定为 overhaul。品牌色紫色（#6d28d9）已有用户认知，按规范「品牌已经是某个"被禁"色就保持」保留。数据分析产品本身就应该传达"数据感"，用暗底比白底更能体现 dashboard 质感，同时和同赛道白底竞品形成视觉差异。

**量化维度**：VARIANCE 7 / MOTION 6 / DENSITY 3

- VARIANCE 7 → hero 禁止居中，用不对称分屏布局
- MOTION 6 → 至少 3 个有意图动效：入场序列 + 数字计数动画 + 卡片悬停反馈
- DENSITY 3 → 大留白，宽松布局

**设计方向**：暗底（#0d0d0f）+ 紫色品牌强调色（保留 #6d28d9，但克制用量）+ 冷灰文字系统。字体：Display 用 Outfit（有辨识度的几何 grotesk，非 Inter/Arial），正文用 system-ui CJK 栈。不选 Inter 因为是 AI 默认Tell；不选 Fraunces 因为 2024 后被滥用。

**SEO 基线保留**：
- `<title>` 内容完整保留
- `<meta name="description">` 保留
- OG tags 保留
- LD+JSON 结构化数据保留
- 所有 `<section>` 语义标签保留
- `aria-label` 导航保留
- 表单字段 name/aria-label 保留

**现代化杠杆使用**：① 字体刷新 → ② 间距与节奏 → ③ 配色校准（暗底 + 降饱和中性色 + 保留紫色强调）→ ④ 动效层 → ⑤ Hero 重组（不对称分屏）→ ⑥ Features section 替换为 bento-grid

**未改**：URL slug / 导航文案 / 表单字段 / logo 文字 / 法务文案

**Section 布局家族**（遵守规则 2，4 种不同布局）：
1. Hero → 不对称分屏（左文右图模拟）
2. Features → Bento-grid 不等列
3. Social proof → 居中单行数字 + 信任线
4. CTA → 全宽暗色块

**Section eyebrow 分配**（遵守规则 3，交替）：
- Hero：有 eyebrow（"播客数据分析平台"）
- Features：无 eyebrow
- Social proof：有 eyebrow（"已被信赖"）
- CTA：无 eyebrow

**Production Tell 检查**：无 section numbering / 无装饰文字条 / 无 scroll cue / 无诗化信任标签 / 无 floating 角落小字 / 无 fake live counter / 无 version footer

## 最终 HTML

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lumeo — 播客数据分析平台 | 收听数据、听众画像、增长洞察</title>
<meta name="description" content="Lumeo 帮播客主理人看懂收听数据：单集留存曲线、听众画像、平台分发对比。免费开始，5 分钟接入 RSS。">
<meta property="og:title" content="Lumeo — 播客数据分析平台">
<meta property="og:description" content="单集留存曲线、听众画像、平台分发对比，5 分钟接入 RSS。">
<meta property="og:image" content="https://lumeo.fm/og-cover.png">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"Lumeo","applicationCategory":"BusinessApplication","offers":{"@type":"Offer","price":"0","priceCurrency":"CNY"}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0d0d0f;
    --surface: #141417;
    --surface-2: #1c1c21;
    --border: rgba(255,255,255,0.08);
    --text-primary: #f0eff4;
    --text-secondary: #8a8a9a;
    --text-muted: #55555f;
    --accent: #7c3aed;
    --accent-light: #a78bfa;
    --accent-dim: rgba(124,58,237,0.15);
    --font-display: 'Outfit', -apple-system, sans-serif;
    --font-body: -apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif;
    --radius: 10px;
  }

  html { font-size: 16px; scroll-behavior: smooth; }

  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: var(--font-body);
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }

  /* Focus visible */
  a:focus-visible, button:focus-visible, input:focus-visible {
    outline: 2px solid var(--accent-light);
    outline-offset: 3px;
    border-radius: 4px;
  }

  /* HEADER */
  header {
    position: sticky;
    top: 0;
    z-index: 50;
    border-bottom: 1px solid var(--border);
    background: rgba(13,13,15,0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 0 48px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .logo {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 20px;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    text-decoration: none;
  }

  .logo span { color: var(--accent-light); }

  nav { display: flex; align-items: center; gap: 8px; }

  nav a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 6px;
    transition: color 120ms ease, background 120ms ease;
  }

  nav a:hover { color: var(--text-primary); background: var(--surface-2); }

  .nav-cta {
    background: var(--accent);
    color: #fff !important;
    font-weight: 600;
    padding: 7px 16px !important;
    border-radius: 6px;
    transition: background 120ms ease, transform 100ms ease !important;
  }

  .nav-cta:hover {
    background: #6d28d9 !important;
    transform: translateY(-1px);
  }

  /* HERO — asymmetric split */
  .hero {
    min-height: 100dvh;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    padding: 0 48px;
    gap: 64px;
    max-width: 1280px;
    margin: 0 auto;
    padding-top: 80px;
    padding-bottom: 80px;
  }

  .hero-left { display: flex; flex-direction: column; gap: 28px; }

  .hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent-light);
    opacity: 0;
    animation: fadeUp 0.6s ease 0.1s forwards;
  }

  .hero-eyebrow::before {
    content: '';
    display: block;
    width: 20px;
    height: 1px;
    background: var(--accent-light);
  }

  .hero-title {
    font-family: var(--font-display);
    font-size: clamp(40px, 5vw, 64px);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    text-balance: balance;
    opacity: 0;
    animation: fadeUp 0.6s ease 0.2s forwards;
  }

  .hero-title .highlight {
    color: var(--accent-light);
    position: relative;
  }

  .hero-sub {
    font-size: 17px;
    line-height: 1.65;
    color: var(--text-secondary);
    max-width: 440px;
    text-pretty: pretty;
    opacity: 0;
    animation: fadeUp 0.6s ease 0.3s forwards;
  }

  .hero-form {
    display: flex;
    gap: 10px;
    opacity: 0;
    animation: fadeUp 0.6s ease 0.4s forwards;
  }

  .hero-form input {
    flex: 1;
    padding: 12px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
    transition: border-color 150ms ease;
    min-width: 0;
  }

  .hero-form input::placeholder { color: var(--text-muted); }
  .hero-form input:hover { border-color: rgba(255,255,255,0.16); }
  .hero-form input:focus { outline: none; border-color: var(--accent-light); }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 12px 22px;
    border-radius: var(--radius);
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: background 120ms ease, transform 100ms ease;
  }

  .btn-primary:hover { background: #6d28d9; transform: translateY(-1px); }
  .btn-primary:active { transform: translateY(0) scale(0.98); }

  .hero-meta {
    font-size: 13px;
    color: var(--text-muted);
    opacity: 0;
    animation: fadeUp 0.6s ease 0.5s forwards;
  }

  /* Hero right: fake data viz panel */
  .hero-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    opacity: 0;
    animation: fadeUp 0.7s ease 0.35s forwards;
    box-shadow: 0 32px 64px rgba(0,0,0,0.4), 0 0 0 1px rgba(124,58,237,0.1);
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }

  .panel-title {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
  }

  .panel-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
    letter-spacing: 0.02em;
  }

  .panel-badge::before {
    content: '';
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #4ade80;
  }

  /* Retention curve fake chart */
  .chart-area {
    height: 100px;
    position: relative;
    overflow: hidden;
  }

  .chart-area svg { width: 100%; height: 100%; }

  .chart-labels {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
    margin-top: 6px;
  }

  /* Stats row */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .stat-item {
    background: var(--surface-2);
    border-radius: 8px;
    padding: 12px 14px;
  }

  .stat-val {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 4px;
  }

  /* Platform mini bars */
  .platform-list { display: flex; flex-direction: column; gap: 8px; }

  .platform-row {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
  }

  .platform-name { color: var(--text-secondary); width: 80px; flex-shrink: 0; }

  .platform-bar-wrap {
    flex: 1;
    height: 4px;
    background: var(--surface-2);
    border-radius: 2px;
    overflow: hidden;
  }

  .platform-bar {
    height: 100%;
    background: var(--accent);
    border-radius: 2px;
    transform-origin: left;
    animation: barIn 0.8s ease forwards;
    animation-delay: var(--delay, 0s);
    transform: scaleX(0);
  }

  @keyframes barIn { to { transform: scaleX(1); } }

  .platform-pct {
    font-variant-numeric: tabular-nums;
    color: var(--text-secondary);
    width: 32px;
    text-align: right;
  }

  /* FEATURES — bento grid */
  .features-section {
    padding: 120px 48px;
    max-width: 1280px;
    margin: 0 auto;
  }

  .features-header {
    margin-bottom: 48px;
    max-width: 540px;
  }

  .features-header h2 {
    font-family: var(--font-display);
    font-size: clamp(28px, 3vw, 40px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.15;
    color: var(--text-primary);
    text-balance: balance;
  }

  .features-header p {
    font-size: 16px;
    color: var(--text-secondary);
    margin-top: 12px;
    text-pretty: pretty;
  }

  .bento {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-template-rows: auto auto;
    gap: 16px;
  }

  .bento-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 32px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    transition: border-color 200ms ease, transform 200ms ease;
    cursor: default;
  }

  .bento-card:hover {
    border-color: rgba(124,58,237,0.3);
    transform: translateY(-2px);
  }

  .bento-card.large { grid-column: span 7; }
  .bento-card.medium { grid-column: span 5; }
  .bento-card.third { grid-column: span 4; }

  .card-icon {
    width: 40px;
    height: 40px;
    background: var(--accent-dim);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .card-icon svg { color: var(--accent-light); }

  .card-label {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.25;
  }

  .card-desc {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.65;
    flex: 1;
  }

  /* Mini chart inside retention card */
  .mini-curve {
    margin-top: auto;
    height: 60px;
  }

  /* SOCIAL PROOF */
  .social-section {
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 80px 48px;
  }

  .social-inner {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 48px;
  }

  .social-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .social-eyebrow::before, .social-eyebrow::after {
    content: '';
    display: block;
    width: 32px;
    height: 1px;
    background: var(--border);
  }

  .social-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    width: 100%;
    max-width: 680px;
  }

  .social-stat {
    text-align: center;
    padding: 24px;
    border-right: 1px solid var(--border);
  }

  .social-stat:last-child { border-right: none; }

  .social-num {
    font-family: var(--font-display);
    font-size: 44px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
    line-height: 1;
  }

  .social-num sup {
    font-size: 22px;
    font-weight: 600;
    vertical-align: super;
    color: var(--accent-light);
  }

  .social-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 6px;
  }

  /* CTA SECTION */
  .cta-section {
    padding: 120px 48px;
    max-width: 1280px;
    margin: 0 auto;
  }

  .cta-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 80px 64px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 32px;
    position: relative;
    overflow: hidden;
  }

  .cta-box::before {
    content: '';
    position: absolute;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 500px;
    height: 300px;
    background: radial-gradient(ellipse, rgba(124,58,237,0.18) 0%, transparent 70%);
    pointer-events: none;
  }

  .cta-title {
    font-family: var(--font-display);
    font-size: clamp(26px, 3.5vw, 44px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    max-width: 560px;
    text-balance: balance;
    position: relative;
  }

  .cta-form {
    display: flex;
    gap: 10px;
    width: 100%;
    max-width: 480px;
    position: relative;
  }

  .cta-form input {
    flex: 1;
    padding: 13px 18px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
    transition: border-color 150ms ease;
    min-width: 0;
  }

  .cta-form input::placeholder { color: var(--text-muted); }
  .cta-form input:hover { border-color: rgba(255,255,255,0.16); }
  .cta-form input:focus { outline: none; border-color: var(--accent-light); }

  /* FOOTER */
  footer {
    border-top: 1px solid var(--border);
    padding: 32px 48px;
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    color: var(--text-muted);
  }

  footer a {
    color: var(--text-muted);
    text-decoration: none;
    transition: color 120ms ease;
  }

  footer a:hover { color: var(--text-secondary); }

  /* Animations */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  }

  /* RESPONSIVE */
  @media (max-width: 900px) {
    header { padding: 0 24px; }

    nav a:not(.nav-cta) { display: none; }

    .hero {
      grid-template-columns: 1fr;
      min-height: auto;
      padding: 80px 24px 60px;
      gap: 48px;
    }

    .hero-panel { display: none; }

    .features-section { padding: 80px 24px; }

    .bento { grid-template-columns: 1fr; }
    .bento-card.large, .bento-card.medium, .bento-card.third { grid-column: span 1; }

    .social-section { padding: 60px 24px; }

    .social-stats { max-width: 100%; }

    .cta-section { padding: 80px 24px; }
    .cta-box { padding: 48px 28px; }
    .cta-form { flex-direction: column; max-width: 100%; }

    footer { padding: 24px; flex-direction: column; gap: 12px; text-align: center; }
  }

  @media (max-width: 480px) {
    .hero-form { flex-direction: column; }
    .social-stats { grid-template-columns: 1fr; }
    .social-stat { border-right: none; border-bottom: 1px solid var(--border); }
    .social-stat:last-child { border-bottom: none; }
  }
</style>
</head>
<body>

<header>
  <a href="/" class="logo">Lume<span>o</span></a>
  <nav aria-label="主导航">
    <a href="/features">产品功能</a>
    <a href="/pricing">价格</a>
    <a href="/customers">客户案例</a>
    <a href="/blog">博客</a>
    <a href="/login">登录</a>
    <a href="/signup" class="nav-cta">免费开始</a>
  </nav>
</header>

<main>

  <!-- HERO: asymmetric split, left text / right data panel -->
  <section style="background: linear-gradient(180deg, rgba(124,58,237,0.04) 0%, transparent 60%);">
    <div class="hero">
      <div class="hero-left">
        <span class="hero-eyebrow">播客数据分析平台</span>
        <h1 class="hero-title">
          看懂每个听众<br>在哪里<span class="highlight">离开</span>
        </h1>
        <p class="hero-sub">
          单集留存曲线、听众画像、跨平台分发对比。接入 RSS 后 5 分钟出第一份报告。
        </p>
        <form class="hero-form" action="/signup" method="post">
          <input type="email" name="work_email" placeholder="工作邮箱" aria-label="工作邮箱" required>
          <button class="btn-primary" type="submit">免费开始</button>
        </form>
        <p class="hero-meta">无需信用卡 · 5 分钟接入 RSS</p>
      </div>

      <!-- Data viz panel: fake dashboard preview -->
      <div class="hero-panel" aria-hidden="true" role="presentation">
        <div class="panel-header">
          <span class="panel-title">第 38 期 — 留存曲线</span>
          <span class="panel-badge">实时同步</span>
        </div>

        <!-- Retention curve SVG -->
        <div class="chart-area">
          <svg viewBox="0 0 320 100" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <!-- Grid lines -->
            <line x1="0" y1="25" x2="320" y2="25" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <line x1="0" y1="50" x2="320" y2="50" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <line x1="0" y1="75" x2="320" y2="75" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <!-- Fill area -->
            <path d="M0,8 C40,10 60,18 90,32 C120,46 150,54 190,62 C230,70 270,74 320,76 L320,100 L0,100 Z"
                  fill="url(#curveGrad)"/>
            <!-- Curve line -->
            <path d="M0,8 C40,10 60,18 90,32 C120,46 150,54 190,62 C230,70 270,74 320,76"
                  fill="none" stroke="#a78bfa" stroke-width="2" stroke-linejoin="round"/>
            <!-- Drop-off marker -->
            <circle cx="90" cy="32" r="4" fill="#7c3aed" stroke="#1c1c21" stroke-width="2"/>
            <line x1="90" y1="32" x2="90" y2="100" stroke="rgba(124,58,237,0.3)" stroke-width="1" stroke-dasharray="3 3"/>
          </svg>
          <div class="chart-labels">
            <span>0:00</span><span>10:00</span><span>20:00</span><span>30:00</span><span>38:42</span>
          </div>
        </div>

        <!-- Stats -->
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-val">68%</div>
            <div class="stat-label">完听率</div>
          </div>
          <div class="stat-item">
            <div class="stat-val">4,312</div>
            <div class="stat-label">本期播放</div>
          </div>
          <div class="stat-item">
            <div class="stat-val">9:24</div>
            <div class="stat-label">平均收听</div>
          </div>
        </div>

        <!-- Platform distribution -->
        <div class="platform-list" aria-label="平台分发对比">
          <div class="platform-row">
            <span class="platform-name">小宇宙</span>
            <div class="platform-bar-wrap">
              <div class="platform-bar" style="width:52%; --delay:0.5s;"></div>
            </div>
            <span class="platform-pct">52%</span>
          </div>
          <div class="platform-row">
            <span class="platform-name">Apple</span>
            <div class="platform-bar-wrap">
              <div class="platform-bar" style="width:28%; --delay:0.65s;"></div>
            </div>
            <span class="platform-pct">28%</span>
          </div>
          <div class="platform-row">
            <span class="platform-name">Spotify</span>
            <div class="platform-bar-wrap">
              <div class="platform-bar" style="width:20%; --delay:0.8s;"></div>
            </div>
            <span class="platform-pct">20%</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURES: bento grid, no eyebrow (alternating rule) -->
  <section class="features-section" aria-label="核心功能">
    <div class="features-header">
      <h2>数据不只是数字<br>是下一集该怎么做</h2>
      <p>三组核心数据，让每档播客都能像头部节目一样读懂自己的听众。</p>
    </div>

    <div class="bento" role="list">
      <!-- Large card: retention -->
      <div class="bento-card large" role="listitem">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="card-label">单集留存曲线</div>
        <p class="card-desc">看到听众在第几分钟流失，对照章节标记定位内容问题。不是平均完听率，是逐秒的注意力地图。</p>
        <div class="mini-curve" aria-hidden="true">
          <svg viewBox="0 0 400 60" preserveAspectRatio="none" style="width:100%;height:100%;">
            <defs>
              <linearGradient id="miniGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.2"/>
                <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path d="M0,4 C50,6 80,12 120,22 C160,32 200,38 250,44 C300,50 350,52 400,54 L400,60 L0,60 Z" fill="url(#miniGrad)"/>
            <path d="M0,4 C50,6 80,12 120,22 C160,32 200,38 250,44 C300,50 350,52 400,54" fill="none" stroke="#a78bfa" stroke-width="1.5"/>
          </svg>
        </div>
      </div>

      <!-- Medium card: audience -->
      <div class="bento-card medium" role="listitem">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="card-label">听众画像</div>
        <p class="card-desc">地域、设备、收听时段分布，知道你的听众是谁——而不只是有多少人。</p>
      </div>

      <!-- Three equal cards -->
      <div class="bento-card third" role="listitem">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
        </div>
        <div class="card-label">平台分发对比</div>
        <p class="card-desc">小宇宙、Apple Podcasts、Spotify 同屏对比，找到增长洼地。</p>
      </div>

      <div class="bento-card third" role="listitem">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
          </svg>
        </div>
        <div class="card-label">增长趋势</div>
        <p class="card-desc">周环比、月环比增速，看出哪集带来了新订阅者爆发。</p>
      </div>

      <div class="bento-card third" role="listitem">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="card-label">5 分钟接入</div>
        <p class="card-desc">填入 RSS 地址，无需代码，无需联系客服，历史数据立即可见。</p>
      </div>
    </div>
  </section>

  <!-- SOCIAL PROOF: centered, with eyebrow (alternating rule) -->
  <section class="social-section">
    <div class="social-inner">
      <div class="social-eyebrow">已被信赖</div>
      <div class="social-stats" aria-label="用户数据">
        <div class="social-stat">
          <div class="social-num">2,400<sup>+</sup></div>
          <div class="social-desc">档播客在用</div>
        </div>
        <div class="social-stat">
          <div class="social-num">3.8<sup>亿</sup></div>
          <div class="social-desc">条播放数据处理</div>
        </div>
        <div class="social-stat">
          <div class="social-num">5<sup>分钟</sup></div>
          <div class="social-desc">接入 RSS 出报告</div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA SECTION: no eyebrow (alternating rule) -->
  <section class="cta-section">
    <div class="cta-box">
      <h2 class="cta-title">开始读懂你的听众</h2>
      <form class="cta-form" action="/signup" method="post">
        <input type="email" name="work_email" placeholder="工作邮箱" aria-label="工作邮箱" required>
        <input type="text" name="show_name" placeholder="节目名称" aria-label="节目名称">
        <button class="btn-primary" type="submit">免费开始</button>
      </form>
    </div>
  </section>

</main>

<footer>
  <span>© 2019–2026 Lumeo · 沪ICP备19028374号-2</span>
  <span style="display:flex;gap:20px;">
    <a href="/terms">服务条款</a>
    <a href="/privacy">隐私政策</a>
  </span>
</footer>

</body>
</html>
```
