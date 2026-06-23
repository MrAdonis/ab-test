---
name: chart-render
description: >
  把图表（HTML/SVG/ECharts/Chart.js/D3 等）渲染成图片。
  主路径用 headless Chrome 截 PNG；Chrome/Playwright 不可用时回退导出 SVG。
  依赖 Node 运行时——没有 Node 则无法运行。
---

# chart-render

把图表渲染成图片。主路径：headless Chrome 截 PNG。降级路径：导出 SVG（同样是合格产出）。

---

## Pre-flight Check (REQUIRED)

运行前按顺序检查两层依赖：

**Layer 1 — Node（硬前提，缺失则 MUST stop）：**

```bash
node --version
```

Node 不存在 → **停下，告知用户需要安装 Node.js（≥18），不进入任何后续步骤。**

**Layer 2 — Chrome/Playwright（可降级，失败走 SVG 路径）：**

```bash
# 检查 Playwright 是否安装
npx playwright --version 2>/dev/null && echo "playwright ok" || echo "playwright missing"

# 检查系统 Chrome/Chromium
which google-chrome 2>/dev/null || which chromium 2>/dev/null || which chromium-browser 2>/dev/null || echo "no system chrome"
```

- **Playwright 可用** → 走 PNG 主路径
- **Playwright 缺失但系统 Chrome 存在** → 用系统 Chrome + `--headless` 走 PNG 主路径
- **两者均不可用** → 走 SVG 降级路径（合格产出，告知用户 PNG 不可用原因）
- **Node 缺失** → 硬停，不进降级链

---

## When to Use

- 把 ECharts / Chart.js / D3 / Vega-Lite 等 JS 图表库渲染成静态图片
- 把含图表的 HTML 页面截图存档
- CI/CD 中自动生成报告配图
- 需要在无交互环境中输出图表图片

### 不适用（自我排除）

| 场景 | 替代方案 |
|------|---------|
| 纯服务器端、无 display、无 xvfb | 改用后端渲染库（如 node-canvas、sharp）直接生成 PNG，不走本 skill |
| 图表数据量 > 10 万点，实时渲染 | 先降采样再渲染，或用 Vega-Lite 的 `--vg2png` CLI 直出 PNG |
| 目标是 PDF 多页报告 | 用 Playwright 的 `page.pdf()`，不走本 skill 的截图流程 |
| 没有 Node 运行时的环境 | 本 skill 整体不可用，见 Pre-flight Check |

---

## Workflow

### 主路径：headless Chrome → PNG

**Step 1：准备图表 HTML**

把图表包进一个完整 HTML 文件，图表容器宽高明确写死（避免截图尺寸不稳定）：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { margin: 0; background: white; }
    #chart { width: 800px; height: 500px; }
  </style>
</head>
<body>
  <div id="chart"></div>
  <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
  <script>
    /* 图表初始化代码 */
  </script>
</body>
</html>
```

**Step 2：用 Playwright 截图（优先）**

```bash
# 安装（如未安装）
npm install -D playwright
npx playwright install chromium --with-deps

# 截图脚本（写入 /tmp/render-chart.mjs 再执行）
```

```js
// /tmp/render-chart.mjs
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const htmlPath = process.argv[2];   // 绝对路径
const outPath  = process.argv[3];   // 输出 PNG 绝对路径
const selector = process.argv[4] || '#chart';  // 容器选择器

const browser = await chromium.launch();
const page    = await browser.newPage();

await page.goto(`file://${htmlPath}`);
await page.waitForSelector(selector);
// 等待图表渲染完成（JS 库异步渲染必须等，否则截到空白）
await page.waitForFunction(
  (sel) => {
    const el = document.querySelector(sel);
    return el && el.children.length > 0;
  },
  selector,
  { timeout: 10000 }
);

const el = await page.$(selector);
await el.screenshot({ path: outPath, type: 'png' });
await browser.close();

console.log(JSON.stringify({ success: true, output: outPath }));
```

```bash
node /tmp/render-chart.mjs /absolute/path/chart.html /absolute/path/output.png '#chart'
```

**Step 3：验证产出**

```bash
# 检查文件存在且大小合理（< 1KB 通常是空白截图）
ls -lh /absolute/path/output.png
file /absolute/path/output.png
```

输出 JSON 结构：
```json
{ "success": true, "output": "/absolute/path/output.png" }
```

失败时：
```json
{ "success": false, "error": "timeout waiting for #chart", "fallback": "svg" }
```

---

### 降级路径：导出 SVG

Chrome/Playwright 均不可用时，直接从图表库提取 SVG 字符串：

**ECharts：**

```js
// /tmp/echarts-svg.mjs
import * as echarts from 'echarts';

const chart = echarts.init(null, null, {
  renderer: 'svg',
  ssr: true,
  width: 800,
  height: 500
});

chart.setOption({ /* 你的 option */ });

import fs from 'fs';
const svgStr = chart.renderToSVGString();
fs.writeFileSync(process.argv[2], svgStr);
chart.dispose();

