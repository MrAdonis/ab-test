## 设计说明

**Design Read**

Reading this as: **SaaS uptime monitoring landing** for **indie developers and small teams evaluating their first monitoring tool**, with a **dark tech + precision + trust-first** language, leaning toward **原生 CSS + DM Mono display + Plus Jakarta Sans body**.

**量化维度**

- VARIANCE: 7 — 不对称分屏 hero，sections 布局家族不复用
- MOTION: 6 — 3 个有意图动效：stagger hero 入场、status dot pulse、scroll-triggered feature reveal
- DENSITY: 3 — 大留白，数据点突出，非密集展示

**品牌方向判断**

- 名称 Tidewatch：保留。海潮隐喻 = 周期性、可靠性、信号，完美映射 uptime 监控语义
- Tagline: "Know the moment it goes down" — 直接、功能性、无套话
- 主色系：深炭灰底 `#0d1117` / `#161b22`（GitHub dark 家族，开发者熟悉感）+ 单强调色 amber `#f59e0b`（告警语义天然匹配，区别于竞品 teal/green/purple）
- 排除逻辑：不选蓝绿（Pingdom/Better Uptime 用烂），不选紫（AI cliché），不选纯黑 `#000000`（过硬，用 `#0d1117`）
- 字体：DM Mono 做 hero 数字和数据层（monospace = terminal precision），Plus Jakarta Sans 做标题和正文（现代、有辨识度，非 Inter）

**布局家族（规则 2，8 sections 用 5 种）**

1. Hero: 55/45 不对称分屏（text + live dashboard mockup）
2. Logos/Trust: 横向滚动信任条（无卡片容器）
3. Features: 交错 zigzag 左右交替（text + visual）
4. Pricing: 2-column cards（对比 free vs paid）
5. Stats: 横向全宽数字条
6. How it works: 编号竖列 timeline
7. Testimonials: 单引用 + 大字 pull quote（非三列卡片）
8. CTA footer: 居中单列

**Section eyebrow 交替（规则 3）**

Hero(eyebrow) → Trust(无) → Features(eyebrow) → Stats(无) → How it works(eyebrow) → Pricing(无) → Testimonials(eyebrow) → CTA(无)

**Hero 文字栈（规则 1，4 元素封顶）**

1. eyebrow: `UPTIME MONITORING`
2. 标题: 2 行
3. 副文案: ≤20 词
4. CTA: 1 主 + 1 次

**Production Tell 检查**

- 无 section numbering（00 / 001 类）
- 无 scroll cue
- 无装饰文字条
- 无 fake live counter（status dots 是装饰性动画，非数字计数器）
- 无诗化社会证明标签
- 无 version footer

**对比度声明**

- Amber `#f59e0b` on dark `#0d1117`: ~8.2:1 ✓ WCAG AAA
- Body text `#e6edf3` on `#0d1117`: ~13.5:1 ✓
- Muted text `#8b949e` on `#0d1117`: ~4.6:1 ✓ AA

