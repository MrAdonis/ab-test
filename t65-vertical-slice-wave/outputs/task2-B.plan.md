# logsift Web 仪表盘 · task_plan.md

## 背景

logsift 是跑了半年的 Python CLI，团队用它扫描服务器日志、输出异常摘要到终端（扫完即丢）。
现在要加一个 Web 仪表盘：历史入库、首页趋势图+Top10、异常详情页、按服务/日期筛选、CLI `--push` 自动上报。

## 技术栈（锁定，不再讨论）

- 后端：FastAPI + SQLite（同步 `sqlite3` 或 SQLAlchemy 均可，由 Wave1 执行 agent 一次性决定并写入 notes，后续 wave 不得更换）
- 前端：Vite + React + Recharts
- CLI：在现有 `logsift` 包基础上加 `--push` 参数
- 假定目录布局（**执行前必须先核实真实仓库结构，若不同以实际为准**）：
  - `logsift/` — 现有 CLI 包（`logsift/cli.py`、`logsift/scanner.py` 等）
  - `logsift/push.py` — 新增：push 客户端逻辑
  - `backend/app/` — 新增 FastAPI 服务
  - `frontend/src/` — 新增 Vite+React 前端

## 最怕的风险：两周后图表跟大家想的不是一回事 —— 如何应对

**应对机制：Wave 1 第一件事就是把首页图表用 mock 数据渲染出来，在浏览器里给真人看，拿到确认后才进 Wave 2。**
不是先搭 DB、再搭 API、最后才拼前端（水平分层，两周后才第一次看到图表）。
F1 必须在 1 个 wave 内产出可运行的浏览器页面，且视觉参数已经是下面锁死的规格（不是占位样式），
这样"图表长什么样"这个最主观、最容易分歧的问题在第 1 天就暴露，而不是第 10 天。

**执行约束：F1 完成后必须停下来，把首页截图/本地预览地址发给用户确认"这就是我们想要的趋势图和Top10样式"，
用户确认后才能开始 Wave 2。这是一个人工 gate，编码 agent 不能跳过。**

## 视觉设计规格（写死，来自 dataviz 校验色板，禁止自由发挥）

范围声明：**本期仅做浅色模式（light mode），深色模式明确排除在 MVP 之外**（内部工具，非公开产品，避免为了双模式验证拖慢首个可见闭环）。

### 色值（浅色）
| 角色 | 取值 |
|---|---|
| 图表/卡片背景 surface | `#fcfcfb` |
| 页面背景 page plane | `#f9f9f7` |
| 主文字 primary ink | `#0b0b0b` |
| 次文字 secondary ink | `#52514e` |
| 弱化文字（坐标轴/标签）muted ink | `#898781` |
| 网格线 hairline | `#e1e0d9` |
| 基线/坐标轴线 | `#c3c2b7` |
| 卡片描边 border ring | `rgba(11,11,11,0.10)` |
| 折线/面积系列色（唯一一条线）| `#2a78d6` |
| 面积填充 | `#2a78d6` @ 10% 透明度 |

> 趋势图默认是**单系列**（全部服务汇总，或筛选后单个服务的汇总），不做多服务分色对比折线——用户需求里没有"比较多个服务"这个诉求，多系列会引入分类色板校验、图例、collision 处理等复杂度，MVP 不需要。若后续明确要"多服务对比"，再按 `references/palette.md` 的 8 色分类色板（固定顺序，≤4 条系列强制直接标注，超过按 ladder 处理）扩展，不要现在预留。

### 间距与圆角
| 项 | 值 |
|---|---|
| 基础间距单位 | 8px |
| 卡片内边距 | 20px |
| 卡片间距 | 16px（同段内）/ 32px（不同区块间）|
| 卡片圆角 | 12px |
| Tooltip 圆角 / 内边距 | 8px / `8px 12px` |
| Top10 表格行高 | 40px |
| 筛选行到图表卡片的下边距 | 24px |

