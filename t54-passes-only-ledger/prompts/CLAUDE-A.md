# shoplist

极简购物清单：纯 Node（node:http + node:test），无外部依赖。`npm start` 起服务（默认 3000），`npm test` 跑测试。

## 任务账本规范

- `task_plan.md` 里的 JSON 是任务账本：每个 feature 有 `id` / `description` / `acceptance` / `passes` / `wave` / `depends` / `notes`
- 完成一个 feature 后更新账本，让 `passes` 反映真实进度
- 执行中遇到的错误、坑、需要人跟进的事项记进 `notes`
