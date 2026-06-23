# 被硬化的方案：users 表增加 plan 字段做功能分级

---

## 收敛过程

### 第 1 轮：列举漏洞

**V1｜已付费用户丢失 pro 状态**
- 什么会坏：migration 把 plan 列默认值设为 `free`，已付费用户全部降级。
- 什么条件下坏：任何付费用户登录，立即出现功能降级（所有 pro 功能消失）。
- 【假设标注】推断现有库里"付过费"可通过某张表（orders / subscriptions / payments）识别，但原方案没说。

**V2｜前端可绕过访问控制**
- 什么会坏：前端隐藏 UI 不是真正的访问控制，API 端点依然可被调用。
- 什么条件下坏：free 用户直接构造 API 请求即可使用 pro 功能，任何时候都可绕过。

**V3｜migration 在 5 万行表上加列是否无锁**
- 什么会坏：直接 `ALTER TABLE ADD COLUMN ... DEFAULT 'free'` 在 MySQL（< 8.0）或旧版 PostgreSQL 上会全表锁；5 万行量级可能几秒内完成，但与并发写冲突时会造成写阻塞。
- 什么条件下坏：高峰期上线；注册、登录等写操作在 migration 执行期间阻塞。
- 【假设标注】推断数据库为 PostgreSQL 或 MySQL；未读代码，仅凭数量级估算锁时间。

**V4｜枚举值约束未写**
- 什么会坏：plan 列若只加为 varchar，应用层 bug 或手动 SQL 可写入非法值（如 `premium`、空字符串、NULL）。
- 什么条件下坏：前端条件判断 `user.plan === 'pro'` 遇到非预期值静默失败，表现为功能随机消失或不稳定。

**V5｜回滚困难**
- 什么会坏：migration 上线后，若需回滚（发现迁移数据错误或字段设计有误），`DROP COLUMN` 会永久丢失已写入的 plan 数据。
- 什么条件下坏：上线后 1 小时内发现已付费用户数据迁移有误；想回滚，但 rollback migration 会擦除所有 plan 值，需要重新推断。

**V6｜并发迁移与双写窗口**
- 什么会坏：部署过程中新旧代码同时运行（rolling deploy），旧代码不写 plan 字段，新代码读 plan 字段——读到 NULL。
- 什么条件下坏：rolling deploy 期间约数分钟内，新代码实例对未经迁移的已有 session 读到 `plan = NULL`，可能报错或错误降级。

**V7｜plan 升级 / 降级的写入路径未定义**
- 什么会坏：方案只定义了"加字段"和"前端展示"，没说谁在何时写 plan 的值。用户付费成功后，plan 如何变成 `pro`？退款后如何变回 `free`？
- 什么条件下坏：付费流程完成后用户刷新仍看到 free 界面；或退款后用户依然是 pro——取决于有没有 webhook/job 更新这个字段。

---

### 第 1 轮：修复或接受

**V1 → 修复**：migration 分两步走：Step 1 仅 `ADD COLUMN plan VARCHAR(10) NOT NULL DEFAULT 'free' CHECK (plan IN ('free','pro'))`；Step 2 紧接一条 `UPDATE users SET plan = 'pro' WHERE id IN (SELECT DISTINCT user_id FROM <付费表> WHERE status = 'active')`。Step 2 必须在 Step 1 的同一事务或同一部署批次内完成，不允许中间态对外暴露。

**V2 → 修复**：在 API 中间件层（而非仅前端）加 plan 检查：所有 pro 端点在服务端校验 `req.user.plan === 'pro'`，否则返回 403。前端隐藏仅为 UX，不作为安全边界。

**V3 → 接受的风险**：5 万行在 PostgreSQL 11+ 上 `ADD COLUMN ... DEFAULT` 为即时操作（不重写行），锁时间微秒级；MySQL 8.0+ instant algorithm 同理。若确认数据库版本符合，可接受。若版本不确认，在低峰期上线并提前测试。【注：此处是假设，需在执行前核实数据库版本。】

**V4 → 修复**：migration 中加 `CHECK (plan IN ('free', 'pro'))` 约束（PostgreSQL）或应用层 enum 校验（MySQL 可用 ENUM 类型）。同时在 ORM model 层也加枚举校验，做双重防守。

**V5 → 修复**：rollback migration 脚本不直接 `DROP COLUMN`，而是先把 plan 值 dump 到一张临时表 `users_plan_backup (user_id, plan, backed_up_at)`，再 DROP。回滚时从备份表恢复。备份写入与主 migration 在同一事务中完成。