### 图表 mark 规格
- 折线：2px，圆头圆角连接（round cap/join）
- 数据点标记：直径 ≥8px（r≥4），填充系列色，2px surface 色描边环（避免和线重叠时糊在一起）
- 面积填充：系列色 10% 透明度的淡淡一层，不是实色块
- 网格线：仅横向参考线，1px hairline `#e1e0d9`，实线，绝不用虚线
- Y 轴刻度：取整数（0/50/100…），千分位逗号；X 轴 7 个刻度，短星期/日期标签（如 `周一`/`07-20`），muted ink
- 单系列不需要图例框——图表标题本身说明画的是什么，如「近7天异常趋势 · 全部服务」或「近7天异常趋势 · nginx」

### Tooltip / hover（折线图必须有，不是可选项）
- 垂直 crosshair，1px，颜色 `#c3c2b7`，吸附到最近的日期点
- Tooltip 框：背景 `#fcfcfb`，1px 描边 `rgba(11,11,11,0.10)`，圆角 8px，内边距 `8px 12px`
- Tooltip 内容：日期（次要文字）+ 当日次数（主要文字，加粗），数值在前、标签在后
- 键盘 focus 态与 hover 态展示同样的信息

### Top10 列表（这是表格，不是图表——超过 7 个有意义的字段用表格是 dataviz 的明确规则）
- 列：排名 / 服务 / 异常摘要（message）/ 次数（右对齐，`tabular-nums`，加粗）/ 首次出现 / 最后出现
- 行高 40px，hover 时背景变 secondary ink @ 5% 透明度的淡色，行下边框 1px `#e1e0d9`
- 点击一行跳转到该异常的详情页
- 排序固定按"次数"降序，取前 10

### 详情页
- 原始日志片段：等宽字体代码块，背景 `#f9f9f7`，内边距 16px，圆角 8px，超长时内部滚动，字号 13px
- 出现次数 / 首次出现 / 最后出现：3 个并排 stat tile，label 用句子大小写不带冒号，value 用半粗（semibold）比例数字（不用 tabular-nums，那是给对齐的表格列用的），tile 间距 24px

### 筛选区（服务名 + 日期范围）
- 单独一行，左对齐，置于图表/列表上方（不要塞进图表卡片内部）
- 日期范围用预设行列表（今日/近7天/近30天/自定义），选中态 16px 加粗对勾，hover 是淡淡的 ghost 底色，自定义范围收在列表底部一条分隔线之后
- 服务名筛选用标准下拉 combobox
- **重新拉取数据时旧图表/旧表格保留在原地、透明度降到 50%，不出现骨架屏、不出现布局跳动**——这是切换筛选时体感是否"顺"的关键，容易被漏掉

### 排除项（明确写清楚，避免执行时自由发挥）
- 不做深色模式
- 不做多服务对比折线（多系列）
- 不做首页 KPI 大数字卡片（用户没要求，不要加）
- 不做导出/下载报表功能

## API / 数据契约（锁定，CLI 和后端都按此实现，避免两边接口对不上）

### POST /api/scan-results（CLI --push 调用）
```json
{
  "server_id": "web-01",
  "scanned_at": "2026-07-26T10:00:00Z",
  "anomalies": [
    {
      "service": "nginx",
      "signature": "归一化后的异常签名/哈希，用于跨次扫描聚合去重",
      "message": "异常摘要文本",
      "count": 12,
      "first_seen": "2026-07-26T09:55:00Z",
      "last_seen": "2026-07-26T10:00:00Z",
      "sample_log": "原始日志片段，截断到 4000 字符以内，避免单条 payload 过大"
    }
  ]
}
```

### GET /api/summary?service=&date_from=&date_to=
```json
{
  "trend": [{"date": "2026-07-20", "count": 34}, "...(7条)"],
  "top10": [{"anomaly_id": 123, "service": "nginx", "message": "...", "count": 41, "first_seen": "...", "last_seen": "..."}]
}
```

### GET /api/anomalies/{anomaly_id}
```json
{"id": 123, "service": "nginx", "message": "...", "count": 41, "first_seen": "...", "last_seen": "...", "sample_log": "..."}
```

## DB Schema（锁定要点）
- `scans(id, server_id, scanned_at, pushed_at)`，**唯一约束 `(server_id, scanned_at)`** —— 从 Wave1 就必须建好，防止 CLI 重试导致重复入库，避免 Wave4 再来一次破坏性迁移
- `anomalies(id, scan_id FK, service, signature, message, count, first_seen, last_seen, sample_log)`
- 索引：`(service, first_seen)` 至少一个，支撑按服务+日期范围筛选的查询性能

