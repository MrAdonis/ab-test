# 内部报销工具 — task_plan.md

## 概览
8 人小团队内部报销系统。技术栈锁定：**Next.js 15 (App Router, TypeScript) + Prisma + SQLite**，内网部署，无多租户/权限系统，登录用邮箱白名单。

## 关键技术决策（锁死，编码 agent 不需自行选型）
- 包管理器 npm；不使用 `src/` 目录，直接用 `app/`。
- 数据变更（提交/审批/驳回）用 **Server Actions**（`"use server"`）；文件上传与 CSV 导出需要文件/流响应，用 **Route Handler**。
- SQLite + Prisma **不支持原生 enum** —— `category`、`status` 字段用 `String`，配合 `zod` 在 `lib/expenses.ts` 做应用层校验，常量定义为字面量联合类型。
- 金额存储：`amountCents`（Int，分为单位），避免浮点误差；对外接口用"元"（number，2 位小数）。
- 鉴权：不用 next-auth/OAuth，手写 JWT（`jose` 库）+ httpOnly cookie，7 天有效期；`middleware.ts` 统一拦截未登录请求，`/approvals`、`/export` 仅 `isManager=true` 可访问。
- 发票文件存本地磁盘 `UPLOAD_DIR`（默认 `./uploads`，不在 `public/` 下），需登录才能读取（`/api/uploads/[filename]` 鉴权后流式返回）。
- UI 文案全部简体中文；日期格式 `YYYY-MM-DD`；主色 `indigo-600 (#4F46E5)`，圆角统一 `rounded-md (6px)`。
- CSV 导出加 UTF-8 BOM，避免财务用 Excel 打开中文乱码；月份边界按 `Asia/Shanghai` 时区计算。

## Wave 划分（供并行调度）
| Wave | Features | 说明 |
|---|---|---|
| 1 | F1 | 项目骨架，阻塞一切 |
| 2 | F2 | Prisma schema + seed |
| 3 | F3 | 邮箱白名单登录 + 路由保护 |
| 4 | F4, F5, F6 | 上传 / 导航壳 / 数据访问层 — 三者互不冲突文件，可并行 |
| 5 | F7, F8, F9, F10 | 提交表单 / 我的列表 / 审批队列 / CSV 导出 — 均只依赖 wave1-4 产物，互不冲突，可并行 |
| 6 | F11 | 部署文档 + 端到端收尾 |

## 进度
尚未开始编码，所有 feature `passes: false`。

---

## Features (JSON)

