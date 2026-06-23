---
name: text-to-infographic
description: 用户给一段文字（新闻、分析、数据摘要、产品说明等），生成一张信息图（infographic）。触发词：信息图、infographic、生成图、画张图（当内容密度高且含结构化信息时）、做成图片、可视化这段文字。
---

# Text-to-Infographic

把一段文字转化为信息图。路径固定：先过决策门选渲染方式，再提取结构，再生成。

## 不适用场景（先排除，别乱触发）

以下场景**不走本 skill**，去对应工具：

- 流程图 / 架构图 / ER 图 / 时序图 → `/diagram`（SVG 确定性渲染，结构精确）
- 数据统计图表（折线/柱线/饼图）→ `/diagram`
- 封面/海报/KV（主要是视觉冲击，信息密度低）→ `references/image-base.md` 决策门
- 纯文章配图（无结构化信息，只需氛围）→ `~/.claude/scripts/codex-imagen.sh`
- 文字超过 3000 字且结构散乱 → 先让用户精简到核心 5-8 个要点再进本 skill

判断口诀：**有结构化信息（列表/数据/流程/对比/层级）且需要视觉排版** = 走本 skill；纯氛围图或纯工程图 = 走别处。

## 决策门：渲染方式（必须先过）

两条路径，选完再动手：

| 场景 | 路径 | 工具 |
|------|------|------|
| 含中文文字且要求准确显示 / 需要确定性排版 / 会反复迭代 | **HTML 渲染** | 内联 CSS + headless Chrome 截图，交付 PNG |
| 纯英文或无中文文字精度要求 / 一次性临时配图 / 用户明说"随便" | **AI 生图** | `/baoyu-infographic` |

默认选 HTML 渲染——中文文字在 AI 生图里高频乱码或错字，HTML 是唯一可靠路径。

## 工作流

### Step 1：解析素材结构

读用户提供的文字，提取：

- **核心主张**（1 句话，整张图的标题/副标）
- **信息块**（3-8 个，每块：标题 + 1-3 行正文或数据）
- **数据点**（如有：数字 + 单位 + 来源）
- **信息类型**（选一个最符合的）：
  - `comparison`（对比两个以上对象）
  - `process`（步骤/流程，有先后顺序）
  - `stats`（以数字为核心）
  - `list`（并列要点，无强顺序）
  - `timeline`（时间轴）
  - `hierarchy`（层级/分类）

提取结果写成内部草稿（不展示给用户），作为 Step 2 的输入。有歧义时按信息密度最高的类型判断，不问用户。

### Step 2：选版式模板

按信息类型对应版式：

| 信息类型 | 版式 | 布局逻辑 |
|----------|------|---------|
| `comparison` | 双列对比卡 | 左右各一列，对应行对齐 |
| `process` | 横向步骤条 | 数字圆圈串联，箭头连接 |
| `stats` | 大字数据卡 | 数字超大字号居中，标签小号说明 |
| `list` | 图标列表 | 每项左侧色块/图标，右侧文字 |
| `timeline` | 纵向时间轴 | 中轴线，左右交替内容块 |
| `hierarchy` | 树形/金字塔 | 顶层大框，逐层展开 |

信息块超过 6 个时，拆成两列或分组，不堆单列。

### Step 3：品质约束（HTML 路径）

以下约束全部硬执行，不靠"感觉好看"：

**留白**：内容区四周 padding ≥ 40px，信息块间距 ≥ 20px。（Calimari Rule：留白比内容本身更产生"高级感"）

**颜色**：主色 1 个 + 强调色 1 个 + 中性色（灰/白）背景，合计 ≤3 色。正文与背景对比度 ≥ 4.5:1（WCAG AA），标题与背景 ≥ 7:1（WCAG AAA）。不用渐变色堆叠。

**字号层级**：最多 3 级，建议：标题 28-32px、副标/数据 18-22px、正文 13-15px。不用小于 12px 的字（截图后缩放会模糊）。

**字重**：标题 font-weight: 700，正文 400 或 500，不混用超过 2 个字重。

**图表宽度**：默认 800px × 自适应高度。高度不硬设，由内容撑开。截图 `--window-size=800,2000` 防截断。

**字体**：中文用系统字体栈 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`，英文 `"Inter", "Helvetica Neue", sans-serif`。不引入外部字体（网络依赖 + 截图环境可能缺字体）。

### Step 4：生成 HTML

写一个完整的单文件 HTML（`<!DOCTYPE html>` 起），所有样式 inline CSS（`<style>` 块在 `<head>` 里），不引用外部资源。

结构约束：
- 根容器 `width: 800px; margin: 0 auto; background: #fff`
- 不用 `position: fixed`（截图时 fixed 元素行为不可预测）
- 数据来源（如有）放底部 10px 小字，颜色 `#999`

### Step 5：渲染截图

```bash
# 截图命令（必须用绝对路径）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --disable-gpu \
  --screenshot=/tmp/infographic-output.png \
  --window-size=800,2000 \
  /tmp/infographic.html
```

截图后检查两件事：
1. 底部是否被截断（图片高度 = 1200px 且内容明显未完 → 加大 `--window-size` 高度重截）
2. 中文字符是否正常显示（出现方块字 → 检查字体栈是否写对）

截图路径告知用户，格式：`/tmp/infographic-output.png`（绝对路径）。

### Step 6：AI 生图路径（baoyu-infographic）

仅当 Step 1 决策门选了"AI 生图"时走本步骤：

调用 `/baoyu-infographic`，传入：
- 核心主张（1 句话，作为图片主标题）
- 信息块列表（提炼后的 3-8 个要点）
- 风格要求（从 `~/.claude/memory/reference_x_article_cover_prompts.md` 的 6 套框架中选一个最匹配的，或用户明确指定）

AI 生图路径**不适合**含精确数字的内容（数字在 AI 生图里容易被改写）。有关键数字时强制走 HTML 路径。

## 输出

- HTML 路径：PNG 文件，绝对路径告知用户。同时保留 HTML 源文件在 `/tmp/infographic.html`（方便用户要求微调后重截）
- AI 生图路径：`/baoyu-infographic` 的原生输出

## Rules

- 中文文字出现在图里 → HTML 路径，不商量
- 信息块 > 8 个 → 先压缩到 ≤ 8 个，问用户要不要手动确认哪些去掉（去掉哪些影响最大的）
- 素材里有具体数字（百分比、金额、增长率）→ 必须验证数字直接来自用户提供的文字，不从背景知识补充或平滑数字
- 截图失败（Chrome 路径不对 / headless 报错）→ 告知用户错误原因，建议手动用浏览器开 `/tmp/infographic.html` 截图，不静默跳 AI 生图

## Gotchas

> 只记真实踩过的坑。

- **Chrome headless 截图路径在 macOS 因版本不同**：`/Applications/Google Chrome.app/...` 是标准路径，若报 `No such file` 先跑 `ls /Applications/ | grep -i chrome` 确认实际目录名，别假设路径
- **`--screenshot` 不支持相对路径**：必须给绝对路径（`/tmp/infographic-output.png`），给相对路径时 Chrome 静默失败、不报错、也不生成文件
- **联网相关坑（字体 CDN / 外部图片）**：headless 截图环境不保证网络可达，见 `rules/routing.md`；信息图 HTML 必须全部 inline，不引用任何外部 URL
- **AI 生图数字被改写**：baoyu-infographic 会按"合理性"自动修改数字（如把 47.3% 改成 约50%），含精确数字的内容绝对不走 AI 生图路径
