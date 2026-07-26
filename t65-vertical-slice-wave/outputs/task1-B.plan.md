# 内部报销工具 · task_plan.md

## 项目概述
8 人小团队内部报销系统。员工提交报销单（金额/类别/日期/发票截图/备注）→ 主管审批（通过/驳回+理由）→ 员工查看自己状态列表 → 主管每月导出 CSV 给财务。

## 技术决策（写死，不留自由发挥空间）
- **框架**：Next.js 15（App Router），`create-next-app` 使用 `--src-dir --typescript --tailwind --app`，即代码在 `src/` 下。
- **ORM/DB**：Prisma 6.x + SQLite，数据库文件 `prisma/dev.db`（`DATABASE_URL="file:./dev.db"`），用 `npx prisma migrate dev` 管理 schema。
- **鉴权**：不接入 NextAuth 等三方库。自建邮箱白名单：`src/config/whitelist.ts` 导出 `WHITELIST: {email, name, role}[]`，`role` 为 `EMPLOYEE | MANAGER`。登录页输入邮箱 → 命中白名单则用 `iron-session` 或手写签名 cookie（`httpOnly, sameSite=lax`）保存 `{email, role, name}`，7 天过期。不做密码/魔法链接（内网工具，接受此风险，已写入 notes）。
- **样式**：Tailwind CSS v4（随 create-next-app 默认版本）。不引入完整组件库，只用少量自封装组件（Button/Input/Select/Badge/Table），统一视觉参数：
  - 容器：`max-w-3xl mx-auto p-6`
  - 圆角：按钮/输入框 `rounded-md`(6px)，卡片 `rounded-lg`(8px)
  - 主按钮：`h-10 px-4 bg-blue-600 text-white hover:bg-blue-700`
  - 状态徽章配色：PENDING=`bg-gray-100 text-gray-700`，APPROVED=`bg-green-100 text-green-700`，REJECTED=`bg-red-100 text-red-700`，均 `text-xs px-2 py-0.5 rounded-full`
  - 无过渡动画要求（内部工具，不做动效）
- **文件存储**：发票截图存本地磁盘 `public/uploads/{expenseId}/{filename}`，数据库仅存相对路径。限制：仅 `image/jpeg|image/png|image/webp`，单文件 ≤ 5MB，前后端双重校验。`public/uploads/` 加入 `.gitignore`。
- **报销类别**：固定枚举五选一 —— `交通 | 餐饮 | 住宿 | 办公用品 | 其他`。
- **报销状态**：`PENDING | APPROVED | REJECTED`。
- **部署**：单实例内网部署，不做多租户/横向扩展。SQLite 文件与 `public/uploads/` 需一并纳入定期备份（写入 notes，非本次开发范围）。

## Wave 划分与每 Wave 可演示成果
| Wave | Feature | 浏览器可见成果 |
|---|---|---|
| 1 | F1 | 打开站点被引导登录；白名单邮箱登录成功进入空的 `/expenses` 页 |
| 2 | F2, F3 | 员工能提交一张带发票图片的报销单，并在自己的列表里看到 PENDING 状态 |
| 3 | F4 | 主管在 `/approvals` 通过/驳回，员工列表里状态和驳回理由随之更新 |
| 4 | F5 | 主管在 `/export` 选月份下载 CSV，内容与已通过报销单一致 |

每个 wave 结束前必须能在浏览器里跑通对应闭环，不允许连续两个 wave 只有后端改动没有可见结果。

## Features（JSON）