**V6 → 修复**：给 plan 列设 `DEFAULT 'free'`（Step 1 已做），保证 NULL 不出现。新代码在读取 plan 时加一层 fallback：`const plan = user.plan ?? 'free'`，防止 NULL 穿透到业务逻辑。rolling deploy 期间影响降为：新用户和未付费旧用户看到 free（正确）；已付费用户在 Step 2 完成前约数秒内也显示 free（短暂降级）——这个窗口可通过把 Step 2 放在代码部署之前执行来消除。

**V7 → 修复**：方案必须明确写入路径：付费成功 webhook → 写 `plan = 'pro'`；退款/订阅到期 → 写 `plan = 'free'`。这不是新功能扩张，是本方案能正确工作的必要条件。方案中需包含这两条写入路径的规格。

---

### 第 2 轮：重查

修复后检查是否引入新漏洞：

**NV1｜Step 2 的付费表关联查询范围**：`SELECT DISTINCT user_id FROM <付费表> WHERE status = 'active'` 依赖"付费表名"和"active 状态定义"——若原系统里退款订单也是 active，会把已退款用户迁成 pro。
- 修复：查询条件改为 `WHERE status = 'active' AND refunded_at IS NULL AND expires_at > NOW()`（或根据实际表结构调整），并在 staging 先跑一遍，人工核对迁移结果数量是否合理。

**NV2｜备份表 users_plan_backup 的安全性**：备份表包含用户 ID 和付费状态，属于敏感数据，若长期留存且访问控制不当会成为信息泄露风险。
- 接受的风险：备份表仅在回滚窗口（上线后 72 小时内）保留，过期后由 DBA 手动删除或写一条定时清理任务。回滚窗口内它就在同一数据库里，访问权限与 users 表相同，不新增暴露面。

**NV3｜webhook 写入 plan 字段与 migration 的时序**：如果付费 webhook 在 migration 执行前到达，plan 列不存在，webhook handler 会报错。
- 修复：webhook handler 对"plan 列不存在"的情况有显式错误处理（捕获 column does not exist 错误，写入死信队列，migration 完成后重放）；或确保 migration 先于任何代码部署执行（migration first 部署顺序）。

第 2 轮无进一步实质性新漏洞（NV2 为可接受风险，NV1/NV3 已修复）。

---

### 第 3 轮：重查

NV1 的修复（加查询条件）引入了一个微小依赖：需要知道实际表结构。这是一个**执行前必须确认的假设**，不是新的设计漏洞。方案中已标注"根据实际表结构调整"，不构成新一轮循环的入口。

收敛完成。

---

## 关闭的漏洞

| 条件 | 修复 |
|------|------|
| migration 默认值把已付费用户降为 free | 同一部署批次内紧跟一条 UPDATE，从付费表筛出 active 用户写 `plan='pro'`；UPDATE 先于代码上线执行 |
| 前端隐藏可被绕过，API 无访问控制 | 所有 pro 端点在服务端中间件校验 `user.plan === 'pro'`，否则 403 |
| plan 列无值约束，非法值静默穿透 | migration 加 CHECK 约束；ORM model 加枚举校验；读取时 fallback `?? 'free'` |
| rollback 会擦除迁移数据 | rollback 前先把 plan 值备份到临时表 `users_plan_backup`，回滚后可恢复 |
| rolling deploy 期间新代码读到 NULL | DEFAULT 'free' 保证无 NULL；新代码加 `?? 'free'` fallback；Step 2 UPDATE 先于代码上线 |
| 付费/退款后 plan 字段无人更新 | 方案规格包含：付费 webhook → `plan='pro'`；退款/到期 → `plan='free'` 两条写入路径 |
| 付费表查询条件可能把退款用户迁成 pro | 查询加 `refunded_at IS NULL AND expires_at > NOW()`；staging 先跑并人工核对迁移数量 |
| webhook 在 migration 前到达导致 handler 报错 | 采用 migration first 部署顺序；或 webhook handler 捕获列不存在错误写死信队列，migration 后重放 |

---

## 接受的风险

| 条件 | 为何可接受 |
|------|-----------|
| 5 万行表加列的锁时间 | PostgreSQL 11+/MySQL 8.0+ instant ADD COLUMN，锁微秒级；需在执行前核实版本。若版本不符，低峰期上线可将影响控制在可接受范围内 |
| users_plan_backup 临时表的数据留存 | 仅在 72 小时回滚窗口内保留，与 users 表同权限，不新增暴露面；窗口关闭后删除 |

---

## 最终方案（可直接执行的规格）

### 目标

给 `users` 表加 `plan` 字段（取值 `free` / `pro`），用于服务端功能分级。5 万存量用户中付过费的迁移为 `pro`，其余为 `free`。

---

### 数据库层

**Migration 脚本（单次事务，migration first）：**