console.log(JSON.stringify({ success: true, output: process.argv[2], format: 'svg' }));
```

```bash
node /tmp/echarts-svg.mjs /absolute/path/output.svg
```

**Chart.js（无 SSR，需用 node-canvas）：**

```bash
npm install canvas chart.js
```

```js
// /tmp/chartjs-png.mjs（canvas 提供 Node 端渲染，直出 PNG，无需 Chrome）
import { createCanvas } from 'canvas';
import { Chart } from 'chart.js/auto';
import fs from 'fs';

const canvas = createCanvas(800, 500);
const ctx = canvas.getContext('2d');

new Chart(ctx, { /* 你的 config */ });

const buf = canvas.toBuffer('image/png');
fs.writeFileSync(process.argv[2], buf);
console.log(JSON.stringify({ success: true, output: process.argv[2], format: 'png' }));
```

**D3（纯 SVG，最轻）：**

```bash
npm install d3 jsdom
```

```js
// /tmp/d3-svg.mjs
import * as d3 from 'd3';
import { JSDOM } from 'jsdom';
import fs from 'fs';

const dom = new JSDOM('<!DOCTYPE html><body></body>');
const body = d3.select(dom.window.document).select('body');

// 在 body 上绘制 D3 图表
const svg = body.append('svg').attr('width', 800).attr('height', 500);
/* 绘图代码 */

fs.writeFileSync(process.argv[2], dom.serialize());
console.log(JSON.stringify({ success: true, output: process.argv[2], format: 'svg' }));
```

---

## 路径选择决策树

```
Node 可用？
├── No  → STOP（告知安装 Node ≥18）
└── Yes
    ├── Playwright 可用？
    │   └── Yes → PNG 主路径（Playwright）
    ├── 系统 Chrome 可用？
    │   └── Yes → PNG 主路径（系统 Chrome + --headless）
    └── 均不可用
        ├── 图表库支持 SSR/Node 渲染？（ECharts ✓, D3+jsdom ✓）
        │   └── Yes → SVG 降级（告知用户 PNG 不可用）
        └── 只有 Chart.js 等需 canvas？
            └── 安装 node-canvas → PNG（无需 Chrome）
```

---

## 关键约束

**脆弱度高，用硬约束：**

1. **容器宽高必须明确写死**，不能用百分比或 `auto`。headless Chrome 默认视口 1280×720，容器不指定尺寸会截到错误大小。

2. **JS 图表库异步渲染必须等待完成再截图**。

   **Bad — 直接截图，拿到空白：**
   ```js
   await page.goto(`file://${htmlPath}`);
   await el.screenshot({ path: outPath });  // 图表还没渲染完
   ```

   **Good — 等待容器有子元素再截图：**
   ```js
   await page.goto(`file://${htmlPath}`);
   await page.waitForSelector('#chart canvas, #chart svg', { timeout: 10000 });
   await el.screenshot({ path: outPath });
   ```

3. **所有路径必须用绝对路径**，`file://` URL 和输出路径都不能是相对路径。

4. **输出产物告知格式**：成功时 JSON 中包含 `format: "png"` 或 `format: "svg"`，让调用方知道拿到的是什么。

5. **SVG 降级是合格产出，不是失败**。只有 Node 不存在才算任务无法完成。

---

## 示例：渐进复杂度

**Basic — ECharts 柱状图 → PNG：**

```bash
# 1. 准备 chart.html（含 #chart div + ECharts 初始化）
# 2. 截图
node /tmp/render-chart.mjs /tmp/chart.html /tmp/output.png '#chart'
```

**With Options — 指定尺寸 + 等待超时：**

```js
await page.setViewportSize({ width: 1200, height: 800 });
await page.waitForSelector('#chart canvas', { timeout: 15000 });
await el.screenshot({ path: outPath, type: 'png' });
```

**Edge Case — 图表含动画，截到中间帧：**

```js
// 禁用动画（ECharts）
chart.setOption({ animation: false });
// 或等待动画结束
await page.waitForTimeout(1000);  // 最后手段，优先用 waitForFunction
```

**SSR 降级 — 无 Chrome 但有 ECharts：**

```bash
npm install echarts
node /tmp/echarts-svg.mjs /tmp/output.svg
```

---

## Gotchas

> 只记真实踩过的坑（执行失败并定位过根因的），不记假设。

_（新 skill，暂无记录。踩坑后按格式补充：**[症状/触发场景]** → 根因：[为什么] → 规避：[具体动作]）_

---

## 依赖版本参考

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Node.js | 18 | ESM + `--experimental-vm-modules` 支持 |
| playwright | 1.40+ | `chromium.launch()` API 稳定 |
| echarts | 5.4+ | `renderToSVGString()` SSR 支持 |
| jsdom | 24+ | D3 服务端渲染 |
| canvas（node-canvas） | 2.11+ | Chart.js Node 端渲染 |
