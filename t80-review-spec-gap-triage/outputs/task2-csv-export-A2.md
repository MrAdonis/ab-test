## P0（安全漏洞 / 静默错误数据）

1. **状态过滤未排除已取消订单** — `buildCsv`（exportOrders.ts:35）用 `.filter(o => o.status !== "pending")`，实际保留 `paid/shipped/cancelled` 三种状态。SPEC.md #2 明确要求"已取消的不导出"，当前实现会把已取消订单一并导出，直接违反需求且是静默错误数据。

2. **金额只保留一位小数** — `formatAmount`（exportOrders.ts:21）用 `.toFixed(1)`，SPEC.md #3 要求"保留两位小数"。不仅位数不对，还会产生错误四舍五入，例如 999 分 → 9.99 元被格式化成 "10.0"，财务核对时金额直接错误。

3. **手机号非 11 位时不脱敏，明文泄露** — `maskPhone`（exportOrders.ts:16）对 `phone.length !== 11` 的情况直接 `return phone`（原样返回未脱敏号码）。只要手机号数据带空格/"+86"前缀/脏数据等非标准格式，就会静默泄露完整手机号，违反 SPEC.md #4 的强制脱敏要求，属 PII 泄露。

4. **CSV 公式注入（Excel 打开风险）** — `csvCell`（exportOrders.ts:24-27）只转义 `"`、`,`、`\n`，未对以 `=`、`+`、`-`、`@` 开头的单元格做防护。SPEC.md 明确用途是"在 Excel 里打开核对"，若 `order.id`/`phone` 等字段包含此类前缀（外部/历史脏数据不可保证不会出现），Excel 会将其解释为公式执行，属 CSV/Excel 公式注入（OWASP CSV Injection），命中 coding-dod.md 显式列出的 CSV 导出安全面。

## P1（边界 / 时区类正确性问题）

5. **结束日期边界排除当天订单** — `exportOrders`（exportOrders.ts:53-54）中 `end = new Date(endYmd)` 是结束日当天 00:00，而 `inRange` 用 `createdAt < end`，导致结束日当天 00:00 之后创建的订单全部被排除在外。SPEC.md #1 要求"两端都含当天"，当前实现结束日几乎完全不含（只含精确 00:00:00.000 这一瞬间）。

6. **日期解析按 UTC，未考虑业务时区** — `new Date("YYYY-MM-DD")` 按 ECMA-262 规范解析为 UTC 零点，而订单 `createdAt` 通常反映本地业务时区（如中国 UTC+8）的创建时刻。若部署/业务时区非 UTC，日期范围边界会整体偏移最多 8 小时，导致靠近日期边界的订单被错误地划入前一天或后一天，与问题 5 叠加会进一步放大误差。

## P2（功能缺失 / 技术债）

7. CSV 未写入 UTF-8 BOM，Windows Excel 直接双击打开中文表头/状态列可能出现乱码，影响 SPEC.md 明确的"在 Excel 里打开核对"这一核心用例。
8. `dir` 参数未做任何校验直接拼入文件路径（`writeFileSync`），若上游从请求参数透传该值存在路径穿越风险，建议限定/校验。
9. `startYmd`/`endYmd` 未做格式校验，非法输入会在 `toISOString()` 处直接抛未捕获异常（而非可读错误），也未处理 start > end 的情况。

## 总体评估

核心业务规则（状态过滤、金额精度、手机号脱敏）均与 SPEC.md 明确条款相悖且属静默数据错误，另有 Excel 公式注入安全隐患，当前实现不可直接上线，需先修复全部 P0 项并复核日期边界逻辑。