```json
{
  "features": [
    {
      "id": "F1",
      "description": "初始化 Next.js 15 (App Router, TypeScript) 项目，配置 Tailwind CSS 3，建立全局布局壳与环境变量样例。",
      "passes": false,
      "acceptance": "`npm run dev` 可启动；访问 http://localhost:3000 返回 200；app/layout.tsx 含 <html lang=\"zh-CN\">；Tailwind 样式生效。",
      "wave": 1,
      "depends": [],
      "must_haves": {
        "artifacts": [
          {"path": "package.json", "min_lines": 15, "contains": ["\"next\"", "\"tailwindcss\"", "\"typescript\""]},
          {"path": "app/layout.tsx", "min_lines": 15, "contains": ["zh-CN", "RootLayout"]},
          {"path": "app/globals.css", "min_lines": 5, "contains": ["@tailwind"]},
          {"path": "tailwind.config.ts", "min_lines": 5, "contains": []},
          {"path": ".env.example", "min_lines": 3, "contains": ["DATABASE_URL", "APP_SECRET", "UPLOAD_DIR"]}
        ],
        "key_links": []
      },
      "notes": "Node.js >=20。不使用 src/ 目录。Server Actions 用于数据变更，Route Handler 仅用于文件上传/CSV导出，这个约定后续所有 feature 遵守。"
    },
    {
      "id": "F2",
      "description": "定义 Prisma schema（SQLite provider），User 与 ExpenseReport 模型，跑首次 migration，编写 seed 脚本写入 8 个白名单邮箱（至少 1 个 isManager=true）。",
      "passes": false,
      "acceptance": "`npx prisma migrate dev` 成功生成 dev.db；`npx prisma db seed` 写入 8 条 User；`npx prisma studio` 可见数据。",
      "wave": 2,
      "depends": ["F1"],
      "must_haves": {
        "artifacts": [
          {"path": "prisma/schema.prisma", "min_lines": 30, "contains": ["model User", "model ExpenseReport", "provider = \"sqlite\"", "isManager", "status", "category", "receiptPath", "amountCents"]},
          {"path": "prisma/seed.ts", "min_lines": 15, "contains": ["isManager: true"]},
          {"path": "lib/prisma.ts", "min_lines": 8, "exports": ["prisma"], "contains": ["PrismaClient"]}
        ],
        "key_links": []
      },
      "notes": "坑点：SQLite + Prisma 不支持字段级 enum，category/status 用 String，业务约束放应用层（见 F6）。amount 用 amountCents(Int) 存储，避免浮点误差。date 只存日期语义，业务上不关心具体时间。receiptPath 存相对路径，不含 UPLOAD_DIR 前缀。"
    },
    {
      "id": "F3",
      "description": "实现邮箱白名单登录：/login 页面输入邮箱 -> POST /api/auth/login 校验邮箱是否存在于 User 表（不区分大小写）-> 用 jose 签发 JWT（userId/email/isManager，7 天有效期）写入 httpOnly cookie `session`；middleware.ts 拦截未登录访问并重定向 /login；/approvals 与 /export 仅 isManager=true 可访问，否则重定向 /expenses。",
      "passes": false,
      "acceptance": "白名单邮箱登录后可访问 /expenses；非白名单邮箱登录返回 401 且提示未授权；未登录访问 /expenses 被重定向 /login；普通员工访问 /approvals 被重定向。",
      "wave": 3,
      "depends": ["F1", "F2"],
      "must_haves": {
        "artifacts": [
          {"path": "lib/auth.ts", "min_lines": 25, "exports": ["createSession", "getSession", "clearSession"], "contains": ["jose", "httpOnly", "SignJWT"]},
          {"path": "middleware.ts", "min_lines": 15, "contains": ["getSession", "isManager", "/login"]},
          {"path": "app/login/page.tsx", "min_lines": 20, "contains": ["input", "email"]},
          {"path": "app/api/auth/login/route.ts", "min_lines": 15, "contains": ["createSession", "findFirst"]},
          {"path": "app/api/auth/logout/route.ts", "min_lines": 5, "contains": ["clearSession"]}
        ],
        "key_links": [
          {"pattern": "createSession", "in": "app/api/auth/login/route.ts"},
          {"pattern": "getSession", "in": "middleware.ts"}
        ]
      },
      "notes": "APP_SECRET 缺失需 fail fast（启动即报错）。开发环境 http://localhost 下 cookie 的 secure 属性需按 NODE_ENV 判断，否则本地登录会失败——这是常见坑，务必处理。"
    },
    {
      "id": "F4",
      "description": "发票文件上传：POST /api/uploads 接收 multipart/form-data，校验 mime（image/jpeg, image/png, image/webp, application/pdf）与大小 <=5MB，用 crypto.randomUUID() 生成文件名存入 UPLOAD_DIR，返回 { path }。GET /api/uploads/[filename] 校验登录后流式返回文件。",
      "passes": false,
      "acceptance": "已登录用户上传 <5MB 的 jpg 返回 200 和 path；上传 6MB 文件返回 400；上传 .exe 返回 400；未登录 GET /api/uploads/xxx 返回 401。",
      "wave": 4,
      "depends": ["F3"],
      "must_haves": {
        "artifacts": [
          {"path": "lib/storage.ts", "min_lines": 20, "exports": ["saveReceiptFile", "readReceiptFile"], "contains": ["randomUUID", "UPLOAD_DIR"]},
          {"path": "app/api/uploads/route.ts", "min_lines": 15, "contains": ["saveReceiptFile", "formData"]},
          {"path": "app/api/uploads/[filename]/route.ts", "min_lines": 10, "contains": ["getSession", "readReceiptFile"]}
        ],
        "key_links": [
          {"pattern": "saveReceiptFile", "in": "app/api/uploads/route.ts"},
          {"pattern": "getSession", "in": "app/api/uploads/\\[filename\\]/route.ts"}
        ]
      },
      "notes": "UPLOAD_DIR 需在启动/首次调用时 fs.mkdirSync(recursive:true)。生产部署要确保该目录持久化（不能是容器临时层），写进 F11 部署文档。"
    },
    {
      "id": "F5",
      "description": "顶部导航栏 + 全局布局容器 + StatusBadge 组件。导航按 session.isManager 显示不同链接：员工看到「我的报销单」「提交报销」，主管额外看到「待审批」「导出 CSV」，都显示当前用户邮箱和登出按钮。",
      "passes": false,
      "acceptance": "登录后所有页面顶部可见导航；员工账号看不到「待审批」/「导出」链接；点击登出跳回 /login 且 cookie 被清除。",
      "wave": 4,
      "depends": ["F3"],
      "must_haves": {
        "artifacts": [
          {"path": "app/components/Nav.tsx", "min_lines": 25, "contains": ["isManager", "待审批", "我的报销单"]},
          {"path": "app/components/StatusBadge.tsx", "min_lines": 15, "contains": ["PENDING", "APPROVED", "REJECTED", "bg-amber-100", "bg-green-100", "bg-red-100"]}
        ],
        "key_links": [
          {"pattern": "getSession", "in": "app/components/Nav.tsx"},
          {"pattern": "import Nav", "in": "app/layout.tsx"}
        ]
      },
      "notes": "视觉参数写死：导航栏高度 h-14(56px)，白底，底部 border-gray-200(1px)，容器 max-w-5xl mx-auto px-6。StatusBadge: rounded-full px-2.5 py-0.5 text-xs font-medium，三态配色见上。Nav 用 Server Component 直接 await getSession()。"
    },
    {
      "id": "F6",
      "description": "lib/expenses.ts 数据访问层：封装报销单的增删查与审批业务规则，供 Server Actions/Route Handler 调用。函数：createExpense, listExpensesByUser, listPendingExpenses, approveExpense, rejectExpense, listExpensesByMonth。校验规则：amount 必须 >0 且 <=100000 元；category 必须属于 CATEGORY 五选一（TRAVEL/MEALS/OFFICE/TRANSPORT/OTHER）；date 不能晚于今天；notes 最长 500 字；receiptPath 必填；rejectReason 必填且最长 300 字。",
      "passes": false,
      "acceptance": "金额为负/0 被拒绝；未来日期被拒绝；驳回无理由被拒绝；approveExpense 写入 reviewedBy/reviewedAt 且 status 变 APPROVED。",
      "wave": 4,
      "depends": ["F2"],
      "must_haves": {
        "artifacts": [
          {"path": "lib/expenses.ts", "min_lines": 60, "exports": ["createExpense", "listExpensesByUser", "listPendingExpenses", "approveExpense", "rejectExpense", "listExpensesByMonth", "CATEGORY", "STATUS"], "contains": ["zod", "prisma.expenseReport"]}
        ],
        "key_links": [
          {"pattern": "import.*prisma.*from ['\"]@/lib/prisma", "in": "lib/expenses.ts"}
        ]
      },
      "notes": "对外金额单位是元（number，2位小数），内部转换成 amountCents=Math.round(amount*100) 存库。CATEGORY/STATUS 常量与数据库里的字符串手动保持一致（无 DB 层约束，这是 SQLite 的已知限制）。"
    },
    {
      "id": "F7",
      "description": "/expenses/new 提交报销表单：金额（元，number, step 0.01）、类别（下拉五选一，中文标签：差旅/餐饮/办公用品/交通/其他）、日期（date input，默认今天，max=今天）、发票上传（先调 /api/uploads 拿 path，再作为 hidden field 随表单一起提交）、备注（textarea，选填，剩余字数提示）。提交用 Server Action，成功后跳转 /expenses 并 toast「提交成功，等待审批」。",
      "passes": false,
      "acceptance": "员工提交含发票的报销单后，在「我的报销单」列表第一行看到该记录，状态为「待审批」；不选发票或金额为 0 时表单阻止提交并显示错误。",
      "wave": 5,
      "depends": ["F2", "F3", "F4", "F5", "F6"],
      "must_haves": {
        "artifacts": [
          {"path": "app/expenses/new/page.tsx", "min_lines": 40, "contains": ["form", "<select"]},
          {"path": "app/expenses/new/actions.ts", "min_lines": 15, "contains": ["\"use server\"", "createExpense", "revalidatePath"]}
        ],
        "key_links": [
          {"pattern": "createExpense", "in": "app/expenses/new/actions.ts"},
          {"pattern": "/api/uploads", "in": "app/expenses/new/page.tsx"}
        ]
      },
      "notes": "视觉参数：表单卡片 max-w-lg bg-white rounded-lg shadow-sm p-6，字段间距 space-y-4；主按钮 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md px-4 py-2；错误文案 text-red-600 text-sm。上传流程锁死为两步（先传文件拿 path，再提交表单），不要在 Server Action 里直接处理大文件流。"
    },
    {
      "id": "F8",
      "description": "/expenses 我的报销单列表：展示当前用户所有报销单，按 date 倒序，列：日期/类别/金额/状态(StatusBadge)/备注摘要(超20字省略)/驳回理由(仅REJECTED时可展开)。空状态：无记录时显示提示+跳转按钮。",
      "passes": false,
      "acceptance": "员工登录后 /expenses 只显示自己的记录（不显示他人）；驳回记录能看到主管填写的理由。",
      "wave": 5,
      "depends": ["F3", "F5", "F6"],
      "must_haves": {
        "artifacts": [
          {"path": "app/expenses/page.tsx", "min_lines": 35, "contains": ["listExpensesByUser", "StatusBadge"]}
        ],
        "key_links": [
          {"pattern": "listExpensesByUser", "in": "app/expenses/page.tsx"},
          {"pattern": "StatusBadge", "in": "app/expenses/page.tsx"}
        ]
      },
      "notes": "视觉参数：表格 divide-y divide-gray-100，行 hover:bg-gray-50，表头 text-xs text-gray-500 uppercase。空状态文案「还没有报销记录，去提交一笔」。"
    },
    {
      "id": "F9",
      "description": "/approvals 主管待审批队列（仅 isManager）：列出所有 status=PENDING 的报销单（含申请人邮箱/姓名），按提交时间正序。每行「通过」「驳回」按钮；驳回弹模态框要求填理由（必填，最长300字），确认后调 rejectExpense；通过直接调 approveExpense。操作后 revalidatePath 使该行消失。",
      "passes": false,
      "acceptance": "主管能看到全员待审批列表；驳回不填理由无法提交；驳回/通过后员工在 /expenses 能看到对应状态与理由；非主管访问 /approvals 被重定向。",
      "wave": 5,
      "depends": ["F3", "F5", "F6"],
      "must_haves": {
        "artifacts": [
          {"path": "app/approvals/page.tsx", "min_lines": 35, "contains": ["listPendingExpenses", "isManager"]},
          {"path": "app/approvals/actions.ts", "min_lines": 20, "contains": ["\"use server\"", "approveExpense", "rejectExpense"]},
          {"path": "app/approvals/RejectDialog.tsx", "min_lines": 20, "contains": ["textarea", "required"]}
        ],
        "key_links": [
          {"pattern": "listPendingExpenses", "in": "app/approvals/page.tsx"},
          {"pattern": "approveExpense|rejectExpense", "in": "app/approvals/actions.ts"}
        ]
      },
      "notes": "视觉参数：驳回模态框 max-w-md 居中，遮罩 bg-black/40，理由 textarea rows=4；通过按钮 bg-green-600 hover:bg-green-700，驳回按钮 bg-red-600 hover:bg-red-700 文字白色。页面内需再次校验 session.isManager（防止绕过 middleware 直接调 action，defense in depth）。"
    },
    {
      "id": "F10",
      "description": "/export CSV 导出（仅 isManager）：月份选择器（默认上个自然月），点击导出调用 GET /api/export?month=YYYY-MM 下载 CSV。列：日期,员工邮箱,员工姓名,类别,金额,状态,审批人,审批时间,驳回理由,备注。文件名 reimbursement-{YYYY-MM}.csv，UTF-8 with BOM。",
      "passes": false,
      "acceptance": "主管导出某月 CSV，Excel 打开中文不乱码，行数与数据库该月记录数一致；员工账号访问 /export 被重定向。",
      "wave": 5,
      "depends": ["F3", "F6"],
      "must_haves": {
        "artifacts": [
          {"path": "lib/csv.ts", "min_lines": 15, "exports": ["toCSV"], "contains": ["\\uFEFF"]},
          {"path": "app/api/export/route.ts", "min_lines": 20, "contains": ["listExpensesByMonth", "toCSV", "Content-Disposition", "text/csv"]},
          {"path": "app/export/page.tsx", "min_lines": 15, "contains": ["month", "isManager"]}
        ],
        "key_links": [
          {"pattern": "toCSV", "in": "app/api/export/route.ts"},
          {"pattern": "listExpensesByMonth", "in": "app/api/export/route.ts"}
        ]
      },
      "notes": "月份边界按 Asia/Shanghai 时区计算当月 1 号 00:00 至下月 1 号 00:00，避免 UTC 偏移导致月初/月末记录漏算。金额导出为两位小数数字，不带 ¥ 符号，方便财务导入 Excel。"
    },
    {
      "id": "F11",
      "description": "内网部署文档 + 端到端收尾：README 写明 pm2/systemd 启动 next start、SQLite 文件路径与备份、UPLOAD_DIR 权限、环境变量清单、白名单增删方式（scripts/add-user.ts）。补全各页面 loading/error/空状态。跑一遍端到端手动验收清单。",
      "passes": false,
      "acceptance": "全新克隆仓库按 README 步骤（npm install -> 配置 .env -> npx prisma migrate deploy -> npx prisma db seed -> npm run build && npm start）5 分钟内跑起来；手动走完登录->提交->上传->列表可见->主管审批->员工侧看到结果->月度导出 全部通过。",
      "wave": 6,
      "depends": ["F7", "F8", "F9", "F10"],
      "must_haves": {
        "artifacts": [
          {"path": "README.md", "min_lines": 40, "contains": ["npx prisma migrate", "UPLOAD_DIR", "npm start", "白名单"]},
          {"path": "scripts/add-user.ts", "min_lines": 10, "contains": ["prisma.user.create"]}
        ],
        "key_links": []
      },
      "notes": "生产环境务必设置 NODE_ENV=production 使 cookie secure 生效（对应 F3 的坑）。SQLite 文件与 uploads 目录必须在同一台机器的持久化磁盘上，不能放临时目录，否则重启丢数据。"
    }
  ]
}
```
