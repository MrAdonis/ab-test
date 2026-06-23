# 限量秒杀方案（硬化后）

---

## 收敛过程

### 第 1 轮：漏洞枚举

**L1 — 竞态条件导致超卖（边界情况：并发）**
什么会坏：10000 个请求同时读到 stock=100，全部判断 >0，全部扣减，实际创建 10000 个订单而非 100 个。
条件：无任何数据库锁保护的「读-判断-写」三步不是原子操作，Postgres 的默认 READ COMMITTED 隔离级别不阻止这种幻读。

**L2 — 前端禁用按钮不构成防重保护（假设：前端能阻止重复提交）**
什么会坏：按钮禁用只防正常点击，不防网络重试、页面刷新、curl 直接调 API、BurpSuite 重放。任何人都能绕过前端。
条件：后端无幂等保护时，同一用户并发或重放请求会产生多张订单。

**L3 — 同一用户多次下单（边界情况：重试/重放）**
什么会坏：用户 A 抢到之后，通过重放 POST /api/seckill 继续抢，占用其他用户的库存名额。
条件：后端未校验「同一用户同一活动只能下一单」。

**L4 — 订单创建失败但库存已扣（部分失败）**
什么会坏：stock 减 1 成功，但后续 INSERT 订单因约束违反、超时或其他原因失败，库存永久丢失。
条件：stock 扣减与订单创建不在同一事务内，或事务中断未回滚。

**L5 — 库存字段可被并发更新到负数（边界情况：极端并发）**
什么会坏：即使加了检查，若用 UPDATE ... SET stock = stock - 1 WHERE stock > 0 但多连接同时执行，Postgres 行级锁会串行化这些 UPDATE，但如果用的是应用层检查（读出来再写），负数仍会出现。
条件：更新语句未包含 WHERE stock > 0 条件，或应用层检查与写入非原子。

**L6 — 活动开始瞬间数据库连接池耗尽（边界情况：最大规模）**
什么会坏：几万并发请求同时到达，每个请求持有一个数据库连接等待行锁，连接池满后新请求报错而非排队，导致大量 500。
条件：连接池上限（通常 20-100）远小于并发请求数（几万）。

**L7 — 从现有状态迁移（迁移）**
什么会坏：若商品表已有数据，stock 字段可能不存在，或现有订单逻辑未感知秒杀约束，普通下单接口仍可绕过限量。
条件：没有显式迁移计划，也没有区分「秒杀商品」和「普通商品」的机制。

**L8 — 无验证覆盖超卖回归（验证）**
什么会坏：功能测试在低并发下通过，但压测未模拟真实争用，上线后才发现超卖。
条件：测试套件未包含并发争用场景。

**L9 — 活动结束后 stock 状态不可逆（可逆性）**
什么会坏：活动中途发现 bug 需要回滚，但已扣减的 stock 和已创建的订单记录如何处理没有定义。
条件：没有「取消活动」的回滚路径，不知道是否能安全重置 stock。

---

### 第 1 轮：修复 / 接受

**L1 → 修复**：使用数据库原子 UPDATE 替代读-判断-写三步：
```sql
UPDATE products
SET stock = stock - 1
WHERE id = $product_id AND stock > 0
RETURNING id;
```
若 RETURNING 返回空行，说明库存已耗尽，拒绝下单。stock 扣减与订单创建放在同一事务。

**L2 → 修复**：前端禁用按钮保留（减少正常用户误操作），但后端必须有幂等保护，不依赖前端。前端不是防护层，只是 UX 层。

**L3 → 修复**：后端在事务内检查 `(user_id, activity_id)` 唯一约束——orders 表建唯一索引 `UNIQUE (user_id, activity_id)`，重复插入触发约束错误，捕获后返回「已参与」而非 500。

**L4 → 修复**：stock 扣减与 INSERT 订单在同一 Postgres 事务内：先 UPDATE stock（原子 WHERE stock > 0），RETURNING 有行则继续 INSERT 订单，任一步骤失败整个事务 ROLLBACK，库存自动恢复。

**L5 → 已被 L1 修复覆盖**：WHERE stock > 0 在数据库层保证，不依赖应用层读-判断。额外加 CHECK (stock >= 0) 约束作为最后一道防线。

**L6 → 修复**：在 Postgres 前加请求队列（排队层）。具体实现：活动开始时，后端接受请求后立即返回「排队中」，通过一个内部队列（Redis List 或 Postgres SKIP LOCKED）串行消费，消费速率由连接池决定，而非并发请求数。这将「几万并发」转化为「几万排队，若干并发」。

