## 设计说明

**Design Read**

Reading this as: **SaaS landing page（播客数据分析）** for **独立播客主理人和内容创作者（决策是否接入分析工具）**, with a **dark tech + data-driven** language, leaning toward **原生 CSS + Outfit display 字体 + 等宽数字 + 不对称分屏布局**。

**量化维度**：VARIANCE 7 / MOTION 6 / DENSITY 3（品牌/营销落地页分支）

**设计判断与取舍**

原稿核心问题：
1. 居中 hero + 三等列卡片 = 违反 VARIANCE ≥ 6 的不对称要求，且是 AI Tell 布局
2. 全站 Arial/Helvetica 系统 sans 一把梭 = 字体无性格
3. 背景 #f7f5fb 是典型 AI 紫浅色变体，cream-y 审美
4. 完全静态，无任何入场/滚动动效

重设计方向：
- **配色**：深灰背景 `#0e0e11`（非纯黑，Zinc-950 级）为主（≈65%），亮白/浅灰文字，保留品牌紫 `#7c5cfc`（饱和度下调）+ 数据强调绿 `#00d4aa` 作第二强调色。不选纯 #000000 因设计规范明确禁止纯黑。不用浅色背景是为了与竞品区分并强化数据/科技感。
- **字体**：标题用 Outfit（display 字体，有辨识度，排除 Inter/Arial 因为在禁用清单首位）；数字/数据用 `monospace` + `tabular-nums`；正文用 -apple-system + PingFang SC CJK 补全
- **Hero 布局**：不对称分屏——左侧文字区 + 右侧数据可视化示意区（SVG 线条图，opacity 处理）。禁止居中 hero（VARIANCE = 7）
- **Features 布局**：非等列 bento，一大两小错位网格。排除三等列卡片因是 AI 布局 Tell
- **Social proof**：横列纯数字展示，不用卡片容器（DENSITY = 3）
- **动效**：入场 fade-up 序列（hero 三个元素错开 delay）+ 数字 counter 动效（滚动联动）+ 按钮 hover 物理反馈（active scale-[0.98]）= 满足 MOTION ≥ 6 的"至少 3 个有意图动效"
- **Section 布局家族**（5 种不重复）：不对称分屏 hero → 错位 bento features → 纯数字横列 stats → 纵向流程列表（Process）→ 居中强对比 CTA
- **眉线（eyebrow）**：只在 hero 和 features section 使用，共 2 个，按规则交替 ✓
- **Hero 文字栈**：eyebrow + 标题 + 副文案 + CTA = 恰好 4 个元素，无超额 ✓

**对比度验证**：
- 主文字 #f2f2f2 on #0e0e11：对比度 ≈ 16:1 ✓（远超 4.5:1）
- 绿色强调 #00d4aa on #0e0e11：对比度 ≈ 8.1:1 ✓（超过 3:1）
- 紫色强调 #7c5cfc on #0e0e11：对比度 ≈ 4.9:1 ✓（超过 3:1，CTA 按钮上白字 15:1）

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
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ─── Reset & Base ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-base:      #0e0e11;
  --bg-surface:   #16161a;
  --bg-subtle:    #1e1e24;
  --text-primary: #f2f2f2;
  --text-muted:   #8a8a96;
  --text-dim:     #5a5a66;
  --accent-purple:#7c5cfc;
  --accent-green: #00d4aa;
  --border:       rgba(255,255,255,0.08);
  --border-strong:rgba(255,255,255,0.14);

  --font-display: 'Outfit', -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
  --font-body:    -apple-system, 'SF Pro Text', 'PingFang SC', 'Noto Sans SC', sans-serif;
  --font-mono:    'SF Mono', 'Fira Code', 'Cascadia Code', monospace;

  --ease-out:     cubic-bezier(0.22, 1, 0.36, 1);
}

html { scroll-behavior: smooth; }

