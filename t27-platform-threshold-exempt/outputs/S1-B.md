---
name: favicon-generator
description: Generate multi-size favicon PNG files (16px, 32px, 48px, 64px, 128px, 256px) from a concept or existing image. Ensures icons remain crisp and legible at actual browser display sizes (16px and 32px). Use when asked to "generate a favicon", "create site icon", "make browser tab icon".
---

# Favicon Generator

## When to Use

触发：用户要为网站生成 favicon、站点图标、browser tab icon，或需要多尺寸图标 PNG 输出。

**不适用（用其他方案）：**

- 需要 `.ico` 容器格式（多尺寸合并为单个 .ico 文件）→ 用 `convert` (ImageMagick) 合并 PNG，不在此 skill 范围
- 需要 Apple Touch Icon (180px) 或 PWA 图标 (192px/512px) → 尺寸覆盖但语义不同，单独交付并命名正确
- 输入是 SVG 且只需要浏览器直接引用（现代浏览器支持 `<link rel="icon" type="image/svg+xml">`） → 直接用 SVG，跳过位图输出

## 核心约束：Favicon 平台硬事实

以下尺寸来自平台显示规范（事实依据，非品味数字）：

| 用途 | 实际显示尺寸 | 输出尺寸 |
|------|------------|---------|
| 浏览器标签页（标准显示屏） | 16×16px | 16px |
| 浏览器标签页（高分屏 2x） | 实际 16px，渲染用 32px | 32px |
| Windows 任务栏快捷方式 | 32×32px | 32px |
| 书签/历史记录列表 | 16px 或 32px | 两者都要 |
| macOS Dock 固定（Add to Dock） | 最大 128px | 128px |

**16px 和 32px 是核心尺寸**——这两个尺寸下图形必须清晰可辨，是验收门。其余尺寸（48/64/128/256px）是补充。

## Workflow

### Step 1：明确输入形式

**A — 从文字概念生成：** 用户描述图形（如"蓝色六边形里有一个白色 F"）→ 进 Step 2。

**B — 从现有图片转换：** 用户提供 PNG/SVG/JPG → 跳到 Step 3，直接缩放输出。

**C — 从品牌色 + 字母生成：** 最常见的 favicon 类型（公司首字母 + 背景色）→ 进 Step 2，但脚本走字母渲染路径。

### Step 2：生成大尺寸源图（512px）

使用 Python + Pillow 生成 512px 基础图，**不直接生成小尺寸**——从大缩小比从小放大保留细节。

**判断路径：能量化的写死，不让 agent 自由发挥（Freedom Matching 高脆弱步骤）：**

```python
# 路径 C：字母型 favicon（最常见）
from PIL import Image, ImageDraw, ImageFont
import os

def generate_letter_favicon(letter, bg_color, text_color, output_dir):
    """生成字母型 favicon 源图 512px"""
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景：圆角矩形（圆角半径 = 尺寸 * 0.2，来自 iOS App Store 规范）
    radius = int(size * 0.2)
    draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=bg_color)
    
    # 字母：居中，字号 = 尺寸 * 0.55（实测 16px 下字母可辨的最小比例）
    font_size = int(size * 0.55)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), letter, fill=text_color, font=font)
    
    return img
```

**路径 A（自定义图形）：** 用 HTML + headless Chrome 渲染 SVG，截图为 512px PNG，再进 Step 3。生成 inline SVG 时：
- 复杂细节（细线、渐变、阴影）在 16px 下会糊掉——**主动告诉用户哪些细节在小尺寸会丢失**
- 图形主体占 SVG 画布的 60-70%（留白 15-20% 四边），防止贴边被裁

### Step 3：缩放输出多尺寸 PNG

