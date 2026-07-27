先说结论：**方案一更好，7.5 vs 6.5**。但两份都有一个致命的共同盲区——整份报告完全是自证的，没有任何东西拿真实工作区去交叉核对。

---

## 总分与理由

### 方案一：7.5 / 10

赢在它正面回答了这个需求真正的风险：40 个代理往你仓库里写了代码，你凭什么信。三个决定性设计——

1. **`fix_diff` 存真实 unified diff**，不是"改了什么"的自然语言描述；
2. **独立的 verify stage**（`diff_safe` / `issues` / `tests_run`），改动由另一个代理复核，不是自己给自己打分；
3. **修复口径写进 prompt**（critical/high + confidence=high 才自动改，涉及接口签名/schema 一律进 blockers）。这条最容易被低估：不写死，40 个子代理就是 40 套松紧标准，最后你拿到的 `fixed: true` 是不可比的。

输在工程完成度：给的脚本片段本身是错的（下面细说），聚合逻辑只给了数据形状没给代码。

### 方案二：6.5 / 10

赢在"能直接跑"：`aggregate()` 是完整可运行的 JS，`category` 用闭合 enum（方案一是自由文本 `"CWE-89 / OWASP A03 等"`，聚合时按分类分组会散架），`id` 加 `${module}::` 前缀去重是方案一漏掉的真实 bug，`false_positive_noted` 让"查过但排除了"留痕。结尾追问 MODULES 列表怎么来（手列还是先扫）也是方案一没提的真问题。

输在它对(c)基本没有交付：`fixDiffSummary` 是一段散文，没有 diff，没有 verify，没有测试。你拿到报告后仍然要自己把 40 个模块的 `git diff` 从头看一遍——那这份报告只是个索引，没有降低你的复核成本。

---

## 四维打分

| 维度 | 方案一 | 方案二 |
|---|---|---|
| (a) 能不能直接落到脚本里 | **6** | **8** |
| (b) 覆盖完整性 | **8** | **7** |
| (c) 改动是否可复核 | **9** | **5** |
| (d) 失败/边界处理 | **7** | **6** |

**(a) 落地性 — 方案二胜**

方案一第 4 节的代码片段是**直接抄进去就错的**：

```js
(r, m) => r && r.findings.some(f => f.fixed)
  ? agent(verifyPrompt(m, r), {...})
  : null          // ← 没修复的模块整条 audit 数据被丢成 null
```

`results` 数组里于是混着 verify 对象和 null，audit 原始数据一条都不剩。它的正文紧接着指出了这个坑（"得在 stage2 里拼成 `{...auditResult, verify}`"），但代码没改——一份"直接落到脚本里"的产出设计，示例代码和正文互相矛盾是硬伤。正确写法两个分支都要合并：

```js
(r, m) => {
  if (!r) return { module: m.name, audit: null, verify: null }
  return r.findings.some(f => f.fixed)
    ? agent(verifyPrompt(m, r), { phase: 'Verify', schema: VERIFY_SCHEMA, label: m.name })
        .then(v => ({ ...r, verify: v }))
    : { ...r, verify: null }
}
```

方案二的 `aggregate()` 是能直接跑的，`MODULES.filter((m, i) => moduleReports[i] === null)` 的索引对齐也正确（pipeline 保序）。

**(b) 覆盖 — 方案一胜，但互有缺口**

方案一多出：`evidence`（原始代码片段）、`residual_risk`（修完还剩什么，且强制修没修都填）、`blockers`（需人决策的事）、干净模块也报 `scanned_files`。方案二多出：category 闭合枚举、cwe 独立字段、`filesReviewed` 文件清单（比方案一的数字更能看出漏扫）、误报留痕、id 去重。

方案二有个 schema 设计失误：`line` 进了 `required`。"全局缺 CSRF 中间件"、"依赖 CVE"这类发现没有行号，强制必填会逼模型编一个。方案一把 `line` 放在可选是对的。

