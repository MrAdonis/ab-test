# 图片生成基础方法（image-base）

内容项目共享的 AI 图片生成规范。

## 通用约束

### 文字污染防护（**按模型分级，不再一刀切**）

历史上 AI 生成中文字符普遍乱码，但 2026 年中文生图能力分化明显，不同模型要用不同策略：

| 模型档位 | 代表 | 中文表现 | 策略 |
|---------|------|---------|------|
| **可直接出字** | Seedream-5（豆包 ARK）、Qwen-Image-2.0（DashScope） | 60+ 字符密集信息图零错字，含专有名词混排 | **鼓励出字**。信息图/海报/封面直接让模型渲染中文，用 `/baoyu-infographic` 路径。验证方式：生图后 Read 逐字核对 |
| **勉强能出字** | GLM-Image（智谱）、MiniMax image-01 | 10 字内短标题勉强可用，密集文字开始变形 | 短标题可出字，长正文转纯视觉意象。如果必须密集文字 → 切 Seedream |
| **几乎不能出字** | DALL·E 2/3、SDXL 系列、老 Midjourney（非 v7） | 中文基本乱码，英文也常有虚构字符 | **必须禁文字**。prompt 开头加 `"absolutely no text of any kind, no Chinese characters, no letters, no symbols, no watermarks, no signatures, no calligraphy, clean imagery only"`。文字靠后期（PIL/Canva/Figma）叠加 |

### 禁文字 prompt 模板（仅第 3 档模型用）
```
"absolutely no text of any kind, no Chinese characters, no Chinese text, no English words, no letters, no symbols, no watermarks, no signatures, no calligraphy, clean imagery only"
```

### 路由首选
- **默认兜底（泛指生图、无任何限定词时先落这）**：用户只说"生成一张图 / generate an image / 出张图"，既无"中文文字/海报/信息图"（→ infographic）也无"流程/架构/数据图"（→ diagram）也无指定 provider/批量（→ baoyu-imagine）→ **默认 `~/.claude/scripts/codex-imagen.sh`（免费）**。收触发面后这类裸请求不再有 skill 自动开火，必须靠本门兜底，别空触发或反射性奔付费 seedream。
- 需要**中文文字准确**的信息图/海报/封面 → 走 `/baoyu-infographic`（Seedream-5 执行端），脚本 `~/.claude/scripts/gen-infographic.sh`
- 需要**确定性精确结构**的流程/架构/数据图 → 走 `/diagram`（SVG 渲染，文字用 DOM，100% 准确）
- **临时配图 / mockup / 插画，不要求中文文字准确** → `~/.claude/scripts/codex-imagen.sh`（gpt-image-2 经 Codex 订阅，**零 API key、不按张计费**）。t2i 与 i2i（`-i ref.png`）都支持，`--json` 出结构化结果。是 baoyu-imagine 之外的**免费 ad-hoc lane**，baoyu-imagine（Seedream）仍是生产 / 中文文字 lane
- **已有图只改局部**（换 logo / 改文字区 / 补角落元素，其余像素不能动）→ 任一 lane 整图重生成后接 `~/.claude/scripts/mask-composite.py --original 原图 --edited 新图 --region x,y,w,h`（区域外像素逐位还原原图，硬保证；默认羽化 4px 防接缝）。坐标不确定先 `mask-composite.py grid --original 原图` 出网格标尺图（红线 + 像素坐标标注），看图读坐标再圈区域。背景：Seedream 官方 API 无 mask 参数、gpt-image 的 mask 是软的（整图重渲染），像素级保真只能靠本地合成。**不适用**：大面积改动（换背景保主体）——全局光照/色调被模型改了硬合成有贴片感，走 i2i 保真骨架
- 纯装饰背景图、无需文字 → 任意模型都行

> **auto-trigger 改道**：2026-06-20 已收触发面——baoyu-imagine 的 description 降为「生产/付费执行后端」、不再对裸"画图"宽泛 auto-trigger，diagram 让出"可视化"、infographic 让出"画图"，三者各带互斥声明（本决策门即单一源，description 只做下游执行）。残余防御：仍命中免费档（临时配图/mockup/无中文文字）时主动走 codex-imagen，别被付费 seedream 拉走。

