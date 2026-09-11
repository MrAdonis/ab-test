## P0

- **[编码失误] 支付回调验签失败未阻断流程**（`wxpay_callback`，`src/membership.py:129-131`）：`verify_sign` 返回 `False` 时只 `log.warning`，没有 `return`，代码继续往下走完整套开通逻辑。任何人只要能猜到/枚举出 `out_trade_no` 并拼出匹配 `amount_cents` 的 `total_fee`，即可在**无有效签名**的情况下把订单标记为已支付、直接开通会员，与需求"验签失败返回失败"直接矛盾，是可被利用的免费开通漏洞。修复：验签失败时立即 `return {"code": "FAIL", "message": "invalid sign"}`。

- **[编码失误] 续费顺延逻辑未实现**（`_grant_membership`，`src/membership.py:121-123`）：无论用户当前是否仍在会员有效期内，`member_expires` 都被直接覆盖为 `today + days`，没有按需求"已经是会员的在原到期日基础上顺延"处理。有效期未到的老会员续费，剩余天数会被直接抹掉、改成新周期，属于静默丢用户已付费权益。应改为：`base = user.member_expires if user.member_expires and user.member_expires >= today else today`，再 `user.member_expires = base + timedelta(days=days)`。

## P1

- **[编码失误] 月卡天数与需求单不符**：`PLAN_DAYS["month"] = 31`（`src/membership.py:16`），需求单明确写"月卡 30 天"。所有月卡用户都会多得 1 天会员，属于跟书面需求直接矛盾的实现偏差。
- **[编码失误] 支付回调未防御不可信输入**（`wxpay_callback`，`src/membership.py:139`）：`int(payload.get("total_fee", -1))` 对非数字字符串会抛未捕获 `ValueError`，导致回调处理直接 500 而非按需求返回 `FAIL`。回调 payload 来自外部（且验签已发现可绕过，等于完全不可信），应 try/except 包裹或先做类型校验。

## P2

- [编码失误] `list_orders` 未校验 `page` 参数（`page<=0` 时切片结果不符合预期，例如 `page=0` 会切出末尾数据而非报错）
- [需求缺口] `login()` 每次登录都作废旧 token（单端登录），需求单未说明是否允许多端同时在线
- [需求缺口] 支付回调到达时，若订单本该被 15 分钟规则关闭但定时任务尚未跑到，此时是否仍允许支付成功，需求单未明确边界

## 总体评估

代码结构清晰但有两处 P0：支付回调验签失败不拦截（可伪造支付）和续费不顺延（吞用户已付费天数），加上月卡天数写错，这三处直接违背需求单的显式描述，必须先修复才能上线。
