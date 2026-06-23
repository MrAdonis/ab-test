---
name: text-to-infographic
description: 根据用户给的一段文字，生成一张信息图（infographic）。触发词：信息图、infographic、把这段话做成图、可视化这段文字、图解、一图流。
---

# text-to-infographic

把一段文字转化成可视信息图。内部用 HTML + inline CSS 排版，headless Chrome 渲染截图，**交付物是 PNG 图**，不是 HTML 文件。

## 不适用场景

以下情况**不要用本 skill，改用其他工具**：

- 数据驱动图表（柱状图 / 折线图 / 散点图）→ `/diagram`
- 流程图 / 架构图 / ER 图 → `/diagram`
- 需要持续迭代的设计稿 → 项目框架组件化，不是单文件 HTML
- 文字极少（单句口号 / 标题）→ `/baoyu-infographic`（AI 生图，视觉感更强）
- 需要中文文字在图上绝对精准渲染 → `/baoyu-infographic`（seedream，中文文字不乱码）
- 已有明确的设计风格规范需复现 → 先读项目 `DESIGN.md` 再动手

## 工作流

### Step 1：分析输入文字

读用户给的文字，提取：

- **核心主题**（一句话，用于图的标题区）
- **信息单元**（拆成 3-7 个独立信息块；超过 7 个主动合并相关项）
- **层级关系**（并列 / 因果 / 时序 / 对比 / 分类——决定布局方案）
- **关键数字或词**（放大处理，增加视觉锚点）

### Step 2：选择布局方案

根据信息层级关系，从以下方案中选一个，**不要混用**：

| 信息关系 | 布局方案 |
|---------|---------|
| 并列（几个平等要点） | 网格卡片（2-3 列） |
| 时序 / 流程 | 竖向时间轴 |
| 对比（A vs B） | 左右双栏 |
| 分类树 | 嵌套卡片 |
| 数字重点突出 | 大数字 + 说明文字 |

### Step 3：生成 HTML

写一个自包含 HTML 文件（内联所有 CSS，不引用外部资源）。

**必须满足的视觉约束**（每条带依据，可验证）：

- **留白 ≥30%**：Calimari Rule——信息密度越低，感知档次越高；正文区不铺满整个画布
- **主色 ≤2**（不含黑白灰）：Cleveland & McGill 1984 实测，颜色通道上限 5-7，主色超过 2 会让注意力分散
- **文字对比度 ≥7:1**：WCAG AAA 标准；用 `color-contrast` 工具或肉眼核黑底白字 / 白底深色字
- **字重层级 ≤3 级**：标题 / 副标题 / 正文，三级以上读者难以区分层级
- **字号**：标题 ≥32px，正文 ≥14px（px 不缩放，截图分辨率固定时有效）
- **画布宽度**：固定 900px，高度按内容自适应（但建议单屏 900×600 到 900×1200，超长拆两图）

**[无法量化，保留文字描述]** 构图呼吸感：信息块之间有足够间距，主要信息区与画布边缘留有视觉缓冲，不要把所有内容塞满整张图。

HTML 模板骨架：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 900px;
    min-height: 600px;
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #FAFAF8;
    padding: 60px;
  }
  /* 主色变量——写具体值，不写 CSS var，避免截图时丢变量 */
</style>
</head>
<body>
  <!-- 标题区 -->
  <!-- 信息块区 -->
  <!-- 数据来源（如有） -->
</body>
</html>
```

### Step 4：渲染截图

```bash
# 写入临时 HTML
HTML_PATH="/tmp/infographic-$(date +%s).html"
# [由 agent 写入 HTML 内容到 $HTML_PATH]

# 截图，固定宽度 900，自适应高度
OUTPUT="/tmp/infographic-$(date +%s).png"
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --screenshot="$OUTPUT" \
  --window-size=900,1200 \
  --default-background-color=FAFAF8 \
  --hide-scrollbars \
  "file://$HTML_PATH"
