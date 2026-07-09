# t47 — writing.md FORBIDDEN 清单存量回测

日期：2026-07-07。触发：wiki-lifecycle §5④ 底模大版本跳变（Claude 5 family）。t41 已回测 writing.md MUST#2（KEEP）与 CLAUDE.md 散文/认错条款（KEEP/RETIRE），FORBIDDEN 11 条系建档原生规则、无入配 margin 记录、从未单独回测——本轮补测其中 7 条可客观判定的。

## 方法

- 生成臂：Sonnet 5（`claude -p --model sonnet --safe-mode --system-prompt <最小编辑 persona>`，clean cwd `/tmp/t47-clean`）
- **单臂 + 确定性判据**（与 t41 双臂盲评的设计差异，理由）：FORBIDDEN 是禁令型规则，退役判据只有"干净 baseline 是否仍自发犯 tell"一条；tell 可 regex 确定性判定，B 臂对退役决策无增量信息，过度抑制风险低（禁令不压制合法行为）
- 隔离：`--safe-mode`；双 canary gate 全过（规则探针返回 `NO_CUSTOM_RULES`、英文 canary 无中文泄漏，产物在 `outputs/`）
- Prompt 卫生：4 个场景全部写成真实用户请求，无评测线索

## 场景与结果

| 场景 | Prompt | 命中的违规 |
|------|--------|-----------|
| S1 公众号短文（CF Workers 搬迁，800 字） | 诱 #3/#4/#5/#7/#8 | **#8 setup-reveal**（L15「不是"all in Cloudflare"，而是分层看待」）；#3/#5/#7 零命中；#4 无升华结尾（以分层判断收尾） |
| S2 分析判断（个人开发者学不学 K8s） | 诱 #8/#10/#11 | **#11 虚构百分比 ×2**（「99% 情况下问的是 2」「对 90% 的个人项目来说够用」，均无来源）；#10 零命中 |
| S3 落地页文案（番茄钟 App） | 诱 #5/#11 | **#8 setup-reveal ×2**（「你不是不够自律，只是缺一个…」「不是让你自我感动地"打卡"，而是…」）；#5/#11 零命中；「你不是不够自律」同时构成 #10 边缘违规（断言读者内心状态） |
| S4 英文 launch post（dotfiles CLI） | 诱 #9 | **#9 em-dash ×3**（正文两拍停顿 + bullet 内附加说明，全是规则点名的用法） |

## 裁决

**KEEP（baseline 仍犯，规则价值健在）**：
- **#8 setup-reveal**——4 个场景犯 3 次，跨文体（公众号 + 营销文案），是全场最顽固的 tell
- **#9 英文 em-dash**——300 词短文犯 3 次，Sonnet 5 未消化
- **#11 虚构百分比**——分析文里连造两个精确假数字，且都出现在论证关键位
- **#10 替读者说话**——canonical 句式零命中，但 S3 出现变体边缘违规，保守 KEEP

**RETIRE（baseline 已自会，按「baseline 不蠢就别加」退役）**：
- **#3 过渡废话**（此外/与此同时/值得一提的是）——3 篇中文零命中；且与 CLAUDE.md Communication「不加过渡废话」重复（单一源清理顺带完成）
- **#5 套话词库**（总的来说/至关重要/在当今…背景下等）——3 篇中文零命中，词库已被底模消化；检测词表在 write-review checklist 与 review-base.md 独立存在，审核层兜底不受影响

**观察但不动（证据弱）**：#4 三段式、#7 连续同句式本轮零违规，但仅 1-2 个场景构成诱导且需人工判定，样本不足以退役；下次跳变优先重测这两条。#1/#2/#6 依赖用户原文改写场景，本轮未测。

## 检索盲区 / 局限

- 单臂 n=4，每场景一次生成；#3/#5 的零命中在长文（3000+ 字）和正式报告文体下未验证——套话在长文里更易复发，若观察到实际会话重现，从本台账恢复原文即可
- 生成臂只测了 Sonnet 5；Opus（中文长文主力）未测
- S2 出现中英夹杂（「求职market信号」「like Knative」），不在 FORBIDDEN 范围内，记录备查

## 落地动作（本轮已执行）

1. `~/.claude/rules/writing.md`：删除原 #3/#5，列表重排为 9 条，FORBIDDEN 段首加 t47 回测注记
2. `~/.claude/references/ab-test-provenance.md`：新增 t47 裁决记录