**L7 → 修复**：
- 显式迁移：ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0);
- 秒杀商品用 is_seckill BOOLEAN 字段标记；/api/seckill 只处理 is_seckill=true 的商品，普通下单接口拒绝 is_seckill=true 的商品（或忽略 stock 字段由业务决定）。

**L8 → 修复**：验收标准必须包含并发压测：用 k6 / pgbench 模拟 10000 并发请求抢 100 库存，断言：最终订单数 ≤ 100，最终 stock ≥ 0，无超卖。

**L9 → 修复**：支持活动取消：增加 activity_status 字段（active / cancelled），取消时设为 cancelled，后续请求拒绝；已成功订单需要业务决定是否退款（不在本方案范围，标为接受的风险详见下方）。

---

### 第 2 轮：重查

检查修复是否引入新漏洞：

**新 L10 — 排队层单点失败（L6 修复引入）**
什么会坏：Redis 或内部队列服务宕机导致整个秒杀不可用。
条件：队列层无高可用配置。

**新 L11 — SKIP LOCKED 不适用于「公平排队」（L6 修复引入，假设）**
什么会坏：SKIP LOCKED 会跳过被锁行，先到达的请求不一定先被处理，排队公平性无保障。
条件：用 Postgres SKIP LOCKED 实现排队时，多 worker 并发消费队列的顺序不确定。

**新 L12 — 唯一索引错误被吞掉（L3 修复引入）**
什么会坏：捕获约束错误时，若代码将所有数据库错误统一返回 500，用户无法区分「库存不足」和「已参与」。
条件：错误处理不区分 Postgres 错误码（23505 = unique violation vs 其他）。

---

### 第 2 轮：修复 / 接受

**L10 → 接受的风险**：排队层（Redis）HA 配置属于基础设施层，超出本功能方案范围。生产部署时应使用 Redis Sentinel 或 Redis Cluster，本方案标注此依赖。

**L11 → 修复**：排队层使用 Redis List（LPUSH 入队，BRPOP 出队），严格 FIFO，不用 Postgres SKIP LOCKED 实现排队。SKIP LOCKED 保留用于订单表的并发 worker 分片场景，不用于主排队逻辑。

**L12 → 修复**：错误处理显式区分 Postgres 错误码：
- `23505`（unique_violation）→ HTTP 409，消息「您已参与本次活动」
- UPDATE 返回空行（stock 耗尽）→ HTTP 410，消息「库存已售罄」
- 其他数据库错误 → HTTP 500，记录日志

---

### 第 3 轮：重查

第 2 轮修复未引入新的实质性漏洞。剩余项已全部具名为接受的风险或已修复。停止。

---

## 关闭的漏洞

| 条件 | 修复 |
|------|------|
| 并发读-判断-写导致超卖 | 改为原子 `UPDATE ... WHERE stock > 0 RETURNING id`，扣减与建单同事务 |
| 前端按钮禁用被绕过 | 后端建 `UNIQUE (user_id, activity_id)` 约束，幂等保护在数据库层 |
| 同一用户多次下单占用名额 | 唯一索引约束，重复插入返回 409 |
| stock 扣减成功但订单创建失败导致库存丢失 | 两步操作在同一 Postgres 事务，任意失败全部 ROLLBACK |
| stock 被更新到负数 | `WHERE stock > 0` + `CHECK (stock >= 0)` 双重约束 |
| 几万并发耗尽连接池导致大量 500 | 接受请求后入 Redis FIFO 队列，后端 worker 按连接池容量串行消费 |
| 现有商品表无 stock 字段、普通下单绕过限量 | 显式迁移脚本；`is_seckill` 标记区分；接口互斥 |
| 测试未覆盖并发争用、上线才发现超卖 | 验收标准强制包含 k6/pgbench 并发压测，断言订单数 ≤ 库存 |
| 活动无法取消回滚 | `activity_status` 字段，cancelled 状态拒绝新请求 |
| Redis SKIP LOCKED 排队不公平 | 排队改用 Redis List LPUSH/BRPOP 严格 FIFO |
| 数据库错误统一返回 500 无法区分场景 | 按 Postgres 错误码（23505/空 RETURNING/其他）分别返回 409/410/500 |

---

## 接受的风险

