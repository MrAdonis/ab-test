# 模型分工 AB Test 报告

**日期**：2026-05-26
**对比**：Opus 4.7 / Sonnet 4.6 / GPT-5.5 (Codex CLI, reasoning=high)
**目的**：验证 leon7hao 的「GPT 强在架构梳理、Opus 强在前端」是否成立，重新校准我们的模型路由

---

## 四项测试

| # | 任务 | 验证什么 |
|---|------|---------|
| T1 | FAQ Accordion HTML 组件 | 前端实现 + 视觉审美 |
| T2 | <project> 架构耦合扫描（33 文件） | 架构梳理深度 |
| T3 | JS 并发缓存 race condition debug | 找 bug 真因 + 生产 awareness |
| T4 | R2 vs S3 中文推文（280-400 字） | 中文写作 + 判断力 |

每项三个模型跑同一 prompt，prompt 自包含（不依赖项目 context）。

---

## 详细评分

### T1 前端实现 HTML 组件

| 模型 | 代码量 | 视觉风格 | 视觉评分 | 代码评分 |
|------|--------|---------|---------|---------|
| Opus 4.7 | 7.7k | 白底 + 蓝紫 chip + Apple 风克制 | 9 | 8 |
| Sonnet 4.6 | 11k (最大) | 白底 + 数字 badge（过度设计） | 7 | 7 |
| **Codex GPT-5.5** | **6.1k (最少)** | **dark slate + cyan + glassmorphism，最现代** | **9** | **9** |

**关键发现**：
- Codex 用最少的代码做出最有视觉冲击力的设计（dark theme + backdrop-blur + SVG chevron）
- Opus 走商务克制路线，留白讲究
- Sonnet 多写 70% 代码做出中等效果（自己加了数字 badge，过度设计）
- **彻底推翻 leon7hao「GPT 不擅长前端」的判断**——GPT-5.5 前端能力已和 Opus 持平甚至局部胜出

### T2 架构梳理

| 模型 | 总 findings | 独占 findings（其他没找到的） | 深度 |
|------|------------|---------------------------|------|
| Opus 4.7 | 16 | 3：3 套 LLM JSON 抽取、6 处 claude CLI 表、3 个 UA 版本 | 最深 |
| Sonnet 4.6 | 12 | 4：config.py mkdir 副作用、backlog 隐式依赖链、ghost imports、dual dedup 机制 | 中 |
| **Codex** | 12 | 2：item schema 隐式契约、Builder 阈值双来源 | 最浅 |

**覆盖矩阵（部分关键 finding）：**

| Finding | Opus | Sonnet | Codex |
|---------|------|--------|-------|
| config.py YAML 加载副作用 | ✅ | ✅ | ✅ |
| config.py mkdir 副作用 | ❌ | ✅ | ❌ |
| generate.py 11 职责 + 7 handler 重复 | ✅ 12-step 分解 | ✅ | ✅ |
| backlog.py 隐式依赖链 | ❌ | ✅ | ❌ |
| Ghost imports (SEEN_FILE) | ❌ | ✅ | ❌ |
| 3 套独立 LLM JSON 抽取 | ✅ 全代码对比 | ❌ | ❌ |
| 6 处 claude CLI 不统一 | ✅ 含 model+timeout 表 | ❌ | ✅ |
| UA 字符串 3 版本 | ✅ | ❌ | ❌ |
| Item schema 隐式契约 | ❌ | ❌ | ✅ |
| Builder 阈值双来源 | ❌ | ❌ | ✅ |
| 同职责双实现 (generate_card vs generate_news_card) | ✅ | ✅ | ❌ |
| dual dedup (seen.json + publisher.db) | ❌ | ✅ | ❌ |

**关键发现**：
- Opus 深度最强（最多 findings + 最详细分析），但漏了 Sonnet 容易抓到的 mkdir 副作用和 ghost imports
- Sonnet 覆盖最均衡：抓到了"低垂果实"+ 部分深度问题
- **Codex 优势在架构框架性思考**（开篇就说"未发现直接循环依赖，是中心型耦合"——明确定性），但 findings 数量少
- **leon7hao「Codex 擅长架构梳理」只对了一半**——擅长"框架定性"，但深度盘点不如 Opus

