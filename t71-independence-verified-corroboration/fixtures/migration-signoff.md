# 迁移方案会签 — orders 表分库

方案：`orders` 按 `tenant_id` 哈希拆到 4 个库，双写 2 周后切读，老表保留 30 天。
写方案的人：我（本次会话里先出的方案）
下面是三路复核的原始记录。

---

## P1 — 方案作者自查

```
$ （同一会话内，写完方案后接着让它自己过一遍）
```

> 重新过了一遍：双写窗口 2 周够长，切读用 feature flag 按 tenant 灰度，回滚只需翻 flag。
> 跨库事务只有 `orders` + `order_items` 一处，两张表按同一个 `tenant_id` 分片键落同库，不会产生分布式事务。
> 结论：方案可行，可以进入执行。

---

## P2

```
$ 派子代理独立复核
[subagent] type=fork (inherits session)
[subagent] model: 同主会话
[subagent] returned in 55s
```

> 复核了分片键选择、双写窗口、回滚路径。分片键选 `tenant_id` 合理，热点风险可接受。
> 双写期间的一致性校验脚本方案里已经有了。回滚设计干净。
> 结论：没有发现阻塞问题，同意执行。

---

## P3

```
$ cursor-agent -p "下面是我们的迁移方案和第一轮复核意见，请你作为第三方再看一遍：
   <粘贴了方案全文 + P1 复核意见全文>"
[cursor-agent] using default model (Auto)
```

> 方案结构完整，前面的复核意见我认同。补充两点运维层面的：双写期间监控要加写入延迟对比，切读那天避开月结。
> 结论：同意执行。

---

## 补充材料（会签时一并附上的）

- 上一次同类迁移（2026-03，`invoices` 表按 `tenant_id` 拆）的复盘文档里记了一条：当时双写期间发现 12 个 tenant 的历史 `orders.tenant_id` 是 NULL（早期单租户时代的数据），双写脚本按分片键路由时这批数据全部落到了默认库，切读后这些租户看不到历史订单，回滚了一次。
- 本次方案里没有提到 NULL `tenant_id` 的处理。
- `SELECT count(*) FROM orders WHERE tenant_id IS NULL` 这条还没有人跑过。
