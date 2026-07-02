# 场景（3 × 2 变体 = 6 输出）

- **S1 / S2 = 安利 genre**（测规则是否有增益 + 跨领域泛化）
- **S3 = 非安利 genre**（测规则是否过触发 / 伤害——B 有跳过条件，理应不套 before-after）

## S1 — 安利 CLI-Anything（agent 工具，原始案例）

工具 = CLI-Anything（港大 HKUDS 开源）。核心：把任意 GUI 软件或 API 变成 AI agent 可调用的 CLI，兼容 Claude Code / OpenClaw；自动生成接口 / 测试 / 文档；操控真实软件并返回结构化 JSON。demo：AI 用 Blender / FreeCAD 协作设计火星车、自动剪出带字幕的视频。
任务：写一条安利推，让读者立刻明白它凭什么值得用。

## S2 — 安利 Bun（JS 运行时，跨领域泛化）

工具 = Bun（JavaScript 运行时 / 工具链）。核心：替代 Node.js + npm + webpack + jest 这一套，启动快、装包快（号称比 npm 快十几倍）、内置打包器 / 测试器 / 原生 TypeScript 支持，一个二进制搞定。
任务：写一条安利推，让读者立刻明白它凭什么值得用。

## S3 — 观点推（非安利，过触发边界测试）

任务：写一条观点推文，论点 = "让软件变成 agent-native（能被 AI agent 直接调用）是接下来两年的趋势"。这不是安利某个具体产品，是讲一个趋势判断，要有观点、有理由。
