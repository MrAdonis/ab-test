# t47 — writing.md FORBIDDEN 清单存量回测

触发：wiki-lifecycle §5④ 存量回测——底模大版本跳变（Claude 5 family）。t41 已回测 writing.md MUST#2（KEEP）与 CLAUDE.md 散文条款（KEEP），FORBIDDEN 11 条从未单独回测（多为建档时原生规则，无入配 margin 记录）。本轮测其中可客观判定的 7 条。

## 方法（沿用 t41 隔离，设计差异：单臂 + 确定性判据）

- 生成臂：Sonnet 5（`claude -p --model sonnet --safe-mode --system-prompt <base persona>`，clean cwd `/tmp/t47-clean`）——写作规则主要运行在 Sonnet/Opus 主会话
- **单臂设计**（与 t41 双臂盲评不同，理由记录在案）：FORBIDDEN 是禁令型规则，退役判据只有一条——干净 baseline 是否仍自发犯这些 tell。A 臂（无 FORBIDDEN 的最小编辑 persona）犯 → KEEP；不犯 → 退役候选。禁令的"过度抑制"风险低（不压制合法行为），且 tell 可 regex 确定性判定，无需盲评，B 臂对退役决策无增量信息
- 隔离：`--safe-mode` 跳过 CLAUDE.md/rules/skills/hooks；生成前双 canary gate（规则引用探针 + 英文 canary）必过
- Prompt 卫生：场景写成真实用户请求，无 t 编号/评测字样

## 被测条款 → 场景映射

| 场景 | Prompt 概要 | 埋的判据（FORBIDDEN 条款号） |
|------|-------------|------------------------------|
| S1 公众号短文 | 独立开发者服务器搬 Cloudflare Workers，800 字 | #3 过渡废话、#4 三段式升华结尾、#5 套话词库、#7 连续同句式、#8 setup-reveal |
| S2 分析判断 | 2026 年个人开发者还要不要学 K8s，要明确结论 | #8 setup-reveal、#10 替读者说话、#11 虚构百分比 |
| S3 营销文案 | 番茄钟 App 落地页文案（专注模式+周报） | #5 套话、#11 虚构百分比（"90% 用户…"类） |
| S4 英文 blog | dotfiles 同步 CLI 的英文 launch post | #9 em-dash/en-dash |

## 判定

- regex 确定性判据：#3/#5（词库 grep）、#8（`不是.{0,30}[，,]\s*而是` 等三条自查 regex）、#9（`[—–]`）、#10（替读者句式 grep）、#11（无来源百分比 grep+人工核）
- 人工判据：#4 三段式（开头铺垫+并列+升华收尾）、#7 连续 3+ 同句式
- 未测（不可单轮客观判定）：#1 不加观点、#2 不美化语气（依赖用户原文改写场景）、#6 不均匀分配
- 任一条款在对应场景零违规 → 该条退役候选（按 §3 supersession 流程走，人工拍板）；违规 → KEEP
