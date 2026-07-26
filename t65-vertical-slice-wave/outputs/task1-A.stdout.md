已创建 `task_plan.md`，共 11 个 feature、6 个 wave：

- **Wave 1-3**：项目骨架 → Prisma schema/seed → 邮箱白名单登录（严格串行，后面一切都依赖它们）
- **Wave 4**（可并行 3 个 agent）：文件上传、导航壳+StatusBadge、数据访问层 `lib/expenses.ts`
- **Wave 5**（可并行 4 个 agent）：提交表单、我的报销单列表、审批队列、CSV 导出——各自独立文件，互不冲突
- **Wave 6**：部署文档 + 端到端验收

已写死的关键决策（避免编码 agent 自由发挥）：
- Server Actions 做数据变更，Route Handler 仅用于上传/导出
- SQLite 不支持原生 enum，category/status 用 String + zod 校验（已知坑，写进 notes）
- 金额用 `amountCents` 整数存储，避免浮点误差
- 手写 JWT(jose)+httpOnly cookie 鉴权，而非 next-auth
- 发票文件存 `UPLOAD_DIR`（非 public），需登录才能读取
- CSV 加 UTF-8 BOM 防止 Excel 中文乱码，月份按 Asia/Shanghai 时区计算边界
- 每个 UI feature 都给了具体的颜色值/圆角/间距（如 StatusBadge 三态配色、导航栏高度 56px）

每个 feature 的 `must_haves.artifacts` 都指定了文件路径、最小行数、必须导出的函数名、必须包含的关键字符串，`key_links` 校验了跨文件的调用关系，可以直接反向验收。