### T3 深度 Debug

所有 3 个模型都正确定位根因（cache.set 在 await 之后，并发调用穿过 cache.has 检查）。差异在生产 awareness：

| 模型 | 根因正确 | 修复方案完整度 | 推理路径 |
|------|---------|--------------|---------|
| Opus 4.7 | ✅ | **3 项细节**：缓存 Promise + 失败时清 cache + img.src 移到事件绑定后 | 5 步 + Step 4 反向验证（3 个反推论）|
| Sonnet 4.6 | ✅ | 1 项：缓存 Promise | 5 步直推 |
| Codex | ✅ | 2 项：缓存 Promise + 失败时清 cache | 5 步直推 |

**关键发现**：
- Opus 多出的「img.src 移到 onload/onerror 绑定之后」是真实生产坑（缓存图片同步触发 onload 会丢失事件）——只有 Opus 想到
- Opus 推理路径有「反向验证」环节（如果根因正确，那么 A/B/C 三个推论应该成立）——其他两个没做
- **leon7hao「Codex 找 bug 真因」对，但 Opus 不输——Opus 在生产 awareness 上反而胜出**
- 注意：此测试是「中等难度 bug」，对真正难定位的（多层栈、跨服务）Codex 的优势会更明显，本测试不能完全否定 leon7hao

### T4 中文写作

| 模型 | 字数 | hook 力度 | 判断明确度 | 平台适配 | 评分 |
|------|------|---------|----------|---------|------|
| Opus 4.7 | 280 | 「独立开发者还在用 S3 的，赶紧算笔账」 | $90 vs 0 具体计算 + 3 档 use case + 结论 | 优秀 X 风格 | 9 |
| Sonnet 4.6 | 300 | 「做过一次实际对比」（假装做过对比，弱） | 有判断但稍 bookish | 良好 | 8 |
| Codex | 250 | 「给独立开发者一句话」（lecture 开场） | 论证完整但缺戏剧性 | 单段无 break，不像 X | **5** |

**关键发现**：
- Opus 的推文最「X-native」：有 hook、有计算（1TB 省 $90）、有判断（"默认 R2，省下来够付一年域名"）
- Codex 写的像 Wikipedia 词条——单段无分隔、academic 语气、最弱的结论
- **leon7hao 没提中文写作，但这是最明显的 gap**：Anthropic 模型 >> Codex
- 不要让 Codex 写中文（除非作为 fallback 翻译）

---

## 综合评分（10 分制）

| 任务类型 | Opus 4.7 | Sonnet 4.6 | GPT-5.5 (Codex) |
|---------|---------|-----------|------------|
| 前端实现（设计感重） | 9 | 7 | **9** |
| 前端实现（简单 CRUD） | 9 (杀鸡用牛刀) | **8 (够用)** | 8 |
| 架构梳理（大型） | **9** | 7 | 7 |
| 架构梳理（中小型） | 8 (杀鸡用牛刀) | **8** | 7 |
| 深度 Debug | **9** | 7 | 8 |
| 中等 Debug | 8 (杀鸡用牛刀) | **8** | 8 |
| 中文长文写作 | **9** | 8 | 5 |
| 英文工程文档 | 8 | 8 | **8** |
| 代码 Review（找 bug） | 8 | 7 | **9 (外人视角强)** |

加粗 = 该场景推荐首选。

---

## 对 leon7hao 判断的验证结果

