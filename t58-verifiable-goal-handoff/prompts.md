# t58 · Verifiable Goal 交接编译器

## 假设
在「跨 session 交接/收工」场景，给 handoff 显式注入「可验证 Goal 编译器」模板（Goal / Current state / Completion criteria / Constraints + 验证附录：验证命令·证据位置·失败定义·回传格式），会让 Sonnet 5 产出的交接文档更自包含、更可验证，优于 baseline 自发交接。

来源：@servasyy_ai 转 tt-a1i 的 matt-skills-with-to-goal 流程（grill→spec→tickets→to-goal→fresh session）。原分享 verifiable-goal-weekly-share-public.pages.dev。

## 单一变量
A（control）= 现状：子代理继承全局配置（已含 /handoff 规则 + coding-dod DoD），纯任务 prompt。
B（treatment）= 现状 + Goal 编译器模板注入。
两组同一 Sonnet 底模、同一任务、同继承配置，唯一差异 = 模板注入。

## 共同任务（真实用户请求，无评测线索）
> 我在做一个 Express + Prisma 的待办 API。当前进度：用户注册/登录（JWT）已完成并通过测试；待办路由 /todos 已写了 GET 和 POST，PUT /todos/:id 和 DELETE /todos/:id 还没写；鉴权中间件 requireAuth 已经实现，但还没挂到 /todos 路由上（现在 todos 路由是公开的，这是个已知问题）；数据库 schema 已经定稿，不要改。我这个对话窗口快满了，帮我写一份交接文档，让我等下开一个全新的对话窗口能直接接着把剩下的部分做完。

## B 组追加指令
> 写交接时把它编译成一份可验证的交接契约，明确包含：(1) Goal 交付什么；(2) Current state 现在什么样、已完成什么、已知缺口；(3) Completion criteria 怎么算做完、逐项可判断 done/not done；(4) Constraints 不做什么、不能碰什么、能否提交；(5) 验证 用什么命令验证、证据看哪、什么算失败、结果按什么格式回报。目标是接手者不看任何聊天记录、光凭这份文档就能做完并自我复核。

## 评委（盲评，不知 A/B 标签）
扮演「全新无上下文的接手 agent」，只拿一份文档做完剩余工作。四维各 1-10：自包含性 / 可验证性 / 边界清晰度 / 可执行性。给逐维分 + 总评 + 胜者 + 一句话理由。A/B 随机映射为 DOC-1/DOC-2。
