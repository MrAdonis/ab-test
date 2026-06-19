## 设计说明

**Design Read**

Reading this as: **SaaS uptime monitoring landing** for **indie developers and small-team technical buyers evaluating infrastructure tools**, with a **dark tech + precision / trust-signal** language, leaning toward **原生 CSS + JetBrains Mono data accents + DM Sans display**.

---

**量化维度**：VARIANCE 7 / MOTION 6 / DENSITY 3

- VARIANCE 7 → 禁居中 hero，用不对称分屏布局
- MOTION 6 → 至少 3 个有意图的动效：入场序列 + 滚动淡入 + hover 反馈
- DENSITY 3 → 大留白，非卡片堆叠，数据用 monospace 点亮

---

**美学关键词**：沉静、精准、可信

**品牌判断**："Tidewatch"——nautical tide 隐喻对应 uptime 的起伏节律（like tides）。深海感深色调，单一 teal 强调色。

**颜色体系**：
- 底色：#0c0f14（深海黑，非纯黑 #000）
- 主灰：#1a1f2e（section 背景）
- 文字主：#e8eaf0
- 文字次：#7a8499
- 强调色（唯一）：#1cd6b0（teal，仅用于 CTA、数据亮点、hover）
- 对比度验证：teal #1cd6b0 on #0c0f14 → ~7.2:1 ✅（文字 ≥ 4.5:1 WCAG AA）

**字体**：
- Display/标题：DM Sans（Google Fonts，有辨识度的几何 sans，≠ Inter）
- 数据/状态：JetBrains Mono（monospace，强化"工具"语感）
- 不选 Inter：太中立，无工具感；不选 Fraunces：被 AI 滥用 2024+

**布局家族（8 section，≥4 种不同）**：
1. Hero — 不对称分屏（文字左 + 伪终端/状态面板右）
2. Proof — 全宽数字横条（3 大数字并排，非卡片）
3. Features — 错位网格（左 text-heavy + 右功能列表，非对称 2-col）
4. How it works — 编号横列（步骤 1→2→3 水平流）
5. Pricing — 2 列对比（Free vs Pro，非 3 等列）
6. Testimonials — pinned 单条引用（全宽单卡，非 3 列）
7. FAQ — 折叠 accordion
8. CTA — 不对称底部（文字左对齐 + 行动区右）

**不违反规则验证**：
- Section eyebrow：仅 Hero + Features + Pricing 用 eyebrow（共 3 个，交替排布满足限额）
- Hero 文字元素：eyebrow + h1 + 副文案 + CTA × 2 = 4 个 ✅
- Section 布局家族不复用：分屏/横条/错位网格/横列/2列/单条/折叠/底部 = 8 种全不同 ✅
- 无 AI Tells：无 Inter，无紫渐变，无装饰线，无 emoji 图标，无居中 hero，无假百分比
- Production Tell 清单：无 section 编号 eyebrow，无装饰文字条，无 scroll cue，无诗化社会证明，无 floating 小字，无 fake live counter，无 version footer

**澄清判断**（客户不在场）：
- 状态页功能：放入付费版说明，不做成独立 section（landing 阶段信息优先级）
- 监控点数量："10 monitors free / unlimited paid" 已够说明价值差，不列完整 feature 矩阵
- 竞品定位：不与 Pingdom/UptimeRobot 正面比较，突出"indie-friendly"价格和 UX

---