**(c) 可复核性 — 方案一大胜，这是决定名次的一项**

这也是你提问里权重最高的一条。方案一：inline diff + 独立复核代理 + `tests_run` + `residual_risk` + 报告第一节就是"需人工复核"。方案二：一张"已自动修复"表格 + "变更文件汇总（便于 git diff 复核）"。后者等于把复核工作原样还给你。

**(d) 边界 — 方案一略胜**

两者都处理了 `agent()` 返回 null 不能静默吞。方案一多一层 verify 兜底，且区分了 `clean` 与 `error`，报告里把"未发现问题的模块"和"出错的模块"分开列。方案二的 `completed_with_errors` 是自报的，没有外部校验。

---

## 两份共同的漏洞

这几条都不是原则建议，是能直接补进脚本的：

**1. 报告 100% 自证，没有任何东西对着真实工作区核对。**
`files_changed` / `filesChanged` 是代理自己说改了什么。代理改了文件但没上报、或上报了没真改，两份设计都发现不了。跑完加一步纯代码校验：

```js
const actual = new Set(gitDiffNameOnly())          // 实际变更文件
const claimed = new Set(agg.allFilesChanged.map(x => x.file))
const unreported = [...actual].filter(f => !claimed.has(f))   // 幽灵改动 ← 最危险
const phantom  = [...claimed].filter(f => !actual.has(f))     // 报了没改
```
`unreported` 非空必须在报告顶部飘红。

**2. 失败模块可能已经改了一半仓库。**
代理在编辑到一半时挂掉 → `agent()` 返回 null → 两份报告都只写"该模块审查失败"。但文件已经被改了，而且没有任何 finding 记录。报告必须写成"以下模块未完成，**且可能残留半成品改动，请优先 `git diff` 这些路径**"。

**3. 40 个代理并发写同一个文件。**
公共 util、`config.js`、中间件注册处，多个模块的修复很可能落在同一个文件上，互相覆盖且谁都不知情。两份都没有冲突检测，也都没提 `isolation: 'worktree'`。最低成本的补法是聚合时算重叠：

```js
const byFile = {}
agg.allFilesChanged.forEach(({module, file}) => (byFile[file] ??= []).push(module))
const contested = Object.entries(byFile).filter(([, ms]) => ms.length > 1)
```
`contested` 单列一节，这些是最需要人看的改动。

**4. 没有构建/测试闸门。**
方案二完全没有；方案一的 `tests_run` 是个字符串且允许写 `"none"`——40 个代理大概率全写 none。报告可以说"修复 37 处"，但仓库编译不过。全部跑完后至少要有一次全局 `build + test`，结果写进报告首屏；这一项是布尔值，不该由代理自陈。

**5. 防漏扫的字段偏偏都是可选的。**
方案一的 `scanned_files`、方案二的 `filesReviewed` 都不在 `required` 里。模型在偷懒少扫的时候，正好也是最可能省略这个字段的时候。两个都应该提进 required。

**6. 跨模块没有归一化。**
同一个模式（比如同一处 SQL 拼接写法）出现在 12 个模块里，会变成 12 条独立 finding、12 个不同 severity。聚合时按 `category + summary` 相似度聚类，报告里合并成一条带 12 个位置，否则 critical 计数会被结构性膨胀。

**7. 体积没控。**
方案一把完整 unified diff 塞进 schema，40 个模块下报告可能爆到几万行，还占子代理输出 token。建议 diff 只留 hunk 头 + 关键几行，完整 diff 落盘或用 `git diff <file>` 指路。

---

## 怎么用

以方案一为骨架（schema 字段集 + verify stage + prompt 里写死修复口径），把方案二的四样东西并进去：`aggregate()` 完整实现、`${module}::` id 前缀、category 闭合枚举 + 独立 cwe 字段、`false_positive_noted` 状态。再补上面 1/2/3/4 四条硬校验。

需要我把合并后的完整 Workflow 脚本写出来吗？
