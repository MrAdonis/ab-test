# 限量秒杀方案压力测试与修订

## 漏洞识别

### 漏洞 1：超卖——经典 TOCTOU 竞态条件

原方案：读 stock → 判断 >0 → 减 1。这三步不原子，10 万并发同时读到 stock=1，全都判断"有货"，全都下单，结果创建远超库存的订单。前端按钮禁用完全无法防止这种情况——按钮只拦住了同一用户的重复提交，对不同用户的并发毫无作用。

根因：`SELECT` 和 `UPDATE` 之间有时间窗口，多个事务同时读到相同的 stock 值。

### 漏洞 2：前端防重复提交不可信

按钮禁用在客户端，攻击者用 curl 或脚本可以绕过。即使是普通用户，网络抖动也可能导致请求重试。后端必须有幂等保证，不能依赖前端。

根因：前端状态不受后端控制。

### 漏洞 3：没有用户级别的重复下单防护

同一用户如果绕过前端（或者网络重试），后端没有任何阻止机制，会为同一用户创建多笔订单。

根因：POST /api/seckill 没有幂等键，也没有用户维度的限购检查。

### 漏洞 4：没有限流

几万人同时请求打到数据库，每个请求都执行事务。Postgres 在高并发下锁争用会急剧上升，连接池耗尽，响应时间飙升，甚至直接把数据库打挂。

根因：请求直接打穿到 DB，没有任何流量削峰。

### 漏洞 5：没有超时和事务失败处理

高并发下事务等锁可能超时，原方案没有说明失败时的行为。如果创建订单失败而 stock 已经被减掉（或者反过来），会导致数据不一致。

根因：没有明确的事务边界和回滚策略。

### 漏洞 6：stock 字段类型和边界

如果 stock 被多个服务同时修改，或者有手动调库存的后台操作，stock 可能出现负数。没有数据库层面的约束。

---

## 修订方案

### 核心修复：用数据库原子操作替代"读-判-写"三步

```sql
UPDATE products
SET stock = stock - 1
WHERE id = $1 AND stock > 0
RETURNING id, stock;
```

这条 SQL 原子执行"检查库存 >0 并减 1"。如果返回了行，说明扣减成功；如果没有返回行（`rowCount === 0`），说明库存已空。把这条 UPDATE 和 INSERT order 放在同一个事务里，保证原子性。

```sql
BEGIN;
  UPDATE products SET stock = stock - 1
  WHERE id = $1 AND stock > 0
  RETURNING id;   -- 没有返回行则 ROLLBACK 并返回 409

  INSERT INTO orders (user_id, product_id, created_at)
  VALUES ($2, $1, NOW());
COMMIT;
```

**数据库层加约束，兜底防负数：**
```sql
ALTER TABLE products ADD CONSTRAINT stock_non_negative CHECK (stock >= 0);
```

这样即使上层逻辑有 bug，数据库也会拒绝写入，不会出现 stock=-5 的情况。

### 修复用户重复下单：唯一约束 + 幂等键

```sql
-- 方案 A：同一用户同一活动只能有一个成功订单
ALTER TABLE orders ADD CONSTRAINT uq_user_product_seckill
  UNIQUE (user_id, product_id, activity_id);
```

后端捕获 unique violation（Postgres error code 23505），返回 409 而不是 500。这样无论用户发多少次请求，数据库只会记录一笔，天然幂等。

如果需要更细粒度的幂等控制（比如允许用户参加多次但每次活动只能一次），可以在 INSERT 时携带前端生成的 `idempotency_key`，后端检查是否已处理过。

### 修复流量问题：请求队列 + 连接池配置

秒杀这类场景，几万请求同时打来，Postgres 连接数默认上限 100，瞬间耗尽。需要两层防护：

**第一层：限流（在应用层或网关层）**

用 Redis 做令牌桶或漏桶限流。活动开始后每秒只放通固定数量的请求进入 DB 事务，其余直接返回"排队中"或 429。

```
GET /api/seckill-queue  ← 用户排队，获得队列 token
POST /api/seckill       ← 凭 token 下单（token 有短暂有效期）
```

**第二层：连接池调优**

pg 连接池 `max` 根据 Postgres 实际能扛的并发事务数设置（通常 20-50），不是越大越好。超出连接池的请求在应用层等待，避免 DB 连接数爆炸。

### 完整的后端处理流程

```
POST /api/seckill
  ↓
1. 验证用户登录态
2. 检查用户是否已购买（Redis 缓存，快速拒绝重复请求）
3. 限流检查（令牌桶，超限返回 429）
4. 开启 Postgres 事务：
   a. UPDATE products SET stock=stock-1 WHERE id=$1 AND stock>0 RETURNING id
   b. 若 rowCount=0，ROLLBACK → 返回 410 Gone（已售罄）
   c. INSERT INTO orders (user_id, product_id, ...)
   d. COMMIT
5. 写 Redis：标记该用户已购买（防重复的快速路径）
6. 返回 201 + 订单 ID
```

错误处理：
- `rowCount=0` → 410，库存不足
- unique violation (23505) → 409，已购买
- 事务超时 → 503，稍后重试
- 其他错误 → 500，事务自动回滚

### 前端的正确姿势

前端按钮禁用保留，但定位为"体验优化"而不是"防重复"。用户看到 4xx 或 5xx 时展示对应文案：
- 410：已售罄
- 409：您已参与过本次活动
- 429：排队中，请稍候
- 503：系统繁忙，请重试

---

## 修订后方案小结

| 问题 | 原方案 | 修订后 |
|------|--------|--------|
| 超卖竞态 | 读-判-写三步，必然超卖 | 原子 UPDATE ... WHERE stock>0，DB 层保证 |
| 负库存 | 无防护 | CHECK (stock >= 0) 兜底 |
| 用户重复下单 | 无防护 | UNIQUE 约束 + Redis 快速拒绝 |
| 前端绕过 | 只有按钮禁用 | 后端完整幂等，前端只管体验 |
| 数据库被打挂 | 全量请求直达 DB | 应用层令牌桶限流 + 连接池调优 |
| 事务失败不一致 | 未说明 | 显式 ROLLBACK + 错误码分类 |