| leon7hao 的说法 | 实测结论 |
|---|---|
| GPT 不擅长写前端 | ❌ **错**——GPT-5.5 前端能力 ≥ Opus，且代码量更少 |
| Codex 擅长架构梳理 | ⚠️ **半对**——擅长"框架定性"，但 finding 深度不如 Opus |
| Codex 擅长找 bug 真因 | ⚠️ **半对**——简单 bug 都能解；难定位 bug 优势在「外人视角」而非"找根因能力" |
| GPT 擅长生图 | ✅ **对**（本次未测，保留判断） |
| Opus 擅长写前端 | ✅ **对**——但 Codex 也行 |
| Opus 擅长写文档总结 | ✅ **对**——中文写作差距最大 |
| Opus 不擅长复杂深入任务 | ❌ **错**——Opus 4.7 在架构/debug/写作三项都最强；这条停留在 4.5 时代 |
| Opus 不能遗漏细节的任务不行 | ⚠️ **半对**——确实漏了 mkdir/ghost imports 这类「低垂果实」，但深度上没人比它强 |

---

## 新的模型路由建议

替换现有 `~/.claude/CLAUDE.md` 的「模型路由」段。核心调整：

1. **拆「前端 vs 后端」**：现有规则只按文件数判断，新规则按内容类型
2. **加 Codex 进首选名单**：现有路由把 Codex 当"R lane 救火"，实际它在前端/找 bug 上是常态选项
3. **明确「Codex 不写中文」**：是一条强约束
4. **明确「Opus 不再是 ceiling-only」**：4.7 在所有质量维度都强，不只是"复杂任务备选"

### 建议的新模型路由段

```markdown
## 模型路由（基于 2026-05-26 AB test 实测）

**主会话默认 Sonnet**（除非用户手动切换），每会话开始自动评估任务：

### 按任务类型分流

| 任务 | 首选 | 次选 | 不推荐 |
|------|------|------|--------|
| 前端实现（简单 CRUD / 单文件 < 300 行） | Sonnet | Opus / Codex | — |
| 前端实现（设计感重 / 复杂组件） | Opus 或 Codex（前者克制商务，后者现代戏剧） | Sonnet | — |
| 架构梳理（大型 5+ 文件） | Opus | Sonnet（实用覆盖） | Codex（finding 漏） |
| 架构梳理（中小型 < 5 文件） | Sonnet | Opus | Codex |
| 后端实现（中等 / 业务逻辑） | Sonnet | Opus（3+ 文件起） | — |
| 后端实现（复杂状态机 / 并发 / 分布式） | Codex（R lane） | Opus | Sonnet |
| 深度 Debug（多层栈 / 失败 2+ 次） | Opus + Codex 交叉（不同视角） | — | Sonnet |
| 中等 Debug | Sonnet | Opus | — |
| 中文长文写作 / 推文 / 公众号 | Opus > Sonnet | — | Codex（academic 太重） |
| 英文工程文档 | Sonnet / Codex / Opus（都行） | — | — |
| 代码 Review / 找 bug | Codex（R lane，外人视角强） | Opus | Sonnet |
| 探索 / 文件读取 / 状态查询 | Sonnet | — | Opus / Codex（杀鸡用牛刀） |

### Auto-choose 行为

判断属 Opus 范畴时，回应前说「这个任务建议用 Opus，输入 `/model opus` 再继续，或者说"继续"用 Sonnet 也行」。判断属 Codex 范畴时，按 lane 路由（R/C/E）执行，不切主会话模型。

### 缓存成本（保留旧规则）

切换模型 = 当前 session 缓存全失效（KV 张量不互用），一个任务阶段内保持同一模型，阶段间再切。例外：Sonnet 已失败 2 次且判断需 Opus，立即切，不为保缓存拖延。
```

### 三处改动总结

1. **新增「前端 vs 后端」拆分**——现有只按文件数，新版按内容类型
2. **Codex 升为常态选项**（前端、找 bug 写法）——不只是 R lane 救火
3. **明确「Codex 不写中文」**——新增禁用场景

---

## 附：产出文件位置

| 任务 | 文件 |
|------|------|
| T1 HTML | `t1-accordion/{opus,sonnet,codex}.html` + `_results/t1-{opus,sonnet,codex}.png` |
| T2 Arch | `t2-arch/{opus,sonnet,codex}.md` |
| T3 Debug | `t3-debug/{opus,sonnet,codex}.md` |
| T4 Tweet | `t4-chinese/{opus,sonnet,codex}.txt` |
| Prompts | `_results/t{1,2,3,4}-prompt.md` |
