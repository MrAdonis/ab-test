```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>墨记 · 让思考留下痕迹</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :root {
    --ink: #1a1a18;
    --ink-muted: #4a4a46;
    --ink-faint: #8a8a84;
    --paper: #f5f2ec;
    --paper-warm: #ede9e0;
    --accent: #2d6a5a;
    --accent-light: #e8f0ed;
    --border: #d8d4cb;

    --serif: "Noto Serif SC", "Songti SC", "SimSun", serif;
    --sans: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    background-color: var(--paper);
    color: var(--ink);
    font-family: var(--sans);
    font-size: 16px;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }

  /* ── 噪点纹理层 ── */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    opacity: 0.4;
    mix-blend-mode: multiply;
  }

  /* ── 导航 ── */
  nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 48px;
    background: rgba(245, 242, 236, 0.88);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
  }

  .nav-logo {
    font-family: var(--serif);
    font-size: 22px;
    font-weight: 900;
    color: var(--ink);
    letter-spacing: -0.02em;
  }

  .nav-logo span {
    color: var(--accent);
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 32px;
    list-style: none;
  }

  .nav-links a {
    color: var(--ink-muted);
    text-decoration: none;
    font-size: 14px;
    transition: color 150ms ease-out;
  }

  .nav-links a:hover {
    color: var(--ink);
  }

  .nav-cta {
    background: var(--ink);
    color: var(--paper) !important;
    padding: 9px 20px;
    border-radius: 4px;
    font-size: 14px !important;
    transition: background 150ms ease-out !important;
  }

  .nav-cta:hover {
    background: var(--accent) !important;
    color: var(--paper) !important;
  }

  /* ── HERO：不对称分屏 ── */
  .hero {
    min-height: 100dvh;
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding-top: 81px;
  }

  .hero-left {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 64px 80px 48px;
    border-right: 1px solid var(--border);
  }

  .hero-eyebrow {
    display: inline-block;
    font-size: 11px;
    font-family: var(--sans);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 32px;
  }

  .hero-title {
    font-family: var(--serif);
    font-size: clamp(52px, 5vw, 76px);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--ink);
    margin-bottom: 28px;
  }

  .hero-title em {
    font-style: normal;
    color: var(--accent);
  }

  .hero-sub {
    font-size: 17px;
    color: var(--ink-muted);
    line-height: 1.75;
    max-width: 380px;
    margin-bottom: 48px;
  }

  .hero-actions {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .btn-primary {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    padding: 14px 32px;
    border-radius: 4px;
    font-size: 15px;
    font-family: var(--sans);
    transition: background 150ms ease-out, transform 100ms ease-out;
  }

  .btn-primary:hover {
    background: #235649;
  }

  .btn-primary:active {
    transform: scale(0.98);
  }

  .btn-secondary {
    font-size: 14px;
    color: var(--ink-muted);
    text-decoration: none;
    border-bottom: 1px solid var(--border);
    padding-bottom: 2px;
    transition: color 150ms ease-out, border-color 150ms ease-out;
  }

  .btn-secondary:hover {
    color: var(--ink);
    border-color: var(--ink);
  }

  .hero-right {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 80px 48px;
    background: var(--paper-warm);
    position: relative;
    overflow: hidden;
  }

  /* 笔记本模拟占位 */
  .notebook-mock {
    width: 320px;
    height: 420px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 
      4px 4px 0 var(--border),
      8px 8px 0 #e0ddd7,
      -2px 0 0 var(--border);
    position: relative;
    padding: 36px 32px;
    animation: float 6s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(-1deg); }
    50% { transform: translateY(-12px) rotate(0.5deg); }
  }

  @media (prefers-reduced-motion: reduce) {
    .notebook-mock { animation: none; }
  }

  .mock-line {
    height: 1px;
    background: #e8e5de;
    margin-bottom: 18px;
  }

  .mock-line.short { width: 60%; }
  .mock-line.shorter { width: 40%; }
  .mock-line.medium { width: 75%; }

  .mock-title-line {
    height: 2px;
    background: var(--ink);
    width: 80%;
    margin-bottom: 24px;
    opacity: 0.85;
  }

  .mock-tag {
    display: inline-block;
    background: var(--accent-light);
    color: var(--accent);
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 2px;
    margin-bottom: 20px;
    font-family: var(--sans);
  }

  .mock-dot-grid {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, var(--border) 1px, transparent 1px);
    background-size: 18px 18px;
    opacity: 0.25;
    border-radius: 2px;
    pointer-events: none;
  }

  /* ── FEATURES：错位布局 ── */
  .features {
    padding: 120px 48px;
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 80px;
    align-items: start;
    border-top: 1px solid var(--border);
  }

  .features-intro h2 {
    font-family: var(--serif);
    font-size: 38px;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.02em;
    margin-bottom: 20px;
  }

  .features-intro p {
    font-size: 15px;
    color: var(--ink-muted);
    line-height: 1.8;
  }

  .features-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }

  .feature-item {
    padding: 40px 36px;
    border-top: 1px solid var(--border);
    border-right: 1px solid var(--border);
    transition: background 200ms ease-out;
  }

  .feature-item:nth-child(2n) {
    border-right: none;
  }

  .feature-item:nth-child(1),
  .feature-item:nth-child(2) {
    border-top: none;
  }

  .feature-item:hover {
    background: var(--paper-warm);
  }

  .feature-num {
    font-family: var(--serif);
    font-size: 11px;
    color: var(--ink-faint);
    letter-spacing: 0.12em;
    margin-bottom: 16px;
  }

  .feature-title {
    font-family: var(--serif);
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: -0.01em;
  }

  .feature-desc {
    font-size: 14px;
    color: var(--ink-muted);
    line-height: 1.75;
  }

  /* ── QUOTE：全宽引语 ── */
  .quote-section {
    padding: 100px 48px;
    background: var(--ink);
    color: var(--paper);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .quote-text {
    font-family: var(--serif);
    font-size: clamp(28px, 3.5vw, 48px);
    font-weight: 400;
    line-height: 1.45;
    text-align: center;
    max-width: 720px;
    letter-spacing: -0.01em;
    margin-bottom: 40px;
    opacity: 0.95;
  }

  .quote-text em {
    font-style: normal;
    color: #7bbfae;
    border-bottom: 1px solid rgba(123, 191, 174, 0.4);
  }

  .quote-attribution {
    font-size: 13px;
    color: rgba(245, 242, 236, 0.45);
    letter-spacing: 0.08em;
  }

  /* ── HOW IT WORKS：横向时间线 ── */
  .process {
    padding: 120px 48px;
    border-top: 1px solid var(--border);
  }

  .process-eyebrow {
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 16px;
    display: block;
  }

  .process h2 {
    font-family: var(--serif);
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 72px;
    letter-spacing: -0.02em;
  }

  .process-steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    position: relative;
  }

  .process-steps::before {
    content: "";
    position: absolute;
    top: 20px;
    left: 24px;
    right: 24px;
    height: 1px;
    background: var(--border);
  }

  .step {
    padding: 0 24px;
    position: relative;
  }

  .step-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--accent);
    margin-bottom: 28px;
    position: relative;
    z-index: 1;
  }

  .step-num {
    font-family: var(--serif);
    font-size: 11px;
    color: var(--ink-faint);
    margin-bottom: 12px;
    display: block;
  }

  .step h3 {
    font-family: var(--serif);
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
  }

  .step p {
    font-size: 14px;
    color: var(--ink-muted);
    line-height: 1.75;
  }

  /* ── CTA 底部：2列 ── */
  .cta-section {
    padding: 120px 48px;
    background: var(--paper-warm);
    border-top: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    align-items: center;
  }

  .cta-left h2 {
    font-family: var(--serif);
    font-size: clamp(36px, 4vw, 56px);
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 24px;
  }

  .cta-left p {
    font-size: 16px;
    color: var(--ink-muted);
    line-height: 1.75;
  }

  .cta-right {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .cta-form {
    display: flex;
    gap: 0;
  }

  .cta-input {
    flex: 1;
    padding: 13px 16px;
    border: 1px solid var(--border);
    border-right: none;
    background: #fff;
    color: var(--ink);
    font-size: 15px;
    font-family: var(--sans);
    border-radius: 4px 0 0 4px;
    outline: none;
    transition: border-color 150ms ease-out;
  }

  .cta-input::placeholder {
    color: var(--ink-faint);
  }

  .cta-input:focus {
    border-color: var(--accent);
  }

  .cta-submit {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 13px 24px;
    font-size: 14px;
    font-family: var(--sans);
    cursor: pointer;
    border-radius: 0 4px 4px 0;
    transition: background 150ms ease-out;
    white-space: nowrap;
  }

  .cta-submit:hover {
    background: #235649;
  }

  .cta-submit:active {
    transform: scale(0.98);
  }

  .cta-note {
    font-size: 13px;
    color: var(--ink-faint);
  }

  /* ── 页脚 ── */
  footer {
    padding: 40px 48px;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .footer-logo {
    font-family: var(--serif);
    font-size: 18px;
    font-weight: 900;
    color: var(--ink);
  }

  .footer-logo span {
    color: var(--accent);
  }

  .footer-links {
    display: flex;
    gap: 24px;
    list-style: none;
  }

  .footer-links a {
    font-size: 13px;
    color: var(--ink-faint);
    text-decoration: none;
    transition: color 150ms ease-out;
  }

  .footer-links a:hover {
    color: var(--ink);
  }

  .footer-copy {
    font-size: 12px;
    color: var(--ink-faint);
  }

  /* ── 入场动效 ── */
  .fade-up {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 600ms ease-out, transform 600ms ease-out;
  }

  .fade-up.visible {
    opacity: 1;
    transform: translateY(0);
  }

  @media (prefers-reduced-motion: reduce) {
    .fade-up {
      opacity: 1;
      transform: none;
      transition: none;
    }
  }

  /* ── 响应式 ── */
  @media (max-width: 900px) {
    nav { padding: 16px 24px; }
    .nav-links { display: none; }

    .hero {
      grid-template-columns: 1fr;
    }
    .hero-left { padding: 48px 24px; border-right: none; }
    .hero-right { display: none; }

    .features { grid-template-columns: 1fr; padding: 80px 24px; }
    .features-grid { grid-template-columns: 1fr; }
    .feature-item:nth-child(2n) { border-right: 1px solid var(--border); }
    .feature-item:nth-child(n) { border-right: none; }
    .feature-item:nth-child(1) { border-top: 1px solid var(--border); }

    .quote-section { padding: 80px 24px; }

    .process { padding: 80px 24px; }
    .process-steps { grid-template-columns: 1fr 1fr; gap: 40px; }
    .process-steps::before { display: none; }

    .cta-section { grid-template-columns: 1fr; padding: 80px 24px; }
    .cta-form { flex-direction: column; }
    .cta-input { border-right: 1px solid var(--border); border-radius: 4px; }
    .cta-submit { border-radius: 4px; }

    footer { flex-direction: column; gap: 20px; text-align: center; }
    .footer-links { flex-wrap: wrap; justify-content: center; }
  }

  @media (max-width: 600px) {
    .process-steps { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- 导航 -->
<nav>
  <div class="nav-logo">墨<span>记</span></div>
  <ul class="nav-links">
    <li><a href="#features">功能</a></li>
    <li><a href="#process">使用方式</a></li>
    <li><a href="#cta" class="nav-cta">免费开始记录</a></li>
  </ul>
</nav>

<!-- HERO：不对称分屏 -->
<section class="hero">
  <div class="hero-left">
    <span class="hero-eyebrow">笔记工具 · 2024</span>
    <h1 class="hero-title">
      让思考<br>
      留下<em>痕迹</em>
    </h1>
    <p class="hero-sub">
      写下的字，不只是文字。墨记用纸质手感与结构化连接，让你的每一个想法都能被找到、被延续。
    </p>
    <div class="hero-actions">
      <a href="#cta" class="btn-primary">免费开始记录</a>
      <a href="#features" class="btn-secondary">了解功能</a>
    </div>
  </div>
  <div class="hero-right">
    <div class="notebook-mock">
      <div class="mock-dot-grid"></div>
      <span class="mock-tag">2024年读书笔记</span>
      <div class="mock-title-line"></div>
      <div class="mock-line"></div>
      <div class="mock-line short"></div>
      <div class="mock-line medium"></div>
      <div class="mock-line shorter"></div>
      <div class="mock-line"></div>
      <div class="mock-line medium"></div>
      <div class="mock-line short"></div>
      <div class="mock-line"></div>
      <div class="mock-line shorter"></div>
      <div class="mock-line medium"></div>
    </div>
  </div>
</section>

<!-- FEATURES：错位布局，无 eyebrow -->
<section class="features" id="features">
  <div class="features-intro">
    <h2>记录，不止于此</h2>
    <p>大多数笔记工具让你在格子里填字。墨记让你的想法自由生长，然后在需要时精准找回。</p>
  </div>
  <div class="features-grid">
    <div class="feature-item fade-up">
      <div class="feature-num">01</div>
      <h3 class="feature-title">纸质触感编辑器</h3>
      <p class="feature-desc">点阵背景、衬线字体、轻微的纸张质感。你会忘记自己在用软件。</p>
    </div>
    <div class="feature-item fade-up" style="transition-delay: 80ms">
      <div class="feature-num">02</div>
      <h3 class="feature-title">双向链接思维图</h3>
      <p class="feature-desc">一个词连接多篇笔记，想法之间的关系自动浮现。</p>
    </div>
    <div class="feature-item fade-up" style="transition-delay: 160ms">
      <div class="feature-num">03</div>
      <h3 class="feature-title">全文语义检索</h3>
      <p class="feature-desc">三年前写的那句话，输入半个关键词就能找到。</p>
    </div>
    <div class="feature-item fade-up" style="transition-delay: 240ms">
      <div class="feature-num">04</div>
      <h3 class="feature-title">离线优先，本地存储</h3>
      <p class="feature-desc">你的文字只属于你。没有网络也能流畅写作，数据不经过任何服务器。</p>
    </div>
  </div>
</section>

<!-- QUOTE：full-width 引语 -->
<section class="quote-section">
  <blockquote class="quote-text">
    「好的工具不该让你意识到它的存在。<em>打开墨记</em>，就像打开一本等待已久的空白本子。」
  </blockquote>
  <p class="quote-attribution">早期用户 · 产品设计师</p>
</section>

<!-- PROCESS：横向时间线，带 eyebrow -->
<section class="process" id="process">
  <span class="process-eyebrow">使用方式</span>
  <h2>从第一个字开始</h2>
  <div class="process-steps">
    <div class="step fade-up">
      <div class="step-dot"></div>
      <span class="step-num">一</span>
      <h3>创建笔记本</h3>
      <p>按项目、书目、或心情分组。不强制任何结构，从你习惯的方式出发。</p>
    </div>
    <div class="step fade-up" style="transition-delay: 100ms">
      <div class="step-dot"></div>
      <span class="step-num">二</span>
      <h3>随手记录</h3>
      <p>Markdown 支持，快捷键写作，图片拖入即用。不打断思路。</p>
    </div>
    <div class="step fade-up" style="transition-delay: 200ms">
      <div class="step-dot"></div>
      <span class="step-num">三</span>
      <h3>建立连接</h3>
      <p>用 [[ ]] 链接任意笔记，想法开始产生联系，知识慢慢成形。</p>
    </div>
    <div class="step fade-up" style="transition-delay: 300ms">
      <div class="step-dot"></div>
      <span class="step-num">四</span>
      <h3>随时找回</h3>
      <p>输入关键词，精准定位。三个月后的灵光一现，不会就此消失。</p>
    </div>
  </div>
</section>

<!-- CTA：2列，无 eyebrow -->
<section class="cta-section" id="cta">
  <div class="cta-left">
    <h2>从今天开始，<br>别让想法溜走</h2>
    <p>墨记免费使用，无限笔记，永久本地存储。注册即可开始。</p>
  </div>
  <div class="cta-right">
    <div class="cta-form">
      <input type="email" class="cta-input" placeholder="your@email.com">
      <button class="cta-submit">创建免费账号</button>
    </div>
    <p class="cta-note">无需信用卡 · 数据本地存储 · 随时导出</p>
  </div>
</section>

<!-- 页脚 -->
<footer>
  <div class="footer-logo">墨<span>记</span></div>
  <ul class="footer-links">
    <li><a href="#">隐私政策</a></li>
    <li><a href="#">使用条款</a></li>
    <li><a href="#">联系我们</a></li>
  </ul>
  <p class="footer-copy">© 2024 墨记</p>
</footer>

<script>
  // 入场动效
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
</script>

</body>
</html>
```