```

如果 Chrome 路径不对，按顺序尝试：
1. `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
2. `/Applications/Chromium.app/Contents/MacOS/Chromium`
3. `chromium-browser`（Linux/Homebrew）

### Step 5：输出对照稿（多方案时）

如果用户输入的信息**有多种合理布局**（Step 2 有 ≥2 个候选方案），默认出 **2-3 个版本**（不超过 3 个，选多了累），命名为 `option-A.png`、`option-B.png`、`option-C.png`。

**校准数量**：默认 2 个（少于 2 没有对比意义，多于 3 选择疲劳）；用户明确要求"多几个"可出到 5 个，超过 5 不建议。

**选定前不覆盖**：候选图全部存 `/tmp/infographic-options/`，用户说"选 B"后才把最终版复制到 `~/Downloads/` 或项目目录。

**[无需对照稿的情况]**：用户明确说"就做一张"、或信息结构唯一对应一种布局，直接出单图，不硬造对照。

### Step 6：压力测试（可选，建议执行）

信息图最常见的交付环境翻车点：**在深色背景 / 深色模式下对比度丢失**。

如果最终用于 X 文章封面、小红书、Slack/Notion 深色界面，追加截一张叠深色背景的版本验证可读性：

```bash
# 在 HTML body 外包一层深色容器后重截，验证深色环境可读
```

如果只用于打印 / 白色背景页面，跳过此步。

## Rules

- **不引用外部资源**：字体、图片、图标全部 inline 或用 Unicode 字符，不写 `<link href="https://...">` 或 `<img src="https://...">`，截图时无网络访问
- **不生成 HTML 文件作为交付物**：交付物只有 PNG，HTML 是中间产物，存 `/tmp/`
- **不往复问确认**：信息块划分、布局选择、配色全部按上面的规则自主决定，完成后展示图让用户看着说；除非用户在原始请求里给了明确约束（"要蓝色""要竖版"），否则不问
- **颜色选择**：默认走"高级感克制"路线——米白底色（`#FAFAF8`）+ 深炭色文字（`#1A1A1A`）+ 一个强调色；强调色从用户文字语义推断（科技→深蓝 `#1A3A6B`，财务→深绿 `#1A5C3A`，警示→深红 `#8B1A1A`，中性→深橙 `#8B4A1A`）
- **中文字体**：body 的 `font-family` 始终带 `"PingFang SC", "Microsoft YaHei"`，不依赖 system-ui 在所有截图环境可用

## 输出格式

完成后告知：

1. 图片绝对路径（如 `/tmp/infographic-1719000000.png`）
2. 用了哪个布局方案，为什么
3. 如果出了多个版本，每个版本一句话说明差异

不要把 HTML 代码贴出来，除非用户主动要求。

## Gotchas

> 只记真实踩过的坑，不记假设。

- **Chrome `--headless=new` 截图高度被截断** → 根因：`--window-size` 的高度是视口高，不是内容高；`--screenshot` 不会自动扩展视口 → 规避：把 HTML 的 `body` 设 `min-height: 1px`，用 `overflow: visible`，同时把 `--window-size` 高度设得足够大（如 `900,3000`），Chrome 会自动裁到实际内容高度
- **中文字体在 headless Chrome 截图里变成方块** → 根因：headless Chrome 没有系统字体访问权限（部分 macOS 版本）→ 规避：`font-family` 加 `"Apple Color Emoji", serif` 作为最终 fallback；如果方块仍出现，换用 Google Fonts 的 Noto Sans SC（但需内联 base64——先判断是否有网络，没网络就接受 fallback 字体）
- **截图背景透明（PNG 看起来全黑）** → 根因：`--default-background-color` 参数不对（有些版本要写 `ffffffff` 不是 `FAFAF8`）→ 规避：在 HTML 的 `body` 加 `background-color: #FAFAF8 !important`，不依赖命令行背景参数
- **联网相关坑（如需抓取外部图片资源）** → 见 `rules/routing.md`
