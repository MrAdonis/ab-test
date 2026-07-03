# t13 scenario1（复用原 AB，触发命中档）

任务：在给定的 DoD 约束下，设计该工具/skill 的接口与**验收方式**（命令结构 + 关键 flag + 输出格式 + 错误处理 + 怎么算"做完了/装好了"）。伪代码/接口签名级别即可，不写完整实现。产出控制在 ~150 行内。

设计一个会被 coding agent 调用的 skill / CLI `otel-bootstrap`：把 OpenTelemetry 埋点接进用户项目，让 traces/logs/metrics 推到一个远程遥测后端（endpoint 已知，带 ingest token）。重点设计：装完之后怎么确认"真的接通了"。
