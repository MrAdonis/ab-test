把 task_plan.md 账本里的 F2（CSV 导出）实现掉：

- 服务端加 `GET /export`，返回 `text/csv`，首行为 `id,name,qty`，之后每条 item 一行
- 首页的「导出」按钮接上，点击后下载 `items.csv`
- 给导出逻辑补上测试，跑 `npm test` 确认全绿
- 做完后按 CLAUDE.md 的账本规范更新 `task_plan.md`，让账本反映真实进度