| 条件 | 为何可接受 |
|------|-----------|
| Redis 排队层无 HA 时单点失败 | 属基础设施配置范围，不属于本功能逻辑。生产部署文档标注需 Redis Sentinel/Cluster，本方案假设 Redis 可用 |
| 活动取消后已成功订单的退款/补偿流程 | 退款属于订单生命周期管理，超出秒杀功能范围。`activity_status=cancelled` 仅阻止新订单，存量订单处理由业务决策 |
| 排队等待超时的用户体验（等了多久、排第几） | 队列深度查询和进度推送属于增强功能，当前方案返回「排队中」状态即可，后续可加 WebSocket 推送 |

---

## 最终方案

### 数据库迁移

```sql
-- 迁移 1：商品表新增字段
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS stock INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS is_seckill BOOLEAN NOT NULL DEFAULT false,
  ADD CONSTRAINT check_stock_non_negative CHECK (stock >= 0);

-- 迁移 2：订单表新增唯一约束（同一用户同一活动只能下一单）
-- activity_id 可以是 product_id，若一次活动只对应一个商品
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS activity_id INTEGER REFERENCES products(id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_user_activity
  ON orders (user_id, activity_id);
```

### 队列层（Redis）

活动开始前，后端持续运行若干 worker 进程（数量 = 连接池上限），每个 worker 执行：

```
BRPOP seckill:queue:{product_id} 0   # 阻塞等待，FIFO
```

取出 `{user_id, product_id, request_id}` 后执行数据库事务（见下）。

### 接口：POST /api/seckill

**请求体**：`{ product_id, user_id }`（user_id 从认证 token 提取，不信任客户端传值）

**处理逻辑**：

```
1. 校验 product 存在且 is_seckill = true 且 activity_status = active
   → 否则 HTTP 400/404

2. 生成 request_id（UUID）

3. LPUSH seckill:queue:{product_id}  "{user_id},{product_id},{request_id}"
   → 入队成功后立即返回 HTTP 202 Accepted
     { "status": "queued", "request_id": "..." }
```

**Worker 内事务逻辑**（Postgres）：

```sql
BEGIN;

-- 原子扣减，stock 不足时返回空行
UPDATE products
SET stock = stock - 1
WHERE id = $product_id
  AND is_seckill = true
  AND activity_status = 'active'
  AND stock > 0
RETURNING id;

-- 若上面返回空行：ROLLBACK，通知用户 410 库存售罄

-- 创建订单（唯一索引自动防重复）
INSERT INTO orders (user_id, activity_id, product_id, status, created_at)
VALUES ($user_id, $product_id, $product_id, 'pending', NOW());

-- 若 INSERT 触发 23505：ROLLBACK，通知用户 409 已参与
-- 其他错误：ROLLBACK，记录日志，通知用户 500

COMMIT;
```

事务完成后，通过 Redis Pub/Sub 或轮询接口将结果写回，客户端可用 `request_id` 查询结果：

```
GET /api/seckill/result/{request_id}
→ { "status": "success" | "sold_out" | "duplicate" | "pending" }
```

### 错误码规范

| Postgres 错误 / 条件 | HTTP 状态 | 消息 |
|---------------------|-----------|------|
| UPDATE 返回空行（stock 耗尽 / 活动非 active） | 410 | 库存已售罄 |
| INSERT 触发 23505（unique violation） | 409 | 您已参与本次活动 |
| 其他数据库错误 | 500 | 系统繁忙，请稍后重试 |

### 活动取消

```sql
UPDATE products
SET activity_status = 'cancelled'
WHERE id = $product_id AND is_seckill = true;
```

取消后，Worker 取出队列中剩余任务时，UPDATE 因 `activity_status != 'active'` 返回空行，统一按 410 处理（活动已结束），不再创建订单。

### 验收标准（必须通过才上线）

1. **单元测试**：事务中 UPDATE 返回空行时，订单表无新增记录，stock 无变化。
2. **唯一约束测试**：同一 (user_id, activity_id) 连续提交两次，第二次返回 409，订单表仅一条记录。
3. **并发压测（k6）**：10000 VU 同时 POST /api/seckill，商品 stock=100，断言：
   - 最终 orders 表该 activity_id 记录数 ≤ 100
   - 最终 `SELECT stock FROM products WHERE id = $id` ≥ 0
   - 无记录显示 stock < 0
4. **取消测试**：活动取消后，队列中剩余请求全部返回 410，订单表无新增。

---

## 迭代数

3 轮收敛。
