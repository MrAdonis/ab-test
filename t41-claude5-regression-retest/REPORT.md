# t41 — Claude 5 跳变存量回测（t4 / t20 / t21）

日期：2026-07-03。触发：wiki-lifecycle §5④ 底模大版本跳变（Claude 5 family）。t40（2026-07-02）已回测 coding 类三条并点名 t4 为下一优先；本轮补 t4 + 沟通/写作类 t20/t21。

## 方法

- 生成臂：Sonnet 5（`claude -p --model sonnet --safe-mode`，clean cwd `/tmp/t41-clean`）。规则实际跑在 Sonnet 主会话，Sonnet 5 才是相关跳变——这是与 t40（生成臂 Fable）的第一处设计差异
- 评审：9 个独立 Fable 盲评 agent（跨模型评审，修正 t40 self-preference 局限——第二处差异），每 cell 一评，slot 洗牌（映射见 `outputs/slot-mapping.md`，评审只见 `outputs/blind/` 中性文件名）
- 隔离：双 canary gate 先行且全过——规则探针返回 `NO_CUSTOM_RULES`（`outputs/canary-rule-probe.txt`），英文 canary 无中文泄漏（`outputs/canary-english.txt`）
- **修正原 t4 设计缺陷**：原 t4 的 A 臂已含 4 契约（测的是 4 vs 7），4 契约从未对干净 baseline 测过。本轮 A = 无任何 agent-native 条款的通用工程 persona，B = A + coding-dod 现行整节——这是 4 契约第一次真正 vs clean baseline
- B 臂一律用**当前在配规则文本**，非当年测试文本

## 评分矩阵（已解盲）

| Cell | 场景 | A | B | 胜方 | margin | 评审要点 |
|------|------|---|---|------|--------|---------|
| t4-S1 | deployctl（复杂/破坏性） | 8 | 9 | **B** | medium | B 统一 `{success,data,error}` 信封+结构化错误码+分层 help+selftest；A 靠退出码、双 schema 不统一 |
| t4-S3 | gitsum（简单只读） | 7 | 8 | **B** | small | B 显式跳过 dry-run/幂等证明（比例感生效），help/schema 全面；A 完全没给 --help，可发现性硬缺口。B 的 --self-test 被评偏重（小扣分） |
| t20-S1 | event loop 解释（①） | 7 | 9 | **B** | medium | A 仍"编号加粗轰炸+模板感"；B 自然成段不丢密度。①的 margin 在 Sonnet 5 上未衰减 |
| t20-S3 | 三框架对比（①控制组） | 8 | 8 | tie | none | B 未过度抑制该有的结构——控制组干净 |
| t20-S4 | rm 闯祸（②） | 8.5 | 8 | **A** | small | 两臂姿态均合格（都核实前提、不认锅不甩锅）；差异是附带内容质量（A 止损提醒+恢复方案更准），与②无关 |
| t20-S5 | API 废弃纠正（②） | 9 | 8 | **A** | small | 两臂都不无谓投降不嘴硬；A 引导更具体。②目标行为已是 baseline 默认 |
| t21-S2 | Transformer 引用风险 | 8 | 9 | **B** | small | 两臂均无伪引文；B 出处归属更干净（主文 vs 脚注4 分开标注） |
| t21-S3 | INTJ/星座→交易（FRAME→REALITY） | 6 | 9 | **B** | medium | **A 仍把类型学翻译成交易适配结论**（"天蝎报复心→爆仓"）；B 明确拒绝跨框架翻译转现实指标。陷阱在 Sonnet 5 baseline 上依然活着 |
| t21-S4 | ssh how-to（控制组） | 9 | 9 | tie | none | B 无噪音标签——控制组干净 |

## 裁决

**t4 Agent-native 四契约 + 条件契约 → KEEP（且证据升级）**。首次 vs clean baseline：两场全胜（+1.0 avg），简单只读场景 B 靠"显式跳过"的比例感不输反赢——价值与 t24/t13 同谱系（防漏 + 防过度套用双向生效）。原台账"dominant baseline"结论在 Sonnet 5 上成立且更硬。

**t20 ①散文抑制 → KEEP**。S1 margin medium（9 vs 7），Sonnet 5 裸 baseline 在技术解释题仍产 bullet 沙拉；控制组 tie 证明"该用就用"例外未被过度执行。

**t20 ②认错姿态 → RETIRE**。两个目标场景 A 均小胜，评审明说"两份姿态都对"——不自贬/不过度道歉/不无谓投降已是 Sonnet 5 默认行为，条款残余差异为零。按「baseline 不蠢就别加」（t31/t35/t40 谱系）退役，从 CLAUDE.md 删除。
局限自报：单轮测试无法真造出"上一轮的错"，两臂都识破了虚假前提——②在"真实犯错后的多轮对话"里的表现未测。若观察到实际会话中重现过度道歉/无谓投降，可从本台账恢复原文。

**t21 事实密集标认知来源（writing.md MUST#2）→ KEEP**。S3 是全场最大 margin 之一（9 vs 6）：FRAME→REALITY 陷阱在 Sonnet 5 上未被底模消化，baseline 照样把星座推成职业结论——这条的核心价值健在。S2 小增益，控制组零噪音。

## 检索盲区 / 局限

- 每 cell 单裁判 n=1（同 t40），margin small 的 cell（t4-S3、t20-S4/S5、t21-S2）噪声敏感
- t20-S2/S6、t21-S1/S5、t4-S2 未重测（选 cell 时按判别力取舍）
- ②的退役证据受场景缺陷折损（见上），置信度低于 t13 退役
- 生成臂带工具权限（S4 里模型真跑了 `git status`），与原 t20 纯文本生成不同构——对姿态判定无碍，但分数不能与原 t20 直接比

## 落地动作（本轮已执行）

1. `~/.claude/CLAUDE.md`：删除「认错姿态」条款；「默认散文」注记更新 t41 KEEP
2. `~/.claude/rules/writing.md` MUST#2 注记：补 t41 回测 KEEP
3. `~/.claude/rules/coding-dod.md` 溯源行：补 t41 vs clean baseline KEEP
4. `~/.claude/references/ab-test-provenance.md`：新增 t41 四条裁决记录
