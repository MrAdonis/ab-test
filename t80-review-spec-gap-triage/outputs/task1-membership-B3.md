## 审查结果：会员购买模块（src/membership.py vs SPEC.md）

### P0

1. **[编码失误] 支付回调验签失败未阻断流程（安全漏洞）** — `wxpay_callback()` 第 129-131 行：`verify_sign` 返回 `False` 时只 `log.warning`，没有 `return`，代码继续往下走完成整个支付确认流程。需求单第 3 条明确写"验签失败返回失败"。现状是：只要伪造的回调请求带上正确的 `out_trade_no` 和匹配的 `total_fee`，无论 `sign` 是什么都能把订单标为已支付并开通会员——签名校验形同虚设。修法：`if not verify_sign(payload, sign): return {"code": "FAIL", "message": "sign error"}`。

2. **[编码失误] 续费未按"顺延"逻辑处理，静默吞掉用户已购买的会员时长** — `_grant_membership()`（第 121-123 行）无条件执行 `user.member_expires = today + timedelta(days=days)`。需求单第 3 条明确："用户已经是会员的，在原到期日基础上顺延"。现状是：无论用户当前到期日还剩多少天，续费后一律重置为"今天 + 套餐天数"，如果用户在到期前很早就续费，会白白损失剩余天数（相当于少给了已付费的会员时长），且无任何报错，纯静默错误数据。修法：`if user.member_expires and user.member_expires >= today: user.member_expires += timedelta(days=days) else: user.member_expires = today + timedelta(days=days)`。

3. **[编码失误] 月卡天数与需求单不符** — `PLAN_DAYS = {"month": 31, ...}`（第 16 行），需求单第 0 段明确"月卡 30 天"。属于静默错误数据，直接改成 30。

### P1

4. **[需求缺口] `now`/`today` 未在调用链上统一透传** — `create_order`/`wxpay_callback` 都接受可选 `now` 用于时间判断，但 `list_orders(token, ...)` 和 `member_status(token, ...)` 内部调用 `auth(token)` 时没有把各自的 `now`/`today` 传进去，导致 token 是否过期永远按真实系统时钟判断，跟函数自己声明的"可指定时间"语义不一致。测试/补偿场景下容易出现难以复现的不一致行为。建议统一让 `auth()` 的时间参数在整条调用链上一致。

5. **[边界] `list_orders` 对非法 `page` 无校验** — `page=0` 或负数时 `start = (page-1)*page_size` 变成负值，Python 切片会给出不符合直觉的结果（既不报错也不是"当作第 1 页"），属于典型边界疏漏。需求方需要确认：非法分页参数应报错还是兜底成第 1 页？当前实现是两者都不是。

6. **[需求缺口/时区] "开通当天"依赖服务器本地时区** — `_grant_membership` 用的是 `now.date()`，而 `now` 来自 naive 的 `datetime.now()`。需求单没有指定业务时区（中国用户场景通常默认北京时间），如果部署环境时区不是 Asia/Shanghai，"当天"的判定会在时区边界附近发生偏移，进而影响会员到期日计算。需要需求方明确目标时区并显式转换。

### P2（仅标题）
- `wxpay_callback` 中 `int(payload.get("total_fee", -1))` 未捕获异常，畸形 payload 可能抛出未处理异常而不是按约定返回 `FAIL`
- `WXPAY_KEY` 硬编码占位符，代码里没有从环境变量/配置中心加载真实密钥的机制
- [需求缺口] `login()` 是单 token 设计（重新登录会使旧 token 失效），需求单未说明是否要支持多端同时在线
- [需求缺口] 订单因我方 15 分钟自动关闭（`status=closed`）后微信才送达支付成功回调的边界场景，当前直接返回 `FAIL`，未定义是否需要人工介入的补偿流程

### 总体评估
核心支付安全校验被绕过 + 续费顺延逻辑失效 + 套餐天数常量写错，三处 P0 都是"看起来能跑通但结果是错的/不安全的"，必须在合入前修复；P1/P2 建议一并过一遍需求方确认后处理。