> **codex-imagen 边界**：gpt-image-2 中文文字不可靠（英文尚可），密集中文一律回 Seedream；尺寸只能在 prompt 给 `-a 16:9` 当 hint，不精确控制（实测多落在 1536×1024 附近）。生产小报 / taoism 配图风格已 AB 调过 Seedream，**不要**用 codex-imagen 替换。

### 生图后核查（适配分级）
1. 用 Read 工具查看每张图
2. **第 1 档（Seedream/Qwen-2.0）**：逐字核对中文准确性；有 >2 处错字 → 检查 prompt 里字是否超长/生僻，简化重试
3. **第 2-3 档模型**：确认无意外生成的文字；有 → 加强 NO TEXT 约束重试
4. 第 2 次仍失败 → 换模型（第 3 档 → 第 1 档）或换纯视觉意象
5. 第 3 次失败 → 标记给用户手动处理

### 比例检查
- 生成后检查 exit code（如脚本支持）
- 比例不合格 → 在 prompt 中加强比例约束，重试最多 2 次

## 禁止意象（**仅第 3 档禁文字模型**）
- 励志风格、办公室场景
- 过于鲜艳的色彩
- 卷轴/书法/石碑/古书等容易引发 AI 生成文字的意象

第 1 档（Seedream/Qwen）不适用，可正常处理书法/古书/竖排中文题材。

## 平台规格速查

| 平台 | 封面 | 正文 | 社交卡片 |
|------|------|------|---------|
| Shopify 博客 | 1200x675 (16:9) | 1200x675 (16:9) | IG 1080x1350 / X 1200x675 |
| Instagram/TikTok 竖版 | — | 720x1280 (9:16) | — |
| X 推文 | — | — | 1200x675 |

## 命名规范
- 封面：`{slug}-cover.png`
- 正文：`{slug}-img1.png`, `{slug}-img2.png`, ...
- 社交卡片：`{slug}-ig.png`, `{slug}-x.png`

## 出图前优先级自检（Less is More）

> 借自阿哲Phil「少即是多（上）」。**「少」指优先级不是数量**，反对的是无效复杂、不是复杂本身（繁复能强化表达就有效）。堆 `高质量/真实/电影感/8K` 反而画乱 = 优先级失控。写 6-block 前先过此 gate，决定砍什么留什么。

- **单一焦点**：这张图第一眼要看到什么？答案不唯一 = 焦点太多。一张图设 1 个主焦点，最多不超过 3 个。
- **冗余判据**：一个元素拿掉后表达没变弱 = 冗余，砍掉（"为了显得丰富"不是保留理由）。
- **一句话原则**：这张图到底只想说哪一件事？同时塞风格+功能+情绪+卖点+故事 = 观者什么都记不住。
- **验收动作**：出图后眯起眼看，第一眼看到的若不是你最想传达的信息 → 是画面优先级排错了，回去调，不是加元素。

（字体/颜色克制见下「跨类目通用避坑」，此处不重复。）

## 提示词结构化写法（Prompt-as-Code）

> 借自 `freestylefly/awesome-gpt-image-2`（465 案例 + 21 套模板，MIT）。这里只沉淀 **provider 无关**的写法骨架；要具体某类模板/案例时去仓库 `docs/templates.md` / `docs/gallery.md` 查，不在本文件复制全文（会臃肿且过时）。原模板为 GPT-Image 2 调，结构可直接迁到 Seedream-5 / baoyu-imagine，具体措辞按目标模型微调。

### 6-block 提示词结构（组装任何生图 prompt 都按这个填）

无论哪个 provider，把意图拆成 6 块再写，比一句话散文 prompt 稳定得多：