## Wave 总览

- **Wave 1**：首页可视化闭环（mock 数据）→ **用户视觉验收 gate**；CLI push + 真实入库闭环（不接前端）
- **Wave 2**：首页换真实数据源；异常详情页
- **Wave 3**：筛选（服务名 + 日期范围）接入首页
- **Wave 4**：多机部署容错（push 失败重试/本地队列）+ 幂等去重验证

每个 wave 结束都必须有一个能在浏览器/CLI 里演示的东西，不允许连续两个 wave 只做后端管道没有可见产出。

## Features (JSON)

```json
{
  "features": [
    {
      "id": "F1",
      "description": "首页可视化原型：FastAPI 骨架 + mock /api/summary 接口，返回固定 7 天趋势 + 10 条 mock 异常；React 首页用 Recharts 折线图 + Top10 表格渲染，视觉参数完全按本文档「视觉设计规格」写死实现（颜色/间距/圆角/tooltip/字体，不使用组件库默认样式）。",
      "passes": false,
      "acceptance": "本地跑 `uvicorn` 和 `vite dev`，浏览器打开首页能看到：(1) 一条 2px 蓝色(#2a78d6)折线 + 10%透明度面积填充的7天趋势图，hover 有 crosshair+tooltip；(2) 下方 Top10 表格，行高40px，次数列右对齐tabular-nums，按次数降序；(3) 整体配色/圆角/间距与规格一致。截图或本地预览地址交付给用户，获得『这就是我们想要的图』的明确确认后才能进入 Wave2。",
      "wave": 1,
      "depends": [],
      "must_haves": {
        "artifacts": [
          {"path": "backend/app/main.py", "min_lines": 20, "exports": ["app"], "contains": ["FastAPI"]},
          {"path": "backend/app/routes/summary_mock.py", "min_lines": 15, "contains": ["/api/summary", "trend", "top10"]},
          {"path": "frontend/src/pages/Home.tsx", "min_lines": 40, "contains": ["fetch\\(.*api/summary", "TrendChart", "Top10Table"]},
          {"path": "frontend/src/components/TrendChart.tsx", "min_lines": 30, "contains": ["#2a78d6", "LineChart|AreaChart"]},
          {"path": "frontend/src/components/Top10Table.tsx", "min_lines": 20, "contains": ["tabular-nums"]}
        ],
        "key_links": [
          {"pattern": "fetch\\(['\"`].*/api/summary", "in": "frontend/src/pages/Home.tsx"},
          {"pattern": "/api/summary", "in": "backend/app/routes/summary_mock.py"}
        ]
      },
      "notes": "这是全 plan 最关键的一步：目的不是‘先能跑’而是‘先让人看到并确认视觉方向’。mock 数据的字段结构必须和后面 Wave2 真实接口的 JSON 契约（见文档 API 契约章节）完全一致，这样 Wave2 只是替换数据源，不改前端组件。FastAPI/SQLAlchemy 选型在本 feature 内一次性定下并写回 notes。"
    },
    {
      "id": "F2",
      "description": "CLI `--push` 真实推送 + 后端真实入库：logsift 新增 push.py，扫描完成后若带 --push 把结果 POST 到 /api/scan-results；后端建 SQLite schema（scans/anomalies 表，含幂等唯一约束）并实现真实写入。",
      "passes": false,
      "acceptance": "在一台机器上执行 `logsift scan --push`（对接本地跑起来的后端），命令行不报错退出；用 `sqlite3 <db文件> 'select * from anomalies;'` 能看到刚才扫描出的异常数据已经落库，字段与 API 契约一致。",
      "wave": 1,
      "depends": ["F1"],
      "must_haves": {
        "artifacts": [
          {"path": "logsift/push.py", "min_lines": 20, "exports": ["push_results"], "contains": ["post\\("]},
          {"path": "logsift/cli.py", "contains": ["--push"]},
          {"path": "backend/app/db.py", "min_lines": 20, "contains": ["CREATE TABLE", "scans", "anomalies", "UNIQUE"]},
          {"path": "backend/app/routes/scan_results.py", "min_lines": 20, "contains": ["/api/scan-results", "post"]}
        ],
        "key_links": [
          {"pattern": "push_results", "in": "logsift/cli.py"},
          {"pattern": "/api/scan-results", "in": "logsift/push.py"}
        ]
      },
      "notes": "依赖 F1 只是为了复用已经建好的 backend/app/main.py 骨架和项目结构，避免两个 feature 并行改同一个文件冲突，不代表业务上有依赖。schema 设计时必须一次到位：(1) scans 表 (server_id, scanned_at) 唯一约束，防止重试导致重复入库；(2) sample_log 截断到 4000 字符存储，不要把每次出现的完整原文都存一遍——只存一条代表性片段 + count/first_seen/last_seen 聚合；这两点现在不做，Wave4 会需要破坏性迁移。"
    },
    {
      "id": "F3",
      "description": "首页接真实数据：把 F1 的 mock /api/summary 换成真实查询——按天聚合近7天全部异常 count 算趋势线，按今日 anomalies 聚合 count 取降序前10。前端组件不变，只换数据源。",
      "passes": false,
      "acceptance": "先执行几次 `logsift scan --push`（用不同服务/时间），刷新首页：折线图和Top10随入库数据变化而变化，不再是固定的 mock 数字；今日 top10 的排序和次数与 sqlite 里直接查询的结果一致（人工核对至少3条）。",
      "wave": 2,
      "depends": ["F1", "F2"],
      "must_haves": {
        "artifacts": [
          {"path": "backend/app/routes/summary.py", "min_lines": 30, "contains": ["SELECT", "GROUP BY", "/api/summary"]}
        ],
        "key_links": [
          {"pattern": "/api/summary", "in": "backend/app/routes/summary.py"},
          {"pattern": "fetch\\(['\"`].*/api/summary", "in": "frontend/src/pages/Home.tsx"}
        ]
      },
      "notes": "今日 top10 的『次数』口径要明确：同一 signature 当天可能被多台服务器/多次扫描各推送一次，count 是把当天所有相关记录的 count 字段求和后再排序，不是取某一次 push 的原始值。这个口径在实现前必须写进代码注释或至少在 PR 描述里说清楚，避免和用户预期对不上。"
    },
    {
      "id": "F4",
      "description": "异常详情页：点击 Top10 或后续列表中的一行，跳转到 /anomaly/:id，展示原始日志片段（代码块）、出现次数、首次/最后出现时间（3个stat tile），样式按规格中的详情页章节实现。",
      "passes": false,
      "acceptance": "在首页 Top10 表格点击任意一行，跳转到详情页且能看到该异常的原始日志片段、次数、首次/最后出现时间，字段与数据库中该条 anomaly 记录一致。",
      "wave": 2,
      "depends": ["F2", "F3"],
      "must_haves": {
        "artifacts": [
          {"path": "backend/app/routes/anomaly_detail.py", "min_lines": 15, "contains": ["/api/anomalies/", "sample_log"]},
          {"path": "frontend/src/pages/AnomalyDetail.tsx", "min_lines": 30, "contains": ["sample_log|sampleLog", "stat"]}
        ],
        "key_links": [
          {"pattern": "navigate\\(.*anomaly", "in": "frontend/src/components/Top10Table.tsx"},
          {"pattern": "/api/anomalies/", "in": "frontend/src/pages/AnomalyDetail.tsx"}
        ]
      },
      "notes": "sample_log 展示时要做 HTML 转义（用 textContent/React 默认转义），日志原文里可能包含尖括号等字符，不能用 dangerouslySetInnerHTML。"
    },
    {
      "id": "F5",
      "description": "首页接入筛选：服务名下拉 + 日期范围预设（今日/近7天/近30天/自定义），筛选行放在图表和表格上方一整行；筛选变化时趋势图和Top10表格都用新参数重新请求 /api/summary，重新拉取期间旧内容保留在原地降到50%透明度（不用骨架屏）。",
      "passes": false,
      "acceptance": "选择某个具体服务后，折线图标题变为『近7天异常趋势 · {服务名}』且数值只统计该服务；切换日期范围为『近30天』后趋势图横轴/数据范围随之变化；切换筛选的瞬间能观察到旧图表半透明保留而不是消失或闪烁。",
      "wave": 3,
      "depends": ["F3"],
      "must_haves": {
        "artifacts": [
          {"path": "frontend/src/components/Filters.tsx", "min_lines": 30, "contains": ["combobox|select", "今日|7|30"]}
        ],
        "key_links": [
          {"pattern": "service=.*date_from=.*date_to=|service.*date_from|params", "in": "frontend/src/pages/Home.tsx"},
          {"pattern": "service.*date_from.*date_to", "in": "backend/app/routes/summary.py"}
        ]
      },
      "notes": "筛选状态放在 Home.tsx 顶层（或简单的 URL query string），不要引入额外状态管理库，需求规模不需要。"
    },
    {
      "id": "F6",
      "description": "5台服务器真实部署联调 + push 容错：后端不可达时 CLI 不崩溃，把本次结果写入本地待重传队列文件（如 ~/.logsift/pending_pushes.jsonl），下次运行 --push 时先尝试补推队列里的旧数据，成功后清空对应条目。",
      "passes": false,
      "acceptance": "临时关掉后端服务，执行 `logsift scan --push`：命令正常退出（非 crash），打印明确警告，本地队列文件里出现一条待推送记录；重新启动后端后再跑一次 `logsift scan --push`，观察到队列里的旧记录被补推成功且从队列文件移除，同时新的扫描结果也推送成功。",
      "wave": 4,
      "depends": ["F2"],
      "must_haves": {
        "artifacts": [
          {"path": "logsift/push.py", "contains": ["pending_pushes", "retry|except.*ConnectionError|except.*RequestException"]}
        ],
        "key_links": [
          {"pattern": "pending_pushes", "in": "logsift/push.py"}
        ]
      },
      "notes": "队列文件用简单的 JSON Lines 追加写即可，不需要引入消息队列中间件；这是 5 台机器场景下最容易被忽略的边界情况——不做的话某台服务器网络抖动就会永久丢一批数据。"
    },
    {
      "id": "F7",
      "description": "幂等去重验证与补强：确保同一次扫描结果被重复 push（CLI 重试、或补推队列与正常推送撞车）不会导致数据库中 count 被重复叠加。基于 F2 已经建好的 (server_id, scanned_at) 唯一约束，在 POST /api/scan-results 里做 upsert-or-ignore。",
      "passes": false,
      "acceptance": "手动对同一批日志运行两次 `logsift scan --push`（模拟重试），用 sqlite3 查询确认该批次对应的 anomalies 记录只入库一次，Top10 的 count 数值没有翻倍。",
      "wave": 4,
      "depends": ["F2"],
      "must_haves": {
        "artifacts": [
          {"path": "backend/app/routes/scan_results.py", "contains": ["INSERT OR IGNORE|ON CONFLICT|IntegrityError"]}
        ],
        "key_links": [
          {"pattern": "ON CONFLICT|OR IGNORE|IntegrityError", "in": "backend/app/routes/scan_results.py"}
        ]
      },
      "notes": "如果 F2 阶段已经把 upsert 逻辑做完，这个 feature 退化为『写测试验证』，也要保留——防止 F2 执行时因为赶时间跳过了这部分。"
    }
  ]
}
```

## 给编码 agent 的执行提醒

1. Wave1 结束、F1 验收后，**必须等待用户对首页视觉的明确确认**，才能开始 Wave2。这是本 plan 里唯一的人工阻塞点，其余 wave 之间可以连续跑。
2. 真实仓库结构如果和本文档"假定目录布局"不同，先花 5 分钟核实实际路径，再调整 must_haves 里的 path，不要凭空按本文档路径硬创建重复目录。
3. 视觉规格章节里的数值是写死的验收标准，不是建议——实现时不要用 UI 库默认的 primary 色、默认圆角替代。
4. API 契约章节的字段名和结构，CLI 侧（F2/F6/F7）和后端侧（F1/F2/F3/F4）必须完全对齐，改动需要双边同步。
