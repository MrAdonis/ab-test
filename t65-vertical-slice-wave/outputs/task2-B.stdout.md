已在 `task_plan.md` 中写好完整规划，核心设计思路：

**针对你最担心的"图表拼图对不上"问题**：Wave1 第一件事就是用 mock 数据把首页折线图 + Top10 表格在浏览器里跑出来（F1），视觉参数（颜色 `#2a78d6`、面积透明度10%、圆角12px、tooltip、表格行高等）全部按 dataviz skill 校验过的规格写死在 plan 里，不留给编码 agent自由发挥。**F1 完成后设了一个人工 gate：必须拿到你对首页视觉的明确确认，才允许进入 Wave2**——避免两周后端管道搭完才第一次看到图长什么样。

**Wave 划分（垂直闭环，非水平分层）**：
- Wave1：首页可视化原型（mock，浏览器可见）+ CLI push 真实入库（sqlite3 可查）—— 两条并行的端到端闭环
- Wave2：首页换真实数据源 + 异常详情页
- Wave3：服务名/日期筛选接入
- Wave4：5台机器部署容错（断网重试队列）+ 幂等去重（防止重复 push 导致 count 翻倍）

**提前锁死的关键决策**（notes 字段里写明，避免后期返工）：
- API JSON 契约（POST /api/scan-results、GET /api/summary、GET /api/anomalies/{id}）一次定死，CLI 和后端两边对齐
- DB schema 从 F2 起就带 `(server_id, scanned_at)` 唯一约束和日志片段截断（4000字符），避免 Wave4 才发现需要破坏性迁移
- 明确排除项：不做深色模式、不做多服务对比折线、不做首页KPI大数字——防止执行时擅自加范围外的功能

7 个 features，每个都有 acceptance / must_haves（含 artifacts 和 key_links）。可以交给编码 agent 按 wave 顺序执行了。
