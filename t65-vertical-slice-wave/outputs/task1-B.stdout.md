已生成 `task_plan.md`，共 5 个 features、4 个 wave，按垂直闭环切分：

- **Wave 1 (F1)**：脚手架 + Prisma 模型 + 邮箱白名单登录，浏览器可见「登录→进空列表页」
- **Wave 2 (F2+F3，可并行)**：提交报销单（含发票上传）+ 我的状态列表，浏览器可见「提交→自己列表里看到 PENDING」
- **Wave 3 (F4)**：主管审批队列，浏览器可见「通过/驳回→员工列表状态联动」
- **Wave 4 (F5)**：月度 CSV 导出，浏览器可见「选月份→下载 CSV」

技术决策全部写死（Next.js 15 src-dir、Prisma+SQLite 路径、手写签名 cookie 鉴权而非 next-auth、Tailwind 视觉参数、发票文件限制、CSV 编码/转义规则），已知坑点（Next 15 async cookies()、Server Action 上传体积限制、时区导致月份归属错乱等）都写进各 feature 的 `notes`。文件末尾还列了"遗留风险/非本次范围"，避免编码 agent 擅自扩展。

可以直接交给编码 agent 按 wave 顺序执行了。
