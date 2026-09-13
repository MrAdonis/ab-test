# Ground truth（评分用，不进候选 prompt）

行号 = 变更后文件的真实行号。判定命中的标准：意见的**描述**指向该缺陷机制即算命中，行号错不影响命中判定（行号准确率单独统计）。

## Task 1 — src/orders.ts

| ID | 维度 | 行 | 缺陷 |
|----|------|----|------|
| T1-1 | 安全 | 14 | `$queryRawUnsafe` 用模板字符串拼 `code`，SQL 注入 |
| T1-2 | 安全 | 21 | `console.log` 打印 authorization header 与整个 body，凭证 + PII 落日志 |
| T1-3 | 行为回归 | 37-38 | `parseFloat` 结果未校验，`percent_off` 非数值时 total = NaN 静默写库 |
| T1-4 | 并发 | 35-39 | 查到 `redeemed=false` 与置 `redeemed=true` 非原子，并发下同一券可重复兑换 |
| T1-5 | 性能 | 27-30 | 循环内 `await db.stock.findUnique`，N+1 查询 |
| T1-6 | 契约 | 47 | 返回字段 `total` 改名为 `amount`，与第 8 行 `OrderResponse` 类型不符，破坏既有调用方 |
| T1-7 | 可靠性 | 48-50 | catch 只 `console.log` 不上报，错误被吞 |

诱饵（报了算误报）：
- D1-1 第 26 行 `let stockOk` — 同步循环内赋值，无竞态
- D1-2 第 4 行 `COUPON_PREFIX = "PROMO-"` — 无害常量，不是硬编码密钥

## Task 2 — pipeline.py

| ID | 维度 | 行 | 缺陷 |
|----|------|----|------|
| T2-1 | 安全 | 24 | `pickle.loads` 反序列化磁盘缓存，可被写入方 RCE |
| T2-2 | 安全 | 19 | `name` 未校验直接进 `os.path.join`，`../` 可穿越出 CACHE_DIR |
| T2-3 | 行为回归 | 18 + 27-29 | 可变默认参数 `fallbacks=[]`，且迭代中向自身 append，跨调用累积状态 |
| T2-4 | 并发 | 20-25 | `_CACHE` check-then-set 非原子；第 10 行 `_LOCK` 定义后从未使用 |
| T2-5 | 性能 | 36 | 双层循环内 `re.compile`，每行每模式重编译 |
| T2-6 | 契约 | 33-39 | `extract_codes` 由返回 list 改为 generator，既有调用方 `len()`／重复迭代会坏 |
| T2-7 | 测试 | — | 两个新函数无对应测试 |

诱饵（报了算误报）：
- D2-1 第 43-47 行 `seen` — 方法内局部变量的 check-then-act，无竞态
- D2-2 第 48 行 `len(_CACHE)` — 只读访问，不该要求加锁

## 统计口径

- **命中**：ground truth 被任一维度 agent 指出（跨 agent 去重，同一条只计一次）
- **误报**：报了诱饵，或报了 diff 中不存在的问题（幻觉），或把正确代码判为缺陷
- **行号准确**：意见给的行号落在 ground truth 行区间内（±1 容差）
- 纯风格/命名/注释类意见不计入命中也不计入误报，单独记数