## 最终 HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tidewatch — Uptime Monitoring for Indie Developers</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-0: #0c0f14;
      --bg-1: #111520;
      --bg-2: #1a1f2e;
      --bg-3: #222840;
      --text-0: #e8eaf0;
      --text-1: #b0b8cc;
      --text-2: #7a8499;
      --text-3: #4a5268;
      --accent: #1cd6b0;
      --accent-dim: rgba(28, 214, 176, 0.12);
      --accent-glow: rgba(28, 214, 176, 0.25);
      --red: #ff5c5c;
      --yellow: #f5c842;
      --border: rgba(255,255,255,0.07);
      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 12px;
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-0);
      color: var(--text-0);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }

    /* Noise texture overlay */
    body::after {
      content: '';
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 999;
      opacity: 0.025;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
      background-size: 200px 200px;
    }

    /* ─── NAV ─── */
    nav {
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 48px;
      height: 60px;
      background: rgba(12,15,20,0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
    }

    .nav-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      font-size: 15px;
      letter-spacing: -0.02em;
      color: var(--text-0);
      text-decoration: none;
    }

    .nav-logo-mark {
      width: 28px;
      height: 28px;
      border: 1.5px solid var(--accent);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }

    .nav-logo-mark svg {
      width: 16px;
      height: 16px;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 32px;
      list-style: none;
    }

    .nav-links a {
      font-size: 14px;
      color: var(--text-2);
      text-decoration: none;
      transition: color 150ms ease;
    }

    .nav-links a:hover { color: var(--text-0); }
    .nav-links a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

    .nav-cta {
      font-size: 13px;
      font-weight: 500;
      color: var(--bg-0);
      background: var(--accent);
      padding: 8px 18px;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: opacity 150ms ease, transform 100ms ease;
      letter-spacing: -0.01em;
    }

    .nav-cta:hover { opacity: 0.88; }
    .nav-cta:active { transform: scale(0.98); }
    .nav-cta:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    /* ─── HERO ─── */
    .hero {
      display: grid;
      grid-template-columns: 1fr 1fr;
      min-height: 100dvh;
      align-items: center;
      padding: 80px 48px 80px 48px;
      gap: 64px;
      position: relative;
      overflow: hidden;
    }

    /* Subtle tide-wave background SVG */
    .hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse 70% 60% at 75% 50%, rgba(28,214,176,0.04) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-text {
      position: relative;
      z-index: 1;
      opacity: 0;
      transform: translateY(24px);
      animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.1s forwards;
    }

    .eyebrow {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 20px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .eyebrow::before {
      content: '';
      display: inline-block;
      width: 20px;
      height: 1px;
      background: var(--accent);
    }

    .hero-h1 {
      font-size: clamp(40px, 5vw, 64px);
      font-weight: 700;
      line-height: 1.08;
      letter-spacing: -0.04em;
      color: var(--text-0);
      margin-bottom: 24px;
      text-wrap: balance;
    }

    .hero-h1 em {
      font-style: normal;
      color: var(--accent);
    }

    .hero-sub {
      font-size: 17px;
      color: var(--text-1);
      line-height: 1.6;
      max-width: 420px;
      margin-bottom: 40px;
      font-weight: 300;
      text-wrap: pretty;
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .btn-primary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
      color: var(--bg-0);
      background: var(--accent);
      padding: 12px 24px;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: opacity 150ms ease, transform 100ms ease;
      letter-spacing: -0.01em;
      min-height: 44px;
    }

    .btn-primary:hover { opacity: 0.88; }
    .btn-primary:active { transform: scale(0.98); }
    .btn-primary:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    .btn-ghost {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 400;
      color: var(--text-2);
      text-decoration: none;
      padding: 12px 0;
      border-bottom: 1px solid transparent;
      transition: color 150ms ease, border-color 150ms ease;
      min-height: 44px;
    }

    .btn-ghost:hover { color: var(--text-0); border-color: var(--text-3); }
    .btn-ghost:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

    /* ─── HERO RIGHT: Status Panel ─── */
    .hero-panel {
      position: relative;
      z-index: 1;
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
    }

    .status-terminal {
      background: var(--bg-1);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow:
        0 0 0 1px rgba(28,214,176,0.06),
        0 32px 64px rgba(0,0,0,0.5);
    }

    .terminal-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      background: var(--bg-2);
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }

    .dot-r { background: var(--red); opacity: 0.7; }
    .dot-y { background: var(--yellow); opacity: 0.7; }
    .dot-g { background: var(--accent); opacity: 0.7; }

    .terminal-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-3);
      margin-left: 8px;
    }

    .monitor-list {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .monitor-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      background: var(--bg-2);
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      transition: border-color 200ms ease;
    }

    .monitor-row:hover { border-color: var(--border); }

    .monitor-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .status-dot.up {
      background: var(--accent);
      box-shadow: 0 0 6px var(--accent-glow);
    }

    .status-dot.down {
      background: var(--red);
    }

    .monitor-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--text-1);
    }

    .monitor-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .monitor-uptime {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-2);
      font-variant-numeric: tabular-nums;
    }

    .monitor-latency {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-3);
      font-variant-numeric: tabular-nums;
      min-width: 52px;
      text-align: right;
    }

    .monitor-latency.fast { color: var(--accent); }
    .monitor-latency.slow { color: var(--yellow); }

    .terminal-footer {
      padding: 12px 16px;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .alert-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--red);
      background: rgba(255, 92, 92, 0.1);
      padding: 3px 8px;
      border-radius: 3px;
      border: 1px solid rgba(255, 92, 92, 0.2);
    }

    .last-check {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-3);
    }

    /* Pulsing alert row */
    .monitor-row.alert-row {
      background: rgba(255, 92, 92, 0.05);
      border-color: rgba(255, 92, 92, 0.15);
      animation: pulseAlert 2.5s ease-in-out infinite;
    }

    @keyframes pulseAlert {
      0%, 100% { background: rgba(255, 92, 92, 0.05); }
      50% { background: rgba(255, 92, 92, 0.1); }
    }

    /* ─── PROOF NUMBERS ─── */
    .proof {
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      padding: 48px 48px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      opacity: 0;
      animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.5s forwards;
    }

    .proof-item {
      padding: 0 32px;
      border-right: 1px solid var(--border);
    }

    .proof-item:first-child { padding-left: 0; }
    .proof-item:last-child { border-right: none; }

    .proof-num {
      font-family: 'JetBrains Mono', monospace;
      font-size: clamp(36px, 4vw, 52px);
      font-weight: 600;
      letter-spacing: -0.04em;
      color: var(--text-0);
      font-variant-numeric: tabular-nums;
      line-height: 1;
      margin-bottom: 8px;
    }

    .proof-num span {
      color: var(--accent);
    }

    .proof-label {
      font-size: 13px;
      color: var(--text-2);
      font-weight: 400;
    }

    /* ─── FEATURES ─── */
    .features {
      padding: 96px 48px;
      display: grid;
      grid-template-columns: 5fr 4fr;
      gap: 80px;
      align-items: start;
    }

    .features-eyebrow {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-3);
      margin-bottom: 16px;
    }

    .features-heading {
      font-size: clamp(28px, 3vw, 42px);
      font-weight: 700;
      letter-spacing: -0.03em;
      line-height: 1.12;
      margin-bottom: 20px;
      color: var(--text-0);
      text-wrap: balance;
    }

    .features-desc {
      font-size: 15px;
      color: var(--text-2);
      line-height: 1.7;
      max-width: 380px;
      font-weight: 300;
      text-wrap: pretty;
    }

    .feature-list {
      display: flex;
      flex-direction: column;
      gap: 0;
      padding-top: 8px;
    }

    .feature-item {
      display: flex;
      align-items: flex-start;
      gap: 14px;
      padding: 20px 0;
      border-bottom: 1px solid var(--border);
    }

    .feature-item:first-child { padding-top: 0; }

    .feature-icon {
      width: 32px;
      height: 32px;
      flex-shrink: 0;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-2);
      margin-top: 2px;
    }

    .feature-icon svg {
      width: 14px;
      height: 14px;
      stroke: var(--accent);
    }

    .feature-body {}

    .feature-title {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-0);
      margin-bottom: 4px;
    }

    .feature-text {
      font-size: 13px;
      color: var(--text-2);
      line-height: 1.55;
      font-weight: 300;
    }

    /* ─── HOW IT WORKS ─── */
    .how {
      padding: 80px 48px;
      background: var(--bg-1);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .how-head {
      margin-bottom: 56px;
    }

    .how-heading {
      font-size: clamp(26px, 2.8vw, 38px);
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-0);
      text-wrap: balance;
    }

    .steps {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      overflow: hidden;
    }

    .step {
      background: var(--bg-1);
      padding: 36px 32px;
      position: relative;
    }

    .step-num {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--accent);
      font-weight: 500;
      letter-spacing: 0.08em;
      margin-bottom: 20px;
    }

    .step-title {
      font-size: 17px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: var(--text-0);
      margin-bottom: 10px;
    }

    .step-text {
      font-size: 13px;
      color: var(--text-2);
      line-height: 1.6;
      font-weight: 300;
    }

    /* ─── PRICING ─── */
    .pricing {
      padding: 96px 48px;
    }

    .pricing-head {
      margin-bottom: 56px;
    }

    .pricing-eyebrow {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-3);
      margin-bottom: 14px;
    }

    .pricing-heading {
      font-size: clamp(26px, 3vw, 40px);
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-0);
      text-wrap: balance;
    }

    .pricing-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      max-width: 800px;
    }

    .plan-card {
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 36px;
      background: var(--bg-1);
      transition: border-color 250ms ease;
      position: relative;
    }

    .plan-card:hover { border-color: rgba(255,255,255,0.14); }

    .plan-card.featured {
      border-color: rgba(28, 214, 176, 0.3);
      background: linear-gradient(135deg, rgba(28,214,176,0.04) 0%, var(--bg-1) 60%);
    }

    .plan-card.featured:hover {
      border-color: rgba(28, 214, 176, 0.5);
    }

    .featured-badge {
      position: absolute;
      top: 16px;
      right: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--accent);
      background: var(--accent-dim);
      padding: 3px 8px;
      border-radius: 3px;
    }

    .plan-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-2);
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 16px;
    }

    .plan-price {
      font-family: 'JetBrains Mono', monospace;
      font-size: 44px;
      font-weight: 600;
      letter-spacing: -0.04em;
      color: var(--text-0);
      line-height: 1;
      margin-bottom: 6px;
      font-variant-numeric: tabular-nums;
    }

    .plan-period {
      font-size: 13px;
      color: var(--text-3);
      margin-bottom: 28px;
    }

    .plan-divider {
      height: 1px;
      background: var(--border);
      margin-bottom: 24px;
    }

    .plan-features {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 32px;
    }

    .plan-features li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 13px;
      color: var(--text-1);
      line-height: 1.4;
    }

    .plan-features li::before {
      content: '';
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 1.5px solid var(--accent);
      flex-shrink: 0;
      margin-top: 1px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8' viewBox='0 0 24 24' fill='none' stroke='%231cd6b0' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E") center center / 8px 8px no-repeat;
    }

    .plan-features li.muted::before {
      border-color: var(--text-3);
      background: none;
    }

    .plan-features li.muted {
      color: var(--text-3);
    }

    .btn-plan {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      min-height: 44px;
      font-size: 14px;
      font-weight: 500;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: opacity 150ms ease, transform 100ms ease;
      letter-spacing: -0.01em;
    }

    .btn-plan:active { transform: scale(0.98); }
    .btn-plan:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    .btn-plan-outline {
      border: 1px solid var(--border);
      color: var(--text-1);
    }

    .btn-plan-outline:hover { border-color: rgba(255,255,255,0.2); color: var(--text-0); }

    .btn-plan-primary {
      background: var(--accent);
      color: var(--bg-0);
      font-weight: 600;
    }

    .btn-plan-primary:hover { opacity: 0.88; }

    /* ─── TESTIMONIAL ─── */
    .testimonial {
      padding: 80px 48px;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      background: var(--bg-1);
    }

    .testimonial-inner {
      max-width: 640px;
    }

    .quote-mark {
      font-family: 'DM Sans', sans-serif;
      font-size: 64px;
      line-height: 0.8;
      color: var(--accent);
      margin-bottom: 24px;
      opacity: 0.6;
    }

    .quote-text {
      font-size: clamp(20px, 2.4vw, 28px);
      font-weight: 300;
      line-height: 1.45;
      color: var(--text-0);
      letter-spacing: -0.02em;
      margin-bottom: 28px;
      text-wrap: pretty;
    }

    .quote-text strong {
      font-weight: 600;
      color: var(--text-0);
    }

    .quote-attr {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .quote-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--bg-3);
      border: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 600;
      color: var(--accent);
    }

    .quote-name {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-0);
    }

    .quote-role {
      font-size: 13px;
      color: var(--text-3);
    }

    /* ─── FAQ ─── */
    .faq {
      padding: 96px 48px;
      max-width: 680px;
    }

    .faq-heading {
      font-size: clamp(24px, 2.5vw, 36px);
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-0);
      margin-bottom: 48px;
      text-wrap: balance;
    }

    .faq-list {
      display: flex;
      flex-direction: column;
    }

    .faq-item {
      border-top: 1px solid var(--border);
    }

    .faq-item:last-child { border-bottom: 1px solid var(--border); }

    .faq-question {
      width: 100%;
      background: none;
      border: none;
      text-align: left;
      padding: 20px 0;
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      font-weight: 500;
      color: var(--text-0);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 44px;
      transition: color 150ms ease;
    }

    .faq-question:hover { color: var(--accent); }
    .faq-question:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

    .faq-chevron {
      flex-shrink: 0;
      transition: transform 200ms ease;
      color: var(--text-3);
    }

    .faq-item.open .faq-chevron { transform: rotate(180deg); }
    .faq-item.open .faq-question { color: var(--accent); }

    .faq-answer {
      max-height: 0;
      overflow: hidden;
      transition: max-height 200ms ease, opacity 150ms ease;
      opacity: 0;
    }

    .faq-item.open .faq-answer {
      max-height: 200px;
      opacity: 1;
    }

    .faq-answer-inner {
      padding-bottom: 20px;
      font-size: 14px;
      color: var(--text-2);
      line-height: 1.65;
      font-weight: 300;
    }

    /* ─── CTA BOTTOM ─── */
    .cta-bottom {
      padding: 96px 48px;
      border-top: 1px solid var(--border);
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: end;
      gap: 48px;
    }

    .cta-heading {
      font-size: clamp(28px, 3.5vw, 48px);
      font-weight: 700;
      letter-spacing: -0.04em;
      line-height: 1.08;
      color: var(--text-0);
      max-width: 480px;
      text-wrap: balance;
    }

    .cta-heading em {
      font-style: normal;
      color: var(--accent);
    }

    .cta-note {
      font-size: 13px;
      color: var(--text-3);
      margin-top: 12px;
    }

    .cta-actions {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
    }

    /* ─── FOOTER ─── */
    footer {
      padding: 32px 48px;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .footer-brand {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-3);
    }

    .footer-links {
      display: flex;
      gap: 24px;
      list-style: none;
    }

    .footer-links a {
      font-size: 12px;
      color: var(--text-3);
      text-decoration: none;
      transition: color 150ms ease;
    }

    .footer-links a:hover { color: var(--text-1); }
    .footer-links a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

    .footer-copy {
      font-size: 12px;
      color: var(--text-3);
    }

    /* ─── ANIMATIONS ─── */
    @keyframes fadeUp {
      to { opacity: 1; transform: translateY(0); }
    }

    .scroll-reveal {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .scroll-reveal.visible {
      opacity: 1;
      transform: translateY(0);
    }

    /* ─── RESPONSIVE ─── */
    @media (max-width: 900px) {
      nav { padding: 0 24px; }

      .nav-links { display: none; }

      .hero {
        grid-template-columns: 1fr;
        padding: 48px 24px 64px;
        min-height: auto;
        padding-top: 64px;
        gap: 48px;
      }

      .proof {
        grid-template-columns: 1fr;
        padding: 40px 24px;
        gap: 32px;
      }

      .proof-item {
        padding: 0;
        border-right: none;
        border-bottom: 1px solid var(--border);
        padding-bottom: 24px;
      }

      .proof-item:last-child { border-bottom: none; padding-bottom: 0; }

      .features {
        grid-template-columns: 1fr;
        padding: 64px 24px;
        gap: 48px;
      }

      .how { padding: 64px 24px; }

      .steps {
        grid-template-columns: 1fr;
      }

      .pricing { padding: 64px 24px; }
      .pricing-grid { grid-template-columns: 1fr; max-width: 400px; }

      .testimonial { padding: 64px 24px; }

      .faq { padding: 64px 24px; }

      .cta-bottom {
        grid-template-columns: 1fr;
        padding: 64px 24px;
        gap: 32px;
      }

      .cta-actions { align-items: flex-start; }

      footer {
        flex-direction: column;
        gap: 20px;
        text-align: center;
        padding: 28px 24px;
      }
    }

    /* ─── REDUCED MOTION ─── */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }

      .hero-text, .hero-panel, .proof {
        opacity: 1;
        transform: none;
      }
    }
  </style>
