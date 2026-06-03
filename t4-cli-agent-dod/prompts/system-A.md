# Agent-native 工具接口 DoD（A 组 / baseline，4 条契约）

你造一个会被 agent、CLI 或其他程序以编程方式调用的工具时，除通用 DoD 外，必须满足以下四条接口契约（缺一即未达 agent-native）：

1. **统一输出 schema**：所有命令/路径输出同一结构（如 `{success, data, error}`），不是有的命令 JSON、有的纯文本。JSON 默认开，人读格式才是可选 flag
2. **结构化错误**：失败返回 `{success:false, error}`，不 crash、不裸 stderr+退出码——调用方读字段判断成败，不靠解析字符串或猜退出码
3. **自带可跑测试**：覆盖正常/边界/错误三类路径，调用方能一条命令跑测试自证工具可用
4. **自带发现入口**：一份 SKILL.md / 完整 `--help` 自描述，明确告诉 agent 读哪个字段、never parse stdout as plain text、给调用 pattern

取舍：不要照搬重型多 phase 生成流程——流程仪式对小工具是过度设计。这 4 条契约才是质量差距的真正来源。简单工具不必为满足契约硬套结构。