```python
# 好的做法：用 LANCZOS 重采样，不用 BILINEAR（小尺寸边缘更锐）
# 来源：Pillow 官方文档 + PIL.Image.Resampling 枚举

def export_favicons(source_img, output_dir):
    """从 512px 源图导出标准 favicon 尺寸"""
    sizes = [16, 32, 48, 64, 128, 256]
    os.makedirs(output_dir, exist_ok=True)
    
    paths = {}
    for size in sizes:
        resized = source_img.resize((size, size), Image.Resampling.LANCZOS)
        path = os.path.join(output_dir, f"favicon-{size}x{size}.png")
        resized.save(path, "PNG", optimize=True)
        paths[size] = path
    
    return paths
```

**不要做：**
```python
# Bad — NEAREST 重采样，小尺寸产生像素化锯齿
resized = source_img.resize((size, size), Image.Resampling.NEAREST)

# Bad — 直接用 AI 生成 16px 图片
# AI 图像生成模型无法保证 16px 下的像素精准度，统一走从大到小缩放
```

### Step 4：验收检查（必做，不跳过）

输出文件后，用以下命令验证关键尺寸：

```bash
# 验证文件存在且尺寸正确
python3 -c "
from PIL import Image
import os

output_dir = '/tmp/favicons'
required = [16, 32]  # 核心验收尺寸
all_ok = True

for size in required:
    path = os.path.join(output_dir, f'favicon-{size}x{size}.png')
    if not os.path.exists(path):
        print(f'MISSING: {path}')
        all_ok = False
        continue
    img = Image.open(path)
    if img.size != (size, size):
        print(f'WRONG SIZE: {path} got {img.size}')
        all_ok = False
    else:
        print(f'OK: {path} {img.size}')

print('PASS' if all_ok else 'FAIL')
"
```

验收结果三态处理：
- `OK` × 2（16px + 32px）→ 完成，继续输出路径清单
- 文件存在但尺寸错 → 根因：Step 3 resize 参数错；重跑 Step 3
- 文件不存在 → 根因：output_dir 路径问题或 Step 3 未执行；检查目录权限再重跑

### Step 5：输出路径清单

生成完成后，向用户输出：

```
生成完成：/tmp/favicons/
├── favicon-16x16.png   ← 浏览器标签页（标准屏）
├── favicon-32x32.png   ← 浏览器标签页（高分屏）/ Windows 任务栏
├── favicon-48x48.png
├── favicon-64x64.png
├── favicon-128x128.png
└── favicon-256x256.png

HTML 引用（放在 <head> 内）：
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
```

## 关键约束

**16px 可辨性原则：** 16px 下只能显示 1-2 个视觉元素（一个字母、一个简单形状）。超过 2 个元素在 16px 下必然糊成一团。如果用户的设计有 3+ 个元素，主动告知并建议简化——不要静默生成一个在小尺寸下不可辨的图标。

**透明背景 vs 实色背景：** 透明背景在深色浏览器主题下可能变成黑图标。询问用户是否需要深/浅色各一套，或直接用实色背景。

**字体依赖：** `/System/Library/Fonts/Helvetica.ttc` 是 macOS 路径。Linux 环境下改为 `/usr/share/fonts/` 下的等价字体。脚本已有 `except` fallback 到 PIL 默认字体（低质量但不会崩）。

## Gotchas

> 只记执行中真实踩过的坑，不记假设。

- **Pillow `Image.LANCZOS` 在旧版本不可用** → 根因：Pillow < 9.1.0 用 `Image.ANTIALIAS`；9.1.0+ 改为 `Image.Resampling.LANCZOS` → 规避：`getattr(Image, 'Resampling', Image).LANCZOS`
- **headless Chrome 截图包含空白边** → 根因：HTML body 默认有 8px margin → 规避：截图前注入 `document.body.style.margin='0'`
- **PNG 文件输出后在 Finder 缩略图显示正常但实际尺寸错** → 根因：Pillow 写入了错误的 DPI metadata → 规避：验收步骤直接读 `img.size`（像素尺寸），不信 Finder 缩略图
