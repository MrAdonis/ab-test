# Agent-native 工具接口 DoD（B 组 / treatment，7 条契约）

你造一个会被 agent、CLI 或其他程序以编程方式调用的工具时，除通用 DoD 外，必须满足以下接口契约（缺一即未达 agent-native）：

1. **统一输出 schema**：所有命令/路径输出同一结构（如 `{success, data, error}`），不是有的命令 JSON、有的纯文本。JSON 默认开，人读格式才是可选 flag
2. **结构化错误**：失败返回 `{success:false, error}`，不 crash、不裸 stderr+退出码——调用方读字段判断成败，不靠解析字符串或猜退出码
3. **自带可跑测试**：覆盖正常/边界/错误三类路径，调用方能一条命令跑测试自证工具可用
4. **自带发现入口**：一份 SKILL.md / 完整 `--help` 自描述，明确告诉 agent 读哪个字段、never parse stdout as plain text、给调用 pattern
5. **幂等性**：agent 爱重试，同一条成功命令跑两次必须安全（no-op 或显式 "already done"），不产生重复副作用
6. **破坏性操作安全**：破坏性命令提供 `--dry-run`（预览将做什么不实际执行）+ `--yes/--force`（跳确认）；人类默认走安全确认，agent 可显式跳过
7. **分层 --help + Examples**：每个 subcommand 自带 `--help`，help 内必含可复制的真实调用例（Examples 比散文更利于 agent 模式匹配）；不一次性 dump 全手册——未用到的命令不进 context，增量发现

取舍：不要照搬重型多 phase 生成流程——流程仪式对小工具是过度设计。这些契约才是质量差距的真正来源。简单工具不必为满足契约硬套结构。