```json
{
  "features": [
    {
      "id": "F1",
      "description": "项目脚手架 + Prisma 数据模型（User/Expense/Role/Status 枚举）+ 邮箱白名单登录鉴权（登录页、签名 cookie session、middleware 路由保护）",
      "passes": false,
      "acceptance": "1) 未登录访问 /expenses 或 /approvals 会被 middleware 重定向到 /login；2) 在 /login 输入 whitelist.ts 中存在的邮箱，提交后设置 httpOnly cookie 并跳转到 /expenses；3) 输入不在白名单中的邮箱，页面显示错误提示且不设置 cookie、不跳转；4) `npx prisma migrate dev` 能成功建出 User/Expense 表且无报错；5) cookie 中能解析出 email/name/role 三个字段供后续页面使用。",
      "wave": 1,
      "depends": [],
      "must_haves": {
        "artifacts": [
          {"path": "prisma/schema.prisma", "min_lines": 25, "contains": ["model User", "model Expense", "enum Role", "enum Status", "EMPLOYEE", "MANAGER"]},
          {"path": "src/lib/prisma.ts", "min_lines": 8, "exports": ["prisma"], "contains": ["PrismaClient"]},
          {"path": "src/config/whitelist.ts", "min_lines": 8, "exports": ["WHITELIST"], "contains": ["email", "role"]},
          {"path": "src/lib/auth.ts", "min_lines": 25, "exports": ["getSession", "createSessionCookie"], "contains": ["cookies\\(\\)", "WHITELIST"]},
          {"path": "src/middleware.ts", "min_lines": 15, "contains": ["matcher", "login"]},
          {"path": "src/app/login/page.tsx", "min_lines": 20, "contains": ["email"]},
          {"path": "src/app/api/login/route.ts", "min_lines": 15, "exports": ["POST"], "contains": ["WHITELIST", "cookies"]}
        ],
        "key_links": [
          {"pattern": "fetch\\(['\"]\\/api\\/login|action=.*api/login", "in": "src/app/login/page.tsx"},
          {"pattern": "getSession|cookies\\(\\)", "in": "src/middleware.ts"}
        ]
      },
      "notes": "Next.js 15 中 cookies()/headers() 是 async API，必须 await；middleware 里不能直接用 next/headers 的 cookies()，要用 NextRequest.cookies。Session 用手写 HMAC 签名 cookie 即可（如用 crypto.createHmac 签 email+role+过期时间），避免引入 next-auth 增加复杂度。白名单邮箱大小写需统一转小写比较，避免同事输入大写邮箱登录失败。这是内部 8 人工具，接受无密码登录的安全取舍，但仍需在 README 里写明该限制。"
    },
    {
      "id": "F2",
      "description": "员工提交报销单表单：金额、类别（五选一枚举）、日期、发票截图上传（≤5MB，jpg/png/webp）、备注，提交后写入 Expense 表 status=PENDING",
      "passes": false,
      "acceptance": "登录员工在 /expenses/new 填写金额(必填,>0)/类别(下拉五选一)/日期(必填,不能晚于今天)/备注(选填,≤500字)/发票图片(必填)，提交后：1) public/uploads/{expenseId}/ 下生成对应图片文件；2) 数据库新增 Expense 记录，submitterId 为当前登录用户，status=PENDING；3) 页面跳转到 /expenses 且新记录可见；4) 上传非图片文件或超过5MB时，前端表单直接阻止提交并显示错误文案，不发起请求；5) 后端 API 对文件类型/大小做二次校验，拒绝非法请求并返回 400。",
      "wave": 2,
      "depends": ["F1"],
      "must_haves": {
        "artifacts": [
          {"path": "src/app/expenses/new/page.tsx", "min_lines": 60, "contains": ["amount", "category", "date", "note", "type=\"file\"", "交通|餐饮|住宿|办公用品|其他"]},
          {"path": "src/app/api/expenses/route.ts", "min_lines": 40, "exports": ["POST", "GET"], "contains": ["formData", "prisma.expense.create", "image/jpeg|image/png|image/webp"]},
          {"path": "src/lib/upload.ts", "min_lines": 15, "exports": ["saveReceiptFile"], "contains": ["writeFile|fs\\."]}
        ],
        "key_links": [
          {"pattern": "fetch\\(['\"]\\/api\\/expenses['\"],\\s*\\{[^}]*method:\\s*['\"]POST", "in": "src/app/expenses/new/page.tsx"}
        ]
      },
      "notes": "Next.js 15 Server Actions 默认 body 上传限制约 1MB，会导致图片上传失败；改用 Route Handler（app/api/expenses/route.ts, export const runtime='nodejs'）配合浏览器端 FormData 提交，避免该限制。文件名需做 sanitize（去掉路径分隔符/特殊字符），防止路径穿越写文件。日期字段前端用 <input type=\"date\">，服务端存 UTC 零点，避免时区导致月份归属错乱（影响后续 F5 导出）。"
    },
    {
      "id": "F3",
      "description": "员工端「我的报销单」列表页：展示当前登录用户提交的所有报销单及状态（含驳回理由）",
      "passes": false,
      "acceptance": "登录员工访问 /expenses，只能看到 submitterId 等于自己的记录（不能看到他人的），列表按创建时间倒序，每行展示 金额/类别/日期/状态徽章/备注；status=REJECTED 的行额外展示驳回理由文本；无记录时显示空状态文案“暂无报销记录”；页面提供跳转到 /expenses/new 的入口按钮。",
      "wave": 2,
      "depends": ["F1"],
      "must_haves": {
        "artifacts": [
          {"path": "src/app/expenses/page.tsx", "min_lines": 40, "contains": ["PENDING", "APPROVED", "REJECTED", "rejectReason"]}
        ],
        "key_links": [
          {"pattern": "prisma\\.expense\\.findMany\\(\\{[^}]*submitterId", "in": "src/app/expenses/page.tsx"}
        ]
      },
      "notes": "此页与 F2 的列表查询共用 GET /api/expenses，但必须带 submitterId 过滤，避免员工看到他人报销单；manager 角色不应从此页面看到全部数据（全部数据是 F4 的职责）。状态徽章配色沿用总览中的量化色值：PENDING灰/APPROVED绿/REJECTED红。"
    },
    {
      "id": "F4",
      "description": "主管待审批队列页：仅 MANAGER 角色可访问，列出所有 PENDING 报销单，支持通过/驳回（驳回必须填写理由）",
      "passes": false,
      "acceptance": "1) role=EMPLOYEE 用户访问 /approvals 返回 403 或重定向，不显示任何数据；2) role=MANAGER 访问 /approvals 看到所有 status=PENDING 的报销单（含提交人姓名/金额/类别/日期/备注/发票图片预览链接），按提交时间正序；3) 点击“通过”后该记录 status 变为 APPROVED，队列中消失，员工在 /expenses 能看到状态变为 APPROVED；4) 点击“驳回”弹出理由输入框，理由为空时前端阻止提交、后端也返回 400 校验失败；理由非空提交后 status 变为 REJECTED 并保存 rejectReason，员工在 /expenses 能看到 REJECTED 状态和该理由文本。",
      "wave": 3,
      "depends": ["F2", "F3"],
      "must_haves": {
        "artifacts": [
          {"path": "src/app/approvals/page.tsx", "min_lines": 40, "contains": ["PENDING", "MANAGER", "驳回|reject"]},
          {"path": "src/app/api/expenses/[id]/route.ts", "min_lines": 30, "exports": ["PATCH"], "contains": ["APPROVED", "REJECTED", "rejectReason"]}
        ],
        "key_links": [
          {"pattern": "fetch\\(['\"]\\/api\\/expenses\\/.*['\"],\\s*\\{[^}]*method:\\s*['\"]PATCH", "in": "src/app/approvals/page.tsx"}
        ]
      },
      "notes": "角色校验必须在服务端（page.tsx 顶部或对应 API 里读取 session.role）做，不能只在前端隐藏入口。驳回理由长度建议限制 ≤300 字并在前后端都校验非空（trim 后长度>0）。审批操作要记录 approverEmail/approvedAt 字段，方便日后追溯和 F5 导出使用（若 F1 schema 未预留，此 wave 需要 prisma migrate 追加字段）。"
    },
    {
      "id": "F5",
      "description": "主管端每月 CSV 导出页：选择月份，导出该月所有已通过（APPROVED）报销单给财务",
      "passes": false,
      "acceptance": "1) role=EMPLOYEE 访问 /export 返回 403；2) role=MANAGER 在 /export 用 <input type=\"month\"> 选择如 2026-07，点击导出按钮触发文件下载；3) 下载文件名格式 expenses-2026-07.csv，UTF-8 with BOM 编码（Excel 中文不乱码）；4) CSV 列顺序为：提交人,金额,类别,日期,状态,备注,审批人,审批时间,驳回理由；5) 内容仅包含该月（按报销日期 date 字段所在自然月）且 status=APPROVED 的记录，按日期升序排列；6) 备注/理由字段中如含英文逗号或双引号，按 CSV 规范转义，Excel 打开不错列。",
      "wave": 4,
      "depends": ["F4"],
      "must_haves": {
        "artifacts": [
          {"path": "src/app/export/page.tsx", "min_lines": 25, "contains": ["month", "input"]},
          {"path": "src/app/api/export/route.ts", "min_lines": 30, "exports": ["GET"], "contains": ["APPROVED", "Content-Disposition", "text/csv"]}
        ],
        "key_links": [
          {"pattern": "\\/api\\/export\\?month=", "in": "src/app/export/page.tsx"}
        ]
      },
      "notes": "月份筛选要用 F2 里存的 UTC 零点日期做区间查询（[月初, 下月初)），避免时区偏移导致 7/31 或 8/1 的记录被错误归月。CSV 生成建议手写简单 escape 函数（字段含 , \" \\n 时用双引号包裹并把内部双引号转义为两个双引号），不必引入第三方 csv 库。响应头需设置 Content-Type: text/csv; charset=utf-8 和 Content-Disposition: attachment; filename=... 才能触发浏览器下载而非跳转打开。"
    }
  ]
}
```

## 遗留风险 / 非本次范围（写在这里避免遗忘）
- 无密码登录、无 HTTPS 强制、无审计日志——内部 8 人工具的既定取舍，若后续接第三方或扩大团队需重新评估。
- SQLite 单文件 + 本地磁盘图片，未做异地备份，建议部署后配置定时 `cp` 备份 `prisma/dev.db` 和 `public/uploads/`。
- 未做报销单编辑/撤回功能（需求未提及，故不在本 plan 内，如后续需要应作为新 feature 补充，depends F2）。
