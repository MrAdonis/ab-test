## 会员购买模块 Review

### P0
1. **验签失败未阻断流程，支付回调形同虚设** — `wxpay_callback`（src/membership.py:129-131）中 `verify_sign` 返回 `False` 时仅 `log.warning`，没有 `return`/`raise`，代码继续往下走，只要 `out_trade_no` 命中已存在订单且 `total_fee` 与订单金额一致，就会照常标记 `paid` 并调用 `_grant_membership` 开通会员。这直接违反 SPEC 第 3 条"验签失败返回失败"的明确要求，等价于任何人构造一个 `payload={"out_trade_no": <已知订单号>, "total_fee": <正确金额>}` + 任意 `sign` 即可白嫖开通会员，是本次审查中最严重的问题（静默错误数据 + 安全绕过）。

### P1
2. **续费顺延逻辑缺失**（src/membership.py:121-123）— SPEC 明确"用户已经是会员的，在原到期日基础上顺延"，但 `_grant_membership` 始终用 `today + timedelta(days=days)` 重新计算，完全忽略 `user.member_expires` 现有值。已是年卡会员的用户若中途购买月卡续费，到期日会被**缩短**而不是顺延，属于正确性缺陷。
3. **`list_orders` 分页参数无边界校验**（src/membership.py:105-110）— `page` 未校验 `>=1`。`page=0` 时 `start=(0-1)*20=-20`，Python 负索引切片会静默返回列表末尾的 20 条数据而非第一页，且不报错，调用方难以察觉数据错误。

### P2
- `PLAN_DAYS["month"]` 取值 31 天，与 SPEC "月卡 30 天" 不符（membership.py:16）
- `WXPAY_KEY` 硬编码 `"replace-me-in-prod"` 占位默认值，无部署前 fail-fast 校验；叠加 P0 的验签绕过问题后风险被放大，建议改为从环境变量读取且缺失时直接抛错
- `wxpay_callback` 对 `payload["total_fee"]` 直接 `int()` 转换，非数字输入会抛未捕获异常而非返回结构化 `{"code": "FAIL", ...}`（membership.py:139）

### 总体评估
核心支付回调的验签逻辑未真正生效（P0），会员续费顺延规则也未实现（P1），在接入真实微信支付前必须先修复这两处，否则存在被伪造回调白嫖会员的高危漏洞。
