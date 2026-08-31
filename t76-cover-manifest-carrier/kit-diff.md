# 两臂 kit 差异（A=kit-r7 改动前 / B=kit-m3 改动后）

```diff
diff --color -r /tmp/covkit/kit-r7/SKILL.md /tmp/covkit/kit-m3/SKILL.md
25c25,26
< - 编译前读 `references/cover-prompt-blueprint.md`
---
> - 编译前读 `references/cover-prompt-blueprint.md`（含 Recipe Manifest 表）
> - 定载体信号：读 `references/carriers.md`，只读选定 carrier 那一节 + 通用禁止信号
39a41
>    - 载体（carrier）由平台推导，不额外问：X/小红书/公众号 → `screen_cover`，PPT/报告 → `deck_slide`，活动海报/KV → `wall_poster`，播客/歌单 → `square_sleeve`，周边印花 → `merch_print`。只有用户提到实体印刷、周边、展陈而平台又不明确时才问一句
48c50,57
< 5. **编译最终 prompt**：
---
> 5. **填 Recipe Manifest（编译 prompt 之前）**：
>    - 按 `references/cover-prompt-blueprint.md` 的 Recipe Manifest 表把输入解析成确定字段，每格一个值，拿不准就问，不写「A 或 B」
>    - `focal_point` 只能有一个；`text_charcount` 必须真数一遍画面全部文字的字符数，不估
>    - `carrier` 从平台推导（见 step 2），`style_anchors_applied` 从选定风格 META.md 抄
>    - 表填不满就说明素材不够或选型没定，回到 step 1/3，不要带着空格往下走
> 
> 6. **编译最终 prompt**：
>    - 输入是填满的 manifest，不是原始素材——manifest 已定的字段逐字用，不在编译阶段重新发挥
55,56c64,65
< 6. **产物纪律（先落盘再生图）**：
<    - prompt 存 `covers/{slug}/prompt.md`（当前项目内；无项目上下文时 `~/Projects/personal/playground/covers/{slug}/`）
---
> 7. **产物纪律（先落盘再生图）**：
>    - manifest 存 `covers/{slug}/recipe.yaml`，prompt 存 `covers/{slug}/prompt.md`（当前项目内；无项目上下文时 `~/Projects/personal/playground/covers/{slug}/`）
61c70
< 7. **生图执行**：默认存完 prompt 就生图，除非用户明说只要 prompt。后端按 `~/.claude/references/image-base.md` 三档决策门（权威，不复制）：含中文文字 → seedream；无中文文字的临时图 → codex-imagen 免费档。seedream 标准命令：
---
> 8. **生图执行**：默认存完 prompt 就生图，除非用户明说只要 prompt。后端按 `~/.claude/references/image-base.md` 三档决策门（权威，不复制）：含中文文字 → seedream；无中文文字的临时图 → codex-imagen 免费档。seedream 标准命令：
71a81,93
> ## Retry 纪律（冻结 manifest，只动一维）
> 
> 出图不合格重来时，**重试的是这一次生成事故，不是重新设计一张封面**。随机性只允许留在生图模型那一层，配方层必须冻结。
> 
> 1. 先用 `references/cover-diagnosis.md` 判出**唯一**一条不合格的维度（文字准确 / 配色作用域 / 主体构型 / 材质质感 / 层级对比）
> 2. 打开 `covers/{slug}/recipe.yaml`，把要改的那一个字段改掉，其余字段逐字保持原值，并在 `retry_frozen` 里写下本轮冻结了什么
> 3. 由改后的 manifest 重新编译 prompt。**不要在编译时顺手润色没被诊断的段落**——上一版的措辞逐字复用
> 4. 出图后五个维度全部重扫一遍，不只看修好的那一条
> 
> 不这样做的话，每轮生图都会在「没被硬约束的那一维」漂移：修好文字那轮装置会走形，收紧装置那轮标题配色又失控，来回三轮回到原点。冻结 manifest 就是把可变面积压到只剩被诊断的那一块。
> 
> 同一维度连改两轮不动的，换手段而不是加码——见 Gotchas「比例约束治不了构型先验」。
> 
99d120
< - **每轮生图会在"没被硬约束的那一维"漂移**：修好文字那轮装置会走形，收紧装置那轮标题配色又会失控。改 prompt 后不要只看修好的那条，四个维度（文字准确 / 配色作用域 / 装置动作 / 材质）每轮都要重扫一遍
Only in /tmp/covkit/kit-m3/references: carriers.md
diff --color -r /tmp/covkit/kit-r7/references/cover-prompt-blueprint.md /tmp/covkit/kit-m3/references/cover-prompt-blueprint.md
6a7,43
> ## Recipe Manifest（编译 prompt 之前先填满）
> 
> 不要从素材直接写 prompt。先把输入解析成下面这张表，每个字段都要有确定的值，再由这张表编译 prompt。
> 
> 这么做解决三件事：同一份输入总是解析出同一份配方（系列封面不会莫名换调性）；重试时知道哪些字段该原样冻结；`text_charcount` 把「画面文字恰好 N 字」这条防错从靠记性变成必填项。
> 
> manifest 落盘 `covers/{slug}/recipe.yaml`，与 `prompt.md` 并列。用户没问过程就不要在对话里展开它。
> 
> ```yaml
> slug:                 # kebab-case，同时是产物目录名
> platform:             # X 文章 / 小红书 / 公众号头条 / PPT / 海报 / 其他
> carrier:              # references/carriers.md 的 carrier ID，默认 screen_cover
> ratio:                # 显式比例，随平台或用户指定
> style_id:             # styles/ 下恰好一个
> language:             # 画面文字语言
> title_a:              # A 层 短冲击视觉标题
> title_b:              # B 层 完整标题
> title_c:              # C 层 副标题或角标；风格无 C 层文字时写 none
> text_charcount:       # 画面上全部文字的准确字符数，逐字数出来，不估
> visual_subject:       # 核心视觉主体
> focal_point:          # 缩略尺寸下第一眼抓住的那一个东西，只能有一个
> metaphor:             # 核心动作 + 一句话（动作动词表见下）
> mood:                 # 情绪
> audience:             # 受众
> summary:              # 1-3 句摘要
> banned_elements:      # 本次禁用元素（叠加通用负面约束与风格专属禁用项）
> style_anchors_applied: # 从选定风格 META.md 抄来的不可妥协锚点
> retry_frozen:         # 本轮重试冻结的字段清单；首轮写 none
> ```
> 
> 填表纪律：
> 
> - 每个字段只能有一个值。拿不准就停下来问，不要写「A 或 B」蒙混过关
> - `focal_point` 只能有一个。列出两个焦点等于没有焦点，缩略图上会互相抵消
> - `text_charcount` 必须真的数一遍 `title_a`+`title_b`+`title_c` 里会画进图的部分，并在 prompt 里写成正向约束（「画面文字恰好是这 N 个字符，不多不少：…」）。写「不要多加字」这类否定式约束实测会反噬
> - 同一份输入不要为了求新而换 palette、换版式、换风格。变化来自 `metaphor` 的核心动作，不来自随机漂移
> 
25a63,65
> - 载体：{carrier}（必须出现的载体信号：{carrier_required_signals}）
> - 画面焦点（只有一个）：{focal_point}
> - 画面文字恰好是这 {text_charcount} 个字符，不多不少：{画面全部文字}
57a98,102
> - mockup 摄影感：纸张投影、翘边、透视变形、桌面或墙面环境、手持展示
> - 设备外框（手机/笔记本/平板/浏览器窗口/UI 状态栏）、画中画取景框、内圈白边、相框
> - 本次载体的禁止信号（从 `references/carriers.md` 选定 carrier 抄入）：{carrier_forbidden_signals}
> 
> 后三条治的是同一个病：模型在画「关于这张图的照片」，而不是画这张图本身。`merch_print` 载体且用户明确要周边效果图时，mockup 一条对该次任务解除。
```