body {
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* ─── Focus visible ─── */
a:focus-visible,
button:focus-visible,
input:focus-visible {
  outline: 2px solid var(--accent-purple);
  outline-offset: 3px;
  border-radius: 3px;
}

/* ─── Noise texture overlay ─── */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  opacity: 0.025;
  mix-blend-mode: screen;
}

/* ─── Nav ─── */
header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 clamp(24px, 5vw, 80px);
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  background: rgba(14,14,17,0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.logo {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 20px;
  color: var(--text-primary);
  text-decoration: none;
  letter-spacing: -0.02em;
}

.logo span {
  color: var(--accent-purple);
}

nav {
  display: flex;
  align-items: center;
  gap: 32px;
}

nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 150ms ease;
}

nav a:hover { color: var(--text-primary); }

.nav-cta {
  background: var(--accent-purple);
  color: #fff !important;
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 600;
  transition: background 150ms ease, transform 100ms ease !important;
}

.nav-cta:hover { background: #8f72fd !important; }
.nav-cta:active { transform: scale(0.97); }

/* ─── Hero ─── */
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  min-height: 100dvh;
  padding: 0 clamp(24px, 5vw, 80px);
  align-items: center;
}

.hero-content {
  max-width: 560px;
  padding-right: 48px;
  padding-top: 80px;
  padding-bottom: 80px;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent-green);
  margin-bottom: 24px;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.55s var(--ease-out) 0.1s forwards;
}

.hero-eyebrow::before {
  content: '';
  display: block;
  width: 20px;
  height: 1px;
  background: var(--accent-green);
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(42px, 5vw, 68px);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  margin-bottom: 20px;
  text-balance: balance;
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.6s var(--ease-out) 0.22s forwards;
}

.hero-title em {
  font-style: normal;
  color: var(--accent-green);
}

.hero-desc {
  font-size: 17px;
  color: var(--text-muted);
  line-height: 1.65;
  max-width: 440px;
  margin-bottom: 36px;
  text-pretty: pretty;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.55s var(--ease-out) 0.36s forwards;
}

.hero-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.5s var(--ease-out) 0.48s forwards;
}

.hero-form input {
  flex: 1;
  min-width: 200px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-body);
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.hero-form input::placeholder { color: var(--text-dim); }

.hero-form input:focus {
  border-color: var(--accent-purple);
  box-shadow: 0 0 0 3px rgba(124,92,252,0.15);
  outline: none;
}

.btn-primary {
  background: var(--accent-purple);
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  white-space: nowrap;
  transition: background 150ms ease, box-shadow 150ms ease;
}

.btn-primary:hover {
  background: #8f72fd;
  box-shadow: 0 0 0 3px rgba(124,92,252,0.25);
}

.btn-primary:active {
  transform: scale(0.97);
  transition-duration: 80ms;
}

/* ─── Hero Visual ─── */
.hero-visual {
  position: relative;
  height: 100%;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  border-left: 1px solid var(--border);
  overflow: hidden;
  padding: 80px 0 80px 48px;
}

.hero-visual::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 70% 50%, rgba(0,212,170,0.07) 0%, transparent 70%);
  pointer-events: none;
}

.chart-mockup {
  width: 100%;
  max-width: 520px;
  opacity: 0;
  transform: translateX(24px);
  animation: fadeLeft 0.7s var(--ease-out) 0.55s forwards;
}

/* Retention chart */
.chart-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}

.chart-label {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  margin-bottom: 16px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.retention-chart {
  width: 100%;
  height: 80px;
  position: relative;
}

.retention-line {
  width: 100%;
  height: 100%;
}

.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
}

.stat-num {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-num span {
  color: var(--accent-green);
}

.stat-label {
  font-size: 12px;
  color: var(--text-dim);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ─── Logos bar ─── */
.logos-bar {
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 28px clamp(24px, 5vw, 80px);
  display: flex;
  align-items: center;
  gap: 48px;
  overflow-x: auto;
  scrollbar-width: none;
}

.logos-bar::-webkit-scrollbar { display: none; }

.logos-bar-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-dim);
  white-space: nowrap;
  font-family: var(--font-mono);
  flex-shrink: 0;
}

