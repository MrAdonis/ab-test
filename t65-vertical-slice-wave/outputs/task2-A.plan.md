# logsift Web 仪表盘 — 开发计划

## 技术栈（已定，不再讨论）
- 后端：FastAPI + SQLite（同步 sqlite3 或 SQLAlchemy，二选一由 F4 落地时定，落地后写入 CONTRACT.md）
- 前端：Vite + React + Recharts
- CLI：现有 logsift 加 `--push` 参数，POST 到后端

## 防"两周后对不上"的核心机制

用户明确担心：做两周、前后端拼起来发现图表/交互跟大家想要的不是一回事。这份计划用**结构性关卡**而非"最后一起测"来防这件事：

1. **Wave 1（F1）先探查现有 CLI 真实输出**，不臆造字段。CLI 已经跑了半年，"异常"到底怎么聚合、字段是什么，必须从代码/真实输出里抠出来，写成 `CONTRACT.md` 作为后续所有字段的唯一真源。
2. **Wave 2 用真实样例数据做纯前端静态原型**（F2 首页、F3 详情页），完全不碰后端，本地跑起来给用户/团队实际看一眼、点一点。这一步不通过，**不允许进入 wave 3**。
3. **Wave 3 才开始写后端真实 API**，且直接对齐已经被确认过的前端原型形状，不会出现"接口设计到一半发现图表方向错了"返工。
4. Wave 4 把原型的 fixture 换成真实接口，wave 5 做 5 台服务器的真实联调。

**执行前置要求**：接手的编码 agent 在做 F1 时必须先定位并阅读现有 logsift 仓库里真正产出"异常摘要"的代码，`CONTRACT.md` 里的字段名以那次探查结果为准；本文档里出现的字段名（`service`/`pattern_hash`/`first_seen` 等）是合理默认猜测，探查后如有出入，以 F1 产出的 `CONTRACT.md` 为准并同步更新下游 feature 的 must_haves 字段引用。

**关键坑点（已知，前置写死，不留到实现时才发现）**：
- **去重语义**：同一异常每天扫描都会再次出现，必须靠 `(service + pattern_hash)` 唯一键做 UPSERT（count+1、更新 last_seen、first_seen 不变），不能每次 INSERT 新行——否则"出现次数""首末次时间"全错，Top10 也会被同一异常的历史行刷屏。
- **"今日"边界**：5 台服务器可能不同时区/夜间扫描，"今日 Top10"的日期边界要用可配置时区计算，不能硬编码 UTC 零点。
- **推送接口鉴权**：POST /api/scans 是 5 台服务器打过来的内网接口，仍需最基本的共享 Token 校验（header `X-API-Key`），防止误用/脏数据，不需要做成 OAuth。
- **CLI 推送不能拖累主流程**：`--push` 失败（网络不通、后端挂了）绝不能让团队每天依赖的扫描主流程报错或明显变慢，需要短超时 + try/except，失败只打印一行 warning。

---

