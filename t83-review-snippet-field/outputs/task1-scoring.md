# Task 1 评分明细（src/orders.ts）

> 留档说明：16 个候选子代理的产出是流式返回的，原始全文未逐字落盘（会话上下文限制）。
> 本文件是按 `prompts/ground-truth.md` 口径逐条核对后的评分明细，含每条命中的具体表述来源，
> 可据此复核评分是否成立。REPORT.md 的结论只依赖本文件。

## 命中矩阵

`✓` = 该维度 agent 明确指出了该缺陷机制；`—` = 未提及。

### A 臂（无 snippet 要求）

| ID | 缺陷 | behavior | security | perf | contract |
|----|------|----------|----------|------|----------|
| T1-1 | SQL 注入（`$queryRawUnsafe` 模板拼接） | ✓ | ✓ | ✓ | ✓ |
| T1-2 | `console.log` 泄露 authorization + body | ✓ | ✓ | ✓ | ✓ |
| T1-3 | `parseFloat` 未校验 → total = NaN | ✓ | ✓(minor) | ✓ | ✓ |
| T1-4 | 优惠券 check-then-act，并发重复兑现 | ✓ | ✓(TOCTOU) | ✓ | ✓ |
| T1-5 | 循环内 `db.stock.findUnique`，N+1 | ✓ | — | ✓ | ✓ |
| T1-6 | 返回字段 `total`→`amount` 破坏 `OrderResponse` | ✓ | ✓(标注越界) | ✓ | ✓ |
| T1-7 | catch 只 `console.log`，错误被吞 | ✓ | — | ✓ | — |

**A 臂并集：7 / 7**

### B 臂（要求 snippet 逐字复制）

| ID | 缺陷 | behavior | security | perf | contract |
|----|------|----------|----------|------|----------|
| T1-1 | SQL 注入 | ✓ | ✓ | ✓ | — |
| T1-2 | `console.log` 泄露凭证 | ✓ | ✓ | ✓ | — |
| T1-3 | `parseFloat` → NaN | ✓ | ✓ | ✓ | ✓ |
| T1-4 | 优惠券 TOCTOU | ✓ | ✓ | ✓ | ✓ |
| T1-5 | N+1 | ✓ | — | ✓ | — |
| T1-6 | `total`→`amount` 契约破坏 | ✓ | — | ✓ | ✓ |
| T1-7 | catch 吞错 | ✓(minor) | — | ✓ | ✓ |

**B 臂并集：7 / 7**

## 误报统计

| 臂 | 诱饵命中 | 幻觉 | 把正确代码判为缺陷 | 合计 |
|----|---------|------|------------------|------|
| A | 0 | 0 | 0 | **0** |
| B | 0 | 0 | 0 | **0** |

- **D1-1**（`let stockOk` 无竞态）：两臂均无人报。
- **D1-2**（`COUPON_PREFIX` 无害常量）：**该诱饵不可评分**，见下方「fixture 局限」。
- B-security 收尾明确写"未见硬编码密钥"，属正确拒答。

## 超出 ground truth 的有效发现（两臂对称，不计分）

- **IDOR**：`body.userId` 未经校验直接写入订单 —— A-security、B-security 均报。这是我写 ground truth 时漏掉的真实缺陷，两臂同时抓到，不构成差异。
- A-contract / B-contract 均报"409 / 500 新分支无对应测试"。
- B-behavior 额外报"重复 itemId 未聚合"；B-contract 额外报"券码前缀匹配但查无此券时静默全价成交"。这两条 A 臂未报，但属于长尾发现，不足以支撑臂间差异（见 REPORT 讨论）。

## 行号准确率

Ground truth 行号：T1-1=14、T1-2=21、T1-3=37-38、T1-4=35-39、T1-5=27-30、T1-6=47、T1-7=48-50。

两臂绝大多数意见落在区间内或 ±1。可辨识的偏差：

- A-security：`console.log` 报 22（真值 21）、SQL 报 13-15（含真值）、`body.itemIds` 报 24（真值 23）—— 整体轻微 +1 漂移，但都在 ±1 容差内。
- B-security：`order.create` 的 `data.userId` 报 48（真值 46），**超出 ±1**，是全场唯一一条明确越界的行号。
- 其余 6 个 agent 全部落在容差内。

**结论：行号准确率上 B 臂未优于 A 臂，唯一一条越界还出在 B 臂。**

## 关键观察（方法论层）

**A 臂 agent 在没被要求的情况下自发贴了逐字代码块。** A-security、A-perf、A-contract 三份产出都在问题描述里直接引用了 diff 原文代码行。这意味着被测变量（显式要求 snippet 字段）在 Sonnet 5 上属于"baseline 已自会"的行为，与 t71 / t73 / t77 / t80-H 的 REJECT 同型。

## fixture 局限（诚实记录）

**D1-2 不可评分。** 诱饵设计为"第 4 行 `COUPON_PREFIX = "PROMO-"` 是无害常量，报成硬编码密钥算误报"，但第 4 行落在 diff hunk 之外，agent 根本看不到该定义。实际发生的是：A-perf 与 B-behavior 各报了一条"`COUPON_PREFIX` 未在本次 diff 中定义，可能 ReferenceError"，且都自行标注"存疑，需结合完整文件确认"。这不是诱饵设定的错误形态（把无害常量当密钥），因此两臂都不计误报。

Task 1 的误报维度因此实际只由 D1-1 一个诱饵支撑，区分力偏弱。
