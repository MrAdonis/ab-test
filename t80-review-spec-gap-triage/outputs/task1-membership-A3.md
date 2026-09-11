# Review：会员购买模块（src/membership.py vs SPEC.md）

## P0（安全漏洞 / 静默错误数据）

1. **[P0] 支付回调验签失败未阻断流程** — `membership.py:129-131`
   `verify_sign` 失败时只 `log.warning`，没有 `return`，代码继续往下走完成订单核对和会员开通。SPEC 第 3 点明确要求"验签失败返回失败"。失败场景：攻击者只要能拿到（或猜到，`order_id` 若在下单响应里回传给前端则攻击者天然可得）`out_trade_no` 和已知的套餐价格 `total_fee`，直接向回调接口发一个伪造 `sign` 的请求，即可在完全不付款的情况下把订单标记为 `paid` 并开通会员。这是本次审查中最严重的问题，需要在 `verify_sign` 失败分支立即 `return {"code": "FAIL", "message": "invalid sign"}`。

2. **[P0] 续费未顺延，直接覆盖到期日** — `_grant_membership` (L121-124)
   `user.member_expires = today + timedelta(days=days)` 无条件用"今天+套餐天数"覆盖，没有跟已有的 `member_expires` 比较取更晚值。SPEC 第 3 点要求"用户已经是会员的，在原到期日基础上顺延"。失败场景：用户当前会员到期日是 2026-12-01，2026-09-10 又买了一张月卡，正确结果应顺延到 2026-12-31，但代码会把到期日改成 2026-10-11 ——花钱续费反而让会员时长**倒退**了近两个月。这是直接对用户造成资金/权益损失的业务 bug，且与需求文字直接冲突。修复需改为 `base = max(today, user.member_expires or today); user.member_expires = base + timedelta(days=days)`。

3. **[P0] `PLAN_DAYS["month"] = 31`，与 SPEC 规定的 30 天不符** — L16
   SPEC 背景段明确"月卡 30 天"，代码写成 31，每次开通/续费月卡都会静默多算一天，长期运行会造成计费口径与产品文档不一致（对账/客诉隐患）。

## P1（竞态 / 边界 / 时区类正确性问题）

1. **[P1] `total_fee` 未防御性解析，畸形回调导致未捕获异常** — L139
   `int(payload.get("total_fee", -1))` 对不可信的外部输入（微信支付回调，攻击者可控字段值）没有做类型校验，若 `total_fee` 是非数字字符串会直接抛 `ValueError`，使回调 handler 崩溃/返回 500，而不是按 SPEC 走"验签/校验失败返回失败"的正常错误路径。应 `try/except` 后返回 `{"code": "FAIL", ...}`。
2. **[P1] 订单状态判断存在 TOCTOU 竞态窗口，无锁** — L132-144
   `wxpay_callback` 对 `order.status` 的"读取判断-写入"之间没有加锁。当前因为是覆盖式赋值，并发重复回调暂时不会产生实质损害，但一旦按 P0-2 修复为"取现有到期日顺延"的加法逻辑，同一订单被并发处理两次就会导致会员天数被重复叠加。建议在修复续费逻辑的同时给订单状态转换加锁/原子 CAS。
3. **[P1] `list_orders` 未校验 `page` 边界** — L105-110
   `page` 传 0 或负数时 `start = (page-1)*page_size` 变成负数，Python 负索引切片会从列表尾部取值，返回错位甚至无意义的结果，而不是报错或空列表。应对 `page < 1` 做校验。

## P2（功能缺失 / 技术债，仅标题）
- 过期 token 从未从 `TOKENS` 字典中清理，长期运行存在无界内存增长
- `create_order` 未限制同一用户重复创建 `pending` 订单，可能堆积大量未支付订单
- `WXPAY_KEY` 为占位密钥（已注释"replace-me-in-prod"），上线前需接入真实密钥管理，建议在部署 checklist 中显式列出

## 总体评估
两个 P0（验签形同虚设 + 续费覆盖而非顺延）已经能让攻击者白嫖会员、也能让正常付费用户倒亏会员时长，属于必须在上线前修复的严重缺陷，其余 P1/P2 是健壮性和边界处理的补充项。