```json
{"features": [
  {"id": "F1", "description": "探查现有 logsift CLI 源码与真实终端输出，与用户/团队确认'异常'的字段定义和首页真正想看到的信息，产出统一数据契约文档 CONTRACT.md，作为后续 DB/API/前端所有字段的唯一真源",
   "passes": false,
   "acceptance": "CONTRACT.md 存在且包含：(1) AnomalyRecord JSON Schema，字段至少含 service, hostname, pattern_hash(指纹/去重键), message_pattern, sample_log_lines(数组), severity, count, first_seen(ISO8601), last_seen(ISO8601); (2) ScanPushPayload JSON Schema（scan_id, service, hostname, started_at, finished_at, anomalies[]); (3) 至少 3 条从真实 CLI 输出提取的样例记录; (4) 一段对'首页最关心什么'的确认摘要（例如：哪个服务最吵、趋势方向、能否一眼看到新出现的异常）",
   "wave": 1, "depends": [],
   "must_haves": {
     "artifacts": [{"path": "CONTRACT.md", "min_lines": 40, "contains": ["AnomalyRecord", "ScanPushPayload", "first_seen", "last_seen", "pattern_hash"]}],
     "key_links": []
   },
   "notes": "必须先读 logsift 现有源码里真正产出异常摘要的那个函数/module，不能凭空猜字段——这里猜错，后面 DB/API/图表全部要返工，是用户最担心的'拼起来对不上'的最大源头。同时要确认清楚现有终端输出的聚合粒度：单条日志 vs 同类日志归并成一条，这决定 count/first_seen/last_seen 的真实含义。"},

  {"id": "F2", "description": "用 F1 产出的真实样例数据做成前端 fixture，纯前端（Vite+React+Recharts）搭出首页静态原型：近7天异常趋势折线图 + 今日Top10列表，不接任何真实后端，供用户/团队确认视觉和交互方向",
   "passes": false,
   "acceptance": "本地 npm run dev 可打开完整首页，数据来自 fixture 非 API。折线图：近7天每日异常总数单折线，颜色 light #2a78d6 / dark #3987e5，线宽2px round join，端点圆点直径≥8px 且带2px surface环，hover 显示十字线+tooltip(日期+当日数量)，Y轴取整千/百刻度，X轴恰好7个刻度对应7天日期，单折线不需要图例框。Top10列表：10行，每行= 异常摘要文本(超60字符省略号截断) + 服务名徽标 + 出现次数(tabular-nums右对齐) + 首次/最后出现相对时间，行高48px，行间1px hairline #e1e0d9 分隔，hover背景 rgba(11,11,11,0.04)，整行可点击跳转 /anomaly/:id。**用户对着本地跑起来的页面明确确认'就是这个方向'后，本feature才能标记passes=true，且是wave3开工的前置条件**",
   "wave": 2, "depends": ["F1"],
   "must_haves": {
     "artifacts": [
       {"path": "frontend/src/fixtures/anomalies.sample.json", "min_lines": 20, "contains": ["service", "first_seen", "last_seen", "count"]},
       {"path": "frontend/src/components/TrendChart.tsx", "min_lines": 30, "exports": ["TrendChart"], "contains": ["recharts", "#2a78d6"]},
       {"path": "frontend/src/components/TopAnomalyList.tsx", "min_lines": 20, "exports": ["TopAnomalyList"]},
       {"path": "frontend/src/pages/Dashboard.tsx", "min_lines": 20, "exports": ["Dashboard"]}
     ],
     "key_links": [{"pattern": "anomalies.sample.json", "in": "frontend/src/pages/Dashboard.tsx"}]
   },
   "notes": "这是防'返工两周'的第一道关卡：做完必须让用户实际看一眼本地页面（截图或直接跑），确认通过才解锁wave3。fixture字段名必须与CONTRACT.md完全一致，否则接真实API时要改两遍。"},

  {"id": "F3", "description": "用 F1 的真实样例数据搭详情页静态原型：原始日志片段、出现次数、首次/最后出现时间，供确认",
   "passes": false,
   "acceptance": "路由 /anomaly/:id 可打开，展示：原始日志片段（等宽字体代码块，背景比页面深一级，padding 16px，圆角8px，超过10行可滚动）；出现次数（大号数字，proportional figures非tabular）；首次出现时间/最后出现时间（并排展示，本地时区，含具体日期时间）；所属服务名徽标；返回首页链接。用户确认样式后才计入wave2完成",
   "wave": 2, "depends": ["F1"],
   "must_haves": {
     "artifacts": [{"path": "frontend/src/pages/AnomalyDetail.tsx", "min_lines": 25, "exports": ["AnomalyDetail"], "contains": ["first_seen", "last_seen", "count"]}],
     "key_links": [{"pattern": "anomalies.sample.json", "in": "frontend/src/pages/AnomalyDetail.tsx"}]
   },
   "notes": "时间显示要统一走本地时区转换（后端存UTC），这是5台服务器分布式场景下容易踩的坑，原型阶段就把转换函数定下来（如 frontend/src/utils/time.ts），后面接真实数据直接复用，不要每个页面各写一套。"},

  {"id": "F4", "description": "搭建FastAPI+SQLite项目骨架和数据库表结构（不含业务API逻辑），表结构字段严格对齐CONTRACT.md",
   "passes": false,
   "acceptance": "uvicorn可启动，GET /health返回200；SQLite按CONTRACT.md建好scans和anomalies两张表；anomalies表以(service, pattern_hash)或等价指纹字段为UNIQUE约束，用于后续upsert去重；建表逻辑可重复执行（CREATE TABLE IF NOT EXISTS或迁移工具，不是一次性手工SQL）",
   "wave": 2, "depends": ["F1"],
   "must_haves": {
     "artifacts": [
       {"path": "backend/app/main.py", "min_lines": 15, "contains": ["FastAPI", "/health"]},
       {"path": "backend/app/models.py", "min_lines": 20, "contains": ["scans", "anomalies", "UNIQUE"]},
       {"path": "backend/app/db.py", "min_lines": 10, "contains": ["sqlite"]}
     ],
     "key_links": []
   },
   "notes": "唯一键设计是关键坑点：同一异常每天扫描都会再出现，必须靠(service+pattern_hash)唯一键做UPSERT（count+1，更新last_seen，first_seen不变），不能每次INSERT新行——否则'出现次数'和'首末次时间'语义全错。首次建表就把这个约束定死，比后面加迁移省事。"},

  {"id": "F5", "description": "实现真实API：POST /api/scans（CLI推送，按F4唯一键UPSERT）、GET /api/anomalies/trend（近N天每日异常数，默认7天）、GET /api/anomalies/top（今日Top10）、GET /api/anomalies/{id}（详情）、GET /api/anomalies（列表，支持service+日期范围筛选）、GET /api/services（服务名下拉用）",
   "passes": false,
   "acceptance": "每个接口有对应pytest测试且通过；POST /api/scans对同一pattern_hash重复推送时count正确累加、first_seen不变、last_seen更新为最新一次；trend接口返回恰好7个日期点（含0值日期，不跳过无异常的天）；top接口仅统计'今日'（按配置时区，非硬编码UTC）范围内数据，按count降序取10条；push接口要求header X-API-Key校验，缺失或错误返回401",
   "wave": 3, "depends": ["F2", "F3", "F4"],
   "must_haves": {
     "artifacts": [
       {"path": "backend/app/api/scans.py", "min_lines": 20, "exports": ["router"], "contains": ["X-API-Key|api_key"]},
       {"path": "backend/app/api/anomalies.py", "min_lines": 40, "exports": ["router"], "contains": ["trend", "top", "service"]},
       {"path": "backend/tests/test_api.py", "min_lines": 30, "contains": ["upsert|UPSERT", "trend", "top"]}
     ],
     "key_links": [{"pattern": "models", "in": "backend/app/api/anomalies.py"}]
   },
   "notes": "wave3在F2/F3（前端原型用户确认）都通过后才开工，避免在需求方向没锁定前把后端往错的字段/接口形状上砌，这是防止'两周后对不上'的核心机制，不要为了赶进度提前并行做。鉴权用简单共享Token即可，团队内网5台机器场景不需要OAuth。"},

  {"id": "F6", "description": "首页从fixture切换到真实API：GET /api/anomalies/trend + GET /api/anomalies/top",
   "passes": false,
   "acceptance": "首页加载调用真实接口，无本地fixture引用残留；近7天无异常时图表显示'暂无异常'文案而非空白/报错；接口失败时显示重试按钮而非白屏",
   "wave": 4, "depends": ["F5", "F2"],
   "must_haves": {
     "artifacts": [{"path": "frontend/src/api/client.ts", "min_lines": 15, "exports": ["fetchTrend", "fetchTopAnomalies"]}],
     "key_links": [
       {"pattern": "fetchTrend|api/anomalies/trend", "in": "frontend/src/pages/Dashboard.tsx"},
       {"pattern": "fetchTopAnomalies|api/anomalies/top", "in": "frontend/src/pages/Dashboard.tsx"}
     ]
   },
   "notes": ""},

  {"id": "F7", "description": "详情页从fixture切换到真实API：GET /api/anomalies/{id}",
   "passes": false,
   "acceptance": "详情页按路由参数id调用真实接口展示原始日志片段；id不存在时显示404态而非白屏",
   "wave": 4, "depends": ["F5", "F3"],
   "must_haves": {
     "artifacts": [{"path": "frontend/src/pages/AnomalyDetail.tsx", "min_lines": 25, "contains": ["fetchAnomalyDetail|api/anomalies/"]}],
     "key_links": [{"pattern": "api/anomalies/", "in": "frontend/src/pages/AnomalyDetail.tsx"}]
   },
   "notes": ""},

  {"id": "F8", "description": "首页/列表加筛选器：服务名下拉（数据来自GET /api/services）+ 日期范围（预设：今天/近7天/近30天/自定义），筛选变化后重新拉取trend/top/list接口",
   "passes": false,
   "acceptance": "选择服务名后trend图和列表只显示该服务数据；选自定义日期范围后trend图X轴切换为对应天数；两个筛选可组合叠加使用；URL query string同步筛选状态，支持刷新页面/分享链接后筛选状态保留",
   "wave": 4, "depends": ["F5"],
   "must_haves": {
     "artifacts": [{"path": "frontend/src/components/Filters.tsx", "min_lines": 25, "exports": ["Filters"]}],
     "key_links": [{"pattern": "service=.*(from|start)", "in": "frontend/src/api/client.ts"}]
   },
   "notes": "日期范围控件按规范：预设行16px勾选样式，hover为ghost wash背景，自定义范围放在footer hairline分隔之后，不要做成弹出式日历默认态。"},

  {"id": "F9", "description": "logsift CLI加--push参数，扫描完成后按ScanPushPayload格式POST到后端，推送失败不影响原有终端输出",
   "passes": false,
   "acceptance": "logsift scan --push 正常完成终端输出的同时POST到配置的后端地址；后端地址和API Key通过配置文件或环境变量读取（不硬编码）；网络失败/后端不可达时打印一行warning但CLI退出码仍为0（除非扫描本身失败）；请求超时设置为3秒，不阻塞主流程明显变慢",
   "wave": 4, "depends": ["F5"],
   "must_haves": {
     "artifacts": [{"path": "cli/logsift/push.py", "min_lines": 20, "exports": ["push_scan_result"], "contains": ["X-API-Key|api_key", "timeout"]}],
     "key_links": [{"pattern": "push_scan_result", "in": "cli/logsift/cli.py"}]
   },
   "notes": "本feature的具体文件路径以F1实际探查到的CLI仓库结构为准，此处cli/logsift/是占位假设，实现前先核对。核心原则：推送失败绝不能让团队每天用的CLI主流程报错或明显变慢。"},

  {"id": "F10", "description": "5台服务器实际部署CLI并--push，端到端联调验证仪表盘全链路", 
   "passes": false,
   "acceptance": "5台服务器各跑一次logsift scan --push，后端anomalies表出现来自5个不同hostname的记录；仪表盘首页trend图和top10反映跨机器汇总数据；按service筛选能筛出预期子集；点击任意异常进详情页数据与该服务器CLI终端输出的原始日志片段一致；全程无CORS/网络报错",
   "wave": 5, "depends": ["F6", "F7", "F8", "F9"],
   "must_haves": {"artifacts": [], "key_links": []},
   "notes": "最终验收关卡，全部通过才能对团队正式发布仪表盘地址。"}
]}
```

## Wave 执行顺序
- **Wave 1**：F1（唯一起点，其余全部依赖它）
- **Wave 2**：F2、F3、F4（可并行，但 F2/F3 做完需人工确认后才算真正"通过"）
- **Wave 3**：F5（等 F2+F3 确认通过 + F4 完成）
- **Wave 4**：F6、F7、F8、F9（可并行）
- **Wave 5**：F10（最终联调）
