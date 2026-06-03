# t4 — CLI-for-Agent DoD 扩充 AB test

**来源**：Cursor 开源 `cursor/plugins` 的 `cli-for-agent` skill，对照 `~/.claude/rules/coding-dod.md` 的「Agent-native 工具接口 DoD」（现有 4 条契约）找缺口。

**测试问题**：把 Cursor 多出的 3 条（幂等性 / dry-run+force / 分层 help 带 Examples）无条件加进 4 条契约（→7 条），是否提升 agent-native 工具设计质量，还是引入过度设计堆料？

**方法**：3 档复杂度场景（复杂 deployctl / 中等 imgkit / 简单 gitsum）× A(4条)/B(7条) 盲测，6 份产出由独立 Sonnet 评分员四维打分（接口质量 / 契约覆盖 / 过度设计惩罚 / 净实用价值）。生成与评分全 Sonnet。

## 汇总

| 场景 | A | B | 胜者 |
|------|---|---|------|
| scenario1 复杂（破坏性部署） | 33 | 36 | B +3 |
| scenario2 中等（图片壳） | 33 | 32 | A +1 |
| scenario3 简单（git 只读摘要） | 36 | 33 | A +3 |
| **总计** | **102** | **101** | **A 微胜** |

## 逐契约裁定

| 契约 | 复杂 | 中等 | 简单 | 裁定 |
|------|------|------|------|------|
| 幂等性 | 真实需求 | batch 有价值 | 废话填坑（只读天然幂等） | **有条件加** |
| dry-run/force | 核心安全门 | 合理但被强制化 | 只读无需 | **有条件加** |
| 分层 help + Examples | 有价值 | 有价值 | 轻微提升 | **可无条件并入契约4** |

## 结论

**原始方案（无条件 4→7）= REJECTED。** 根因：system-B 准则缺触发条件，"简单工具不必硬套"这句 disclaimer 和"强制 7 条"框架自我矛盾——model 读到 disclaimer 但无可操作触发门，只能机械套，于是 gitsum 这类只读小工具被迫写"契约5 幂等性：只读操作天然幂等"这种纯 noise，稀释文档信息密度。

**派生改良方案（落地）= DOMINANT A：** 4 通用契约 + 1 条并入 + 2 条件契约。
- 契约4 增强：`--help` 必含可复制 Examples，多 subcommand 分层、不 dump 全手册（零过度设计风险，全场景 ≥ A）
- 新增**条件契约**（满足触发才加）：
  - 幂等性 — 触发：有写副作用且 agent 可能重试
  - 破坏性安全（dry-run + force）— 触发：不可逆操作（删除/覆盖/部署/发布）；**只读工具明确跳过**

改良版在已测 6 份产出上 dominant baseline：复杂场景命中触发=B 行为（>A），简单场景不命中=A 行为（=A，不再 -3）。三场景均 ≥ A，至少一场景 > A。

**核心发现**：只读工具不需要幂等条款——不是"可以不写"，是"写了就是 noise"。好准则的判断逻辑应可执行（"有无写副作用？"），不是免责 disclaimer。这与 coding-dod 自身的 CLI-Anything 教训（"别照搬重型流程，4 条契约才是质量来源"）同源——靠触发门控膨胀，不靠堆契约。

**产出留痕**：`prompts/`（system-A/B + scenarios）、`outputs/`（6 份设计）。
