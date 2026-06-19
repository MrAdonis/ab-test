# Ground Truth — payment-service.js 植入 bug 清单

评分时对照本清单。agent 不可见。

| # | 行 | 类型 | 期望分级 | 描述 |
|---|----|------|---------|------|
| B1 | 17 | SQL 注入 | P0 | `findUserByEmail` 字符串拼接 email 进 SQL |
| B2 | 44 | SQL 注入 | P0 | checkout 里 `UPDATE ... balance - ' + total` 拼接 |
| B3 | 55-56 | SQL 注入 | P0 | admin/refund 拼接 orderId |
| B4 | 64 | SQL 注入 | P0 | order/first-item 拼接 req.params.id |
| B5 | 43 | 密钥日志泄露 | P0 | `console.log` 打印 STRIPE_SECRET_KEY |
| B6 | 53 | 鉴权缺失 | P0 | `/admin/refund` 端点无任何 auth 检查,任意人可退款到任意账户 |
| B7 | 42-46 | 竞态条件 | P1 | 余额 check-then-deduct 非原子,并发可超额扣款 |
| B8 | 6-14 | 浮点金额 | P1 | 用 float 算钱(price*qty*0.9),金额应用整数分/decimal |
| B9 | 25-27 | 日期/类型 bug | P1 | `coupon.expires > today` 字符串比较且未校验 coupon.amount 是否为负(负 amount 反向加钱) |
| B10 | 36 | 空指针/边界 | P1 | `user` 可能 undefined(email 不存在),`user.balance` 抛错 |
| B11 | 64 | 空指针/边界 | P1 | `items[0].name` 未检查空数组 |
| B12 | 69-75 | 错误吞掉 | P2 | `syncToWarehouse` 空 catch,同步失败静默 |
| B13 | 全局 | 输入校验缺失 | P2 | checkout 未校验 items/email 存在性与类型 |

总计:6×P0 / 5×P1 / 2×P2 = 13 项。

注:SQL 注入有 4 处(B1-B4),可合并报"全文多处 SQL 注入"算 1 个发现(按抓到模式算命中,但漏报具体端点扣细节分)。