1. **主体 + 任务**：画什么、用途（如「为健身 App 生成 iOS 界面图」）
2. **构图 + 布局**：版式、信息层级、留白（如「卡片流 + 底部 Tab，层级清晰」）
3. **视觉风格 + 材质**：风格关键词、主色/强调色、质感
4. **文字 + 标签**：要出现的确切文字（中文逐字写死）、可读性要求（与「文字污染防护」分级配合：第 1 档鼓励出字，第 3 档这一块改成 NO TEXT）
5. **比例 + 输出格式**：9:16 / 16:9 / 1:1，写在靠前位置（不写则模型默认手机 9:16）
6. **约束 + 负面**：明确「不要 X、不要 Y」（错乱器材、乱码占位、杂乱拼贴）

### 套用「具名风格」时：融合，不是拼接

6-block 教的是凭空写一条 prompt。当 prompt 要套一个**具名风格**（弥散/巨型透视/麦肯锡/科研等，风格库见 memory `reference_x_article_cover_prompts`）时，多一层纪律——借自 @AdrianPunk115 的 Punk-Skill 架构（learning 2026-06-20）：

- **融合而非拼接**：不写「通用封面 + 风格关键词」两段并列，也不叠加第二个风格。标题、主体、背景、辅助文字、材质配色、视觉隐喻——6 块每一项都用所选风格的视觉语言实现（例：手撕拼贴风的标题=撕纸+旧报纸+胶带本身，不是普通标题配拼贴背景）。风格是组织语言，不是末尾追加的滤镜段。
- **不可见不写**：prompt 里提到的风格特征必须在成图里真看得见；写了但出不来 = 删掉或换措辞。
- **封面标题三层级**（长标题专用）：A 层=超短高冲击主视觉词 / B 层=完整标题或完整语义 / C 层=副标题、语境行、小标签。长文只填派生字段（标题/摘要/视觉主体/隐喻），**禁止把正文灌进 prompt 或图里**。

### i2i 商品/人物保真型（精准出图，款式/识别度不能变）

6-block 是 **t2i**（凭空生成）骨架。做**商品/人物保真**出图（上传产品/人物图，款式或识别度必须保留——珠宝/手表/鞋包/化妆品/3C/模特带货）时，改用 **i2i 保真型骨架**：在 6-block 前面多一个**保真锚定块**（保留 X / 允许改 Y / 禁止 Z），并用**条件分支**（`如果是戒指→突出手指；如果是项链→突出锁骨`）让一套 prompt 覆盖整品类。完整 8 机制 + 填空骨架 + 4 套标杆实例（含 t2i 单品 / i2i 真人保真两条质量基准线）见 memory `reference_jewelry_prompts.md`。判据一句话：**普通图只要好看，商品图还要准确**。

### JSON 进阶格式（批量 / 给 baoyu-imagine agent 调用）

需要批量出图或喂给 agent 时，把 6-block 转成 JSON（`type / platform / layout / style / content / constraints`），比散文更可控、可程序化变量替换：一套模板复用，只变 subject / composition / palette / scene。

### 跨类目通用避坑（从 21 套模板「避坑指南」提炼的共性）

- **拒绝模糊指令**：平台 + 比例 + 布局必须写死，否则模型乱排版
- **数量克制**：信息图/海报强制限定「模块数量」（冗余/正文取舍走上「出图前优先级自检」，此处不重复）
- **先锁场景再填细节**：带货直播 vs 才艺直播、X vs 小红书，UI 差异大，先定品类
- **比例前置**：特殊屏幕比例（21:9 车机等）写在 prompt 最前，否则默认 9:16
- **负面约束显式化**：「不要错误器材 / 不要乱码占位 / 不要杂乱拼贴」单独成句

### 分类案例库（找视觉方向时查，不搬进本文件）

仓库 `docs/gallery.md` 按类目分：UI 73 / 信息图 50 / 海报 73 / 产品 35 / 品牌 23 / 摄影 58 / 插画 47 / 人物 21 / 建筑 11。做 edonspace 配图 / 小红书图文 / 封面前，先去对应类目找视觉方向，再用上面 6-block 转成结构化 prompt。
