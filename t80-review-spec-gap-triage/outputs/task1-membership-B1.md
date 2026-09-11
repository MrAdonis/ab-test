## P0（安全漏洞 / 静默错误数据）

- **[编码失误] 验签失败未阻断流程**：`wxpay_callback`（membership.py:129-131）在 `verify_sign` 返回 `False` 时只 `log.warning`，没有 `return`，代码继续往下走到订单校验、标记已支付、开通会员的成功路径。等于验签形同虚设，任何人伪造 `out_trade_no`+`total_fee` 即可白嫖会员，直接违反需求单"验签失败返回失败"。修复：验签失败处立即 `return {"code": "FAIL", "message": "invalid sign"}`。

- **[编码失误] 续费未按到期日顺延**：`_grant_membership`（membership.py:121-123，调用点 144）恒定 `member_expires = today + timedelta(days=days)`，忽略已有 `member_expires`。需求单明确"用户已经是会员的，在原到期日基础上顺延"，当前实现会让提前续费的用户白白损失剩余天数（老到期日被今天覆盖）。修复：`base = user.member_expires if user.member_expires and user.member_expires >= today else today; user.member_expires = base + timedelta(days=days)`。

- **[编码失误] 月卡天数与需求不符**：`PLAN_DAYS = {"month": 31, ...}`（membership.py:16），需求单写明"月卡 30 天"，当前多算 1 天，属于静默错误数据，无异常无日志，只有对账时才会发现。

## P1（边界 / 竞态类正确性问题）

- **[需求缺口] 回调未二次校验订单是否已超时**：`wxpay_callback` 只检查 `order.status`，不检查 `now - order.created_at` 是否已超过 `ORDER_TTL`。若定时任务 `close_expired_orders` 未及时跑（cron 延迟/宕机），一个实际已超时 15 分钟但状态仍是 `pending` 的订单可以被继续支付成功。需求单未说明这个"定时关闭"与"回调到达"之间的竞态该怎么处理——建议在回调里补一道 `now - order.created_at > ORDER_TTL → FAIL` 的兜底判断，双保险，不完全依赖外部 cron 时效。
- **[编码失误] 不可信输入未做防御性解析**：`int(payload.get("total_fee", -1))`（membership.py:139）对外部可控字段直接 `int()`，若微信回调（或伪造请求）传入非数字字符串会抛出未捕获 `ValueError`，导致 500 而非约定的 `{"code": "FAIL"}` 结构，属于不可信输入处理面的遗漏。
- **[编码失误] 分页参数未校验，page≤0 时行为异常**：`list_orders`（membership.py:105-110）未校验 `page`/`page_size`，`page=0` 时 `start = -page_size`，触发 Python 负数切片，返回结果与预期不符（不报错但数据错位），需求单未提及非法分页参数如何处理，但这是典型边界疏漏。

## P2（技术债 / 功能缺失，仅标题）

- 硬编码占位签名密钥 `WXPAY_KEY = "replace-me-in-prod"` 位于生产可达的验签路径，属加密面遗留项（P0-1 修复后仍需走配置/密钥管理，不能仍留在源码里）
- `auth()` 对过期 token 不做清理，`TOKENS` 字典条目永久驻留直到下次 login 覆盖

## 总体评估

支付回调验签结果被忽略是本次实现中最严重的问题（等同无验签的支付确认接口），加上续费不顺延、月卡天数多算，三条 P0 都是"看起来跑得通、但和需求单逐句对照就能发现"的静默偏差，建议优先修完 P0 再进入联调。
