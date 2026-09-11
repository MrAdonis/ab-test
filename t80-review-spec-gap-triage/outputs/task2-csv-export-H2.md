# Review：`src/exportOrders.ts` vs `SPEC.md`

## P0（安全漏洞 / 静默错误数据）

**[编码失误] 状态过滤未按白名单执行，已取消订单会被导出**
`src/exportOrders.ts:35` — `orders.filter((o) => o.status !== "pending")` 只排除了 `pending`，`cancelled` 订单会通过过滤被导出。SPEC.md 第 2 条明确写"只导出已支付和已发货的订单，已取消的不导出"。修法：改为白名单 `o.status === "paid" || o.status === "shipped"`。

**[编码失误] 日期范围排除了结束日期当天的全部订单**
`src/exportOrders.ts:29-31` 的 `inRange` 用 `createdAt < end`，而 `end`（`exportOrders.ts:54`）就是结束日期当天 00:00:00（`new Date(endYmd)`），并未 +1 天或设为 23:59:59.999。结果是结束日期当天创建的订单**全部被排除**，与 SPEC.md 第 1 条"两端都含当天"直接矛盾。修法：`end` 应改为结束日期次日 00:00，再配合 `< end`；或改比较符为 `<=` 且把 `end` 设到当天 23:59:59.999。

**[编码失误] 金额只保留 1 位小数，与需求"保留两位小数"不符**
`src/exportOrders.ts:20-22` `formatAmount` 用 `.toFixed(1)`。SPEC.md 第 3 条明确要求"金额（元，保留两位小数）"。这不只是格式问题——`toFixed(1)` 会做四舍五入，例如 12345 分（123.45 元）会被输出成 `"123.5"`，运营核对到的金额是错的。修法：`.toFixed(2)`。

## P1（正确性边界 / 需求缺口）

**[需求缺口] CSV 未带 UTF-8 BOM，中文表头在 Excel 打开大概率乱码**
`src/exportOrders.ts:57` `writeFileSync(file, csv, { encoding: "utf8" })` 没有前置 `\uFEFF`。SPEC.md 开头明确场景是"运营……在 Excel 里打开核对"，而表头含中文（订单号/用户手机号/状态等）。Windows 版 Excel 对无 BOM 的 UTF-8 CSV 默认按本地编码（GBK 等）解析，中文列头/内容会乱码。需求单没写编码要求，但这是实现必须替它做的具体选择，建议默认加 BOM，请需求方确认是否符合运营的 Excel 版本环境。

**[需求缺口] 手机号非 11 位时直接原样输出，未打码**
`src/exportOrders.ts:15-18` `maskPhone` 在 `phone.length !== 11` 时直接返回原始手机号（完全不打码）。SPEC.md 只给了标准 11 位手机号的打码示例，没有定义异常/脏数据号码（如带区号、国际号码、测试数据）的处理方式。当前实现选择的兜底行为是把敏感信息原样导出，存在隐私泄露风险。建议：请需求方确认非标准号码的来源是否存在；若存在，倾向于"仍尽量打码（如只保留前后各若干位）"而不是"完全裸露"。

**[需求缺口] 非法日期输入无校验，静默产生 Invalid Date**
`src/exportOrders.ts:52-58` 若 `startYmd`/`endYmd` 不是合法的 `YYYY-MM-DD`（如前端传参异常），`new Date(...)` 会得到 `Invalid Date`，所有比较结果为 `false`，导出静默变成空表，文件名里还会出现字符串 `"Invalid Date"`，没有任何报错。SPEC.md 未定义异常输入分支。建议请需求方明确：是否需要在导出前显式校验日期格式并报错，而不是静默产出一个内容为空、文件名异常的文件。

## P2（技术债 / 次要，仅标题）
- CSV 转义未处理裸 `\r`，仅处理 `",\n`（`csvCell`，`exportOrders.ts:24-26`）
- 缺少 Excel/CSV 公式注入（CSV Injection）防护，`id`/`phone` 等字段若以 `=+-@` 开头未做前置转义（`exportOrders.ts:24-26, 37-43`）

## 总体评估
三处 P0 均是会直接产出错误数据且不会报错的编码失误（漏单、丢单、金额四舍五入），必须在合并前修复；三处 P1 是需求单未覆盖但影响真实可用性的空白点（尤其 BOM 乱码几乎必现），建议连同推荐方案一起交回需求方拍板后再定实现。