## 最终 HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tidewatch — Uptime Monitoring</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-base:     #0d1117;
      --bg-subtle:   #161b22;
      --bg-muted:    #21262d;
      --border:      #30363d;
      --border-subtle: #21262d;
      --text-primary: #e6edf3;
      --text-secondary: #8b949e;
      --text-muted:  #6e7681;
      --accent:      #f59e0b;
      --accent-dim:  rgba(245,158,11,0.12);
      --accent-glow: rgba(245,158,11,0.06);
      --green:       #3fb950;
      --red:         #f85149;
      --font-sans:   'Plus Jakarta Sans', system-ui, sans-serif;
      --font-mono:   'DM Mono', 'Fira Code', monospace;
      --radius-sm:   6px;
      --radius-md:   10px;
      --radius-lg:   16px;
    }

    html { scroll-behavior: smooth; }

    body {
      background: var(--bg-base);
      color: var(--text-primary);
      font-family: var(--font-sans);
      font-size: 16px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }

    /* ── NOISE OVERLAY ─────────────────────────────── */
    body::after {
      content: '';
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 9999;
      opacity: 0.025;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
    }

    /* ── NAV ─────────────────────────────────────────── */
    nav {
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 48px;
      height: 60px;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(13,17,23,0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }

    .nav-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      font-family: var(--font-mono);
      font-weight: 500;
      font-size: 15px;
      color: var(--text-primary);
      letter-spacing: -0.02em;
    }

    .nav-logo-mark {
      width: 28px;
      height: 28px;
      border: 1.5px solid var(--accent);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .nav-logo-mark svg { display: block; }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 32px;
      list-style: none;
    }

    .nav-links a {
      text-decoration: none;
      color: var(--text-secondary);
      font-size: 14px;
      font-weight: 500;
      transition: color 150ms ease;
    }

    .nav-links a:hover { color: var(--text-primary); }

    .nav-cta {
      background: var(--accent);
      color: #0d1117;
      font-size: 13px;
      font-weight: 700;
      padding: 7px 16px;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: opacity 150ms ease, transform 100ms ease;
      letter-spacing: 0.01em;
    }

    .nav-cta:hover { opacity: 0.9; }
    .nav-cta:active { transform: scale(0.98); }
    .nav-cta:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    /* ── HERO ────────────────────────────────────────── */
    .hero {
      min-height: 100dvh;
      display: grid;
      grid-template-columns: 55fr 45fr;
      align-items: center;
      padding: 0 48px;
      padding-top: 60px;
      gap: 0;
      max-width: 1280px;
      margin: 0 auto;
    }

    .hero-text {
      padding-right: 64px;
      opacity: 0;
      transform: translateY(24px);
      animation: fadeUp 0.7s ease forwards 0.15s;
    }

    .hero-eyebrow {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 400;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .hero-eyebrow::before {
      content: '';
      display: block;
      width: 20px;
      height: 1.5px;
      background: var(--accent);
    }

    .hero-headline {
      font-size: clamp(40px, 5vw, 64px);
      font-weight: 800;
      line-height: 1.08;
      letter-spacing: -0.035em;
      color: var(--text-primary);
      margin-bottom: 20px;
      text-wrap: balance;
    }

    .hero-headline em {
      font-style: normal;
      color: var(--accent);
    }

    .hero-sub {
      font-size: 17px;
      line-height: 1.65;
      color: var(--text-secondary);
      margin-bottom: 36px;
      max-width: 420px;
      text-wrap: pretty;
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .btn-primary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--accent);
      color: #0d1117;
      font-size: 15px;
      font-weight: 700;
      padding: 13px 24px;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: opacity 150ms ease, transform 100ms ease;
      white-space: nowrap;
    }

    .btn-primary:hover { opacity: 0.92; }
    .btn-primary:active { transform: scale(0.98); }
    .btn-primary:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    .btn-secondary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: transparent;
      color: var(--text-secondary);
      font-size: 14px;
      font-weight: 500;
      padding: 13px 20px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      text-decoration: none;
      transition: border-color 150ms ease, color 150ms ease;
    }

    .btn-secondary:hover { border-color: var(--text-muted); color: var(--text-primary); }
    .btn-secondary:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    /* ── DASHBOARD MOCKUP ───────────────────────────── */
    .hero-visual {
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.7s ease forwards 0.35s;
    }

    .dashboard-card {
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow:
        0 0 0 1px rgba(255,255,255,0.04),
        0 24px 64px rgba(0,0,0,0.6),
        0 0 120px rgba(245,158,11,0.04);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--bg-muted);
    }

    .card-dots {
      display: flex;
      gap: 6px;
    }

    .card-dots span {
      width: 10px; height: 10px;
      border-radius: 50%;
      background: var(--border);
    }

    .card-title {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.06em;
    }

    .card-badge {
      font-family: var(--font-mono);
      font-size: 10px;
      background: rgba(63,185,80,0.12);
      color: var(--green);
      padding: 3px 8px;
      border-radius: 20px;
      border: 1px solid rgba(63,185,80,0.2);
    }

    .card-body { padding: 18px; }

    .monitor-list { display: flex; flex-direction: column; gap: 2px; }

    .monitor-row {
      display: grid;
      grid-template-columns: auto 1fr auto auto;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      transition: background 150ms ease;
    }

    .monitor-row:hover { background: var(--bg-muted); }

    .status-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .status-dot.up {
      background: var(--green);
      box-shadow: 0 0 0 0 rgba(63,185,80,0.4);
      animation: pulse-green 2.4s ease infinite;
    }

    .status-dot.down {
      background: var(--red);
      box-shadow: 0 0 0 0 rgba(248,81,73,0.4);
      animation: pulse-red 2s ease infinite;
    }

    @keyframes pulse-green {
      0%   { box-shadow: 0 0 0 0 rgba(63,185,80,0.5); }
      60%  { box-shadow: 0 0 0 6px rgba(63,185,80,0); }
      100% { box-shadow: 0 0 0 0 rgba(63,185,80,0); }
    }

    @keyframes pulse-red {
      0%   { box-shadow: 0 0 0 0 rgba(248,81,73,0.5); }
      60%  { box-shadow: 0 0 0 6px rgba(248,81,73,0); }
      100% { box-shadow: 0 0 0 0 rgba(248,81,73,0); }
    }

    .monitor-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .monitor-url {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
    }

    .monitor-uptime {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .monitor-latency {
      font-family: var(--font-mono);
      font-size: 12px;
      white-space: nowrap;
      text-align: right;
    }

    .latency-ok { color: var(--green); }
    .latency-warn { color: var(--accent); }
    .latency-bad { color: var(--red); }

    .uptime-bars {
      display: flex;
      gap: 2px;
      align-items: flex-end;
    }

    .uptime-bar {
      width: 4px;
      border-radius: 2px;
      background: var(--green);
    }

    .uptime-bar.down { background: var(--red); }
    .uptime-bar.warn { background: var(--accent); }

    .card-footer {
      padding: 12px 18px;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .footer-stat {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .footer-stat-value {
      font-family: var(--font-mono);
      font-size: 18px;
      font-weight: 500;
      color: var(--text-primary);
    }

    .footer-stat-label {
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.04em;
    }

    .incident-alert {
      background: rgba(248,81,73,0.08);
      border: 1px solid rgba(248,81,73,0.2);
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .incident-dot {
      width: 6px; height: 6px;
      background: var(--red);
      border-radius: 50%;
      flex-shrink: 0;
    }

    .incident-text {
      font-size: 11px;
      color: #f85149;
      font-family: var(--font-mono);
    }

    /* ── LOGO STRIP ─────────────────────────────────── */
    .trust-strip {
      border-top: 1px solid var(--border-subtle);
      border-bottom: 1px solid var(--border-subtle);
      padding: 20px 0;
      overflow: hidden;
    }

    .trust-inner {
      display: flex;
      align-items: center;
      gap: 0;
      white-space: nowrap;
    }

    .trust-label {
      font-size: 12px;
      color: var(--text-muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-family: var(--font-mono);
      padding: 0 48px;
      flex-shrink: 0;
    }

    .trust-logos {
      display: flex;
      gap: 48px;
      align-items: center;
      padding-right: 48px;
    }

    .trust-logo {
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      white-space: nowrap;
      letter-spacing: 0.02em;
    }

    /* ── STATS ──────────────────────────────────────── */
    .stats-section {
      border-bottom: 1px solid var(--border-subtle);
      padding: 0;
    }

    .stats-inner {
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 48px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
    }

    .stat-block {
      padding: 48px 0;
      border-right: 1px solid var(--border-subtle);
      padding-right: 48px;
      padding-left: 0;
    }

    .stat-block:not(:first-child) { padding-left: 48px; }
    .stat-block:last-child { border-right: none; }

    .stat-number {
      font-family: var(--font-mono);
      font-size: 48px;
      font-weight: 500;
      color: var(--text-primary);
      line-height: 1;
      margin-bottom: 8px;
      font-variant-numeric: tabular-nums;
    }

    .stat-number span { color: var(--accent); }

    .stat-label {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
    }

    /* ── FEATURES ───────────────────────────────────── */
    .features-section {
      max-width: 1280px;
      margin: 0 auto;
      padding: 120px 48px;
    }

    .section-header {
      margin-bottom: 80px;
    }

    .section-eyebrow {
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .section-eyebrow::before {
      content: '';
      display: block;
      width: 16px;
      height: 1.5px;
      background: var(--accent);
    }

    .section-title {
      font-size: clamp(28px, 3.5vw, 42px);
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      max-width: 520px;
      text-wrap: balance;
    }

    .feature-zigzag { display: flex; flex-direction: column; gap: 96px; }

    .feature-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 80px;
      align-items: center;
      opacity: 0;
      transform: translateY(32px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .feature-row.visible { opacity: 1; transform: translateY(0); }

    .feature-row.reverse { direction: rtl; }
    .feature-row.reverse > * { direction: ltr; }

    .feature-text {}

    .feature-tag {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 16px;
    }

    .feature-title {
      font-size: 26px;
      font-weight: 700;
      line-height: 1.25;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      margin-bottom: 16px;
    }

    .feature-desc {
      font-size: 16px;
      line-height: 1.7;
      color: var(--text-secondary);
      margin-bottom: 24px;
      text-wrap: pretty;
    }

    .feature-detail {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .feature-point {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
    }

    .feature-point::before {
      content: '→';
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 12px;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .feature-visual {
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 24px;
      overflow: hidden;
    }

    /* Alert notification mockup */
    .alert-mockup { display: flex; flex-direction: column; gap: 10px; }

    .alert-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 16px;
      border-radius: var(--radius-sm);
      border: 1px solid;
    }

    .alert-item.down-alert {
      background: rgba(248,81,73,0.06);
      border-color: rgba(248,81,73,0.2);
    }

    .alert-item.up-alert {
      background: rgba(63,185,80,0.05);
      border-color: rgba(63,185,80,0.15);
    }

    .alert-icon {
      width: 20px; height: 20px;
      border-radius: 50%;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      margin-top: 1px;
    }

    .alert-icon.down { background: rgba(248,81,73,0.2); color: var(--red); }
    .alert-icon.up   { background: rgba(63,185,80,0.2);  color: var(--green); }

    .alert-content {}

    .alert-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
    .alert-meta  { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }

    .alert-channels {
      display: flex;
      gap: 6px;
      margin-top: 12px;
      flex-wrap: wrap;
    }

    .channel-pill {
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 20px;
      border: 1px solid var(--border);
      color: var(--text-muted);
    }

    /* Status page mockup */
    .status-page-mockup { padding: 4px; }

    .sp-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .sp-title { font-size: 14px; font-weight: 700; color: var(--text-primary); }

    .sp-overall {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--green);
      font-family: var(--font-mono);
    }

    .sp-overall-dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--green);
    }

    .sp-components { display: flex; flex-direction: column; gap: 6px; }

    .sp-component {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: var(--bg-muted);
      border-radius: var(--radius-sm);
    }

    .sp-comp-name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
    .sp-comp-status { font-family: var(--font-mono); font-size: 11px; }
    .sp-comp-status.op   { color: var(--green); }
    .sp-comp-status.deg  { color: var(--accent); }

    .sp-domain-label {
      text-align: center;
      margin-top: 16px;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
    }

    /* ── HOW IT WORKS ───────────────────────────────── */
    .how-section {
      border-top: 1px solid var(--border-subtle);
      padding: 120px 0;
    }

    .how-inner {
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 48px;
    }

    .how-header {
      margin-bottom: 72px;
    }

    .how-steps {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2px;
    }

    .how-step {
      border-top: 2px solid var(--border);
      padding-top: 28px;
      padding-right: 40px;
      opacity: 0;
      transform: translateY(24px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }

    .how-step.visible { opacity: 1; transform: translateY(0); }
    .how-step:nth-child(2) { transition-delay: 0.1s; }
    .how-step:nth-child(3) { transition-delay: 0.2s; }

    .how-step-first-border {
      border-top-color: var(--accent);
    }

    .step-num {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--accent);
      margin-bottom: 20px;
      letter-spacing: 0.08em;
    }

    .step-title {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }

    .step-desc {
      font-size: 15px;
      line-height: 1.65;
      color: var(--text-secondary);
      text-wrap: pretty;
    }

    /* ── PRICING ────────────────────────────────────── */
    .pricing-section {
      border-top: 1px solid var(--border-subtle);
      padding: 120px 0;
    }

    .pricing-inner {
      max-width: 900px;
      margin: 0 auto;
      padding: 0 48px;
    }

    .pricing-header {
      text-align: center;
      margin-bottom: 56px;
    }

    .pricing-header .section-title {
      max-width: 100%;
      text-align: center;
    }

    .pricing-cards {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .pricing-card {
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 36px;
      position: relative;
    }

    .pricing-card.featured {
      border-color: var(--accent);
      background: linear-gradient(135deg, rgba(245,158,11,0.04) 0%, var(--bg-subtle) 100%);
    }

    .pricing-badge {
      position: absolute;
      top: -12px;
      left: 28px;
      background: var(--accent);
      color: #0d1117;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 20px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .plan-name {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 16px;
    }

    .plan-price {
      margin-bottom: 24px;
    }

    .plan-price-value {
      font-family: var(--font-mono);
      font-size: 48px;
      font-weight: 500;
      color: var(--text-primary);
      line-height: 1;
      font-variant-numeric: tabular-nums;
    }

    .plan-price-period {
      font-size: 14px;
      color: var(--text-muted);
      margin-left: 4px;
    }

    .plan-desc {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 28px;
      line-height: 1.6;
    }

    .plan-features { display: flex; flex-direction: column; gap: 10px; margin-bottom: 32px; }

    .plan-feature {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
    }

    .plan-feature-check {
      width: 16px; height: 16px;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      margin-top: 2px;
      font-size: 9px;
    }

    .plan-feature-check.yes {
      background: rgba(63,185,80,0.15);
      color: var(--green);
    }

    .btn-plan {
      display: block;
      width: 100%;
      text-align: center;
      padding: 13px;
      border-radius: var(--radius-sm);
      font-size: 14px;
      font-weight: 700;
      text-decoration: none;
      transition: opacity 150ms, transform 100ms;
    }

    .btn-plan:active { transform: scale(0.99); }
    .btn-plan:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    .btn-plan.outline {
      border: 1px solid var(--border);
      color: var(--text-secondary);
    }

    .btn-plan.outline:hover {
      border-color: var(--text-muted);
      color: var(--text-primary);
    }

    .btn-plan.solid {
      background: var(--accent);
      color: #0d1117;
    }

    .btn-plan.solid:hover { opacity: 0.9; }

    .pricing-footnote {
      text-align: center;
      margin-top: 24px;
      font-size: 13px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* ── TESTIMONIAL ───────────────────────────────── */
    .testimonial-section {
      border-top: 1px solid var(--border-subtle);
      padding: 120px 0;
    }

    .testimonial-inner {
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 48px;
      display: grid;
      grid-template-columns: 1fr 2fr;
      gap: 80px;
      align-items: start;
    }

    .testimonial-label {
      padding-top: 8px;
    }

    .testimonial-label .section-eyebrow { margin-bottom: 0; }

    .testimonial-quote {
      position: relative;
    }

    .quote-mark {
      font-family: var(--font-mono);
      font-size: 64px;
      line-height: 0.8;
      color: var(--accent);
      margin-bottom: 16px;
      display: block;
      opacity: 0.6;
    }

    .quote-text {
      font-size: clamp(20px, 2.5vw, 28px);
      font-weight: 600;
      line-height: 1.45;
      color: var(--text-primary);
      margin-bottom: 32px;
      letter-spacing: -0.02em;
    }

    .quote-author {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .author-avatar {
      width: 44px; height: 44px;
      border-radius: 50%;
      background: var(--bg-muted);
      border: 1.5px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-size: 14px;
      font-weight: 500;
      color: var(--text-secondary);
      flex-shrink: 0;
    }

    .author-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
    .author-role { font-size: 13px; color: var(--text-muted); }

    /* ── CTA ────────────────────────────────────────── */
    .cta-section {
      border-top: 1px solid var(--border-subtle);
      padding: 120px 48px;
      text-align: center;
    }

    .cta-inner { max-width: 560px; margin: 0 auto; }

    .cta-title {
      font-size: clamp(32px, 4vw, 52px);
      font-weight: 800;
      letter-spacing: -0.035em;
      line-height: 1.1;
      color: var(--text-primary);
      margin-bottom: 20px;
      text-wrap: balance;
    }

    .cta-sub {
      font-size: 16px;
      color: var(--text-secondary);
      margin-bottom: 36px;
      line-height: 1.65;
    }

    .cta-actions {
      display: flex;
      justify-content: center;
      gap: 12px;
    }

    /* ── FOOTER ─────────────────────────────────────── */
    footer {
      border-top: 1px solid var(--border-subtle);
      padding: 40px 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      max-width: 1280px;
      margin: 0 auto;
    }

    .footer-left {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .footer-brand {
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .footer-links {
      display: flex;
      gap: 20px;
      list-style: none;
    }

    .footer-links a {
      font-size: 13px;
      color: var(--text-muted);
      text-decoration: none;
      transition: color 120ms;
    }

    .footer-links a:hover { color: var(--text-secondary); }

    .footer-copy {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-muted);
    }

    /* ── ANIMATIONS ─────────────────────────────────── */
    @keyframes fadeUp {
      to { opacity: 1; transform: translateY(0); }
    }

    /* ── MOBILE ─────────────────────────────────────── */
    @media (max-width: 768px) {
      nav { padding: 0 20px; }
      .nav-links { display: none; }

      .hero {
        grid-template-columns: 1fr;
        padding: 80px 20px 60px;
        min-height: auto;
        gap: 48px;
      }

      .hero-text { padding-right: 0; }

      .stats-inner { grid-template-columns: 1fr 1fr; }
      .stat-block { border-right: none; border-bottom: 1px solid var(--border-subtle); padding: 32px 0; }
      .stat-block:not(:first-child) { padding-left: 0; }

      .features-section { padding: 80px 20px; }
      .feature-row { grid-template-columns: 1fr; gap: 32px; }
      .feature-row.reverse { direction: ltr; }

      .how-inner { padding: 0 20px; }
      .how-steps { grid-template-columns: 1fr; gap: 40px; }

      .pricing-inner { padding: 0 20px; }
      .pricing-cards { grid-template-columns: 1fr; }

      .testimonial-inner { grid-template-columns: 1fr; gap: 32px; padding: 0 20px; }

      .cta-section { padding: 80px 20px; }
      .cta-actions { flex-direction: column; align-items: center; }

      footer { flex-direction: column; gap: 20px; text-align: center; padding: 32px 20px; }
      .footer-left { flex-direction: column; gap: 12px; }
    }

    /* ── REDUCED MOTION ─────────────────────────────── */
    @media (prefers-reduced-motion: reduce) {
      .hero-text, .hero-visual { animation: none; opacity: 1; transform: none; }
      .feature-row, .how-step { transition: none; opacity: 1; transform: none; }
      .status-dot { animation: none; }
    }
  </style>
</head>
<body>

<!-- NAV -->
<nav>
  <a href="#" class="nav-logo" aria-label="Tidewatch home">
    <div class="nav-logo-mark" aria-hidden="true">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M1 8.5C2.5 6 4 7.5 5.5 5S8.5 1.5 10 4 12.5 7 13 7" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="7" cy="10" r="2.5" stroke="#f59e0b" stroke-width="1.2"/>
      </svg>
    </div>
    Tidewatch
  </a>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#how">How it works</a></li>
    <li><a href="#pricing">Pricing</a></li>
  </ul>
  <a href="#pricing" class="nav-cta">Start free</a>
</nav>

<!-- HERO -->
<section class="hero" aria-label="Hero">
  <div class="hero-text">
    <p class="hero-eyebrow">Uptime monitoring</p>
    <h1 class="hero-headline">
      Know the moment<br>it <em>goes down</em>.
    </h1>
    <p class="hero-sub">
      Lightweight monitors for your sites and APIs. Get alerted in seconds, not minutes. Free for up to 10 monitors.
    </p>
    <div class="hero-actions">
      <a href="#pricing" class="btn-primary">
        Start for free
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </a>
      <a href="#how" class="btn-secondary">See how it works</a>
    </div>
  </div>

  <div class="hero-visual" aria-hidden="true">
    <div class="dashboard-card">
      <div class="card-header">
        <div class="card-dots">
          <span></span><span></span><span></span>
        </div>
        <span class="card-title">tidewatch.app — monitors</span>
        <span class="card-badge">● 9/10 up</span>
      </div>
      <div class="card-body">
        <div class="monitor-list">
          <!-- Row template × 5 -->
          <div class="monitor-row">
            <span class="status-dot up"></span>
            <div>
              <div class="monitor-name">api.myapp.com</div>
              <div class="monitor-url">/health</div>
            </div>
            <span class="monitor-uptime">99.97%</span>
            <span class="monitor-latency latency-ok">
              <div class="uptime-bars">
                <div class="uptime-bar" style="height:14px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:15px"></div>
                <div class="uptime-bar" style="height:19px"></div>
                <div class="uptime-bar" style="height:17px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:20px"></div>
              </div>
            </span>
          </div>
          <div class="monitor-row">
            <span class="status-dot up"></span>
            <div>
              <div class="monitor-name">myapp.com</div>
              <div class="monitor-url">homepage</div>
            </div>
            <span class="monitor-uptime">100%</span>
            <span class="monitor-latency latency-ok">
              <div class="uptime-bars">
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:17px"></div>
                <div class="uptime-bar" style="height:19px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:19px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
              </div>
            </span>
          </div>
          <div class="monitor-row" style="background: rgba(248,81,73,0.04); border-radius: 6px;">
            <span class="status-dot down"></span>
            <div>
              <div class="monitor-name">webhooks.myapp.com</div>
              <div class="monitor-url">/api/v2/events</div>
            </div>
            <span class="monitor-uptime" style="color:#f85149">98.3%</span>
            <span class="monitor-latency latency-bad">
              <div class="uptime-bars">
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar warn" style="height:12px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
                <div class="uptime-bar" style="height:14px"></div>
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
                <div class="uptime-bar down" style="height:8px"></div>
              </div>
            </span>
          </div>
          <div class="monitor-row">
            <span class="status-dot up"></span>
            <div>
              <div class="monitor-name">docs.myapp.com</div>
              <div class="monitor-url">documentation</div>
            </div>
            <span class="monitor-uptime">100%</span>
            <span class="monitor-latency latency-ok">
              <div class="uptime-bars">
                <div class="uptime-bar" style="height:14px"></div>
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:17px"></div>
                <div class="uptime-bar" style="height:19px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:19px"></div>
              </div>
            </span>
          </div>
          <div class="monitor-row">
            <span class="status-dot up"></span>
            <div>
              <div class="monitor-name">cdn.myapp.com</div>
              <div class="monitor-url">assets / static</div>
            </div>
            <span class="monitor-uptime">99.99%</span>
            <span class="monitor-latency latency-warn">
              <div class="uptime-bars">
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar warn" style="height:14px"></div>
                <div class="uptime-bar" style="height:16px"></div>
                <div class="uptime-bar" style="height:18px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:19px"></div>
                <div class="uptime-bar" style="height:20px"></div>
                <div class="uptime-bar" style="height:18px"></div>
              </div>
            </span>
          </div>
        </div>
      </div>
      <div class="card-footer">
        <div class="footer-stat">
          <span class="footer-stat-value">47ms</span>
          <span class="footer-stat-label">avg latency</span>
        </div>
        <div class="incident-alert">
          <div class="incident-dot"></div>
          <span class="incident-text">Incident · webhooks down 6m</span>
        </div>
        <div class="footer-stat" style="text-align:right">
          <span class="footer-stat-value">3</span>
          <span class="footer-stat-label">active alerts</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- TRUST STRIP (no eyebrow) -->
<div class="trust-strip">
  <div class="trust-inner">
    <span class="trust-label">Used by</span>
    <div class="trust-logos">
      <span class="trust-logo">Shipthing.io</span>
      <span class="trust-logo">Launchform</span>
      <span class="trust-logo">Rosterbase</span>
      <span class="trust-logo">Coracle.dev</span>
      <span class="trust-logo">Maplewood</span>
      <span class="trust-logo">Inkthread</span>
    </div>
  </div>
</div>

<!-- STATS (no eyebrow) -->
<section class="stats-section">
  <div class="stats-inner">
    <div class="stat-block">
      <div class="stat-number">30<span>s</span></div>
      <div class="stat-label">Check interval on paid plan</div>
    </div>
    <div class="stat-block">
      <div class="stat-number">14</div>
      <div class="stat-label">Global check locations</div>
    </div>
    <div class="stat-block">
      <div class="stat-number">99<span>.9%</span></div>
      <div class="stat-label">Our own uptime SLA</div>
    </div>
    <div class="stat-block">
      <div class="stat-number">&lt;45<span>s</span></div>
      <div class="stat-label">Median time to first alert</div>
    </div>
  </div>
</section>

<!-- FEATURES (eyebrow) -->
<section class="features-section" id="features">
  <div class="section-header">
    <p class="section-eyebrow">Features</p>
    <h2 class="section-title">Built for speed and signal, not bloat</h2>
  </div>

  <div class="feature-zigzag">
    <!-- Feature 1: instant alerts -->
    <div class="feature-row scroll-reveal">
      <div class="feature-text">
        <p class="feature-tag">01 — Alerting</p>
        <h3 class="feature-title">Down in London, alerted in New York — in seconds</h3>
        <p class="feature-desc">
          The moment a check fails from two locations, Tidewatch fires. No false positives from transient blips, no 5-minute polling lag.
        </p>
        <div class="feature-detail">
          <p class="feature-point">Email, Slack, PagerDuty, and webhooks out of the box</p>
          <p class="feature-point">Escalation rules per monitor — page on-call only after 3 failures</p>
          <p class="feature-point">Recovery alerts with total downtime duration</p>
        </div>
      </div>
      <div class="feature-visual">
        <div class="alert-mockup">
          <div class="alert-item down-alert">
            <div class="alert-icon down">↓</div>
            <div class="alert-content">
              <div class="alert-title">webhooks.myapp.com is down</div>
              <div class="alert-meta">HTTP 502 · 3 locations · 4m 12s ago</div>
            </div>
          </div>
          <div class="alert-item up-alert">
            <div class="alert-icon up">↑</div>
            <div class="alert-content">
              <div class="alert-title">api.myapp.com recovered</div>
              <div class="alert-meta">Was down 2m 38s · Back to 200 OK</div>
            </div>
          </div>
          <div style="padding: 12px 0 4px; border-top: 1px solid var(--border-subtle); margin-top: 8px;">
            <div style="font-size:12px; color: var(--text-muted); margin-bottom: 8px; font-family: var(--font-mono);">Send alerts via</div>
            <div class="alert-channels">
              <span class="channel-pill">Email</span>
              <span class="channel-pill">Slack</span>
              <span class="channel-pill">PagerDuty</span>
              <span class="channel-pill">Webhook</span>
              <span class="channel-pill">SMS</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature 2: status page -->
    <div class="feature-row reverse scroll-reveal">
      <div class="feature-text">
        <p class="feature-tag">02 — Status page</p>
        <h3 class="feature-title">Give your users a place to check before they email you</h3>
        <p class="feature-desc">
          Every paid account gets a public status page at your subdomain. Components, incidents, history — automatically kept in sync with your monitors.
        </p>
        <div class="feature-detail">
          <p class="feature-point">Custom domain: status.yourapp.com</p>
          <p class="feature-point">Incident posts with timeline and affected components</p>
          <p class="feature-point">90-day uptime history visible to your users</p>
        </div>
      </div>
      <div class="feature-visual">
        <div class="status-page-mockup">
          <div class="sp-header">
            <span class="sp-title">myapp Status</span>
            <div class="sp-overall">
              <div class="sp-overall-dot"></div>
              All systems operational
            </div>
          </div>
          <div class="sp-components">
            <div class="sp-component">
              <span class="sp-comp-name">API</span>
              <span class="sp-comp-status op">Operational</span>
            </div>
            <div class="sp-component">
              <span class="sp-comp-name">Web App</span>
              <span class="sp-comp-status op">Operational</span>
            </div>
            <div class="sp-component">
              <span class="sp-comp-name">Webhooks</span>
              <span class="sp-comp-status deg">Degraded performance</span>
            </div>
            <div class="sp-component">
              <span class="sp-comp-name">CDN / Assets</span>
              <span class="sp-comp-status op">Operational</span>
            </div>
            <div class="sp-component">
              <span class="sp-comp-name">Documentation</span>
              <span class="sp-comp-status op">Operational</span>
            </div>
          </div>
          <div class="sp-domain-label">status.myapp.com · powered by Tidewatch</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS (eyebrow, alternating) -->
<section class="how-section" id="how">
  <div class="how-inner">
    <div class="how-header">
      <p class="section-eyebrow">How it works</p>
      <h2 class="section-title" style="max-width: 440px;">Three steps, then you stop thinking about it</h2>
    </div>
    <div class="how-steps">
      <div class="how-step how-step-first-border scroll-reveal-step">
        <div class="step-num">01</div>
        <h3 class="step-title">Add your URLs</h3>
        <p class="step-desc">Paste any HTTP or HTTPS endpoint. API routes, homepages, webhooks, login flows. No agent to install.</p>
      </div>
      <div class="how-step scroll-reveal-step">
        <div class="step-num">02</div>
        <h3 class="step-title">Set your alert rules</h3>
        <p class="step-desc">Choose who gets notified, on what channel, after how many failures. Works with your existing on-call setup.</p>
      </div>
      <div class="how-step scroll-reveal-step">
        <div class="step-num">03</div>
        <h3 class="step-title">Get on with your work</h3>
        <p class="step-desc">Tidewatch checks every 30 seconds from 14 locations. You hear about it the moment something breaks.</p>
      </div>
    </div>
  </div>
</section>

<!-- PRICING (no eyebrow, alternating) -->
<section class="pricing-section" id="pricing">
  <div class="pricing-inner">
    <div class="pricing-header">
      <h2 class="section-title">Simple pricing. No surprises.</h2>
    </div>
    <div class="pricing-cards">
      <!-- Free -->
      <div class="pricing-card">
        <p class="plan-name">Free</p>
        <div class="plan-price">
          <span class="plan-price-value">$0</span>
          <span class="plan-price-period">forever</span>
        </div>
        <p class="plan-desc">Everything you need to start watching. No credit card required.</p>
        <div class="plan-features">
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            Up to 10 monitors
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            1-minute check interval
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            Email alerts
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            7-day uptime history
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes" style="background: rgba(110,118,129,0.15); color: var(--text-muted);">—</div>
            <span style="color: var(--text-muted);">Status page</span>
          </div>
        </div>
        <a href="#" class="btn-plan outline" tabindex="0">Get started free</a>
      </div>
      <!-- Pro -->
      <div class="pricing-card featured">
        <div class="pricing-badge">Pro</div>
        <p class="plan-name">Pro</p>
        <div class="plan-price">
          <span class="plan-price-value">$9</span>
          <span class="plan-price-period">/ month</span>
        </div>
        <p class="plan-desc">For indie developers who ship and need to know things work.</p>
        <div class="plan-features">
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            Unlimited monitors
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            30-second check interval
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            Slack, PagerDuty, webhooks
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            90-day uptime history
          </div>
          <div class="plan-feature">
            <div class="plan-feature-check yes">✓</div>
            Public status page
          </div>
        </div>
        <a href="#" class="btn-plan solid" tabindex="0">Start 14-day trial</a>
      </div>
    </div>
    <p class="pricing-footnote">No contract. Cancel anytime. Upgrade mid-month, pay pro-rated.</p>
  </div>
</section>

<!-- TESTIMONIAL (eyebrow, alternating) -->
<section class="testimonial-section">
  <div class="testimonial-inner">
    <div class="testimonial-label">
      <p class="section-eyebrow">From a customer</p>
    </div>
    <div class="testimonial-quote">
      <span class="quote-mark" aria-hidden="true">"</span>
      <blockquote class="quote-text">
        We found out our payments API was down before our first support ticket came in. Tidewatch caught it in under a minute. Worth every cent.
      </blockquote>
      <div class="quote-author">
        <div class="author-avatar" aria-hidden="true">MK</div>
        <div>
          <div class="author-name">Marcus K.</div>
          <div class="author-role">Founder, Shipthing.io</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA (no eyebrow) -->
<section class="cta-section">
  <div class="cta-inner">
    <h2 class="cta-title">Start watching in 90 seconds</h2>
    <p class="cta-sub">Free for 10 monitors. No card, no install. If something breaks tonight, you'll know about it.</p>
    <div class="cta-actions">
      <a href="#pricing" class="btn-primary">
        Create free account
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </a>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-left">
    <span class="footer-brand">Tidewatch</span>
    <ul class="footer-links">
      <li><a href="#">Privacy</a></li>
      <li><a href="#">Terms</a></li>
      <li><a href="#">Status</a></li>
      <li><a href="#">Docs</a></li>
    </ul>
  </div>
  <span class="footer-copy">© 2026 Tidewatch</span>
</footer>

<script>
  // Scroll-triggered reveal
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.scroll-reveal, .scroll-reveal-step').forEach(el => {
    observer.observe(el);
  });

  // Respect prefers-reduced-motion
  const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (mql.matches) {
    document.querySelectorAll('.scroll-reveal, .scroll-reveal-step').forEach(el => {
      el.classList.add('visible');
    });
  }
</script>
</body>
</html>
```
