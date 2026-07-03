# changelog-gen — description 设计交付

## 最终 description（frontmatter 用）

```yaml
description: Generates a structured CHANGELOG.md fragment from a git repo's recent commit history, formatted to the Keep-a-Changelog spec (Added / Changed / Fixed / Removed / Deprecated / Security sections). Supports a specific version/tag/commit range (e.g. v1.2.0..v1.3.0, or "last N commits"). Trigger when the user asks to "generate a changelog", "write/update CHANGELOG.md", "把 commit 按 Added/Changed/Fixed/Removed 分类", "生成变更日志", "整理一份 Keep a Changelog 格式的记录", or gives a version/tag range and wants the commits between them bucketed into those categories — even if they don't say the word "changelog" explicitly, as long as the ask is a categorized log entry derived from commit history. Do NOT use for: writing a single commit message (authoring one commit's message, not summarizing a range of history — no categorization involved); summarizing/describing what a PR did in prose ("总结这个 PR 干了啥", PR description — narrative writing, not a Keep-a-Changelog structured list); producing release notes or an announcement/email meant for an external or customer-facing audience (different register and structure — marketing/comms copy, not a developer-facing categorized changelog); writing a migration guide for breaking API changes; or general git log inspection / code review of specific commits.
```

## 设计过程

### 1. 先锁定可观测触发特征（模式 8）

避免"用户想要总结改动时判断要不要触发"这种含糊表述。把触发条件拆成两类可枚举信号：

- **产物信号**：目标文件/产物是 `CHANGELOG.md` 或"变更日志"，且要求按 Keep-a-Changelog 的固定分类（Added/Changed/Fixed/Removed/Deprecated/Security）分桶。
- **输入信号**：给定的是一个 commit 区间/版本区间/tag 区间（不是单个 commit，不是当前工作区 diff 的代码审查）。

两个信号任一命中即可判定为候选，不依赖"agent 自己判断这算不算 changelog 任务"的主观裁量。

### 2. 治 undertrigger：写得 pushy（模式 9）

初稿只写了"当用户要生成 changelog 时触发"，会漏掉用户没说"changelog"这个词、但描述的其实就是这个任务的情况（比如"把这段时间的 commit 按新增/修复/移除分个类写进去"）。按模式 9 的建议追加了一句显式覆盖：

> "even if they don't say the word 'changelog' explicitly, as long as the ask is a categorized log entry derived from commit history"

同时把中英文关键词都列全（用户可能用中文描述："生成变更日志""按 Added/Changed/Fixed/Removed 分类""整理一份 Keep a Changelog 格式的记录"），因为这个 skill 的使用场景大概率中英文都会出现。

### 3. 构造 20 条 eval query，覆盖 near-miss 负例（模式 13）

没有可执行的 3-run 触发率统计环境，所以用同样的 train/test 思路做**人工推演**：写出 20 条 query（10 正例 + 10 负例），负例专门挑共享关键词（commit / release / PR / 总结）但实际该走别处的场景，不用"帮我订披萨"这种无意义负例。

**正例（应触发）**
1. 帮我生成一下 CHANGELOG，从上个 tag 到现在
2. 给这个仓库按 Keep a Changelog 规范整理一份 changelog
3. v1.2.0 到 v1.3.0 之间的改动，分类成 Added/Changed/Fixed 输出
4. 发布前需要一份 changelog 片段，从最近 20 个 commit 生成
5. 把这段时间的 commit 按变更类型分好类写进 CHANGELOG.md
6. 这个仓库有没有工具能自动生成结构化的更新日志
7. 对比这两个 tag 之间的历史，输出规范格式的 changelog
8. 我要在 CHANGELOG.md 里加一节，列出新增/修复/移除的内容
9. 根据 git log 生成本次版本的变更记录（分类展示）
10. changelog 怎么写，帮我按最近的提交历史生成一份

**负例（近似但不该触发，均为共享关键词的 near-miss）**
1. 帮我写个 commit message —— 共享"commit"，但目标是单条提交的信息，不是历史区间的分类汇总
2. 总结一下这个 PR 干了啥 —— 共享"总结改动"，但是叙事性描述而非结构化分类
3. 生成 release notes 发到邮件给客户 —— 共享"发布/版本"，但受众是外部客户，语域是营销文案不是开发者向 Keep-a-Changelog
4. 帮我写一下这次发布的公告文案 —— 共享"发布"，但是宣传文案
5. review 一下这几个 commit 的代码质量 —— 共享"commit 历史"，但是代码审查不是变更归类
6. 帮我把这几个 commit squash 一下 —— 共享"commit"，但是 git 操作不是文档生成
7. 这个版本改了哪些 API，写个迁移指南 —— 共享"版本改动"，但产物是迁移指南不是分类日志
8. 给这次 PR 写个描述 —— 共享"PR"，但是叙事性 PR description
9. 帮我看看提交历史里有没有能追溯到某个 bug 的 commit —— 共享"commit 历史"，但是 debug/archaeology 不是生成文档
10. 总结一下这周团队做了什么工作 —— 共享"总结近期变更"，但是站会/工作汇报不是面向版本的 changelog

### 4. 按负例反推 description 的排除条款

第一版 description 只写了触发词，没写排除项，逐条推演上面 10 个负例时发现三处真实误触发风险，据此把 description 从"纯正例列举"改成"正例 + 显式 Do NOT use for"：

- **commit message vs changelog**：都含"commit"，区分点写成"authoring one commit's message" vs "summarizing a range of history"——单数/复数 + 是否分类，是可观测的区分特征，不是语气判断。
- **PR 总结 / PR 描述 vs changelog**：都含"总结改动"，区分点写成"narrative writing" vs "a Keep-a-Changelog structured list"——产物形态（散文 vs 固定分类列表）可观测。
- **release notes/公告文案 vs changelog**：都含"发布/版本"，区分点写成受众和语域"external/customer-facing" vs "developer-facing categorized"——这条风险最高，因为 release notes 和 changelog 在很多团队里其实内容重叠，所以特意用"受众"而非"内容"做区分锚点，避免两个 skill 抢同一批任务。

追加了迁移指南、代码 review、git 历史 debug 三条低风险但仍算 near-miss 的排除项，做完整覆盖。

### 5. 复核最终 description 对 20 条 query 的判定（人工过一遍，非自动化统计）

正例 1-10：均命中"产物=CHANGELOG/changelog 分类"或"给定版本区间要求分桶"两个信号之一，判定触发。
负例 1-10：均命中 Do NOT use for 里某一条排除项的关键区分特征（单条 vs 区间、叙事 vs 结构化列表、外部受众 vs 开发者向、迁移指南、代码审查、debug 溯源、站会汇报），判定不触发。

局限说明：这是单次人工推演，不是模式 13 描述的"实际跑 3 次取稳定触发率"的自动化统计闭环——没有环境能反复起 fresh session 调用真实 Claude 触发判断并计数。如果要做到模式 13 完整闭环，下一步应该是把上面 20 条 query 灌进实际的 skill 触发测试脚本，各跑 3 次，按 test 集（后 8 条，即负例 6-10 与正例 6-10）的稳定触发率而非 train 集分数选择最终版本，防止过拟合到本次手写的这 20 条。
