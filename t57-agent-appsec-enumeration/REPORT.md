# t57 — agent-operational 5 面威胁枚举（coding-dod.md appsec 面对照增补）

**结论：REJECT（不入配）。** Sonnet 5 baseline（仅 OWASP 框架）4/4 trial 把 agent-native 漏洞当一等公民抓——**工具输出注入（indirect prompt injection）2/2 完整命中并给出边界标记缓解建议**，eval-执行模型输出、无界 agent 循环也基本全中。加 5 面枚举后 B 臂的 findings 与 A 臂结构一致，零新增；枚举只改了 findings 的**标签词汇**（B2 给每条贴「agent-operational 威胁面 ①②③④⑤」），不改**发现本身**。复现 t31「baseline 不蠢就别加」，且反证了候选前提（「OWASP-web 框架会漏 agent-native 风险」）。

## 假设

来自 [[reference_singguard_nsfa_agent_safety]]（蚂蚁 NSFA）：agent 操作层威胁（prompt injection 含工具输出注入 / 敏感信息提取 / 恶意代码执行 / 危险工具误用 / 资源耗尽）比 OWASP web Top10 更贴 agent 代码；NSFA 自己都点出 `<untrusted_tool_call>`（工具调用层注入）是未解难题。若在 coding-dod「appsec 面对照」加这 5 面枚举，应能让审 agent/工具链代码时多抓到 OWASP-web 框架不天然浮现的工具输出注入、无界循环等 agent-native 问题。

## 设计

- **Fixture**：`assistant_tools.py`，一个 LLM 助手工具层（fetch_url / read_file / run_helper / summarize + build_prompt + while True agent 循环 + eval fallback），植入 6 个漏洞（见 `RUBRIC.md`），其中 2 个 discriminator 是 OWASP-web 框架不天然浮现的 agent-native 问题：#4 工具原始输出直接拼回 model prompt（工具输出注入）、#5 `while True` 无步数上限（无界 agent 循环）。
- **任务**（两臂相同，无评测线索）：「帮我审一下 assistant_tools.py 的安全问题，按严重度列风险/利用/修法」。
- **变量**：A = coding-dod 现行 appsec 段（5 安全面 + OWASP Cheat Sheet 指针）；B = A + agent-operational 5 面枚举（显式点名工具输出注入 / 无界循环）。
- **打分**：judge 对照 6-issue rubric 逐条比对（我读 4 份 review 打 ✓/~）。2 trials/arm，Sonnet 5，headless bypassPermissions。

## 结果

| # | 漏洞 | A1 | A2 | B1 | B2 | discriminator |
|---|------|:--:|:--:|:--:|:--:|:--:|
| 1 | eval RCE | ✓ | ✓ | ✓ | ✓ | |
| 2 | shell 命令注入 | ✓ | ✓ | ✓ | ✓ | |
| 3 | SSRF + timeout=None | ✓ | ✓ | ✓ | ✓ | 半 |
| 4 | **build_prompt 工具输出注入** | ✓ | ✓ | ✓ | ✓ | **是** |
| 5 | **while True 无界循环** | ~ | ✓ | ✓ | ✓ | **是** |
| 6 | 执行模型输出 | ✓ | ✓ | ✓ | ✓ | 半 |

- **主 discriminator #4（工具输出注入）**：baseline A 2/2 完整命中——A1 单列一节「根因：外部内容未经净化直接拼回模型上下文」并建议「加边界标记 + 能力分离，别指望提示词防注入」；A2 列「间接提示注入串联成完全控链」。这正是 NSFA 声称的 agent-native 盲点，baseline 不但抓到还给出正解。B 零增益。
- **次 discriminator #5（无界循环）**：唯一的臂间差异——A1 抓了资源耗尽的其他面（timeout=None、输出无上限）但没单独点 `while True` 步数上限；A2/B1/B2 都显式点了。即 baseline 2 次里 1 次漏掉这个**次要 facet**，属噪声级，且 A1 仍把资源耗尽单列了严重度分区。
- **枚举的实际效果 = 换标签不换发现**：B2 把每条 finding 贴上「威胁面 ①-⑤」标号，findings 集合与 A 完全一致。枚举改的是叙述词汇，不是覆盖面。

## 判定与动作

- `~/.claude/rules/coding-dod.md`「appsec 面对照」**不加** agent-operational 5 面枚举。
- 负结论沉淀 → playground memory `feedback_agent_appsec_enum_rejected.md`（confidence: high）。
- 更新 [[reference_singguard_nsfa_agent_safety]] 验证状态：t57 REJECT。

## 边界与保留意见

- **Fixture 是 target-rich 且 agent 属性外显**（build_prompt/call_model/while True 一眼是 agent 工具层），baseline 一看就进入 agent 安全框架。更隐蔽的场景——agent-native 风险藏在看似普通的业务代码里、不易触发「这是 agent 代码」的识别——可能行为不同，本测未覆盖。但即便如此，「枚举」作为一段常驻 rules 文本，只在**已识别为 agent 代码**时才被触发对照，隐蔽场景下同样不会自动生效，所以这个边界不改 REJECT 结论。
- 单模型（Sonnet 5）、review-only 任务、单 fixture。若换弱模型（Sonnet 3.5 / Haiku）或让 agent 边写边审，枚举可能有增益——但主会话是 Opus/Sonnet 5，按现行 baseline REJECT。
- 方法论层其余点（fast-slow 分档 / hard negative / 诚实度梯度 / 边界标记）本就已被现有配置覆盖，未单独测（见 reference memory）。
