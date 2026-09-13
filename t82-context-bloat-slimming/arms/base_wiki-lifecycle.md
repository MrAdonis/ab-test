# Wiki Lifecycle

管理 brain/01-Wiki/ 的知识生命周期。四个机制：蒸馏、隧道、替换、清理。

## 核心定位

**Wiki = 跨项目共享知识层。** 项目特定信息留在各自 memory（`~/.claude/projects/*/memory/`）和 HANDOFF.md，跨项目通用知识蒸馏到 `brain/01-Wiki/`。

分流标准：
- "FleetOS-HK 的 WebSocket 配置是 X" → 项目 memory
- "Cloudflare proxy 后 WebSocket 会被 idle timeout 断开" → wiki（任何项目都可能遇到）
- "用户偏好直接给命令不绕快捷键" → 全局 memory（行为偏好）

## 1. Crystallization（会话蒸馏）

完成非平凡工作后，提取**跨项目可复用**的洞察写入 `~/Documents/brain/01-Wiki/_inbox/`。

### 触发条件（满足任一）

- Debug 找到根因（理解了"为什么"，不只是"改了就好"），且根因不限于当前项目
- 技术选型做了有取舍的决策，取舍逻辑对其他项目也有参考价值
- 发现跨项目适用的模式或反模式
- 学到工具/框架的非显而易见用法
- 工作流改进被验证有效

### 不触发

- 纯执行类（改文案、调样式、跑命令）
- 项目特定的临时状态（→ HANDOFF.md）
- 发现只对当前项目有用（→ 项目 memory）
- 已有 wiki 页覆盖的内容（→ 更新已有页）
- 本次会话没有产出新认知

### 写入格式

文件名：`{topic}-{date}.md`（如 `symlink-bypass-hook-2026-04-13.md`）

```yaml
---
title: 简短标题
sources:
  - "会话蒸馏 YYYY-MM-DD"
  - "[[其他相关来源]]"
updated: YYYY-MM-DD
type: concept | method
tags: [从 SCHEMA.md taxonomy 选]
status: inbox
---
```

正文结构：

```markdown
## 发现
[一段话：什么场景下发现了什么]

## 关键细节
[具体技术细节、代码、配置——让未来的你不用重新推导]

## 适用场景
[什么时候会再遇到这个]

## 关联
- [[已有wiki页]] — 关系说明
```

### 执行时机

- /handoff 时自动检查：本次会话是否有 inbox 候选
- 主动提示但不强制：如果有候选，说"本次有 wiki 蒸馏候选：{topic}，要写入吗？"
- 用户说"不用"则跳过，不追问

### inbox 生命周期

inbox 页面是草稿，不更新 index.md。用户定期 review _inbox/：
- 通过 → 移到正式分区（concepts/methods/tools/），更新 index.md，加 wikilinks
- 不通过 → 删除或合并到已有页

## 2. Cross-Project Tunnels（跨项目隧道）

不同项目遇到相同概念时，wiki 页面是天然的连接点。

### 机制

当在项目 A 中发现的知识已有 wiki 页（或刚蒸馏出一篇），在项目 B 的会话中遇到相关问题时：

1. **写入时建隧道**：蒸馏新页面时，在"关联"部分标注所有涉及的项目
   ```markdown
   ## 关联
   - [[已有wiki页]] — 关系说明
   - 项目: FleetOS-HK, edonspace — 都部署在 Cloudflare 后面
   ```

2. **读取时走隧道**：进入新项目会话，遇到 wiki 已覆盖的问题，先查 wiki 再动手。具体来说：
   - debug 陷入僵局时，搜索 wiki 看有无已知模式
   - 技术选型时，搜索 wiki 看有无已做过的取舍决策

3. **回写更新**：如果在项目 B 中发现 wiki 页内容需要补充（新的边界情况、新的适用场景），直接更新 wiki 页而非写新的项目 memory

### 不需要做的

- 不维护显式的"项目→wiki 页"映射表——wikilinks + 关联部分已足够
- 不在每个项目 memory 里重复写 wiki 已有的知识——引用 wiki 页名即可
- 不强制每个项目都关联 wiki——只有真正跨项目复现的知识才值得

## 3. Supersession（知识替换链）

