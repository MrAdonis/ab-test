---
name: favicon-gen
description: Generate favicons. Use when user asks to create, generate, or make a favicon, site icon, or browser tab icon for a website. Outputs multi-size PNG files (16×16, 32×32, 48×48, 180×180) optimized for legibility at small sizes.
---

# favicon-gen

生成网站 favicon，输出多尺寸 PNG（16px、32px、48px、180px）。核心约束：图形在 16px 和 32px 实际显示尺寸下必须清晰可辨。

## Not for This Skill

以下情况不要用本 skill，直接告知用户：

- **全彩摄影图或渐变复杂 logo** → favicon 尺寸会糊，先让用户简化图形为单色矢量版本再来
- **仅需 ICO 格式**（老 IE 兼容）→ ICO 容器格式用 `convert` 或 `magick` 多帧合并，本 skill 只出 PNG；PNG 现代浏览器全支持，优先 PNG
- **SVG 转 favicon**（保留矢量，浏览器原生支持）→ 在 `<head>` 加 `<link rel="icon" type="image/svg+xml" href="/favicon.svg">` 并输出 PNG 作 fallback，本 skill 可处理 PNG 那一侧

## Pre-flight：确认工具可用

```bash
# 检查 ImageMagick（优先）
magick --version 2>/dev/null || convert --version 2>/dev/null || echo "MISSING"

# 或 Pillow（Python 备选）
python3 -c "from PIL import Image; print('ok')" 2>/dev/null || echo "MISSING"
```

**如果两者都缺**：告知用户运行 `brew install imagemagick` 或 `pip install Pillow`，**不要用其他工具替代**——其他工具（如 sips）不支持多尺寸批量输出。

## 可辨性阈值（带依据）

favicon 最终显示在 16×16 到 32×32 像素区域。可辨性不是主观"好看"，有可测阈值：

| 维度 | 阈值 | 依据 |
|------|------|------|
| 主色数 | ≤ 2 | 16px 下色彩混叠严重，>2 色肉眼无法区分（Nielsen 1993 小尺寸图标认知实验） |
| 最细笔画宽度 | ≥ 2px（以 16px 画布计） | 1px 线在抗锯齿后变 0.5px 半透明，实际不可见 |
| 图形与背景对比度 | ≥ 4.5:1 | WCAG AA 最低对比度标准（非无障碍要求，是可辨性下限） |
| 识别特征数量 | ≤ 3 个独立元素 | Subitizing 上限：人眼在 200ms 内能无计数识别的对象上限为 3-4 个（Kaufman et al. 1949） |
| 留白（内边距） | ≥ 10%（以画布尺寸计） | 防止图形贴边在浏览器 tab 被截切 |

**不能量化的，诚实留文字**：整体造型辨识度——在缩略图旁边和 10 个同类 favicon 对比时，1 秒内能否锁定这个图标。这一条靠人眼判断，没有公式。

## Good vs Bad

```
# Bad — 把复杂 logo 缩小
原始 SVG：多层渐变 + 细线字母组合 + 阴影
→ 16px 结果：一团模糊的灰色方块

# Good — 抽取核心识别元素
从 logo 中提取首字母或最具辨识度的几何形状
→ 16px 结果：清晰的单色字母/图形，背景对比鲜明
```

```
# Bad — 用细描边作为主要元素
border: 1px / stroke: 0.5px
→ 16px 抗锯齿后完全消失

# Good — 用实心色块，描边宽度 ≥ 2px（16px 画布）
fill: #1a1a1a on white, or fill: white on #1a1a1a
```

## Workflow

### Step 1：收集输入

询问或从用户提供的素材中确认：

1. **图形来源**：SVG 文件路径 / PNG 文件路径 / 或由我根据文字描述生成简单几何图形
2. **主色**：前景色和背景色的十六进制值（默认：前景 `#1a1a1a`，背景透明）
3. **输出目录**：默认 `./public/` 或用户指定路径

如果用户给了 SVG，直接进 Step 2。如果只有描述（"一个红色的 R 字母"），先用 ImageMagick 生成简单几何 SVG 或直接光栅化，见下方。

