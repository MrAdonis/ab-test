```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>墨记 — 写下，就不会忘</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500&display=swap');

  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :root {
    --ink: #1a1410;
    --ink-light: #3d342c;
    --ink-muted: #7a6e65;
    --paper: #f5f0e8;
    --paper-warm: #ede6d8;
    --paper-dark: #e0d8c8;
    --accent: #c0392b;
    --accent-muted: #e74c3c;
    --white: #fdfaf5;
  }

  html {
    font-size: 16px;
    scroll-behavior: smooth;
  }

  body {
    background-color: var(--paper);
    color: var(--ink);
    font-family: 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
    line-height: 1.7;
    overflow-x: hidden;
  }

  /* 噪点纹理层 */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 999;
    opacity: 0.04;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 200px 200px;
  }

  /* ─── NAV ─── */
  nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    padding: 20px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(12px);
    background: rgba(245, 240, 232, 0.85);
    border-bottom: 1px solid rgba(26, 20, 16, 0.08);
  }

  .nav-brand {
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
    text-decoration: none;
  }

  .nav-brand span {
    color: var(--accent);
  }

  .nav-links {
    display: flex;
    gap: 36px;
    list-style: none;
  }

  .nav-links a {
    font-size: 14px;
    color: var(--ink-muted);
    text-decoration: none;
    transition: color 0.2s ease;
  }

  .nav-links a:hover {
    color: var(--ink);
  }

  .nav-cta {
    font-size: 14px;
    font-weight: 500;
    color: var(--white);
    background: var(--ink);
    padding: 10px 24px;
    border-radius: 2px;
    text-decoration: none;
    transition: background 0.2s ease, transform 0.1s ease;
  }

  .nav-cta:hover {
    background: var(--ink-light);
    transform: translateY(-1px);
  }

  .nav-cta:active {
    transform: translateY(0) scale(0.98);
  }

  /* ─── HERO ─── */
  .hero {
    min-height: 100dvh;
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding-top: 80px;
    overflow: hidden;
  }

  .hero-left {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 64px 80px 80px;
    position: relative;
  }

  .hero-eyebrow {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 28px;
    opacity: 0;
    animation: fadeUp 0.6s ease 0.1s forwards;
  }

  .hero-title {
    font-family: 'Noto Serif SC', 'Songti SC', serif;
    font-size: clamp(48px, 5.5vw, 80px);
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.01em;
    color: var(--ink);
    margin-bottom: 32px;
    opacity: 0;
    animation: fadeUp 0.7s ease 0.2s forwards;
  }

  .hero-title em {
    font-style: normal;
    color: var(--accent);
  }

  .hero-desc {
    font-size: 17px;
    line-height: 1.75;
    color: var(--ink-light);
    max-width: 420px;
    margin-bottom: 48px;
    opacity: 0;
    animation: fadeUp 0.7s ease 0.35s forwards;
  }

  .hero-actions {
    display: flex;
    align-items: center;
    gap: 20px;
    opacity: 0;
    animation: fadeUp 0.7s ease 0.5s forwards;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 500;
    color: var(--white);
    background: var(--ink);
    padding: 14px 32px;
    border-radius: 2px;
    text-decoration: none;
    transition: background 0.2s ease, transform 0.12s ease, box-shadow 0.2s ease;
  }

  .btn-primary:hover {
    background: var(--ink-light);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(26, 20, 16, 0.2);
  }

  .btn-primary:active {
    transform: translateY(0) scale(0.98);
    box-shadow: none;
  }

  .btn-primary:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
  }

  .btn-secondary {
    font-size: 14px;
    color: var(--ink-muted);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    padding-bottom: 2px;
    transition: color 0.2s, border-color 0.2s;
  }

  .btn-secondary:hover {
    color: var(--ink);
    border-color: var(--ink);
  }

  .btn-secondary:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
    border-radius: 2px;
  }

  /* 墨水装饰线 */
  .hero-left::before {
    content: '';
    position: absolute;
    left: 0;
    top: 25%;
    bottom: 25%;
    width: 2px;
    background: linear-gradient(to bottom, transparent, var(--ink-muted), transparent);
    opacity: 0.15;
  }

  .hero-right {
    position: relative;
    background: var(--paper-dark);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  /* 模拟笔记本界面 */
  .hero-mockup {
    width: 320px;
    background: var(--white);
    border-radius: 4px;
    box-shadow:
      0 4px 6px rgba(26,20,16,0.06),
      0 24px 64px rgba(26,20,16,0.14),
      8px 8px 0 var(--paper-warm);
    overflow: hidden;
    transform: rotate(-1.5deg);
    opacity: 0;
    animation: riseIn 0.9s cubic-bezier(0.34, 1.36, 0.64, 1) 0.4s forwards;
  }

  .mockup-toolbar {
    background: var(--paper-dark);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--paper-dark);
  }

  .mockup-dots {
    display: flex;
    gap: 6px;
  }

  .mockup-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .mockup-dot:nth-child(1) { background: #e5534b; }
  .mockup-dot:nth-child(2) { background: #c69026; }
  .mockup-dot:nth-child(3) { background: #57ab5a; }

  .mockup-filename {
    font-size: 12px;
    color: var(--ink-muted);
    flex: 1;
    text-align: center;
  }

  .mockup-body {
    padding: 24px 20px;
    min-height: 340px;
  }

  .mockup-date {
    font-size: 11px;
    color: var(--ink-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
  }

  .mockup-heading {
    font-family: 'Noto Serif SC', serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 16px;
    line-height: 1.4;
  }

  .mockup-text {
    font-size: 13px;
    color: var(--ink-light);
    line-height: 1.8;
    margin-bottom: 12px;
  }

  .mockup-highlight {
    background: rgba(192, 57, 43, 0.12);
    padding: 2px 4px;
    border-radius: 2px;
  }

  .mockup-tag {
    display: inline-block;
    font-size: 11px;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 2px;
    padding: 2px 8px;
    margin-top: 8px;
  }

  /* 背景大字水印 */
  .hero-right::before {
    content: '记';
    position: absolute;
    font-family: 'Noto Serif SC', serif;
    font-size: 320px;
    font-weight: 900;
    color: var(--ink);
    opacity: 0.04;
    right: -40px;
    bottom: -40px;
    line-height: 1;
    pointer-events: none;
    user-select: none;
  }

  /* ─── STATS STRIP ─── */
  .stats-strip {
    background: var(--ink);
    color: var(--paper);
    padding: 32px 80px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
  }

  .stat-item {
    padding: 0 40px;
    position: relative;
  }

  .stat-item + .stat-item::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background: rgba(245, 240, 232, 0.12);
  }

  .stat-number {
    font-family: 'Noto Serif SC', serif;
    font-size: 40px;
    font-weight: 700;
    color: var(--paper);
    line-height: 1;
    margin-bottom: 8px;
    font-variant-numeric: tabular-nums;
  }

  .stat-number span {
    color: var(--accent-muted);
    font-size: 24px;
  }

  .stat-label {
    font-size: 13px;
    color: rgba(245, 240, 232, 0.5);
    letter-spacing: 0.05em;
  }

  /* ─── FEATURES ─── */
  .features {
    padding: 120px 80px;
  }

  .features-header {
    margin-bottom: 80px;
    max-width: 600px;
  }

  .section-title {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(32px, 3.5vw, 48px);
    font-weight: 700;
    line-height: 1.25;
    color: var(--ink);
    margin-bottom: 20px;
  }

  .section-subtitle {
    font-size: 16px;
    color: var(--ink-muted);
    line-height: 1.7;
  }

  .features-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 0;
  }

  .feature-card {
    padding: 48px;
    border-top: 1px solid rgba(26,20,16,0.1);
    transition: background 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .feature-card:nth-child(odd) {
    border-right: 1px solid rgba(26,20,16,0.1);
  }

  .feature-card:hover {
    background: var(--paper-warm);
  }

  .feature-num {
    font-family: 'Noto Serif SC', serif;
    font-size: 64px;
    font-weight: 900;
    color: var(--ink);
    opacity: 0.06;
    position: absolute;
    top: 20px;
    right: 24px;
    line-height: 1;
    user-select: none;
  }

  .feature-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 16px;
    line-height: 1.3;
  }

  .feature-title em {
    font-style: normal;
    color: var(--accent);
  }

  .feature-desc {
    font-size: 15px;
    color: var(--ink-light);
    line-height: 1.8;
  }

  /* ─── QUOTE ─── */
  .quote-section {
    background: var(--paper-dark);
    padding: 96px 80px;
    display: grid;
    grid-template-columns: 64px 1fr;
    gap: 40px;
    align-items: start;
  }

  .quote-mark {
    font-family: 'Noto Serif SC', serif;
    font-size: 120px;
    font-weight: 900;
    color: var(--accent);
    line-height: 0.8;
    margin-top: 8px;
    user-select: none;
  }

  .quote-content blockquote {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(20px, 2.5vw, 30px);
    font-weight: 400;
    line-height: 1.6;
    color: var(--ink);
    margin-bottom: 32px;
    max-width: 720px;
  }

  .quote-attribution {
    font-size: 14px;
    color: var(--ink-muted);
  }

  .quote-attribution strong {
    color: var(--ink);
    font-weight: 500;
  }

  /* ─── HOW IT WORKS ─── */
  .how-section {
    padding: 120px 80px;
  }

  .how-section .section-title {
    margin-bottom: 64px;
  }

  .steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
  }

  .step {
    padding: 0 48px 0 0;
    position: relative;
  }

  .step + .step {
    padding-left: 48px;
    border-left: 1px solid rgba(26,20,16,0.1);
  }

  .step-index {
    font-family: 'Noto Serif SC', serif;
    font-size: 13px;
    font-weight: 600;
    color: var(--ink-muted);
    letter-spacing: 0.1em;
    margin-bottom: 20px;
    display: block;
  }

  .step-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 16px;
    line-height: 1.3;
  }

  .step-desc {
    font-size: 15px;
    color: var(--ink-muted);
    line-height: 1.8;
  }

  /* ─── TESTIMONIALS ─── */
  .testimonials {
    background: var(--ink);
    padding: 96px 80px;
  }

  .testimonials-label {
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(245,240,232,0.4);
    margin-bottom: 56px;
  }

  .testimonials-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 40px;
  }

  .testimonial {
    border-top: 1px solid rgba(245,240,232,0.12);
    padding-top: 32px;
  }

  .testimonial-text {
    font-size: 15px;
    color: rgba(245,240,232,0.75);
    line-height: 1.8;
    margin-bottom: 24px;
  }

  .testimonial-author {
    font-size: 13px;
    color: rgba(245,240,232,0.45);
  }

  .testimonial-author strong {
    display: block;
    color: rgba(245,240,232,0.8);
    font-weight: 500;
    margin-bottom: 4px;
  }

  /* ─── CTA FINAL ─── */
  .cta-section {
    padding: 140px 80px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }

  .cta-section::before {
    content: '写';
    position: absolute;
    font-family: 'Noto Serif SC', serif;
    font-size: 480px;
    font-weight: 900;
    color: var(--ink);
    opacity: 0.03;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    line-height: 1;
    pointer-events: none;
    user-select: none;
  }

  .cta-inner {
    position: relative;
    z-index: 1;
    max-width: 600px;
    margin: 0 auto;
  }

  .cta-title {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(36px, 4vw, 56px);
    font-weight: 900;
    line-height: 1.15;
    color: var(--ink);
    margin-bottom: 24px;
  }

  .cta-title em {
    font-style: normal;
    color: var(--accent);
  }

  .cta-sub {
    font-size: 16px;
    color: var(--ink-muted);
    margin-bottom: 48px;
    line-height: 1.7;
  }

  .cta-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;
    color: var(--white);
    background: var(--ink);
    padding: 18px 48px;
    border-radius: 2px;
    text-decoration: none;
    transition: background 0.2s ease, transform 0.12s ease, box-shadow 0.2s ease;
  }

  .cta-action:hover {
    background: var(--ink-light);
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(26,20,16,0.22);
  }

  .cta-action:active {
    transform: scale(0.98);
  }

  .cta-action:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 4px;
  }

  .cta-fine {
    margin-top: 20px;
    font-size: 13px;
    color: var(--ink-muted);
  }

  /* ─── FOOTER ─── */
  footer {
    border-top: 1px solid rgba(26,20,16,0.08);
    padding: 40px 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .footer-brand {
    font-family: 'Noto Serif SC', serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
  }

  .footer-brand span {
    color: var(--accent);
  }

  .footer-links {
    display: flex;
    gap: 28px;
    list-style: none;
  }

  .footer-links a {
    font-size: 13px;
    color: var(--ink-muted);
    text-decoration: none;
    transition: color 0.2s;
  }

  .footer-links a:hover {
    color: var(--ink);
  }

  .footer-copy {
    font-size: 12px;
    color: var(--ink-muted);
  }

  /* ─── ANIMATIONS ─── */
  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes riseIn {
    from {
      opacity: 0;
      transform: rotate(-1.5deg) translateY(40px);
    }
    to {
      opacity: 1;
      transform: rotate(-1.5deg) translateY(0);
    }
  }

  /* scroll 入场 */
  .reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.7s ease, transform 0.7s ease;
  }

  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* ─── reduced-motion ─── */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
    .reveal {
      opacity: 1;
      transform: none;
    }
  }

  /* ─── RESPONSIVE ─── */
  @media (max-width: 900px) {
    nav {
      padding: 16px 24px;
    }

    .nav-links {
      display: none;
    }

    .hero {
      grid-template-columns: 1fr;
      min-height: auto;
    }

    .hero-left {
      padding: 100px 24px 60px;
    }

    .hero-right {
      min-height: 320px;
    }

    .hero-right::before {
      font-size: 200px;
    }

    .hero-mockup {
      width: 260px;
    }

    .stats-strip {
      padding: 40px 24px;
      grid-template-columns: 1fr;
      gap: 32px;
    }

    .stat-item + .stat-item::before {
      display: none;
    }

    .stat-item {
      padding: 0;
      border-top: 1px solid rgba(245,240,232,0.08);
      padding-top: 24px;
    }

    .stat-item:first-child {
      border-top: none;
      padding-top: 0;
    }

    .features {
      padding: 80px 24px;
    }

    .features-grid {
      grid-template-columns: 1fr;
    }

    .feature-card:nth-child(odd) {
      border-right: none;
    }

    .quote-section {
      padding: 64px 24px;
      grid-template-columns: 40px 1fr;
      gap: 16px;
    }

    .quote-mark {
      font-size: 72px;
    }

    .how-section {
      padding: 80px 24px;
    }

    .steps {
      grid-template-columns: 1fr;
      gap: 48px;
    }

    .step + .step {
      padding-left: 0;
      border-left: none;
      border-top: 1px solid rgba(26,20,16,0.1);
      padding-top: 48px;
    }

    .step {
      padding-right: 0;
    }

    .testimonials {
      padding: 64px 24px;
    }

    .testimonials-grid {
      grid-template-columns: 1fr;
    }

    .cta-section {
      padding: 100px 24px;
    }

    footer {
      padding: 32px 24px;
      flex-direction: column;
      gap: 24px;
      text-align: center;
    }

    .footer-links {
      flex-wrap: wrap;
      justify-content: center;
      gap: 16px;
    }
  }
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <a href="#" class="nav-brand">墨<span>记</span></a>
  <ul class="nav-links">
    <li><a href="#features">功能</a></li>
    <li><a href="#how">如何使用</a></li>
    <li><a href="#voices">用户声音</a></li>
  </ul>
  <a href="#cta" class="nav-cta">免费开始</a>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-left">
    <p class="hero-eyebrow">Your thinking space</p>
    <h1 class="hero-title">
      写下，<br>就<em>不会</em>忘
    </h1>
    <p class="hero-desc">
      墨记是一款专为深度思考设计的笔记工具。把散落的想法落成文字，让思维生长出结构。
    </p>
    <div class="hero-actions">
      <a href="#cta" class="btn-primary">免费下载 →</a>
      <a href="#how" class="btn-secondary">看看怎么用</a>
    </div>
  </div>

  <div class="hero-right">
    <div class="hero-mockup" aria-hidden="true">
      <div class="mockup-toolbar">
        <div class="mockup-dots">
          <div class="mockup-dot"></div>
          <div class="mockup-dot"></div>
          <div class="mockup-dot"></div>
        </div>
        <span class="mockup-filename">2026年6月 · 读书笔记</span>
      </div>
      <div class="mockup-body">
        <div class="mockup-date">2026 · JUN · 21</div>
        <div class="mockup-heading">《万物理论》读后感</div>
        <p class="mockup-text">
          霍金说时间是<span class="mockup-highlight">方向性的</span>——它总是朝一个方向流动。而我们记下的那些字，某种程度上在和遗忘对抗。
        </p>
        <p class="mockup-text">
          记录不只是保存，它是在整理你对世界的理解方式。
        </p>
        <span class="mockup-tag"># 物理 · 时间</span>
      </div>
    </div>
  </div>
</section>

<!-- STATS STRIP -->
<div class="stats-strip reveal">
  <div class="stat-item">
    <div class="stat-number">47<span>万</span></div>
    <div class="stat-label">活跃用户的日记与笔记</div>
  </div>
  <div class="stat-item">
    <div class="stat-number">2.3<span>亿</span></div>
    <div class="stat-label">条记录从未因此遗忘</div>
  </div>
  <div class="stat-item">
    <div class="stat-number">4.8<span>分</span></div>
    <div class="stat-label">App Store 用户评分</div>
  </div>
</div>

<!-- FEATURES -->
<section id="features" class="features">
  <div class="features-header reveal">
    <h2 class="section-title">思维需要<br>一个干净的容器</h2>
    <p class="section-subtitle">墨记不做花哨，只做一件事做到极致——让你不费力地把想法变成文字，把文字变成思路。</p>
  </div>

  <div class="features-grid">
    <div class="feature-card reveal">
      <span class="feature-num" aria-hidden="true">一</span>
      <h3 class="feature-title">打开即写，<em>无干扰</em></h3>
      <p class="feature-desc">没有工具栏轰炸，没有格式焦虑。全屏编辑器，只有你和文字。鼠标停在角落，工具才出现。</p>
    </div>
    <div class="feature-card reveal">
      <span class="feature-num" aria-hidden="true">二</span>
      <h3 class="feature-title">双向链接，<em>连接想法</em></h3>
      <p class="feature-desc">用 [[ ]] 把散落的笔记串联成网。六个月前的一个念头，今天可能正好是你需要的线索。</p>
    </div>
    <div class="feature-card reveal">
      <span class="feature-num" aria-hidden="true">三</span>
      <h3 class="feature-title">端对端加密，<em>只有你看得到</em></h3>
      <p class="feature-desc">服务器永远只存加密后的密文。我们没有钥匙，连自己也无法读取你的内容。</p>
    </div>
    <div class="feature-card reveal">
      <span class="feature-num" aria-hidden="true">四</span>
      <h3 class="feature-title">跨设备，<em>总是同步</em></h3>
      <p class="feature-desc">手机地铁里记一句话，到了桌面自动出现。iOS、macOS、网页版，三端即时同步。</p>
    </div>
  </div>
</section>

<!-- QUOTE -->
<section class="quote-section reveal">
  <div class="quote-mark" aria-hidden="true">"</div>
  <div class="quote-content">
    <blockquote>
      用了很多笔记工具，总觉得是在给软件服务，而不是给自己的思维服务。墨记第一次让我感觉——这个工具是懂我的。
    </blockquote>
    <p class="quote-attribution">
      <strong>陈小雪</strong>
      产品设计师，上海
    </p>
  </div>
</section>

<!-- HOW IT WORKS -->
<section id="how" class="how-section">
  <h2 class="section-title reveal">三步开始，<br>然后就变成习惯</h2>
  <div class="steps">
    <div class="step reveal">
      <span class="step-index">01</span>
      <h3 class="step-title">下载，打开，开写</h3>
      <p class="step-desc">不需要注册教程，不需要看演示视频。下载后打开，光标在等你。用 Markdown 写，或者直接白板风格写，都行。</p>
    </div>
    <div class="step reveal">
      <span class="step-index">02</span>
      <h3 class="step-title">标签和链接，让笔记自己生长</h3>
      <p class="step-desc">写的时候随手加 #标签 或 [[引用]]。时间长了，你会发现笔记之间开始形成意想不到的关联。</p>
    </div>
    <div class="step reveal">
      <span class="step-index">03</span>
      <h3 class="step-title">需要的时候，找得到</h3>
      <p class="step-desc">全文搜索，0.2 秒内出结果。不需要想"我当时存在哪个文件夹"——搜一个关键词，它就在那里。</p>
    </div>
  </div>
</section>

<!-- TESTIMONIALS -->
<section id="voices" class="testimonials reveal">
  <p class="testimonials-label">Trusted by thinkers</p>
  <div class="testimonials-grid">
    <div class="testimonial">
      <p class="testimonial-text">「每天早上六点，打开墨记写半小时。一年下来，感觉脑子里的存货多了不少，乱也乱得更有条理。」</p>
      <div class="testimonial-author">
        <strong>李明远</strong>
        律师，北京
      </div>
    </div>
    <div class="testimonial">
      <p class="testimonial-text">「读书的时候随手记，后来发现很多笔记自动串在一起，变成了我自己的知识库。这才是我一直在找的东西。」</p>
      <div class="testimonial-author">
        <strong>沈凯欣</strong>
        研究生，武汉
      </div>
    </div>
    <div class="testimonial">
      <p class="testimonial-text">「界面太干净了，干净到让我不好意思不好好写。一个 App 能有这种效果，挺少见的。」</p>
      <div class="testimonial-author">
        <strong>郑一鸣</strong>
        创业者，杭州
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section id="cta" class="cta-section">
  <div class="cta-inner reveal">
    <h2 class="cta-title">从今天开始，<br>把想法<em>留下来</em></h2>
    <p class="cta-sub">免费下载，无订阅门槛。个人使用永久免费，团队版按需升级。</p>
    <a href="#" class="cta-action" aria-label="免费下载墨记 App">免费下载墨记 →</a>
    <p class="cta-fine">支持 iOS · macOS · 网页版</p>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <span class="footer-brand">墨<span>记</span></span>
  <ul class="footer-links">
    <li><a href="#">隐私政策</a></li>
    <li><a href="#">服务条款</a></li>
    <li><a href="#">联系我们</a></li>
    <li><a href="#">帮助中心</a></li>
  </ul>
  <span class="footer-copy">© 2026 墨记</span>
</footer>

<script>
  // Scroll reveal
  const revealEls = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealEls.forEach(el => observer.observe(el));
</script>

</body>
</html>
```
