# t58 · Verifiable Goal 交接编译器 — REPORT

**日期**：2026-07-15
**来源**：@servasyy_ai 转 tt-a1i 的 `matt-skills-with-to-goal` 流程（grill→spec→tickets→to-goal→fresh session），原分享 verifiable-goal-weekly-share-public.pages.dev
**假设**：在「跨 session 交接/收工」场景，给 handoff 显式注入「可验证 Goal 编译器」模板（Goal / Current state / Completion criteria / Constraints + 验证附录：验证命令·证据位置·失败定义·回传格式），会让 Sonnet 5 产出的交接文档更自包含、更可验证，优于 baseline 自发交接。

## 设计
- 单一变量：A = 现状（子代理继承全局配置，已含 /handoff 规则 + coding-dod DoD），纯任务 prompt；B = 现状 + Goal 编译器模板注入。
- 底模：两组均 Sonnet 5 子代理，同任务同继承配置。
- 任务：真实交接请求（Express+Prisma 待办 API 做一半，PUT/DELETE 未写、requireAuth 未挂载=已知安全缺口、schema 定稿不改），无评测线索。
- 盲评：两份产出随机映射 DOC-1（=B）/DOC-2（=A），评委不知标签。跑两个独立评委：① 标准四维评委；② 对抗怀疑派评委（默认「越短越好、baseline 够用就别加」，复现 t31 逻辑）。

## 结果

### 评委① 四维打分（1-10）
| 维度 | B(treatment) | A(baseline) |
|---|---|---|
| 自包含性 | 9 | 7 |
| 可验证性 | 10 | 5 |
| 边界清晰度 | 10 | 6 |
| 可执行性 | 8 | 9 |
| **总分** | **37** | **27** |

胜者 B，margin 10 分（相对 +37%）。可执行性上 baseline 反而略高（步骤更直白好照做）。

### 评委② 对抗怀疑派
默认立场偏向短文档，仍选 B。关键辨析：模板价值**不普适**——当接手者是「会走捷径、会删测试凑过、会猜测未知信息」的 LLM agent 时，B 多出的三件（curl 验证命令 / 古德哈特禁令「测试数量不能变少」/ 强制逐项 done-not-done 举证）精确对应三种真实失败模式，是对抗性防御不是仪式。**若接手者是自律的人类工程师，这些是冗余。** 可砍的仪式：commit 拆 fix+feat、不跳 hooks。

## 判定：KEEP（方向），但须收窄触发

**与之前那串 rejected（t49/t51/t53/t54/t57）不同**：那些是 baseline 自发覆盖了规则。本次 baseline **没有**自发覆盖——A 缺了可跑验证命令、逐项验收表、古德哈特防御、回报格式、「未验证需自行确认」栏。说明现有配置里 coding-dod 的 DoD 精神在「写交接文档」场景没被自动调用（handoff skill 未要求交接产物长这样）。gap 真实。

**核心边界（对抗评委给出）**：价值条件 = **交接对象是另一个 LLM/agent 或无人值守续接**。人类同行接手时套用会啰嗦回归。故规则必须收窄触发，不是无条件让 handoff 都编译成可验证 Goal。

## 入配前待办（按 CLAUDE.md「Verification」+ wiki-lifecycle §④）
1. 跑 HELDOUT.md 三任务（held-in 交接类 + held-out 其他类型），确认 held-out 不因新规则回归（尤其人类/简单交接场景不被啰嗦化）。
2. 若过闸，给 handoff skill 加**一条收窄规则**（非整包搬 tt-a1i 流程）：交接对象是 agent/无人值守续接时，编译成可验证 Goal（Goal/Current state/Completion criteria/Constraints + 验证附录）；人类接手保持精简。
3. 走 §① 少而准：这条是把 coding-dod 的 DoD 接到 handoff 产出规范，检查不与现有 handoff/coding-dod 重复堆料——它补的是「产出结构」不是「新增判断」。

## 入配检查（2026-07-15，已完成）

**held-out 回归**（真正该跑的不是 HELDOUT.md 三通用任务，而是这条收窄规则最易回归的场景——带规则草案喂两个 case）：
- HO-A 琐碎 CSS 微调 + 人类续接 → 保持基础结构 4 行，未触发 Goal 编译器 ✓
- HO-B 中等改动（上传接口加大小校验）+ 未说接手者 → 判为「人类同行+单点小修」保持基础结构 ✓

两个 held-out 均无回归。触发判断稳、且偏保守（默认精简，只有明确 agent/无人值守才触发）——方向正确：handoff 绝大多数人在用，undertrigger 代价 << 把所有交接啰嗦化。

**堆料核对（§① 少而准）**：读 handoff SKILL.md 现有结构（本次完成/当前状态/关键决策/下一步/已知问题/Live 引用），确认缺 Completion criteria（验收闸）、Constraints（禁区）、验证协议，且不区分接手者。gap 属实、不与现有段重复。

**落地**：`~/.claude/skills/handoff/SKILL.md` 加「## Agent 接手 / 无人值守续接（条件追加）」段——净增一个条件触发段 + 指针引 `coding-dod.md`（古德哈特/DoD 不复制，单一源）。未搬 B 组 180 行模板。收窄触发写明「人类/琐碎不套用」。

**margin**：评委① 37 vs 27（+37%），评委② 对抗视角守住。KEEP 入配。

## 产物
- `prompts.md` — 假设/设计/任务/评委 prompt
- `output-A-baseline.md` — 组A 产出（45 行）
- `output-B-treatment.md` — 组B 产出（180 行）
