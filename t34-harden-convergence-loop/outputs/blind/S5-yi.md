# 方案压力测试与修订：users 表加 plan 字段

## 发现的漏洞与风险

**漏洞 1：历史付费用户数据丢失**

原方案"跑一条 migration 把列加上"没说默认值，5 万用户里已付费的那批会被默默标成 free（或 NULL），等于把他们的权益清零。这是最严重的问题，上线即产生客诉。

**漏洞 2：前端校验形同虚设**

"前端根据 user.plan 决定显示哪些功能"意味着 pro 保护只在渲染层。前端拿到 user.plan=free 不渲染按钮，但 API 端点没有守卫——任何人改一下请求参数或直接调接口就能访问 pro 功能。这是安全漏洞，不是 UX 问题。

**漏洞 3：migration 在 5 万行表上的锁风险**

ALTER TABLE 加列在主流数据库行为不同：PostgreSQL 加带 DEFAULT 的列在旧版本（<11）会全表重写，在新版本是即时操作但 DEFAULT 值是非 volatile 函数才行；MySQL/MariaDB 则加列通常需要重建表，5 万行虽然不大，但如果没估过执行时间，生产环境还是有短暂锁表风险。

**漏洞 4：plan 字段是个裸枚举，扩展性差**

free/pro 两个值用字符串存，没有约束。将来要加 enterprise、trial、grandfathered 等，每次都要 ALTER TABLE 改枚举或者约定字符串值，散落在代码各处的 if user.plan === 'pro' 会越来越难维护。

**漏洞 5：plan 字段和付费状态耦合不清楚**

plan 字段是当前状态快照，还是权益来源？如果用户订阅到期，谁负责把 plan 从 pro 改回 free？没有这个机制，过期用户会永久保留 pro 权限。

---

## 修订后的方案

### 第一步：摸清付费用户数据，再写 migration

上线前先出一条查询，把历史付费用户的 ID 列出来（从订单表、支付记录、或原有会员字段导出），确认数量和分布。migration 必须用这份数据做差异化初始化，不能全库默认 free。

```sql
-- migration 示意（PostgreSQL）
ALTER TABLE users ADD COLUMN plan VARCHAR(20) NOT NULL DEFAULT 'free';

-- 紧接着，根据已知付费用户批量更新
UPDATE users
SET plan = 'pro'
WHERE id IN (
  SELECT DISTINCT user_id FROM orders WHERE status = 'paid' AND expires_at > NOW()
);
```

这两步必须在同一个事务里，或者 migration 工具能保证原子执行。上线前用 staging 环境验证 pro 用户数量是否和预期一致。

### 第二步：服务端守卫必须先于前端隐藏上线

每个 pro 功能的 API 端点加鉴权中间件，在服务端读取 user.plan 做校验：

```typescript
// 示例中间件
function requirePro(req, res, next) {
  if (req.user.plan !== 'pro') {
    return res.status(403).json({ error: 'pro_required' });
  }
  next();
}

// 路由注册
router.post('/api/export', requirePro, exportHandler);
```

前端的功能隐藏只是体验层，服务端守卫才是安全边界。两者都要有，但服务端优先。

### 第三步：给 plan 字段加数据库约束

不要裸字符串，加 CHECK 约束或用枚举类型防止脏数据写入：

```sql
ALTER TABLE users
  ADD CONSTRAINT users_plan_check
  CHECK (plan IN ('free', 'pro'));
```

应用层所有读取 plan 的地方，用常量而不是字面字符串：

```typescript
const PLAN = { FREE: 'free', PRO: 'pro' } as const;
```

### 第四步：权益同步机制

plan 字段是快照，必须有机制让它和付费状态保持一致：

- 支付成功 webhook → 把对应用户 plan 改为 pro
- 订阅到期 → cron job 或 webhook 把 plan 改回 free
- 退款成功 → 立即降为 free

这个同步逻辑写在服务端，不依赖前端触发。建议在 users 表同时记录 plan_expires_at，cron 扫这个字段定期同步，而不是只依赖 webhook（webhook 会丢）。

### 第五步：migration 执行策略

5 万行不算大，但养成习惯：

1. 先在 staging 跑，记录执行时间
2. 生产在低峰期执行
3. 如果是 MySQL 且没有 online DDL，考虑用 pt-online-schema-change 或 gh-ost
4. PostgreSQL >= 11 加 NOT NULL 列带 DEFAULT 是 metadata-only 操作，风险极低，但仍要确认版本

---

## 修订后的上线顺序

1. 导出历史付费用户 ID 列表，确认数量
2. 写 migration（加列 + 批量更新 pro 用户），staging 验证
3. 服务端 pro 守卫中间件上线（此时前端还没改，守卫静默放行所有人也可以先空跑验证）
4. 生产跑 migration
5. 前端上线功能隐藏逻辑
6. 验证：用已知 pro 账号和 free 账号各走一遍 pro 功能，确认服务端 403 生效、前端 UI 差异符合预期
7. 接入订阅到期同步机制，验证降级流程
