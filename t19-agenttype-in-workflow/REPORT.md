# t19 — Workflow 里要不要定制 agentType

**日期**：2026-06-14
**起因**：@yaohui12138 推文鼓吹「Subagent 身份提示词 + 动态工作流」。验证我们的 workflow 里用 `agentType` 接预定义 agent 有没有质量增量。
**评分**：对照 ground truth（13 植入 bug）人工评，n=1。

## 关键设计：隔离真正的变量

`agentType` 接进来带四样东西，只有两样裸 `agent(prompt)` 复刻不了：

| 带什么 | 裸 prompt 能复刻 | 是否本测变量 |
|---|---|---|
| system prompt（角色+分级+格式） | ✅ | 否（A 组已内联） |
| `skills:` 预加载（cross-review） | ❌ | **是（唯一变量）** |
| `tools:` 白名单（只读硬约束） | ❌ | 否（review 是只读任务，不影响输出质量） |
| `model:` 绑定 | ❌ | 否（两组都 sonnet） |

A 组 = general-purpose + 内联 code-reviewer 完整 system prompt（无 skill）
B 组 = code-reviewer agent（自带身份 + cross-review skill + 只读工具）
→ **唯一差异 = cross-review skill 预加载**

不跑 workflow：agentType 的差异在「单个 agent 带什么」，workflow 只是批量调同一 agent。测单 agent 即可，省 token、隔离干净。

## 结果

| | A（无 skill） | B（带 cross-review skill） |
|---|---|---|
| P0 | 6/6 | 5/6（漏 checkout UPDATE 注入） |
| P1 | 4.5/5 | 4/5（漏 checkout 余额竞态） |
| P2 | 2/2 | 2/2 |
| 核心命中 | **12.5/13** | 11/13 |
| 误报 | 0 | 0 |
| bonus | 2 | 4 |
| token 纪律 | 守住 ≤1500 | 超出 |

## 结论

**cross-review skill 预加载在单文件 review 没有可观测的质量增量，A 组覆盖率反而略高。** 推文的「身份提示词是被忽略的秘诀」卖点不成立——身份（system prompt）裸 prompt 能完全复刻，真正不可复刻的 skill 预加载没帮上覆盖率。

可能机制：cross-review skill 设计为「跨模型交叉验证」（调外部 codex），在 sonnet 子代理内部它没真正执行外部协作，只作为方法论文档占 context，反而稀释了对基础 bug 的注意力。B 组的「深度」（bonus 多、给修复码）更像是 code-reviewer system prompt 更细致所致，与 skill 无关。

### 对「要不要定制 agentType」的回答

| 动机 | 判断 |
|---|---|
| 为「质量/身份」定制 | ❌ 不值得。裸 prompt 内联角色一样甚至更好。直接反驳推文。 |
| 为「工具白名单约束」用现成 agentType | ✅ 值得。workflow 里 agent 有写权限风险时（批量改文件），接 code-reviewer/researcher 这种只读 agent 是免费安全保险。这是不靠打分就成立的工程价值。 |
| 为「省 prompt 重复」用现成 agentType | ✅ 值得。同角色跨多 workflow 复用时省重写。 |
| 新建定制 agent（如推文的 api-security-auditor） | ❌ 不值得。除非某角色跨多 workflow 高频复用（第二消费方判据，coding.md）。造了不用 = 堆料。 |

### 不改配置

无规则/agent 变更。现有「子代理选择」（skill-chains.md）的 4 个预定义 agent 够用；workflow 脚本里按需用 `agentType` 接只读 agent 当安全约束即可，无需新建或系统性强制。符合「无提升则回滚」。

## 局限

n=1，单次运行 noise 大，12.5 vs 11 的差距不足以下「A 一定更好」的强结论。但方向清楚：**skill 预加载没带来覆盖率优势**，这一点足以否决推文「定制身份 agent 提升质量」的主张。