Memory 文件（~/.claude/projects/*/memory/）更新时，区分**补充**和**替代**。

### 判断标准

| 类型 | 定义 | 操作 |
|------|------|------|
| 补充 | 新信息扩展旧信息，核心主张不变 | 直接编辑旧文件（mtime 自动反映改动时间，不手动记日期）|
| 替代 | 新信息否定旧信息的核心主张 | 走 supersession 流程 |

### Supersession 流程

1. 创建新 memory 文件，frontmatter 加 `supersedes: old_filename.md`
2. 旧文件 frontmatter 加 `superseded_by: new_filename.md`，confidence 降为 low
3. MEMORY.md 中旧条目后追加 `(superseded by new_filename.md)`
4. 新条目放到对应 confidence 分组

### 粒度注意

综合性 memory（如 project_xxx.md 包含多个主张）只有被否定的**那条主张**需要 supersession。如果文件中其他主张仍然有效，优先拆出被否定的部分单独建新文件，而非整文件替换。

### 读取时

遇到 `superseded_by` 标记的 memory，跳转读取替代文件。引用时用新文件的内容。

## 4. Self-healing Lint

`~/.claude/scripts/wiki-lint.sh` 扫描 brain/01-Wiki/ 健康状态。

### 检查项

| 检查 | 严重度 | 说明 |
|------|--------|------|
| 孤立页 | warn | 在 index.md 中但 wiki 内无 incoming `[[wikilink]]` |
| 缺失页 | error | `[[wikilink]]` 指向不存在的文件 |
| 过期页 | warn | `updated` 超过 180 天 |
| Frontmatter 缺失 | error | 缺少 title/updated/type/tags 任一字段 |
| 超长页 | warn | 超过 200 行（SCHEMA 建页阈值要求拆页） |
| inbox 积压 | info | _inbox/ 超过 5 篇未 review |

### 运行方式

- 手动：`bash ~/.claude/scripts/wiki-lint.sh`
- 在 Claude 会话中：处理 wiki 内容后主动运行一次
- 输出修复建议，不自动修改文件

## 5. Edit Discipline（编辑纪律）

借自微软 SkillOpt 的编辑纪律。**只取纪律思路，不装代码、不跑训练循环**——它的全自动 optimizer 需要可打分 benchmark，只适合 pass/fail 型 skill，写作/`/biz`/design-system 这类无法自动打分的不适用；但编辑原则适用于一切 rules/skill/memory 维护。

### ① 少而准：只增不删 = 在堆料

最好的 skill 整轮优化只接受 **1–4 次编辑**——接受了自己提出的大部分编辑，不是在优化，是在 appending。

- 改 rules/skill/CLAUDE.md 时，单次只动几处，且**必须能说出这次删了什么**。一次改动里只有新增、零删除 → 默认判定为堆料，停下重审「这条真的不能合进已有段落 / 替换掉某条旧规则吗」
- 这是对 supersession（§3 管「替换」）的反向补充：§3 处理「新否定旧」，本条处理「主动精简」——配置膨胀的压力来自后者缺失
- 触发自检场景：CLAUDE.md / rules 任一文件因本次改动**净增行数**，或新建 memory 文件而未检查能否更新已有文件

### ② Bounded edit（文本学习率）

一次只改一个相关簇，改完过验证门再改下一处，不要一轮糊上一大片。

- 大批量编辑 = 高方差，出问题无法归因到具体哪一处
- 与 `coding.md` 假设驱动调试的「单变量」同源：改 rules 也是单变量——一次验证一条规则的效果，别同时动 3 条再跑 AB test

### ③ Rejected-edit buffer（被拒编辑记负反馈）

每次 AB test 回滚 / 评估否决的改动，单独记一行：改了什么、为什么没提升。下次别重复同方向。

- 落点：在对应 skill 的 `## Gotchas` 段或 `~/.claude/projects/*/memory/` 记一条 `*_rejected.md`，frontmatter `confidence: high`（被验证过的负结论比正结论更稳）
- 两层记录：规则级（这条编辑为何没提升）必记；能提炼出「这类方向不值得再探」的（如 t44 否定的不是一条规则而是「检索型风格库用于创意场景」整个方向），在同一条 rejected memory 里显式写出方向级结论——方向级复用面大，防换个皮重试同方向

### ④ 存量回测（只增不减的反向闸）

①管「别加堆料」，本条管「已加的过时了要拔」——AB 框架是单向棘轮，只在「加规则」那刻验证一次「baseline 是否已会」，之后规则永久驻留 slow-state。但 baseline 在涨（所有 AB 用 Sonnet 当 baseline 测，主会话可能已是更强 model），针对旧 baseline 弱点测出的规则会随底模普涨衰减成 context 噪声。

- **退役触发 = 底模大版本跳变**（Sonnet / Opus 大版本号变），不必定期全量回测（成本高）。只在这个「baseline 能力可能质变」的节点，回测 margin 最小的几条已加规则——每条 AB 入配时注释已留 margin + 日期（如 coding-dod t32「B 49.5 vs A 41.2」），margin 大的更可能仍有效，优先重测 margin 小的
- 重测翻盘（baseline 已自会，复现 t31「baseline 不蠢就别加」）→ 退役该规则，走 §3 supersession 降级/删除。这是 §① 少而准的存量版，配置才不至于只增不减

### Fast/Slow 边界（结构不变量）

SkillOpt 的核心稳定机制——fast-state 不能覆盖 slow-state。你已在做，本节把它写成硬约束：

| 层 | 内容 | 文件 |
|----|------|------|
| **slow-state**（累积心得、规则、方法论，慎改，走本节①②③） | 规则、wiki 正式分区、方法论 | `rules/`、`brain/01-Wiki/`（非 _inbox） |
| **fast-state**（会话级临时状态，随时覆写，不进 slow） | 进度、候选、交接、临时草稿 | `round-state.md`、`candidates.md`、`HANDOFF.md`、`_inbox/` |

- **不变量**：fast-state 的内容不得直接写入 slow-state——必须经过提炼/验证（candidates → memory 走三色晋升；_inbox → 正式分区走 review）。绕过晋升直接把临时观察塞进 rules = 违反边界
- 这条解释了为什么 `candidates.md`（fast）和正式 memory（slow）必须分开：fast 频繁覆写，混进 slow 会污染稳定知识
