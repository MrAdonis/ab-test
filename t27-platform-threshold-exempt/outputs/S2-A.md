---
name: poster-cover
description: 生成营销海报/封面图。将"高级感、配色克制、有呼吸感"等主观品味要求落成 agent 可确定性执行的视觉规则，输出 HTML+headless Chrome 渲染截图或 AI 生图 prompt。触发词：海报、封面、宣传图、KV图、banner、cover。
---

# Poster / Cover 生成 Skill

## When to Use

用户说"出张海报""做封面""生成 KV 图""宣传图"时触发。明确要求"代码组件化、纳入项目迭代"→ 不走本 skill，改用项目框架组件。纯结构图（流程/架构/ER）→ 不走本 skill，改用 `/diagram`。

## 路由决策（动手前先选路）

| 需求特征 | 路由 |
|---------|------|
| 有中文文字且要求精准渲染 / 生产级成品 | HTML + headless Chrome 截图 |
| 临时配图 / mockup / 无中文文字要求 | `~/.claude/scripts/codex-imagen.sh`（免费，codex 订阅） |
| X 文章封面 / 小红书封面 / 高质量 AI 风格图 | `/baoyu-infographic` + `memory/reference_x_article_cover_prompts.md` |

本 skill 覆盖 **HTML + headless Chrome** 这条路，是三者里唯一能确定性渲染中文文字的路径。

## 核心规则：主观品味 → 可测阈值

主观词"高级感 / 克制 / 呼吸感"全部拆成可验证规则。**每条阈值必须带依据**，裸数字等于堆料。

### 留白

留白面积 ≥ 画面总面积的 30%（Calimari Rule：信息密度越低，感知档次越高。来源：John Calimari 设计密度研究，高端品牌广告的实证归纳）。

检查方式：估算主体+文字占用的像素面积，剩余部分 / 总面积 ≥ 0.30。

### 主色数

主色 ≤ 2 种（不含纯白/纯黑）。来源：Cleveland & McGill 1984 认知实验——颜色编码上限 5-7 类时人眼开始混淆，营销单页视觉焦点高度集中，阈值压到 2 种才能维持"克制"感。

辅色（点缀、描边）允许 1 种，不计入主色。渐变算 1 种颜色，不另计。

### 对比度

正文字与背景对比度 ≥ 4.5:1（WCAG AA），标题字与背景 ≥ 7:1（WCAG AAA）。来源：W3C Web Content Accessibility Guidelines 2.1，是领域公认的最低可读性标准。

工具验证：`npx contrast-ratio <fg-hex> <bg-hex>` 或在线工具 contrast-ratio.com。

### 字重层级

全图字重层级 ≤ 3 级（如：主标题 700 / 副标题 500 / 正文 400）。超过 3 级视觉层次会崩散，来源：Robert Bringhurst《The Elements of Typographic Style》§4.3。

字号最小值：正文 ≥ 14px（屏幕）/ ≥ 11px（打印等比）。来源：WCAG 2.1 §1.4.4 最小文字尺寸基准。

### 字体

中文：优先 PingFang SC / Noto Serif SC / 思源宋体，不用 SimSun（锯齿感重）。英文：优先 Inter / DM Sans / PP Neue Montreal，避免 Times New Roman（旧报纸感）。

系统字 fallback 必须写全：`font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;`。

### 无法量化的部分（诚实保留文字）

以下三项无法压缩为单一数字，保留文字描述，agent 按判断执行：

**构图呼吸感**：主体不居中塞满，与留白之间有张力。通常主体偏向黄金分割点（画面宽/高的约 1/3 处）而非正中央。

**颜色叙事统一**：同一画面内颜色的温度（暖/冷）和饱和度（高/低）保持一致，不出现既有暖黄又有冷蓝的混搭。

**视觉重心**：最重要的信息（标题/产品）是视觉入口，眼睛第一眼落在那里，不被装饰元素抢先。

---

## 执行流程（HTML 路径）

### Step 1：信息收集（动笔前锁定）

从用户需求里提取：
- 尺寸（1:1 / 3:4 / 16:9 / 自定义 px）
- 核心文案（主标题 + 副标题 + 品牌名，≤20 字/行）
- 色彩方向（有无品牌色；冷/暖；深底/浅底）
- 风格关键词（极简 / 质感 / 科技感 / 手工感）
- 输出用途（X 封面 / 小红书首图 / 印刷 / 屏幕展示）

