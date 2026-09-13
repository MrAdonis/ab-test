# t82 瘦身判据（先定死，再执行，每处删减对应一条）

## 背景

两家官方同月给出同向结论：模型变强后，为弱模型堆的指令变成负担。
- OpenAI `Rethinking skills and prompts for GPT-6 Astra`（2026-09）：描述过长会被截断、互相矛盾；渐进式加载；别再催跑测试；边界语言过紧会让模型该继续时停住。
- Anthropic / Thariq（memory `reference_thariq_claude5_context_engineering`）：Claude 5 删 80% 系统提示词无损失。

单条 AB 结构上测不出总量效应（每条都是边际测试）。本轮测整体 vs 整体。

## 保留（不动，任何情况不删）

- **K1 安全闸**：hard-gates.md 全文 + CLAUDE.md NEVER/Security 段。安全/资金/密钥/不可逆操作，官方原文也明说该留。
- **K2 高 margin 已验证条款**（margin ≥2 分或 ≥20%）：
  - writing.md 材料边界 + 假细节禁令（40v19 / 41v24）
  - writing.md 事实密集标认知来源（9v6）
  - writing.md 判定类报证据类型（35.5v32.2，8/8 维度同向）
  - CLAUDE.md 默认散文抑制格式化（9v7）
  - coding-dod.md 反向验证（31v24，靶向 8v4）
  - coding-dod.md appsec 面对照（53v43.5）
  - coding.md 垂直切片排期（38v29，靶向 17v8）
  - coding.md 检索盲区（8.2v7.5，靶向 8v5）
  - coding.md 轨迹可审（7.5v6.5，靶向 9v5）
  - coding.md Assumptions 前置（8v7 但规则独有出口，clean 无替代）
  - agents/code-reviewer 发现归因（13v10.2）
- **K3 用户显式偏好**：中文回复、绝对路径铁律、认动词再动手、效果优先不省 token。

## 删除判据

- **D1 溯源元信息**（已执行，两臂共同起点）：AB 编号、margin 注释、日期标记、`未 AB` 声明。执行层零价值，已存 `references/ab-test-provenance.md`。
- **D2 margin ≤1 分或已实测平手的条款**：
  - coding.md 反馈分级四档·接收侧（t62 盲评 8/8 平手，零质量增量；输出侧已 t66 退役）
  - CLAUDE.md Orphan 清理边界（8v7，margin 1）
  - coding-dod.md 目标定义防御（8v7，台账自记「规则可归因约一半」）
- **D3 taxonomy / 罗列表**：大表格、清单式枚举，压成原则句 + 指针。对应官方「skill 描述过长互相矛盾」的同类病：表格越全，判断越被格子牵着走。
- **D4 单一源违反**：同一规则在 2+ 处出现的，留权威处删副本。
- **D5 弱模型脚手架**：step-by-step 微规则、"不准做 X" 的枚举式禁令、过紧边界语言。官方明说这类现在有害（Astra 会当真而停住；Claude 同理未测，本轮即测）。

## 不在本轮范围

- skill description 瘦身（39,005 chars，12 条 >600）——独立议题，等本轮结论再定。
- references/ 按需加载文件（不常驻，不占固定成本）。

## 判定

A = base（完整，D1 后 75,352 chars），B = slim。HELDOUT 三任务（写作/代码/判断）盲评。
- B 不输 → 瘦身无损失，按 slim 入配
- B 输且差距 > ±12% 噪声基线 → 规则在起作用，维持现状，本方向记负反馈
- 差距在噪声内 → 按「删完更好才删」的既定 bar，维持现状
