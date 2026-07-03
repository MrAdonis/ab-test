# changelog-gen — description 设计交付

## 最终 description（frontmatter）

```yaml
---
name: changelog-gen
description: Generates a structured CHANGELOG fragment from a git repo's commit history, grouped into Keep a Changelog categories (Added / Changed / Fixed / Removed / Deprecated / Security), for a specified version or commit range (e.g. "since v1.2.0", "between v1.2 and v1.3", "since last tag"). Trigger when the user asks to "generate a changelog", "write CHANGELOG entries", "update CHANGELOG.md", "生成 changelog", "更新变更日志", "整理这个版本的变更记录", names Keep a Changelog / "keepachangelog" format explicitly, or gives a version/tag/commit range together with intent to categorize the changes for a changelog file. The deliverable is a structured, categorized changelog fragment — NOT prose summary, NOT a single commit message, NOT audience-facing release notes. Do NOT trigger for: writing/improving one commit message for the change currently being committed (that's forward-looking, single-commit — plain commit authoring, no categorization); summarizing "what did this PR/branch do" in narrative prose for a reviewer (→ conversational summary, not Keep-a-Changelog sections); or drafting human-readable release notes / announcement copy for email, blog, or marketing audiences (release notes are narrative and reader-facing; this skill's output is a developer-facing structured diff by change type, not narrative). If the user says "release notes" or "summarize this PR" without asking for CHANGELOG-style Added/Changed/Fixed/Removed sections, do not trigger silently — surface that a structured changelog is available and ask if that's what they want instead.
---
```

## 设计过程

### 1. 先钉可观测触发特征，不留"自己判断"空间（模式 8）

把"用户想不想要 changelog"拆成三类可枚举信号，触发条件只认这三类，不认"感觉像是相关任务":

- **动作词 + 产物词命中**："生成/写/更新" ×「changelog / CHANGELOG.md / 变更日志」的组合，或直接点名 "Keep a Changelog" / "keepachangelog" 格式。
- **版本区间信号**：出现 tag/commit range 表达（"since v1.2"、"v1.2..v1.3"、"since last tag"、"这个版本的变更"）且伴随"分类整理变更"的意图——单独一个版本号不够，必须搭配分类/归纳意图，否则会被"帮我看看 v1.2 到 v1.3 之间改了什么 bug"这种纯问答任务误触发。
- **中文触发词**：单独列出「生成 changelog」「更新变更日志」「整理这个版本的变更记录」，不依赖英文词根匹配中文场景。

三类都是可枚举的词面/结构特征，不是"AI 自己判断这是不是 changelog 任务"——避免 undertrigger（模式 9 指出的默认倾向）也避免把判断权交给模型的临场发挥。

### 2. 显式反例排除三个易混任务

用户点名的三个相邻任务逐一分析为什么会被误触发、以及排除依据：

| 相邻任务 | 为什么容易误触发 | 排除依据（写入 description） |
|---|---|---|
| "帮我写个 commit message" | 都涉及"读 git 历史 + 描述变更"，动作词高度重叠（"写""生成"） | 时间方向不同：commit message 是对**即将提交的单个变更**的前瞻描述，changelog-gen 是对**已发生的一段历史**做回顾分类。description 里显式点名"single-commit""forward-looking"排除 |
| "总结这个 PR 干了啥" | 都是"看 commit/diff 总结变更内容" | 输出形态不同：PR 总结是**给 reviewer 看的叙事段落**，changelog-gen 输出是**按 Added/Changed/Fixed 分类的结构化条目**。description 显式要求"没有要求 CHANGELOG 分类结构就不触发"，把判据锚定在"有没有要求分类结构"而非"是不是在总结变更" |
| "生成 release notes 发邮件" | 都是"面向发布的变更文档"，都可能引用同一段 commit 历史 | 受众不同：release notes 是**读者/客户向的叙事文案**（要吸引人、要讲人话），changelog-gen 是**开发者向的结构化 diff**（要精确、要分类）。这个区别在写作层面也对应 content-profiles 的"平台/受众决定文体"逻辑——changelog 不是给人当故事读的 |

三个反例没有停留在"不要用于 X"的一句话，而是各自给了一条**结构性判据**（时间方向 / 输出结构 / 受众），这样即使用户换了措辞（比如说"整理一下这次发布要讲给客户听的变更"而非直接说"release notes"），模型也能靠判据本身识别，而不是靠字面关键词硬匹配失败就漏判。

### 3. 加一条"歧义时不要静默不触发"的兜底

模式 9 强调 Claude 默认倾向 undertrigger。三个反例排除容易让模型在边界模糊时（比如用户说"总结一下这次发布"，没说清是要 PR 叙事还是要 changelog 分类）直接判定"不是我的任务"就沉默过去。description 末尾补了一条：命中"release notes"或"总结 PR"但没提结构化分类要求时，**不要静默跳过**，要主动反问用户是否想要结构化 changelog——这样即使排除判据判断有误差，也不会真的漏掉该触发的场景，只是多问一句确认，比误触发（在纯叙事请求上跑分类流程）或漏触发（用户其实想要 changelog 却没得到）都更安全。

### 4. 自检（对照方法库两条）

- 触发条件是否可观测、可枚举，不是"判断力"？→ 是：动作词+产物词组合、版本区间+分类意图、中文关键词，三类都是词面/结构层面可枚举的，不依赖模型对"这是不是历史类任务"的主观裁量。
- description 是否覆盖了所有该触发的措辞，包括用户不会直接说出技能名的场景？→ 覆盖了中英文变体、"since last tag"这类隐式版本区间表达；同时用排除判据（时间方向/输出结构/受众）而非关键词黑名单来防止在相邻任务上误触发，判据比关键词更能扛住措辞变化。