**Good（信息锁定后）**：
```
主标题：打破边界
副标题：2026 产品发布
品牌：OpenEdon
尺寸：1200×675px（16:9，X 文章封面）
主色：#0A0A0A（深黑底）+ #E8E0D4（暖米白字）
风格：极简、高级感、留白充足
```

**Bad（直接开始写 HTML）**：
```
"帮我做个很好看的封面"
```

如果用户没给足信息，先问一次把以上字段填完，再动手。

### Step 2：HTML 起草

单文件 HTML，inline CSS，不引用外部资源（字体用系统字 + Google Fonts CDN）。

骨架结构：
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1200px; height: 675px;
    background: #0A0A0A;
    display: flex; align-items: center; justify-content: flex-start;
    padding: 0 10%;  /* 留白：左右各 10% = 总宽 20%，加上内容本身留白 ≥30% */
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  }
  .main { max-width: 60%; }
  h1 { font-size: 72px; font-weight: 700; color: #E8E0D4; line-height: 1.1; }
  p  { font-size: 20px; font-weight: 400; color: #8A8A8A; margin-top: 24px; }
  .brand { font-size: 14px; font-weight: 500; color: #E8E0D4;
           position: absolute; bottom: 48px; right: 10%; letter-spacing: 2px; }
</style>
</head>
<body>
  <div class="main">
    <h1>打破边界</h1>
    <p>2026 产品发布</p>
  </div>
  <span class="brand">OPENEDON</span>
</body>
</html>
```

写完后立即做三项检查（对照核心规则）：

- [ ] 留白目测 ≥30%（主体 + 文字占画面 ≤70%）
- [ ] 主色计数（不含黑/白）≤ 2 种
- [ ] 字重层级：h1 / p / brand 三级，没有第 4 级

### Step 3：headless Chrome 截图

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --screenshot=/tmp/poster_preview.png \
  --window-size=1200,675 \
  /tmp/poster.html
```

截图后用 `screencapture -l` 核查四边是否有 fixed overlay 遮挡（参见 memory `feedback_screenshot_verification`）。

### Step 4：对照验证

截图出来后，逐项核对可测阈值，输出验证报告：

```
留白面积估算：约 38%  ✓（≥30%）
主色数：1 种（#0A0A0A 底 + #E8E0D4 字算同组，无辅色）  ✓（≤2）
标题对比度：#E8E0D4 on #0A0A0A ≈ 16.7:1  ✓（≥7:1）
正文对比度：#8A8A8A on #0A0A0A ≈ 5.1:1  ✓（≥4.5:1）
字重层级：700 / 400 / 500 = 3 级  ✓（≤3）
```

有不达标项立即修 HTML，重截图，再验。

### Step 5：交付

截图路径：`/tmp/poster_preview.png`（告知用户绝对路径）。

如用户要调整：修改 HTML 文件重跑 Step 3-4，不需要重新问 Step 1 的信息。

---

## 不适用边界（本 skill 不适合的场景）

| 场景 | 改用 |
|------|------|
| 需要 AI 生成风格图、摄影感图像 | `/baoyu-infographic` 或 `codex-imagen.sh` |
| 海报要纳入项目 React/Vue 组件持续迭代 | 项目框架组件化，不用 HTML 单文件 |
| 流程图 / 架构图 / 数据图表 | `/diagram`（SVG 确定性渲染） |
| 用户没提供任何文案、品牌信息且无参考 | 先做 Step 1 信息收集，不跳过 |

---

## Gotchas

> 只记执行中真实踩坑的模式，不记假设。

- **headless Chrome 字体渲染偏差**：本地 headless 截图中文字体可能回退到 Arial（特别是 CI 环境），导致中文字间距异常。解决：`<link>` 引入 Google Fonts Noto Sans SC CDN，确保网络可达；或改用 Puppeteer 并显式设 `--font-render-hinting=none`。

- **留白"看起来够但测不够"**：主体内容居中时，视觉上有留白，但实际主体 px 占比可能超 70%（大标题字号 90px+ 时常见）。检查时按字符串包围盒估算，不按"感觉"。

- **对比度检查忽略渐变**：背景用渐变时，对比度检测要用渐变最浅处（最低对比度点），不能用平均值。若最浅处 < 7:1，文字颜色必须加深，或缩小渐变范围。

- **联网相关坑（Google Fonts CDN 超时）**：见 `rules/routing.md`。headless 环境无网时，Google Fonts 加载超时会导致截图字体降级，且不报错只是 silent fallback。解决：优先用系统字 + fallback 链，CDN 字体作为 optional 增强。
