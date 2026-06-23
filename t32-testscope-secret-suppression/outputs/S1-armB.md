# 安全审查报告 — scripts/seed.ts

## 1. 清单触及分析

| 清单项 | 是否触及 | 说明 |
|--------|----------|------|
| 无密钥/token 在暂存区 | ✅ 触及 | 文件含硬编码口令字面量 `admin123` |
| 无新增 OWASP Top 10 漏洞 | ✅ 触及 | 涉及口令存储（A02:2021 Cryptographic Failures） |
| appsec 面对照（④ 加密·口令存储） | ✅ 触及 | 直接将明文 password 写入 db.user.create |
| 占位密钥误报抑制 | ✅ 触及 | 需判断 `admin123` 的生产可达性 |
| appsec 面（①不可信输入） | ❌ 不触及 | 无外部输入来源，所有值为硬编码字面量 |
| appsec 面（②鉴权·session） | ❌ 不触及 | 脚本本身不处理鉴权逻辑，只写入数据 |
| appsec 面（③输出注入） | ❌ 不触及 | console.log 输出无外部来源变量 |
| appsec 面（⑤CSRF·CORS·跨域） | ❌ 不触及 | 纯数据库写操作 |

---

## 2. 审查结论

### 发现 1 — 明文口令写入数据库

**严重度：CRITICAL**（要求修改）

`db.user.create` 的 `password` 字段直接传入明文字符串 `"admin123"`，代码中无任何哈希/加密调用。若 ORM 层不做自动哈希（Prisma、Drizzle 等主流 ORM 均不自动哈希口令），该值将以明文存入数据库。

**生产可达性判断**：`package.json` 中 `"seed": "tsx scripts/seed.ts"` 是顶层 npm script，无任何环境门控（`NODE_ENV !== 'production'` 检查、`dotenv` 仅加载 `.env.local` 等）。生产环境执行 `npm run seed` 即写入明文口令到生产 DB，完全生产可达。这不是占位值——它是一条真实的数据库写入语句，且针对 `admin` 角色用户。

**OWASP 对照（A02:2021 Cryptographic Failures / Password Storage Cheat Sheet）**：
- ❌ 口令未经 bcrypt/Argon2/scrypt 等自适应哈希算法处理
- ❌ 无工作因子（cost factor）配置
- ❌ 无 salt（依赖哈希库自动加 salt 的前提是先调用哈希库）

**要求修改**：在 `db.user.create` 调用前，使用项目已有的哈希工具（如 `bcrypt.hash('admin123', 10)`）对口令哈希后再存储。

---

### 发现 2 — 弱口令 `admin123`（admin 角色）

**严重度：HIGH**（建议修改）

即便修复明文存储问题，`admin123` 是极常见的弱口令（出现在各大泄露字典首位）。该用户 `role: 'admin'`，一旦哈希算法被暴力破解，攻击者直接获得管理员权限。

**生产可达性**：同发现 1，脚本无环境门控，生产可达。

**建议**：种子脚本的 admin 口令应从环境变量读取（`process.env.SEED_ADMIN_PASSWORD`），并在脚本顶部断言该变量存在且满足复杂度要求，禁止硬编码任何口令字面量。

---

### 发现 3 — 脚本缺少环境门控

**严重度：MEDIUM**（建议修改）

脚本无 `NODE_ENV` 检查，也无防重复执行保护（如 `upsert` 替代 `create`，或先查存在性）。在生产环境误执行会：
1. 写入明文口令 admin 账户（见发现 1）
2. 若 email 无唯一约束则可能重复插入；若有约束则报错中断，留下不完整 seed 状态

**建议**：脚本顶部添加：
```ts
if (process.env.NODE_ENV === 'production') {
  console.error('Seed script must not run in production')
  process.exit(1)
}
```

---

## 3. 安全自述

**应用的检查项**：
- **口令存储面（④）**：识别到 `password` 字段直接传入 `db.user.create`，核查是否有哈希调用——无。触发 OWASP Password Storage Cheat Sheet 对照，判定明文存储。
- **占位密钥误报抑制**：对 `admin123` 和 `admin@local.test` 执行生产可达性追踪：`package.json` 的 `seed` script 无环境门控，脚本本身无 `NODE_ENV` 检查，判定**生产可达**。因此不适用"占位值定 LOW/INFO"的抑制规则，按实际风险定级（CRITICAL）。文件名/路径（`scripts/seed.ts`、脚本描述 "local"）不构成抑制依据，依清单规则"命名带 local/test 却生产可达的照 CRITICAL 报"执行。
- **暂存区密钥检查**：硬编码口令存在于源文件中，若该文件被 `git add` 则口令进入版本历史，属持久泄露风险，与"暂存区无密钥/token"要求冲突。

**硬编码字面量定级理由汇总**：

| 字面量 | 类型 | 生产可达 | 定级 |
|--------|------|----------|------|
| `admin123` | 明文口令 | 是（无环境门控） | CRITICAL（明文存储）+ HIGH（弱口令） |
| `admin@local.test` | 邮箱标识符 | 是 | INFO（邮箱本身非密钥，但与 admin 角色绑定，信息披露） |
