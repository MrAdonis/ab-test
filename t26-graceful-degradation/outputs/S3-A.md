---
name: chart-to-image
description: Render a chart or diagram to an image file. Primary path: headless Chrome → PNG screenshot. Fallback: export SVG (valid output when Chrome/Playwright unavailable). Requires Node.js runtime — stops hard if Node is absent.
---

# chart-to-image

把图表渲染成图片。主路径用 headless Chrome 截 PNG；Chrome/Playwright 不可用时回退导出 SVG，SVG 同样是合格产出。整个流程依赖 Node 运行时。

## Pre-flight Check (REQUIRED)

执行任何渲染前，**必须**先跑这一段：

```bash
# 1. Node 运行时——缺失则硬停，无 fallback
node --version 2>/dev/null || echo "NODE_MISSING"
```

Node 缺失时 **MUST stop**，告知用户：`chart-to-image 需要 Node.js，请先安装（brew install node 或 https://nodejs.org）`。**Do NOT** 尝试用其他语言运行时替代。

```bash
# 2. 检测渲染路径可用性（Node 存在后再跑）
node -e "require('playwright')" 2>/dev/null && echo "PLAYWRIGHT_OK" || echo "PLAYWRIGHT_MISSING"
which google-chrome-stable chromium-browser chromium 2>/dev/null | head -1 || echo "CHROME_BIN_MISSING"
```

根据检测结果选路径：

| 检测结果 | 渲染路径 | 产出格式 |
|---------|---------|---------|
| Playwright OK **或** Chrome 二进制存在 | 主路径：headless Chrome 截图 | PNG |
| 两者皆缺 | 回退路径：导出 SVG | SVG |

SVG 回退是合格产出，不是降级失败——告知用户"Chrome/Playwright 不可用，已输出 SVG"，继续执行，不报错停止。

## Workflow

### 主路径：headless Chrome → PNG

**Step 1** 准备图表 HTML

把图表源（ECharts / D3 / Chart.js / Mermaid 等）包装成独立 HTML 文件，图表填满整个 `<body>`，无滚动条，无外部依赖（所有资源内联或走 CDN）。

```bash
# 最小结构示例
cat > /tmp/chart-render.html << 'HTML'
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>body{margin:0;padding:0;}</style>
</head>
<body>
  <!-- 图表容器，宽高由 JS 设 -->
  <div id="chart" style="width:800px;height:600px;"></div>
  <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
  <script>
    const chart = echarts.init(document.getElementById('chart'));
    chart.setOption(CHART_OPTION_JSON);
  </script>
</body></html>
HTML
```

将 `CHART_OPTION_JSON` 替换为实际图表配置。

**Step 2** headless Chrome 截图

```bash
# 优先用 Playwright（自带 Chromium，最稳定）
node - << 'JS'
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 800, height: 600 });
  await page.goto('file:///tmp/chart-render.html');
  // 等待图表渲染完成——读 #chart 的 canvas/svg 子元素出现
  await page.waitForSelector('#chart canvas, #chart svg', { timeout: 10000 });
  await page.screenshot({ path: '/tmp/chart-output.png', fullPage: false });
  await browser.close();
  console.log('DONE:/tmp/chart-output.png');
})();
JS
```

如果 Playwright 不可用，改用系统 Chrome：

```bash
CHROME=$(which google-chrome-stable chromium-browser chromium 2>/dev/null | head -1)
"$CHROME" \
  --headless=new \
  --disable-gpu \
  --window-size=800,600 \
  --screenshot=/tmp/chart-output.png \
  "file:///tmp/chart-render.html"
echo "DONE:/tmp/chart-output.png"
```

**Step 3** 验证产出

```bash
# 文件存在且大于 1KB 才算成功
[ -s /tmp/chart-output.png ] && \
  node -e "const fs=require('fs'); const s=fs.statSync('/tmp/chart-output.png'); console.log('SIZE:'+s.size)" || \
  echo "OUTPUT_EMPTY_OR_MISSING"
```

输出 `OUTPUT_EMPTY_OR_MISSING` 时进 Gotchas 排查，不直接报"完成"。

### 回退路径：导出 SVG

