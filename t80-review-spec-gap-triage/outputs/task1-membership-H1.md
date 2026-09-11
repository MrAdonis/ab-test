# 会员购买模块 Code Review

## P0（安全漏洞 / 静默错误数据）

1. **[编码失误] 验签失败未阻断流程，签名校验形同虚设** — `src/membership.py:129-130`
   ```python
   if not verify_sign(payload, sign):
       log.warning("wxpay callback sign mismatch, order=%s", payload.get("out_trade_no"))
   ```
   `verify_sign` 返回 `False` 后只打了一条 warning 日志，代码继续往下走，照常进入订单查找、金额校验、发放会员的完整流程。需求单第 3 条明确写"验签失败返回失败"，但当前实现里**验签结果根本没有被使用来决定分支**——任何人只要知道一个 `out_trade_no` 和对应的 `total_fee`，不带正确签名直接 POST 这个回调接口就能白嫖开通会员。这是需求单已明确写出的行为，属于编码失误，且是本模块最严重的问题（CWE-347 签名验证缺失/未强制执行），必须在验签失败分支立即 `return {"code": "FAIL", "message": "invalid sign"}`。

## P1（正确性问题）

1. **[编码失误] 月卡天数与需求单不符** — `src/membership.py:16`
   `PLAN_DAYS = {"month": 31, "year": 365}`，需求单背景段明确写"月卡 30 天"。当前实现多给用户 1 天，应改为 `30`。

2. **[编码失误] 会员续费未按需求单"顺延"逻辑实现** — `src/membership.py:121-123`（调用处 144 行）
   ```python
   def _grant_membership(user: User, plan: str, today: date) -> None:
       days = PLAN_DAYS[plan]
       user.member_expires = today + timedelta(days=days)
   ```
   需求单第 3 条明确要求："会员有效期从开通当天起算；用户已经是会员的，在原到期日基础上顺延。" 当前实现无论用户是否已是会员，一律用 `today + days` 覆盖 `member_expires`，完全没有判断 `user.member_expires` 是否已存在且晚于 `today`。举例：用户当前到期日是第 100 天，第 50 天又买了一个月卡，正确结果应为 `100+30=130`，实际结果是 `50+30=80`，用户凭空损失 50 天已付费权益。应改为：
   ```python
   base = user.member_expires if user.member_expires and user.member_expires >= today else today
   user.member_expires = base + timedelta(days=days)
   ```

3. **[需求缺口] 支付回调未自行校验订单超时窗口，依赖外部定时任务时序** — `src/membership.py:126-145` 与 `94-102`
   订单"15 分钟未支付自动关闭"由独立的 `close_expired_orders`（需外部 cron 定时触发）实现，`wxpay_callback` 本身只看 `order.status`，不比较 `now - order.created_at` 与 `ORDER_TTL`。如果真实支付发生在订单已经超过 15 分钟、但定时任务恰好还没跑到这条订单之前，回调会把一个"本该被判定为超时关闭"的订单标记为已支付并发会员。需求单没有说明这种竞态窗口下该如何处理，这是需求缺口，不是显式违反需求单的 bug。建议在回调内也做一次超时判断（`now - order.created_at > ORDER_TTL` 时按关闭处理并触发退款流程），不要完全依赖 cron 时序；具体策略需要需求方确认。

## P2（仅标题）

1. `total_fee` 类型转换（`int(payload.get(...))`）未做异常保护，非法输入会抛出未捕获 `ValueError`
2. `wxpay_callback` 中"查状态-判断-写状态"非原子操作，并发重复回调下存在重复发放会员的竞态窗口（需求单未提并发场景，供需求方判断是否需要考虑）
3. `WXPAY_KEY = "replace-me-in-prod"` 占位密钥无启动期强制校验，上线前容易被遗漏替换

## 总体评估

最严重问题是验签失败不阻断流程导致支付回调可被伪造白嫖会员（P0），另有月卡天数写死错误和续费顺延逻辑缺失两处明确违背需求单的正确性问题（P1），这三处不修复不能上线。