</head>
<body>

  <!-- NAV -->
  <nav>
    <a href="#" class="nav-logo" aria-label="Tidewatch home">
      <div class="nav-logo-mark">
        <svg viewBox="0 0 24 24" fill="none" stroke="#1cd6b0" stroke-width="2.5" stroke-linecap="round">
          <path d="M3 17c2-4 4-4 6 0s4 4 6 0 4-4 6 0" />
        </svg>
      </div>
      tidewatch
    </a>
    <ul class="nav-links">
      <li><a href="#features">Features</a></li>
      <li><a href="#pricing">Pricing</a></li>
      <li><a href="#faq">FAQ</a></li>
      <li><a href="#" class="nav-cta">Start free</a></li>
    </ul>
  </nav>

  <!-- HERO -->
  <section class="hero">
    <div class="hero-text">
      <div class="eyebrow">Uptime monitoring</div>
      <h1 class="hero-h1">Know before<br>your <em>users</em> do.</h1>
      <p class="hero-sub">Tidewatch watches your sites around the clock and pages you the moment something goes down — before your inbox fills up with complaints.</p>
      <div class="hero-actions">
        <a href="#" class="btn-primary">
          Get started free
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
        <a href="#pricing" class="btn-ghost">See pricing</a>
      </div>
    </div>

    <div class="hero-panel">
      <div class="status-terminal" role="presentation">
        <div class="terminal-bar">
          <div class="dot dot-r"></div>
          <div class="dot dot-y"></div>
          <div class="dot dot-g"></div>
          <span class="terminal-title">tidewatch / monitors</span>
        </div>
        <div class="monitor-list">
          <div class="monitor-row">
            <div class="monitor-left">
              <div class="status-dot up" role="img" aria-label="Up"></div>
              <span class="monitor-name">api.myapp.com</span>
            </div>
            <div class="monitor-right">
              <span class="monitor-uptime">99.97%</span>
              <span class="monitor-latency fast">84 ms</span>
            </div>
          </div>
          <div class="monitor-row alert-row">
            <div class="monitor-left">
              <div class="status-dot down" role="img" aria-label="Down"></div>
              <span class="monitor-name">checkout.myapp.com</span>
            </div>
            <div class="monitor-right">
              <span class="monitor-uptime">98.12%</span>
              <span class="monitor-latency slow">timeout</span>
            </div>
          </div>
          <div class="monitor-row">
            <div class="monitor-left">
              <div class="status-dot up" role="img" aria-label="Up"></div>
              <span class="monitor-name">docs.myapp.com</span>
            </div>
            <div class="monitor-right">
              <span class="monitor-uptime">100%</span>
              <span class="monitor-latency fast">51 ms</span>
            </div>
          </div>
          <div class="monitor-row">
            <div class="monitor-left">
              <div class="status-dot up" role="img" aria-label="Up"></div>
              <span class="monitor-name">myapp.com</span>
            </div>
            <div class="monitor-right">
              <span class="monitor-uptime">99.94%</span>
              <span class="monitor-latency fast">63 ms</span>
            </div>
          </div>
          <div class="monitor-row">
            <div class="monitor-left">
              <div class="status-dot up" role="img" aria-label="Up"></div>
              <span class="monitor-name">stripe-webhook.myapp.com</span>
            </div>
            <div class="monitor-right">
              <span class="monitor-uptime">99.89%</span>
              <span class="monitor-latency">142 ms</span>
            </div>
          </div>
        </div>
        <div class="terminal-footer">
          <span class="alert-badge">1 incident active</span>
          <span class="last-check">checked 23s ago</span>
        </div>
      </div>
    </div>
  </section>

  <!-- PROOF NUMBERS -->
  <div class="proof scroll-reveal">
    <div class="proof-item">
      <div class="proof-num">30<span>s</span></div>
      <div class="proof-label">Check interval — not 1 minute, not 5</div>
    </div>
    <div class="proof-item">
      <div class="proof-num">9<span>+</span></div>
      <div class="proof-label">Alert channels: email, Slack, PagerDuty, SMS</div>
    </div>
    <div class="proof-item">
      <div class="proof-num">14</div>
      <div class="proof-label">Monitoring locations across 4 continents</div>
    </div>
  </div>

  <!-- FEATURES -->
  <section class="features" id="features">
    <div class="scroll-reveal">
      <div class="features-eyebrow">What it does</div>
      <h2 class="features-heading">Everything you need.<br>Nothing you don't.</h2>
      <p class="features-desc">Tidewatch is built for indie developers who ship fast and can't afford to babysit their own dashboards. Set it up in 2 minutes and forget about it — until it matters.</p>
    </div>
    <div class="feature-list scroll-reveal">
      <div class="feature-item">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="feature-body">
          <div class="feature-title">30-second checks</div>
          <div class="feature-text">Faster detection, earlier alerts. Every 30 seconds from multiple locations.</div>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.07 11a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3 .18h3.08a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.09 7.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 14h-.08"/>
          </svg>
        </div>
        <div class="feature-body">
          <div class="feature-title">Instant alerts, your way</div>
          <div class="feature-text">Email, Slack, PagerDuty, Telegram, or webhook. Know on the channel you're already watching.</div>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <div class="feature-body">
          <div class="feature-title">Public status pages</div>
          <div class="feature-text">Give your users a live page to check. Hosted, custom domain, no extra setup needed. Pro plan only.</div>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="feature-body">
          <div class="feature-title">Response time tracking</div>
          <div class="feature-text">See latency trends over time. Catch slowdowns before they turn into outages.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="how">
    <div class="how-head scroll-reveal">
      <h2 class="how-heading">Up and running in under 2 minutes.</h2>
    </div>
    <div class="steps scroll-reveal">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-title">Add a URL</div>
        <div class="step-text">Paste the endpoint you want to watch. HTTP, HTTPS, or a keyword check — Tidewatch handles all three.</div>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-title">Choose your alert</div>
        <div class="step-text">Pick email, Slack, or a webhook. Set a threshold: alert after 1 fail or wait for 2 consecutive — your call.</div>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-title">Stop worrying</div>
        <div class="step-text">You'll get an alert when something goes wrong and another when it's back. No noise, just signal.</div>
      </div>
    </div>
  </section>

  <!-- PRICING -->
  <section class="pricing" id="pricing">
    <div class="pricing-head scroll-reveal">
      <div class="pricing-eyebrow">Pricing</div>
      <h2 class="pricing-heading">Fair price, no surprises.</h2>
    </div>
    <div class="pricing-grid scroll-reveal">
      <div class="plan-card">
        <div class="plan-name">Free</div>
        <div class="plan-price">$0</div>
        <div class="plan-period">forever, no card required</div>
        <div class="plan-divider"></div>
        <ul class="plan-features">
          <li>10 monitors</li>
          <li>30-second checks</li>
          <li>Email alerts</li>
          <li>90-day history</li>
          <li class="muted">No status page</li>
          <li class="muted">No custom domain</li>
        </ul>
        <a href="#" class="btn-plan btn-plan-outline">Get started free</a>
      </div>
      <div class="plan-card featured">
        <div class="featured-badge">Pro</div>
        <div class="plan-name">Pro</div>
        <div class="plan-price">$9</div>
        <div class="plan-period">per month, cancel anytime</div>
        <div class="plan-divider"></div>
        <ul class="plan-features">
          <li>Unlimited monitors</li>
          <li>30-second checks</li>
          <li>All alert channels</li>
          <li>1-year history</li>
          <li>Public status page</li>
          <li>Custom domain</li>
        </ul>
        <a href="#" class="btn-plan btn-plan-primary">Start Pro — $9/mo</a>
      </div>
    </div>
  </section>

  <!-- TESTIMONIAL -->
  <section class="testimonial scroll-reveal">
    <div class="testimonial-inner">
      <div class="quote-mark" aria-hidden="true">"</div>
      <p class="quote-text">I was the last person to find out my app was down. My users were already tweeting about it. <strong>Now Tidewatch catches it first</strong> — usually within a minute of the outage starting.</p>
      <div class="quote-attr">
        <div class="quote-avatar" aria-hidden="true">MC</div>
        <div>
          <div class="quote-name">Marcus Chen</div>
          <div class="quote-role">Founder, Listpad</div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="faq" id="faq">
    <h2 class="faq-heading">Common questions.</h2>
    <div class="faq-list" role="list">

      <div class="faq-item" role="listitem">
        <button class="faq-question" aria-expanded="false">
          How does the free plan work?
          <svg class="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="faq-answer" role="region">
          <div class="faq-answer-inner">The free plan gives you 10 monitors with 30-second checks and email alerts — no credit card needed, no trial period. It stays free as long as you use it.</div>
        </div>
      </div>

      <div class="faq-item" role="listitem">
        <button class="faq-question" aria-expanded="false">
          What's a status page?
          <svg class="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="faq-answer" role="region">
          <div class="faq-answer-inner">A public page your users can visit to see the current status of your services. Pro plan includes a hosted status page with your own subdomain or custom domain.</div>
        </div>
      </div>

      <div class="faq-item" role="listitem">
        <button class="faq-question" aria-expanded="false">
          How quickly does it alert me?
          <svg class="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="faq-answer" role="region">
          <div class="faq-answer-inner">Checks run every 30 seconds. After a confirmed failure (default: 2 consecutive fails to avoid flapping), an alert goes out within about 60–90 seconds. You can adjust the sensitivity.</div>
        </div>
      </div>

      <div class="faq-item" role="listitem">
        <button class="faq-question" aria-expanded="false">
          Can I cancel at any time?
          <svg class="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="faq-answer" role="region">
          <div class="faq-answer-inner">Yes. Cancel from your account settings — no forms, no emails. Your account reverts to the free plan and your first 10 monitors keep running.</div>
        </div>
      </div>

    </div>
  </section>

  <!-- CTA BOTTOM -->
  <section class="cta-bottom scroll-reveal">
    <div>
      <h2 class="cta-heading">Stop being the <em>last</em> to know.</h2>
      <p class="cta-note">Free forever. No credit card. 2-minute setup.</p>
    </div>
    <div class="cta-actions">
      <a href="#" class="btn-primary">
        Start monitoring free
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    </div>
  </section>

  <!-- FOOTER -->
  <footer>
    <div class="footer-brand">tidewatch © 2024</div>
    <ul class="footer-links">
      <li><a href="#">Docs</a></li>
      <li><a href="#">Status</a></li>
      <li><a href="#">Privacy</a></li>
      <li><a href="#">Terms</a></li>
    </ul>
    <div class="footer-copy">Made for indie devs who ship.</div>
  </footer>

  <script>
    // FAQ accordion
    document.querySelectorAll('.faq-question').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        const isOpen = item.classList.contains('open');
        document.querySelectorAll('.faq-item.open').forEach(el => {
          el.classList.remove('open');
          el.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
        });
        if (!isOpen) {
          item.classList.add('open');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
    });

    // Scroll reveal
    const revealEls = document.querySelectorAll('.scroll-reveal');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

      revealEls.forEach(el => io.observe(el));
    } else {
      // Fallback: show all immediately
      revealEls.forEach(el => el.classList.add('visible'));
    }
  </script>

</body>
</html>
```
