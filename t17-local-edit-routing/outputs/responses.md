# t17 原始产出（8 个 Sonnet 子代理）

## S1-A（换 logo，无条目）

用 ImageMagick 合成，纯确定性路径：
1. `magick new-logo.png -resize <目标尺寸>` 缩放新 logo
2. `magick banner.png new-logo-resized.png -geometry +<x>+<y> -composite output.png` 精确坐标覆盖

路由规则里没有工具能满足"一个像素都不能变"——AI 工具 inpaint 不保证像素级一致。ImageMagick 是像素级精确合成，非 AI 生成，硬保证未覆盖区域 bit-for-bit 不变。

## S1-B（换 logo，有条目）

1. `mask-composite.py grid --original banner.png` → 网格标尺图，圈出 logo 区域坐标
2. codex-imagen.sh `-i banner.png` 或 baoyu-imagine 生成换了新 logo 的整图
3. `mask-composite.py --original banner.png --edited 新图 --region x,y,w,h` → 区域外像素逐位还原

约束满足：region 外每个像素直接取原图值，硬保证，不依赖模型判断。注意：生成图尺寸不一致需先校准。

## S2-A（改文字，无条目）

这个任务没有合适的工具能硬保证"其他内容原样"。codex-imagen i2i 是风格参考不是精确复制，版式会漂移；baoyu-imagine 无 mask，整图重生成会改其他区域；/diagram 不能编辑现有 PNG。正确做法：回到海报源文件（PSD/Figma）改字重导出；只有 PNG 则用 Photoshop/Pixelmator 手工覆盖——超出以上 AI 工具能力范围。

## S2-B（改文字，有条目）

1. `mask-composite.py grid --original poster.png` → 确认"2025"坐标区域
2. i2i prompt "副标题改为 2026 其余不变" 生成 edited.png
3. `mask-composite.py --original poster.png --edited edited.png --region x,y,w,h`

"其他内容原样"靠硬合成保证，区域外 100% 像素一致。无法硬保证的一条：区域内字体/字号还原质量取决于 i2i 模型，不像则迭代。

## S3-A（换背景，无条目）

baoyu-imagine i2i，保真锚定块 prompt（保留脸/发型/衣服，替换背景，禁止改人物）。"人物不变"无法硬保证——无 mask 参数，靠 prompt 引导，模型可能微调肤色发丝。像素级锁定需 ComfyUI inpaint，当前工具链无此能力。

## S3-B（换背景，有条目）

baoyu-imagine i2i 同上。i2i 是模型级保真，无法硬保证人物像素不变。**mask-composite.py 不适用：本任务是大面积背景替换，人物/背景光照需融合，硬合成人物区域会有贴片感。** 商业级保真需 mask inpaint 工具，当前链无法硬保证。

## S4-A（中文海报，无条目）

`/baoyu-infographic`（Seedream-5）一步，prompt 写明标语。排除 codex-imagen（中文不可靠）、/diagram（结构图）。

## S4-B（中文海报，有条目）

`/baoyu-infographic` 一步，同上。无需 mask/inpaint。