```sql
BEGIN;

-- 1. 备份现有 plan 状态（此时列不存在，仅记录付费用户 ID）
CREATE TABLE IF NOT EXISTS users_plan_backup (
  user_id BIGINT NOT NULL,
  plan VARCHAR(10) NOT NULL,
  backed_up_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO users_plan_backup (user_id, plan)
SELECT DISTINCT user_id, 'pro'
FROM <付费表>                        -- 替换为实际表名，如 subscriptions / orders
WHERE status = 'active'
  AND refunded_at IS NULL
  AND expires_at > NOW();            -- 根据实际表结构调整字段名

-- 2. 加列，默认 free，加 CHECK 约束
ALTER TABLE users
  ADD COLUMN plan VARCHAR(10) NOT NULL DEFAULT 'free'
  CHECK (plan IN ('free', 'pro'));

-- 3. 把付费用户迁为 pro（JOIN 备份表，避免重复查付费表）
UPDATE users u
SET plan = 'pro'
FROM users_plan_backup b
WHERE u.id = b.user_id;

COMMIT;
```

**执行前检查清单：**
1. 确认数据库版本（PostgreSQL ≥ 11 或 MySQL ≥ 8.0），验证 instant ADD COLUMN 可用。
2. 在 staging 环境跑一遍，核对 `SELECT COUNT(*) FROM users WHERE plan = 'pro'` 数量是否与业务预期一致。
3. 确认 `<付费表>` 表名和字段名（status / refunded_at / expires_at）与实际 schema 匹配。

**回滚方案：**
```sql
-- 回滚时（72 小时内）
ALTER TABLE users DROP COLUMN plan;
-- plan 数据已在 users_plan_backup，重建列后可从中恢复
-- 72 小时后清理备份表：DROP TABLE users_plan_backup;
```

---

### 部署顺序

1. **先跑 migration**（migration first），在任何新代码上线前完成。
2. **再部署新代码**（API + 前端）。
3. 部署期间若 webhook 到达，handler 已包含死信队列处理（见下）。

---

### API 层（服务端访问控制）

所有 pro 端点必须在中间件层校验，不依赖前端隐藏：

```typescript
// middleware/requirePro.ts
export function requirePro(req, res, next) {
  const plan = req.user?.plan ?? 'free';   // fallback 防 NULL
  if (plan !== 'pro') {
    return res.status(403).json({ error: 'pro_required' });
  }
  next();
}

// 用法：在路由上挂载
router.get('/api/pro-feature', requirePro, proFeatureHandler);
```

---

### 应用层 model 校验

在 User model（ORM）中加枚举约束，防止非法值写入：

```typescript
// 以 Prisma 为例
model User {
  id   Int    @id
  plan Plan   @default(free)
  // ...
}

enum Plan {
  free
  pro
}
```

若使用其他 ORM，在 model 层加 `enum` 或 `validator`，确保写入时只接受 `'free'` 或 `'pro'`。

---

### plan 字段的写入路径

付费和退款的 plan 更新必须显式实现，不能依赖 migration 一次性写入后永不更新：

**付费成功（webhook handler）：**
```typescript
async function onPaymentSuccess(userId: number) {
  await db.users.update({
    where: { id: userId },
    data: { plan: 'pro' },
  });
}
```

**退款 / 订阅到期（webhook handler 或 cron job）：**
```typescript
async function onSubscriptionExpiredOrRefunded(userId: number) {
  await db.users.update({
    where: { id: userId },
    data: { plan: 'free' },
  });
}
```

**webhook handler 容错（migration first 部署期间保护）：**
```typescript
try {
  await onPaymentSuccess(userId);
} catch (err) {
  if (err.message?.includes('column') && err.message?.includes('plan')) {
    // migration 尚未完成，写入死信队列，migration 后重放
    await deadLetterQueue.push({ type: 'set_pro', userId });
  } else {
    throw err;
  }
}
```

---

### 前端展示

前端根据 `user.plan` 控制 UI 可见性，仅作 UX 用途，不作安全边界：

```typescript
const isPro = (user.plan ?? 'free') === 'pro';

// 隐藏 pro 功能入口
{isPro && <ProFeatureButton />}
```

---

### 上线验收检查

1. `SELECT COUNT(*) FROM users WHERE plan = 'pro'` 数量与付费用户预期数量一致。
2. 抽查 3-5 个已知付费用户，确认 `plan = 'pro'`。
3. 抽查 3-5 个已知免费用户，确认 `plan = 'free'`。
4. 用 free 用户 token 直接调用 pro API 端点，确认返回 403。
5. 用 pro 用户 token 调用 pro API 端点，确认正常返回。
6. 查 `users_plan_backup` 表存在，确认可用于回滚。
7. 72 小时后：`DROP TABLE users_plan_backup`（或写定时任务）。

---

## 迭代数

**3 轮收敛**（第 1 轮发现 7 条漏洞并修复；第 2 轮发现 3 条新漏洞并修复/接受；第 3 轮确认无新漏洞，停止）。
