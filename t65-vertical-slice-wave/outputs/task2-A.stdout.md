已写入 `task_plan.md`，10 个 feature、5 个 wave。关键设计：

**防"两周后对不上"的关卡设计**（针对你最担心的点）：
- Wave 1 只做一件事：F1 探查现有 CLI 真实输出，产出 `CONTRACT.md` 作为字段唯一真源，不许凭空猜。
- Wave 2 里 F2/F3 是**纯前端静态原型**（真实样例数据、假路由），完全不碰后端——本地跑起来就能让你和团队实际看一眼折线图、Top10 列表、详情页长什么样，确认过了才解锁 wave 3。
- Wave 3 才开始写后端 API，此时前端形状已经锁定，接口设计不会跟着图表返工。
- Wave 4 把 fixture 换成真实接口 + 筛选器 + CLI 推送，wave 5 是 5 台服务器真实联调。

**已提前写进 notes 的坑**：异常去重需要 `(service+pattern_hash)` 唯一键 UPSERT（否则 count/first_seen/last_seen 语义全错、Top10 被刷屏）、"今日"边界要按可配置时区算（5 台服务器场景）、推送接口要有 `X-API-Key` 简单鉴权、CLI 推送失败不能拖累主流程。

图表规格（颜色 `#2a78d6`/`#3987e5`、2px 线宽、8px 端点、tooltip 交互等）已经按 dataviz skill 的验证规范量化写进 F2 的 acceptance，编码 agent 不需要自己拍脑袋配色。
