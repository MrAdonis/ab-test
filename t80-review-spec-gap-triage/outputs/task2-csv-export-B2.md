# 订单导出功能 Review

## P0

1. **[编码失误] 状态过滤条件错误，已取消订单被导出**
   `src/exportOrders.ts:35` `filter((o) => o.status !== "pending")` 只排除了 pending，paid/shipped/cancelled 全部放行。SPEC 明确写"只导出已支付和已发货的订单，已取消的不导出"。修法：`filter((o) => o.status === "paid" || o.status === "shipped")`。

2. **[编码失误] 结束日期未包含当天，右边界整体错误**
   `src/exportOrders.ts:29-30` `inRange` 用 `createdAt < end`，而 `end = new Date(endYmd)` 是结束日 00:00。等价于结束日当天全部订单被排除，而不是 SPEC 要求的"两端都含当天"。修法：`end` 取结束日 +1 天再用 `<`，或改用 `<= endOfDay(23:59:59.999)`。

3. **[编码失误] 金额只保留一位小数**
   `src/exportOrders.ts:21` `(cents / 100).toFixed(1)`，SPEC 明确"保留两位小数"，应为 `toFixed(2)`。当前如 12.30 元会被截成 "12.3"，导出金额格式与需求不符（财务类字段，属静默错误数据）。

4. **[编码失误] CSV 公式注入未防护（Excel 场景）**
   `csvCell`（`src/exportOrders.ts:24-27`）只转义 `"`, `,`, `\n`，未处理以 `=`、`+`、`-`、`@` 开头的字段。SPEC 明确"在 Excel 里打开核对"，`id`/`phone` 若来自外部可控输入且以这些字符开头，Excel 打开时会被当公式执行（CSV Injection，OWASP 已收录）。需对危险前缀字段加 `'` 前缀转义。

## P1

1. **[编码失误] 日期解析未考虑时区，边界日订单可能被误判**
   `new Date("YYYY-MM-DD")` 按 UTC 零点解析，而 `order.createdAt` 若代表业务本地时间（如 UTC+8），UTC 边界与"当天"的业务语义不一致，会导致日期边界附近的订单被错误纳入/排除。

2. **[需求缺口] 手机号非 11 位时直接原样导出，未脱敏**
   `maskPhone`（`src/exportOrders.ts:15-18`）对非 11 位手机号直接 `return phone`，完全跳过打星。SPEC 只给了标准 11 位示例，未说明异常格式如何处理，这是实现者自行拍的决定，且当前选择（原样导出未脱敏）与"打星"这一隐私要求的初衷相悖，有 PII 泄露风险。需要需求方确认：非标准手机号是全部打星（如中间统一遮蔽若干位）、直接跳过导出、还是允许原样导出？推荐：无论长度都做通用规则脱敏（如中间 40% 字符打星），不应该有"完全不脱敏"的兜底路径。

3. **[编码失误] CSV 无 BOM，Excel 直接打开中文可能乱码**
   `writeFileSync(file, csv, { encoding: "utf8" })` 未写 BOM（`\uFEFF`）。SPEC 场景是"运营在 Excel 里打开核对"，Windows 版 Excel 对无 BOM 的 UTF-8 CSV 常把中文表头/状态列显示为乱码，直接影响核对可用性。

4. **[编码失误] 非法日期输入静默产出空结果**
   `startYmd`/`endYmd` 若格式非法，`new Date()` 产出 `Invalid Date`，比较全部为 `false`，导出一个只有表头的空 CSV，没有任何报错或提示，调用方/运营无法区分"这段时间真的没订单"还是"日期传错了"。

## P2

- 创建时间列用 `toISOString()` 输出完整 UTC 时间戳（含毫秒和时区 `Z`），SPEC 未约定格式 [需求缺口]
- 无任何测试覆盖（金额格式化、脱敏、日期边界、状态过滤均无验证）
- 目标文件已存在时 `writeFileSync` 静默覆盖，无提示

## 总体评估
核心业务规则（状态过滤、日期边界、金额精度）三处都与 SPEC 直接冲突且是静默错误数据，加上一处 CSV 注入安全漏洞，建议这四项 P0 全部修复后再合入；手机号脱敏兜底路径需要产品明确后再定实现。