### Step 2：可辨性自检（动手前）

拿到图形后，对照阈值表执行以下检查——**任一 FAIL 则停下，告知用户需要调整，不继续生成**：

```bash
# 如果输入是 SVG，先转 32px PNG 快速预览
magick -background none input.svg -resize 32x32 /tmp/favicon-preview-32.png
magick -background none input.svg -resize 16x16 /tmp/favicon-preview-16.png

# 检查主色数（命令行近似）
magick /tmp/favicon-preview-16.png -colors 8 -unique-colors txt:- | wc -l
# 结果 > 5 → 警告用户颜色过多（含透明度变体，阈值放宽到 5）
```

目视检查 `/tmp/favicon-preview-16.png`：在 16px 下能否识别出图形的核心元素？
- ✅ 能，继续 Step 3
- ❌ 不能，告知用户具体问题（笔画太细 / 元素太多 / 对比不足），建议修改后重试

### Step 3：生成多尺寸 PNG

**用 ImageMagick（首选）**：

```bash
OUTPUT_DIR="./public"
INPUT="input.svg"   # 替换为实际输入文件

# 标准浏览器 favicon 尺寸
magick -background none "$INPUT" -resize 16x16  "$OUTPUT_DIR/favicon-16x16.png"
magick -background none "$INPUT" -resize 32x32  "$OUTPUT_DIR/favicon-32x32.png"
magick -background none "$INPUT" -resize 48x48  "$OUTPUT_DIR/favicon-48x48.png"

# Apple Touch Icon（iOS 主屏幕）
magick -background white "$INPUT" -resize 180x180 -gravity center -extent 180x180 \
  "$OUTPUT_DIR/apple-touch-icon.png"
```

注意：`apple-touch-icon.png` 用 `-background white` 填充不透明背景，iOS 不支持透明 Touch Icon。

**用 Pillow（备选，输入是 PNG 时）**：

```python
from PIL import Image

src = Image.open("input.png").convert("RGBA")
sizes = [16, 32, 48]
for s in sizes:
    img = src.resize((s, s), Image.LANCZOS)
    img.save(f"public/favicon-{s}x{s}.png")

# Apple Touch Icon
touch = src.resize((180, 180), Image.LANCZOS)
bg = Image.new("RGB", (180, 180), (255, 255, 255))
bg.paste(touch, mask=touch.split()[3])
bg.save("public/apple-touch-icon.png")
```

### Step 4：验证输出

```bash
# 确认文件生成且非空
ls -lh "$OUTPUT_DIR"/favicon-*.png "$OUTPUT_DIR"/apple-touch-icon.png

# 确认尺寸正确
for f in "$OUTPUT_DIR"/favicon-*.png; do
  magick identify "$f" | grep -oE '[0-9]+x[0-9]+'
done
```

所有文件存在且尺寸匹配 → 完成。任一文件缺失或 0 字节 → 报错，不声明成功。

### Step 5：告知用户 HTML 引用

```html
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

如果项目有 `public/` 目录（Next.js / Astro / Vite），把文件放在那里，框架会自动服务 `/favicon-32x32.png`。

## Gotchas

> 只记执行中真实踩过的坑，不记假设。

- **SVG viewBox 含隐式 padding** → `magick` 转换时实际图形比声明的小，16px 下图形占画布 < 50%，显得很小。规避：转换前用 `magick svg: -trim` 裁掉透明边缘，再缩放
- **`-resize 16x16` 不等于 `-resize 16x16!`** → 前者保持宽高比并居中（可能出现空白条带），后者强制拉伸变形。favicon 用前者（保持比例），不用 `!`
- **PNG 透明背景在 Windows 任务栏显示为黑色** → 32×32 和 16×16 建议保持透明（Chrome/Firefox 自动用浏览器主题色填充），但如果用户指定了深色图标，提醒可能在深色任务栏上对比度不足
- **`convert` 在新版 macOS 上是 ImageMagick 7 的别名，但行为略不同** → 统一用 `magick` 命令（ImageMagick 7 原生），不混用 `convert`
