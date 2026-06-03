# t4 场景（A/B 共享，三档复杂度）

每个生成任务：在给定的 DoD 约束下，设计该 CLI 工具的接口（命令结构 + 关键 flag + 输出格式 + 错误处理；伪代码/接口签名级别即可，不必写完整实现）。产出控制在 ~150 行内。

## scenario1 — 复杂（破坏性 + 多 subcommand）
设计一个会被 agent 调用的 `deployctl` 部署工具：支持部署到 staging/production、列出历史部署、回滚到指定版本。其中部署和回滚是破坏性操作。

## scenario2 — 中等（给已有脚本套 agent-native 壳）
你有一个能跑的图片批处理脚本（resize/格式转换/加水印）。把它包装成一个 agent 能可靠调用的 CLI `imgkit`。

## scenario3 — 简单（单功能小工具）
做一个 `gitsum` 工具：读当前 git 仓库状态，输出本周提交数 + 改动文件数的摘要。单一功能，给 agent 调。
