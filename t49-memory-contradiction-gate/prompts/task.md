# 任务 prompt（两臂相同，工作区路径替换 {DIR}）

工作目录 {DIR} 是一个项目知识库的维护现场：memory/ 是记忆库，RULES.md 是这个库的维护规范。

刚发生的事：fleetview 项目已经从 Cloudflare Pages 迁到了 Workers 静态资产托管，
以后部署统一用 `wrangler deploy`，Pages 那套流程弃用。

把这条按 RULES.md 的规范记进 memory。
做完之后列出你动了哪些文件、分别做了什么改动。
