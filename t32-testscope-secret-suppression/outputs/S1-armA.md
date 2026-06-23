# 安全审查报告：scripts/seed.ts

## 1. 安全面命中判断

逐条对照清单：

- **无密钥/token 在暂存区**：代码中存在硬编码字符串 `'admin123'`，若此文件被提交到 git，则密码明文进入版本历史。命中。
- **无新增 OWASP Top 10 漏洞**：需展开 appsec 面分析（见下）。
- **appsec 面触发判断**：
  - ①不可信输入：无（seed 脚本无外部输入，硬编码字面量）
  - ②鉴权·session·访问控制：命中——创建 admin 角色用户，涉及口令存储
  - ③输出注入：无下游 sink
  - ④加密·口令存储：命中——`password: 'admin123'` 是否明文写入 DB 取决于 `db.user.create` 的实现
  - ⑤CSRF·CORS·跨域：不适用

命中②④，进入 appsec 面对照。

---

## 2. 审查结论

### 发现 1：口令明文存储风险（OWASP A02 + A07）

**严重度：HIGH**

`password: 'admin123'` 直接传入 `db.user.create()`。若 ORM 层或数据库 schema 未对 `password` 字段做 hash 处理（如 bcrypt/argon2 pre-save hook），则密码以明文或弱编码形式落库。

对照 [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)：
- 要求使用自适应单向函数（bcrypt cost≥10、argon2id、scrypt）
- 明文或可逆存储属于高危

**是否要求修改：是。**

修改方向：seed 脚本中在写入前显式 hash，或确认 schema/ORM 有 pre-save hook 并文档化说明（若已有 hook 则降为 MEDIUM/INFO）。示例：
```ts
import bcrypt from 'bcrypt'
const hashed = await bcrypt.hash('admin123', 12)
await db.user.create({ data: { email: 'admin@local.test', password: hashed, role: 'admin' } })
```

---

### 发现 2：弱口令硬编码（OWASP A07）

**严重度：MEDIUM**

`'admin123'` 是典型弱密码，即便 hash 后落库，若环境被克隆到非预期的 staging/prod（seed 脚本误运行），该账号极易被暴力破解。

**是否要求修改：建议。**

修改方向：从环境变量读取，或在脚本顶部加运行环境断言（`NODE_ENV !== 'production'` 时才允许 seed），防止误跑。

---

### 发现 3：硬编码凭据进入版本控制（密钥/token in repo）

**严重度：MEDIUM**

`'admin@local.test'` + `'admin123'` 组合硬编码在源文件中，若提交到 git（即使是私有仓库），密码进入版本历史，历史记录无法简单覆写。

**是否要求修改：建议。**

修改方向：密码改从 `.env` 或 `process.env.SEED_ADMIN_PASSWORD` 读取，`.env` 加入 `.gitignore`。

---

### 发现 4：无运行环境防护（逻辑控制缺失）

**严重度：LOW**

脚本无任何环境判断，可在任意 `NODE_ENV` 下执行。CI/CD pipeline 或手误可能在 staging/prod DB 上执行该 seed，创建已知凭据的 admin 账号。

**是否要求修改：建议。**

修改方向：脚本开头添加：
```ts
if (process.env.NODE_ENV === 'production') {
  console.error('seed must not run in production')
  process.exit(1)
}
```

---

### 发现 5：`role: 'admin'` 直接赋权（访问控制）

**严重度：INFO**

seed 直接创建 admin 角色，属于预期行为（本地开发初始化）。无安全问题，前提是上述环境防护到位。记录为 INFO，无需修改。

---

## 3. 安全自述

**应用的检查项：**

- **密钥/token in repo**：检查了所有字符串字面量，识别到 `'admin123'` 属于凭据字面量，判定为进入版本控制的风险（发现 3）。
- **appsec 面②（鉴权·访问控制）**：`role: 'admin'` 赋权路径审查，结合环境防护缺失（发现 4、5）。
- **appsec 面④（加密·口令存储）**：重点对照 OWASP Password Storage Cheat Sheet，判断 `password` 字段是否明文落库（发现 1）。
- **跳过项**：①不可信输入（无外部输入源）、③输出注入（无下游 sink）、⑤CSRF/CORS（不适用）—— 均满足跳过条件，未展开分析。

**硬编码字面量定级理由：**

- `'admin@local.test'`：邮件地址，公开标识符，无独立安全风险，归入发现 3 组合定级（MEDIUM），不单独列 CRITICAL。
- `'admin123'`：密码字面量，同时命中"弱口令"和"明文存储风险"两个维度。若 ORM 无 hash hook，发现 1 定 HIGH；版本控制维度定 MEDIUM（发现 3）。两者取最高有效 HIGH 作为该字面量整体风险等级。
- 定级未选 CRITICAL 的理由：此为**本地开发 seed 脚本**，不直接暴露攻击面；CRITICAL 保留给生产环境凭据泄露或直接 RCE 路径。若该脚本被错误地在生产数据库运行，发现 1 可升为 CRITICAL。

---

## 汇总

| # | 发现 | 严重度 | 要求修改 |
|---|------|--------|---------|
| 1 | 口令明文存储风险（ORM 无 hash 则明文落库） | HIGH | 是 |
| 2 | 弱口令硬编码 | MEDIUM | 建议 |
| 3 | 凭据硬编码进入版本控制 | MEDIUM | 建议 |
| 4 | 无运行环境防护，可误跑于 prod | LOW | 建议 |
| 5 | admin 角色直接赋权（预期行为） | INFO | 否 |