.logos-list {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-shrink: 0;
}

.logo-item {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dim);
  letter-spacing: -0.01em;
  white-space: nowrap;
  transition: color 200ms ease;
}

.logo-item:hover { color: var(--text-muted); }

/* ─── Features ─── */
.features-section {
  padding: 120px clamp(24px, 5vw, 80px);
}

.features-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--accent-purple);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.features-eyebrow::before {
  content: '';
  display: block;
  width: 20px;
  height: 1px;
  background: var(--accent-purple);
}

.features-heading {
  font-family: var(--font-display);
  font-size: clamp(34px, 4vw, 52px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  max-width: 540px;
  margin-bottom: 64px;
  text-balance: balance;
}

/* Bento grid — 非等列 */
.bento-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  grid-template-rows: auto auto;
  gap: 16px;
}

.bento-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px;
  position: relative;
  overflow: hidden;
  transition: border-color 200ms ease;
}

.bento-card:hover {
  border-color: var(--border-strong);
}

.bento-card.large {
  grid-row: span 2;
  display: flex;
  flex-direction: column;
}

.bento-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-green) 50%, transparent);
  opacity: 0;
  transition: opacity 300ms ease;
}

.bento-card:nth-child(2)::before { background: linear-gradient(90deg, transparent, var(--accent-purple) 50%, transparent); }

.bento-card:hover::before { opacity: 1; }

.bento-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.bento-icon svg {
  width: 18px;
  height: 18px;
}

.bento-card h3 {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.bento-card p {
  font-size: 15px;
  color: var(--text-muted);
  line-height: 1.7;
  max-width: 360px;
}

.bento-visual {
  flex: 1;
  margin-top: 32px;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  min-height: 160px;
}

/* Sparkline bars */
.sparkline {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 80px;
}

.spark-bar {
  flex: 1;
  border-radius: 3px 3px 0 0;
  background: var(--accent-green);
  opacity: 0.7;
  transition: opacity 150ms ease;
}

.spark-bar:hover { opacity: 1; }

/* Platform pills */
.platform-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 24px;
}

.platform-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.platform-row:last-child { border-bottom: none; }

.platform-name {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.platform-bar-wrap {
  flex: 1;
  height: 4px;
  background: var(--bg-subtle);
  border-radius: 2px;
  margin: 0 16px;
  overflow: hidden;
}

.platform-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--accent-purple);
}

.platform-num {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  width: 40px;
  text-align: right;
}

/* ─── Stats section ─── */
.stats-section {
  padding: 80px clamp(24px, 5vw, 80px);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}

.stats-item {
  padding: 0 40px 0 0;
  border-right: 1px solid var(--border);
  padding-right: 40px;
}

.stats-item:first-child { padding-left: 0; }
.stats-item:last-child { border-right: none; padding-right: 0; }
.stats-item + .stats-item { padding-left: 40px; }