Chrome/Playwright 均不可用时执行此路径。

```bash
node - << 'JS'
// 根据图表库选对应导出方式
// ECharts: chart.renderToSVGString()
// D3: 直接序列化 document.querySelector('svg').outerHTML
// Mermaid: mermaid.render() 返回 svg 字符串
const fs = require('fs');
// 将 SVG 字符串写入文件
fs.writeFileSync('/tmp/chart-output.svg', SVG_STRING);
console.log('DONE_SVG:/tmp/chart-output.svg');
JS
```

SVG 回退必须告知用户：`Chrome/Playwright 不可用，已输出 SVG（/tmp/chart-output.svg）。SVG 可在浏览器直接打开或用 Inkscape 转 PNG。`

## 输出契约

成功时 stdout 最后一行格式固定：

- PNG 主路径：`DONE:<绝对路径>.png`
- SVG 回退：`DONE_SVG:<绝对路径>.svg`

**读最后一行、取冒号后面的路径。** 不要 parse 中间的渲染日志。状态判断：

- 最后一行以 `DONE:` 或 `DONE_SVG:` 开头 → 成功，路径有效
- 出现 `OUTPUT_EMPTY_OR_MISSING` → 渲染完成但文件异常，进 Gotchas §1
- 出现 `NODE_MISSING` → 前置未满足，停下装 Node

`DONE` 不等于图表内容正确——检查文件实际大小（< 5KB 的 PNG 几乎肯定是空白页），进 Gotchas §2。

## 边界声明：不适用场景

以下场景此 skill **不处理**，改用对应工具：

- 需要把 PNG 进一步嵌入 PDF/DOCX/PPTX → `/pdf` / `/docx` / `/pptx` skill
- 图表源是 Python（matplotlib/seaborn/plotly）→ 直接 `plt.savefig()` / `fig.write_image()`，不需要绕 headless Chrome
- 需要 AI 生成配图/海报（不是确定性数据图表）→ `/baoyu-infographic` 或 codex-imagen.sh
- 工程架构图/流程图（Mermaid/Graphviz 文本描述）→ `/diagram` skill（SVG 确定性渲染，不需截图）

判断口诀：数据驱动的图表（柱/线/饼/散点）→ 本 skill；视觉设计类或纯文本描述的结构图 → 其他 skill。

## Gotchas

> 只记执行此 skill 时的专属坑。联网/抓取相关见 `rules/routing.md`，调试方法论见 `rules/coding.md`。

- **§1 PNG 文件存在但全白（< 5KB）** → 根因：图表库的异步渲染在截图前未完成（ECharts `setOption` 是异步的，`waitForSelector` 等到容器但 canvas 内容还空）→ 规避：在 HTML 里用图表库的 `finished` 事件或 `chart.on('finished', ...)` 回调，渲染完成后在页面里 `document.title = 'READY'`，截图前改等 `waitForFunction(() => document.title === 'READY')`

- **§2 `--headless=new` flag 在旧版 Chrome（< 112）不识别** → 根因：旧版只支持 `--headless`（无 `=new`）→ 规避：先试 `--headless=new`，exit code 非 0 时降级为 `--headless`

- **§3 file:// 协议下 CDN 脚本加载失败（跨域 / 离线环境）** → 根因：headless Chrome 对 `file://` 页面的 CORS 策略，CDN 资源有时被阻 → 规避：加 `--disable-web-security --allow-file-access-from-files`（仅临时渲染场景可接受），或改用内联 bundle（`npx webpack --bundle`）

- **§4 SVG 回退路径：ECharts 在纯 Node 环境无 DOM** → 根因：ECharts 的 `renderToSVGString()` 需要 `canvas` / `jsdom` 环境，裸 Node 没有 → 规避：`npm install jsdom canvas` 后用 `const { JSDOM } = require('jsdom')` 模拟 DOM，或改用 `echarts-node-canvas` 包

- **§5 Playwright 安装后找不到 Chromium** → 根因：`npm install playwright` 只装了驱动，未下浏览器二进制 → 规避：运行 `npx playwright install chromium`，确认输出 `chromium X.X.X installed`
