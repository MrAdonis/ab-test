# 评审结论

## 评分总表（10 分制）

| 维度 | 方案甲 | 方案乙 | 说明 |
|---|---|---|---|
| 1. 方向性错误最早暴露点 | **8** | **4** | 甲在 wave2/4（50% 进度）跑通"提交→我的列表"；乙要到 wave5/6（83%）才第一次看见报销单长什么样 |
| 2. 每 wave 可演示结果 | **9** | **4** | 甲 4 个 wave 全有浏览器闭环并写死了这条纪律；乙 wave2（schema）、wave4（上传 API + 指向 404 的导航）基本不可见 |
| 3. 可并行执行性 | **6** | **7** | 乙 wave4/wave5 的 fan-out 更宽且文件不冲突；但 wave1-3 三个单 feature wave 过度串行，屏障多。甲串行度高，且 wave2 内部有措辞矛盾 |
| 4. 约束完整性与零歧义 | **7** | **8** | 甲的视觉/CSV/时区参数更细，但踩了 SQLite enum 硬伤且漏了金额类型；乙技术决策更准，但有两处 acceptance 不可判定 |
| 5. 总体交付风险 | **8** | **6** | 甲风险在早期且易修；乙风险集中在 wave5 一次性集成四个 UI，且 F6 的 API 契约在此之前从未被 UI 验证过 |
| **总分（50）** | **38** | **29** | |

## 各方案的硬伤（不是风格问题，是会阻塞的）

**方案甲**

1. **`enum Role` / `enum Status` 在 SQLite 上跑不起来。** Prisma 至今不支持 SQLite connector 的字段级 enum，`migrate dev` 会直接报错。而 F1 的 must_haves 强制 `contains: ["enum Role", "enum Status"]`，与它自己 acceptance 第 4 条"migrate 成功"直接冲突——编码 agent 会陷在"满足产物检查"和"满足验收"之间。乙恰好明确点出了这个坑。
2. **发票图存在 `public/uploads/`**，等于任何拿到 URL 的人（含未登录）都能看别人的报销发票。乙把它移出 public 并加了鉴权流式读取，是对的。
3. **没有 seed，也没有 User 记录的创建路径。** 白名单在 `config/whitelist.ts`，但 `Expense.submitterId` 指向 User 表，session 里只有 email/role/name——登录时 upsert User 这一步全 plan 没有任何地方规定。同时因为没有 seed，F3 的验收条"不能看到他人的记录"在 wave2 根本无法验证（库里只有一个人的数据）。
4. **金额存储类型未定**（乙明确 `amountCents: Int`）。报销工具用 Float 存钱是会出事的。
5. F4 notes 自认"若 F1 schema 未预留 approverEmail/approvedAt，此 wave 需要追加 migrate"——已知返工，应该直接在 F1 补全。
6. F3 的 notes 说"与 F2 共用 GET /api/expenses"，但它的 key_links 又要求 page.tsx 里直接 `prisma.expense.findMany`。二选一，否则 F2 的 GET 是死代码。
7. 全 plan 没有 README/部署 feature，只在 notes 里说"要写"。

**方案乙**

1. **结构性问题：前 4 个 wave（约 2/3 的工作量）没有任何业务可见结果。** 如果"报销单该有哪些字段""审批要不要多级""导出给财务的口径"理解偏了，要到 wave5 才发现，而那时 schema、DAL、上传、导航全已建成。这是交付顾问视角下最贵的失败模式。
2. **F10 的验收不可判定：** "行数与数据库该月记录数一致"——没说只导 APPROVED。给财务的月度导出到底含不含 PENDING/REJECTED，这是需求核心口径，plan 里悬空了。甲明确写死"仅 APPROVED"。
3. **middleware 里 `getSession` 的坑没警告。** 乙的 key_links 强制 `middleware.ts` 里出现 `getSession`，而同一个 `getSession` 又要被 Nav.tsx（Server Component，用 `next/headers`）调用——middleware 只能用 `NextRequest.cookies`。甲的 F1 notes 明确警告了这一点，乙反而把这个易错连接写成了硬性检查项。
4. `listExpensesByMonth` 没说按 `date` 还是 `createdAt` 归月；CATEGORY 里 TRAVEL 与 TRANSPORT 语义重叠却没有"住宿"；`prisma db seed` 需要的 package.json seed 配置没进任何 must_haves。
5. F7 锁死的两步上传会产生孤儿文件（传完不提交），无清理机制。

## 选哪份

**选方案甲**，但必须先打补丁。

一句话理由：**两份的工程判断力差不多，但甲每个 wave 都能让人在浏览器里看见东西、方向性错误在半程就会暴露，而乙要到 83% 进度才第一次显形——对 8 人内部工具来说，返工成本比技术优雅重要得多。**

## 交给编码 agent 前必须做的 6 处修改（把乙的优点移植进甲）

1. F1 schema：`enum Role/Status` → `String` + 应用层常量校验；相应改掉 must_haves 的 contains。
2. F1 schema 一次性补全 `approverEmail`、`approvedAt`、`rejectReason`，消除 F4 的已知返工。
3. 金额字段改为 `amountCents Int`，对外用元（2 位小数）。
4. 上传目录移出 `public/`，改为 `UPLOAD_DIR` + `/api/uploads/[id]` 鉴权后流式返回。
5. F1 增加 seed（8 个白名单用户，含 ≥1 个 MANAGER，其中至少 2 个员工各有 1 条报销单），并明确"登录时按 email upsert User"。否则 wave2 的越权验收无法执行。
6. 追加一个 wave5 收尾 feature：README（部署/备份/白名单增删）+ 端到端手动验收清单——直接抄乙的 F11。

补完之后甲大约能到 45/50。
