# Prompts

两组任务相同：审查 `fixture/payment-service.js`。唯一差异 = A 组用 general-purpose + 内联 code-reviewer 完整 system prompt（无 skill）；B 组用 code-reviewer agent（自带身份 + cross-review skill + 只读工具）。

## A 组（general-purpose, model=sonnet）
内联了 code-reviewer 的 system prompt（角色 / P0-P2 分级定义 / ≤1500token / P0→P1→P2 格式 / 每条带行号），任务为读取并审查 fixture 文件。

## B 组（code-reviewer agent）
只给任务：审查 fixture 文件，按你的标准格式返回。身份与 skill 由 agent 定义自带。

两组均未见 ground-truth.md。
