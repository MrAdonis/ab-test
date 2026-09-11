## Review: `src/exportOrders.ts`（对照 `SPEC.md`）

### P0
1. **[P0] 状态过滤保留了取消订单** — `exportOrders.ts:35` `.filter((o) => o.status !== "pending")` 只排除 pending，`cancelled` 订单未被过滤，直接违反 spec「已取消的不导出」，导致导出数据静默错误（运营核对时会看到不该出现的取消订单）。应改为 `o.status === "paid" || o.status === "shipped"`。
2. **[P0] 金额只保留一位小数** — `exportOrders.ts:21` `(cents / 100).toFixed(1)` 而 spec 要求两位小数。不仅位数不对，还会把分位四舍五入丢失（如 12345 分 → 123.45 元被写成 "123.5"），是静默的财务数据错误。应为 `.toFixed(2)`。
3. **[P0] CSV 公式注入（Formula Injection）** — `exportOrders.ts:24-27` `csvCell` 只转义 `"`、`,`、`\n`，未处理以 `=`、`+`、`-`、`@` 开头的单元格内容。手机号/订单号等字段一旦以这些字符开头，Excel 打开时会被当公式执行（OWASP CSV Injection，是本任务明确的输出注入 sink，因为 spec 就是"在 Excel 里打开"）。应对上述前缀单元格加前置 `'` 或制表符转义。

### P1
4. **[P1] 结束日期当天被完全排除** — `exportOrders.ts:29-31,53-54` `inRange` 用 `createdAt < end`，且 `end = new Date(endYmd)` 是 endYmd 当天 UTC 00:00，导致结束日期当天的订单全部丢失，违反 spec「两端都含当天」。应将 end 设为 `endYmd` 次日 00:00（或当天 23:59:59.999）再做 `<=`/`<` 比较。
5. **[P1] 日期边界按 UTC 解析，未考虑业务时区** — `exportOrders.ts:53-54` `new Date("YYYY-MM-DD")` 恒为 UTC 零点。若订单 `createdAt`/运营选择日期以本地时区（如东八区）为准，边界会整体偏移最多 8 小时，导致日期首尾附近订单被错误纳入或排除，且与问题 4 叠加加剧数据缺失。
6. **[P1] 手机号非 11 位时明文返回，脱敏被绕过** — `exportOrders.ts:15-18` `if (phone.length !== 11) return phone;`，畸形数据会直接导出完整手机号，与脱敏要求的初衷矛盾（fail-open）。
7. **[P1] 未写 UTF-8 BOM，Windows Excel 双击打开中文乱码** — `exportOrders.ts:57` `writeFileSync(file, csv, { encoding: "utf8" })` 无 BOM，直接违背 spec 核心场景「在 Excel 里打开核对」（表头"订单号"等中文会显示为乱码）。

### P2
8. 状态列直接输出英文枚举值（paid/shipped）而非中文
9. 无输入校验（startYmd/endYmd 非法格式、start > end 未处理）
10. `dir` 参数未做路径校验直接拼入文件路径（风险较低，非用户直接可控）

**总体评估**：实现存在 3 处会静默产生错误业务数据/存在注入风险的 P0 问题（取消订单泄漏、金额精度错误、CSV 公式注入），且日期范围与时区处理未满足 spec 的边界要求，不建议在当前状态上线，需先修复 P0 后重新测试日期边界与金额用例。
