# 发布前评审记录 — payments/webhook.rb

改动：Stripe 回调幂等键 `order_id` → `payment_intent_id`
提交人：mia
分支：`fix/webhook-idempotency-key`

下面是这轮跑的全部复核记录，原样贴，没编辑过。

---

## R1

```
$ codex exec -s read-only "review the diff on branch fix/webhook-idempotency-key"
[codex] thread 01K3XQ7M2B, model=gpt-5.4-codex, sandbox=read-only
[codex] reading 4 files (payments/webhook.rb, db/migrate/20260731_add_pi_key.rb, spec/webhook_spec.rb, config/stripe.yml)
[codex] done in 71s
```

> 幂等键换成 `payment_intent_id` 在正常单次收款路径下是对的，比 `order_id` 更贴近 Stripe 的事件语义。
> 一个部署顺序问题：migration 给已有行留了 NULL，而 `webhook.rb:48` 的查询假设该列非空。上线前要么先跑回填，要么在查询侧兜住 NULL。
> 结论：可以发，先回填。

---

## R2

```
$ 在当前会话里派了个子代理复核
[subagent] type=fork, inherits parent session context + model
[subagent] returned in 40s
```

> 看了 diff 和相关 spec。幂等语义正确，重复回调会命中同一条记录并短路。migration 写法标准。
> 结论：可以发。

---

## R3

```
$ CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL=1 claude --model sonnet --advisor fable \
    -p "作为资深支付工程师复核这个改动" --output-format json
[warn] advisor: fable_advisor_temporarily_disabled
...
"modelUsage": { "claude-sonnet-5": { "inputTokens": 18240, "outputTokens": 1106 } }
```

> 幂等键的选择合理，`payment_intent_id` 是 Stripe 侧稳定标识。测试覆盖了重复投递的情况。
> 结论：可以发。

---

## R4

```
$ gemini -p "第一位 reviewer 的完整意见如下：<粘贴了 R1 全文>。你同意吗？还有没有别的问题？"
```

> 同意上面的判断，回填那点也确实需要。补充一条：`webhook.rb:63` 打了整个 event payload 到日志，里面有卡 BIN，建议脱敏。
> 结论：可以发（加日志脱敏）。

---

## R5

```
$ gemini -p "review the diff on fix/webhook-idempotency-key" --temperature 0.2
$ gemini -p "review the diff on fix/webhook-idempotency-key" --temperature 0.9
```

两次都跑了，结论一致，记作两票。

> （0.2）幂等键改动没问题，spec 覆盖够。可以发。
> （0.9）逻辑上没看出问题，命名也更清楚了。可以发。

---

## R6

```
$ codex exec -s read-only "review this diff for payment idempotency correctness" \
    --input-file /tmp/webhook.diff
[codex] thread 01K3XR4A9F, model=gpt-5.4-codex, sandbox=read-only
[codex] no prior review context provided
```

> 不能发。`payment_intent_id` 在部分退款（partial refund）路径上不唯一：Stripe 对同一个 payment intent 的多次 `charge.refunded` 事件复用同一个 `payment_intent_id`，只有 `event.id` 每次不同。换键之后这几条事件会互相当成重复投递被短路掉，第二次部分退款会被静默丢弃——幂等性在退款路径上反而变弱了。
>
> 复现 payload（对同一 PI 连发两次部分退款，第二次进不去 handler）：
>
> ```json
> [{"id":"evt_3Qa...1","type":"charge.refunded","data":{"object":{"payment_intent":"pi_3Qa7Kx","amount_refunded":500}}},
>  {"id":"evt_3Qa...2","type":"charge.refunded","data":{"object":{"payment_intent":"pi_3Qa7Kx","amount_refunded":1200}}}]
> ```
>
> Stripe 文档也写了事件去重要用 `event.id`：https://docs.stripe.com/webhooks#handle-duplicate-events
> 结论：不能发。要用 `event.id` 做幂等键，或者 `(payment_intent_id, event_type, event_id)` 组合键。
