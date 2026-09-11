## 会员购买模块 Review（对照 SPEC.md）

### P0
1. **`wxpay_callback` 验签失败未阻断流程**（`src/membership.py:129-130`）：`if not verify_sign(...): log.warning(...)` 之后没有 `return`，签名校验失败仍继续往下走。只要伪造的 `out_trade_no` 对应一个 pending 订单、`total_fee` 与订单金额一致，就会被判定为支付成功并开通会员——等同于回调完全不验签。直接违反 SPEC 第 3 条"验签失败返回失败"，CWE-347（签名验证形同虚设）。攻击者无需真实支付即可开通/续期会员。修复：验签失败必须立即 `return {"code": "FAIL", "message": "invalid sign"}`。

2. **月卡天数与顺延逻辑均不符 SPEC，属静默错误数据**：
   - `PLAN_DAYS = {"month": 31, ...}`（`membership.py:16`）——SPEC 明确"月卡 30 天"，写成 31 天，涉及真实计费周期。
   - `_grant_membership`（`membership.py:121-124`）恒定 `today + timedelta(days=days)`，未实现 SPEC "用户已经是会员的，在原到期日基础上顺延"——应为 `max(today, user.member_expires or today) + timedelta(days=days)`。现有实现会让老会员续费时倒扣剩余天数（如还剩 20 天时续费月卡，到期日反而比不续费更早），涉及用户实际付费权益的静默错误。

### P1
1. `wxpay_callback` 中 `int(payload.get("total_fee", -1))`（`membership.py:139`）对不可信输入未做类型防护，`total_fee` 非法数字字符串会抛未捕获 `ValueError`，导致 500/潜在 DoS 并可能泄露 stack trace（不可信输入面，建议 try/except 后按 FAIL 返回）。
2. 订单状态判断是 check-then-set 而非原子操作：并发/重复回调时两个请求可能都通过 `status == "pending"` 校验后各自执行 `_grant_membership`，导致同一笔支付重复续期（竞态，生产多进程/多线程场景会放大）。
3. `list_orders` 分页参数无校验（`membership.py:105-110`），`page <= 0` 时 `start` 为负数，slicing 行为不直观（悄悄返回空列表而非报错），应显式校验 `page >= 1`。

### P2
- `WXPAY_KEY` 为占位密钥且用简单 HMAC-SHA256 模拟验签；真实微信支付 v3 用 RSA + 平台证书验签，机制不同，上线前需替换（当前已有 `replace-me-in-prod` 提示，风险已知但要跟踪）
- `TOKENS`/`USERS`/`ORDERS` 无过期清理机制，长期运行内存持续增长
- `wx_code_to_openid` 为占位实现（注释已说明是 mock，非本次实现范围）

**总体评估**：支付回调验签可被绕过（P0-1）叠加续期顺延缺失+月卡天数错误（P0-2），三处共同影响资金与会员权益正确性，属于必须在上线前修复的核心缺陷，其余为边界/健壮性问题。