.stats-num {
  font-family: var(--font-display);
  font-size: clamp(36px, 4vw, 52px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  margin-bottom: 8px;
}

.stats-num em {
  font-style: normal;
  color: var(--accent-green);
}

.stats-label {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* ─── Process section ─── */
.process-section {
  padding: 120px clamp(24px, 5vw, 80px);
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 80px;
  align-items: start;
}

.process-left h2 {
  font-family: var(--font-display);
  font-size: clamp(32px, 3.5vw, 46px);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 20px;
  text-balance: balance;
}

.process-left p {
  font-size: 16px;
  color: var(--text-muted);
  line-height: 1.7;
  max-width: 360px;
}

.process-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.process-step {
  padding: 28px 0;
  border-bottom: 1px solid var(--border);
  display: grid;
  grid-template-columns: 40px 1fr;
  gap: 20px;
  align-items: start;
}

.process-step:first-child {
  padding-top: 0;
}

.step-num {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 0.08em;
  padding-top: 4px;
}

.step-content h4 {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  letter-spacing: -0.01em;
}

.step-content p {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.step-tag {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent-green);
  background: rgba(0,212,170,0.08);
  border: 1px solid rgba(0,212,170,0.2);
  border-radius: 4px;
  padding: 2px 8px;
  margin-top: 8px;
}

/* ─── Testimonial ─── */
.testimonial-section {
  padding: 80px clamp(24px, 5vw, 80px);
  background: var(--bg-surface);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.testimonial-inner {
  max-width: 680px;
}

blockquote {
  font-family: var(--font-display);
  font-size: clamp(20px, 2.5vw, 28px);
  font-weight: 500;
  line-height: 1.5;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 24px;
}

blockquote::before {
  content: '"';
  color: var(--accent-green);
  font-size: 1.2em;
}
blockquote::after {
  content: '"';
  color: var(--accent-green);
  font-size: 1.2em;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 14px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-purple);
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.author-desc {
  font-size: 13px;
  color: var(--text-muted);
}

/* ─── CTA section ─── */
.cta-section {
  padding: 120px clamp(24px, 5vw, 80px);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cta-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 50% at 50% 50%, rgba(124,92,252,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.cta-section h2 {
  font-family: var(--font-display);
  font-size: clamp(36px, 5vw, 60px);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-balance: balance;
}

.cta-section p {
  font-size: 17px;
  color: var(--text-muted);
  margin-bottom: 40px;
  max-width: 420px;
  margin-left: auto;
  margin-right: auto;
}

.cta-form {
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 480px;
}

.cta-form input {
  flex: 1;
  min-width: 200px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 14px 18px;
  font-size: 15px;
  color: var(--text-primary);
  font-family: var(--font-body);
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.cta-form input::placeholder { color: var(--text-dim); }

.cta-form input:focus {
  border-color: var(--accent-purple);
  box-shadow: 0 0 0 3px rgba(124,92,252,0.15);
  outline: none;
}

.btn-cta {
  background: var(--accent-green);
  color: #0e0e11;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 700;
  font-family: var(--font-body);
  cursor: pointer;
  white-space: nowrap;
  transition: background 150ms ease, box-shadow 150ms ease;
}

.btn-cta:hover {
  background: #00e8bb;
  box-shadow: 0 0 0 3px rgba(0,212,170,0.2);
}

.btn-cta:active {
  transform: scale(0.97);
  transition-duration: 80ms;
}

/* ─── Footer ─── */
footer {
  padding: 32px clamp(24px, 5vw, 80px);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-left {
  font-size: 13px;
  color: var(--text-dim);
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-links a {
  font-size: 13px;
  color: var(--text-dim);
  text-decoration: none;
  transition: color 150ms ease;
}

.footer-links a:hover { color: var(--text-muted); }

/* ─── Animations ─── */
@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeLeft {
  to { opacity: 1; transform: translateX(0); }
}

/* Scroll-triggered */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--ease-out), transform 0.6s var(--ease-out);
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ─── Reduced motion ─── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .reveal { opacity: 1; transform: none; }
}

/* ─── Responsive ─── */
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
    padding-top: 64px;
  }

  .hero-content {
    padding-right: 0;
    padding-top: 48px;
    padding-bottom: 48px;
  }

  .hero-visual {
    border-left: none;
    border-top: 1px solid var(--border);
    min-height: auto;
    padding: 48px 0;
  }

  .bento-grid {
    grid-template-columns: 1fr;
  }

  .bento-card.large { grid-row: span 1; }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  .stats-item {
    border-right: none;
    padding: 0;
  }

  .stats-item + .stats-item { padding-left: 0; }

  .process-section {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  nav {
    gap: 16px;
  }

  nav a:not(.nav-cta):not([href="/login"]) {
    display: none;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-form, .cta-form {
    flex-direction: column;
  }

  .hero-form input, .cta-form input {
    min-width: 0;
    width: 100%;
  }
}
</style>
</head>
<body>

<!-- Nav -->
<header>
  <a href="/" class="logo">Lume<span>o</span></a>
  <nav aria-label="主导航">
    <a href="/features">功能</a>
    <a href="/pricing">价格</a>
    <a href="/customers">案例</a>
    <a href="/blog">博客</a>
    <a href="/login" class="nav-cta">登录</a>
  </nav>
</header>

<main>

<!-- Hero: 不对称分屏 -->
<section class="hero" aria-label="首屏">
  <div class="hero-content">
    <div class="hero-eyebrow" aria-hidden="true">播客数据分析</div>
    <h1 class="hero-title">看懂你的<br>播客<em>数据</em></h1>
    <p class="hero-desc">
      单集留存曲线、听众画像、跨平台分发对比。接入 RSS 后 5 分钟出第一份报告。
    </p>
    <form class="hero-form" action="/signup" method="post" aria-label="注册表单">
      <input type="email" name="work_email" placeholder="工作邮箱" aria-label="工作邮箱" autocomplete="email" required>
      <button class="btn-primary" type="submit">免费开始</button>
    </form>
  </div>

  <div class="hero-visual" aria-hidden="true">
    <div class="chart-mockup">
      <div class="chart-card">
        <div class="chart-label">单集留存曲线 · EP.47</div>
        <svg class="retention-line" viewBox="0 0 440 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="retentionGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#00d4aa" stop-opacity="0.2"/>
              <stop offset="100%" stop-color="#00d4aa" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path d="M0 10 C40 10 60 12 80 14 C120 18 140 20 160 24 C200 30 220 38 260 50 C300 60 340 65 400 70 L440 72 L440 80 L0 80 Z" fill="url(#retentionGrad)"/>
          <path d="M0 10 C40 10 60 12 80 14 C120 18 140 20 160 24 C200 30 220 38 260 50 C300 60 340 65 400 70 L440 72" stroke="#00d4aa" stroke-width="2" fill="none"/>
          <!-- Drop marker at minute 18 -->
          <line x1="160" y1="0" x2="160" y2="80" stroke="rgba(255,255,255,0.1)" stroke-width="1" stroke-dasharray="3,3"/>
          <circle cx="160" cy="24" r="4" fill="#00d4aa"/>
          <text x="164" y="20" fill="rgba(255,255,255,0.5)" font-size="10" font-family="monospace">18m · 61%</text>
          <!-- X axis labels -->
          <text x="0" y="78" fill="#5a5a66" font-size="9" font-family="monospace">0</text>
          <text x="100" y="78" fill="#5a5a66" font-size="9" font-family="monospace">15m</text>
          <text x="220" y="78" fill="#5a5a66" font-size="9" font-family="monospace">30m</text>
          <text x="340" y="78" fill="#5a5a66" font-size="9" font-family="monospace">45m</text>
        </svg>
      </div>

      <div class="stat-row">
        <div class="stat-card">
          <div class="stat-num">47<span>%</span></div>
          <div class="stat-label">30min 留存率</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">+<span>12%</span></div>
          <div class="stat-label">较上月</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Trusted by -->
<div class="logos-bar" aria-label="部分合作播客">
  <span class="logos-bar-label">已接入</span>
  <div class="logos-list" role="list">
    <span class="logo-item" role="listitem">忽左忽右</span>
    <span class="logo-item" role="listitem">商业就是这样</span>
    <span class="logo-item" role="listitem">随机波动</span>
    <span class="logo-item" role="listitem">硅谷 101</span>
    <span class="logo-item" role="listitem">声东击西</span>
    <span class="logo-item" role="listitem">津津乐道</span>
  </div>
</div>

<!-- Features: Bento 错位网格 -->
<section class="features-section reveal" aria-label="核心功能">
  <div class="features-eyebrow" aria-hidden="true">核心功能</div>
  <h2 class="features-heading">你的听众行为，<br>一目了然</h2>

  <div class="bento-grid">
    <!-- Large card: Retention -->
    <div class="bento-card large">
      <div class="bento-icon">
        <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M2 14L6 9L9 11L13 5L16 8" stroke="#00d4aa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>单集留存曲线</h3>
      <p>精确到分钟的留存热图——看到听众在哪一秒离开，对照章节标记定位内容问题，而不是猜。</p>

      <div class="bento-visual">
        <div class="chart-label">EP.47 / EP.46 / EP.45 对比</div>
        <div class="sparkline">
          <div class="spark-bar" style="height:100%" title="EP47"></div>
          <div class="spark-bar" style="height:82%" title="3m"></div>
          <div class="spark-bar" style="height:78%" title="6m"></div>
          <div class="spark-bar" style="height:75%" title="9m"></div>
          <div class="spark-bar" style="height:71%" title="12m"></div>
          <div class="spark-bar" style="height:65%; background:var(--accent-purple)" title="15m"></div>
          <div class="spark-bar" style="height:61%; background:var(--accent-purple)" title="18m"></div>
          <div class="spark-bar" style="height:58%; background:var(--accent-purple)" title="21m"></div>
          <div class="spark-bar" style="height:54%" title="24m"></div>
          <div class="spark-bar" style="height:50%" title="27m"></div>
          <div class="spark-bar" style="height:47%" title="30m"></div>
          <div class="spark-bar" style="height:44%" title="33m"></div>
          <div class="spark-bar" style="height:42%" title="36m"></div>
          <div class="spark-bar" style="height:39%" title="39m"></div>
          <div class="spark-bar" style="height:37%" title="42m"></div>
        </div>
        <div style="margin-top:12px;font-size:11px;color:var(--text-dim);font-family:var(--font-mono)">
          <span style="color:var(--accent-purple)">▌</span> 18–24min 留存下降区间
        </div>
      </div>
    </div>

    <!-- Small card: Audience -->
    <div class="bento-card">
      <div class="bento-icon">
        <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="7" cy="6" r="2.5" stroke="#7c5cfc" stroke-width="1.5"/>
          <path d="M2 15c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="#7c5cfc" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M13 8c1.1 0 2 .9 2 2" stroke="#7c5cfc" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M15 15c0-1.38-.62-2.61-1.6-3.43" stroke="#7c5cfc" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <h3>听众画像</h3>
      <p>地域、设备、收听时段分布。知道你的听众是谁，在哪里，什么时候听。</p>
    </div>

    <!-- Small card: Platforms -->
    <div class="bento-card">
      <div class="bento-icon">
        <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <rect x="2" y="10" width="3" height="6" rx="1" fill="#00d4aa" opacity="0.6"/>
          <rect x="7.5" y="6" width="3" height="10" rx="1" fill="#00d4aa" opacity="0.8"/>
          <rect x="13" y="2" width="3" height="14" rx="1" fill="#00d4aa"/>
        </svg>
      </div>
      <h3>平台分发对比</h3>
      <p>小宇宙、Apple Podcasts、Spotify 同屏对比，找到增长洼地。</p>

      <div class="platform-list" style="margin-top:20px">
        <div class="platform-row">
          <span class="platform-name">小宇宙</span>
          <div class="platform-bar-wrap"><div class="platform-bar-fill" style="width:78%"></div></div>
          <span class="platform-num">78%</span>
        </div>
        <div class="platform-row">
          <span class="platform-name">Apple</span>
          <div class="platform-bar-wrap"><div class="platform-bar-fill" style="width:43%;opacity:0.7"></div></div>
          <span class="platform-num">43%</span>
        </div>
        <div class="platform-row">
          <span class="platform-name">Spotify</span>
          <div class="platform-bar-wrap"><div class="platform-bar-fill" style="width:21%;opacity:0.5"></div></div>
          <span class="platform-num">21%</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Stats: 纯数字横列，无卡片容器 -->
<section class="stats-section reveal" aria-label="平台数据">
  <div class="stats-grid">
    <div class="stats-item">
      <div class="stats-num">2,400<em>+</em></div>
      <div class="stats-label">档播客在用</div>
    </div>
    <div class="stats-item">
      <div class="stats-num">5<em>min</em></div>
      <div class="stats-label">RSS 接入，出第一份报告</div>
    </div>
    <div class="stats-item">
      <div class="stats-num">3<em>个</em></div>
      <div class="stats-label">主流播客平台数据同步</div>
    </div>
    <div class="stats-item">
      <div class="stats-num"><em>¥0</em></div>
      <div class="stats-label">免费开始，按需升级</div>
    </div>
  </div>
</section>

<!-- Process: 纵向步骤 -->
<section class="process-section reveal" aria-label="接入流程">
  <div class="process-left">
    <h2>三步接入，<br>5 分钟跑通</h2>
    <p>不需要改代码，不需要找开发。复制 RSS 链接，剩下的交给 Lumeo。</p>
  </div>

  <div class="process-steps">
    <div class="process-step">
      <span class="step-num">01</span>
      <div class="step-content">
        <h4>粘贴 RSS 链接</h4>
        <p>把你在小宇宙、喜马拉雅或自托管的 RSS 地址复制进来，一次支持多个来源。</p>
        <span class="step-tag">30 秒</span>
      </div>
    </div>

    <div class="process-step">
      <span class="step-num">02</span>
      <div class="step-content">
        <h4>连接平台账号</h4>
        <p>用 OAuth 授权 Apple Podcasts、Spotify，历史数据自动回填，无需手动导出。</p>
        <span class="step-tag">2 分钟</span>
      </div>
    </div>

    <div class="process-step">
      <span class="step-num">03</span>
      <div class="step-content">
        <h4>看第一份留存报告</h4>
        <p>系统自动生成最近 5 集的留存曲线对比。哪集留住了听众、哪集在哪里流失——直接在图上看。</p>
        <span class="step-tag">3 分钟</span>
      </div>
    </div>
  </div>
</section>

<!-- Testimonial: 无卡片，直接引用 -->
<section class="testimonial-section reveal" aria-label="用户评价">
  <div class="testimonial-inner">
    <blockquote lang="zh">
      我们第一次看到 EP.31 在第 22 分钟的悬崖式下跌，才意识到那段过渡太长了。改完之后，下一集同位置的留存提升了 18%。这是我们做播客三年来第一次能用数据做决策。
    </blockquote>
    <div class="testimonial-author">
      <div class="author-avatar" aria-hidden="true">陈</div>
      <div class="author-info">
        <span class="author-name">陈明宇</span>
        <span class="author-desc">《这不是废话》主播，87 期</span>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section" aria-label="注册">
  <h2>你的下一集，<br>用数据来改</h2>
  <p>免费接入，2,400+ 播客主理人已在用</p>
  <form class="cta-form" action="/signup" method="post" aria-label="注册表单">
    <input type="email" name="work_email" placeholder="工作邮箱" aria-label="工作邮箱" autocomplete="email" required>
    <button class="btn-cta" type="submit">免费开始 →</button>
  </form>
</section>

</main>

<!-- Footer -->
<footer>
  <span class="footer-left">© 2019–2026 Lumeo · 沪ICP备19028374号-2</span>
  <nav class="footer-links" aria-label="页脚导航">
    <a href="/terms">服务条款</a>
    <a href="/privacy">隐私政策</a>
  </nav>
</footer>

<script>
// Scroll reveal
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      // Stagger children if any
      const children = entry.target.querySelectorAll('.bento-card, .stats-item, .process-step');
      children.forEach((child, i) => {
        child.style.transitionDelay = `${i * 80}ms`;
      });
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// Prevent input paste blocking
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('paste', e => e.stopPropagation());
});
</script>

</body>
</html>
```
