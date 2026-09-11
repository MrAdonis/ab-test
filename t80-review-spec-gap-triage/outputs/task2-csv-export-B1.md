## P0（安全漏洞或静默错误数据）

**1. [编码失误] 已取消订单未被排除，导出结果包含 cancelled 订单**
`src/exportOrders.ts:35`
`buildCsv` 的过滤只有 `o.status !== "pending"`，等于放行 paid / shipped / cancelled 三种状态。SPEC 第 2 条明确写"只导出已支付和已发货的订单，已取消的不导出"——这是需求单已写明的场景，属编码实现与需求不符。
修法：`.filter((o) => o.status === "paid" || o.status === "shipped")`。

**2. [编码失误] 结束日期当天的订单被漏导，违反"两端都含当天"**
`src/exportOrders.ts:29-31, 53-54`
`end = new Date(endYmd)` 是结束日当天 00:00，`inRange` 用 `createdAt < end`（不含 end）。结果是结束日当天 00:00 之后创建的订单全部被静默丢弃，只有恰好 00:00:00.000 创建的订单才会被计入——实际上约等于"结束日完全不导出"。SPEC 第 1 条明确写"两端都含当天"，这是编码失误不是需求模糊。
修法：`end` 取结束日的下一天 00:00，作为排他上界；或用 `createdAt <= endOfDay(end)`。

**3. [编码失误] 金额只保留 1 位小数，需求要求 2 位**
`src/exportOrders.ts:20-22`
`formatAmount` 用 `toFixed(1)`，SPEC 第 3 条明确写"金额（元，保留两位小数）"。财务字段格式错误且是静默错误数据（如 1050 分应显示 "10.50"，实际显示 "10.5"）。
修法：`toFixed(2)`。

## P1（竞态/边界/时区类正确性问题）

**4. [编码失误/appsec-输出注入] 无 UTF-8 BOM，Excel 打开中文列大概率乱码**
`src/exportOrders.ts:57`
`writeFileSync` 写入纯 UTF-8、无 BOM。SPEC 开篇即写明用途是"在 Excel 里打开核对"，而表头、`status` 值均含中文/英文混排，Windows 版 Excel 在无 BOM 时默认按本地编码（常见 GBK）解析 CSV，会导致中文表头/内容乱码——破坏了整个导出功能的核心使用场景。
修法：写入时前置 `\uFEFF`。

**5. [编码失误/appsec-输出注入] CSV/Excel 公式注入未防护（CWE-1236）**
`src/exportOrders.ts:24-27`
`csvCell` 只转义了 `"`、`,`、`\n`，未处理单元格以 `=`/`+`/`-`/`@` 开头的情况。`phone`、`id` 均来自订单数据（非常量可信源），若其中任一字段以上述字符开头，Excel 打开时会被当公式执行，属于 OWASP CSV Injection 场景。
修法：cell 内容以 `=+-@` 开头时前置 `'` 或制表符再走现有转义。

**6. [需求缺口] 日期区间按 UTC 天边界计算，未与业务时区对齐**
`src/exportOrders.ts:53-54`
`new Date(startYmd)` / `new Date(endYmd)` 按 ISO 日期串解析为 **UTC** 当天 00:00。若订单 `createdAt` 是按北京时间产生业务意义的"当天"，UTC 与 UTC+8 的 8 小时偏移会导致边界附近的订单被错误地划入/划出所选区间。SPEC 未说明时区口径。
**推荐**：明确"开始/结束日期"按 Asia/Shanghai 日历日计算，而不是 UTC；需产品/需求方确认预期时区。

## P2（功能缺失或技术债，仅标题）

- [需求缺口] 手机号非 11 位时 `maskPhone` 直接原样返回未打码号码，存在 PII 泄露路径，SPEC 未定义异常格式处理策略
- [需求缺口] `创建时间` 列直接输出 `toISOString()`（UTC，含 T/Z），未做本地化/格式化，SPEC 未规定具体时间格式
- [需求缺口] `状态` 列直接输出内部英文枚举值（pending/paid/shipped/cancelled），与其余中文表头风格不一致，是否需要翻译成中文展示 SPEC 未说明
- [技术债] `dir` 目录不存在时 `writeFileSync` 会直接抛错，无 mkdir 兜底

## 总体评估
三个 P0 都是需求单已经写清楚、实现却做反/做错的硬编码失误（漏筛已取消订单、结束日整天漏导、金额小数位数错），必须先修；另外 UTF-8 BOM 缺失和 CSV 公式注入两个 P1 会让"在 Excel 里核对"这个核心场景直接失效或存在安全风险，建议一并处理；时区口径等 P2/需求缺口项建议打包回传需求方确认后再定。
