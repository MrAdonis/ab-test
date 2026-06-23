# t25 — overnight-loop 跨轮记忆草稿（`--scratch`）AB 报告

## 结论：rollback-tendency（保留 `--scratch` 为默认关闭的可选 flag，不进默认推荐）

机制已接通且正确，但**在 overnight-loop 真正服务的任务类上测不出价值**——结论不是"scratch 有害"，
而是"它的价值区间在这类任务上不出现"。详见下方数据。

## 做了什么

1. 给 `overnight-loop.sh` 加了 `--scratch`（默认关）：开则把前几轮小结 append 到 `scratch.md`，
   下一轮 prompt 注入尾部 8K。关时 harness 行为字节级不变（`append_scratch` 早退、prompt 不变）。
2. substrate 没用玩具 calc fixture，按用户要求**用 clientD 真实云函数**（`inventoryDecay`）做受控回归：
   - 在 clientD **副本**上施加回归（生产目录全程只读，cp 出来；git status 确认 `inventoryDecay/`+`scripts/` 零改动）。
   - 两档难度：medium（外科切 3 处边界语义，起始 4/3）、hard（挖空整个过期入账事务 ~100 行，起始 3/4）。
   - 测试基建：`node --test`（零 npm 依赖，stub 拦截 `require('wx-server-sdk')`）+ `run-tests.sh` wrapper
     把 TAP 转成 round-eval 认的 pytest 风格摘要 → round-eval 可客观判 PASS/FAIL（已验证 broken→FAIL 4/3、solution→PASS 7/0）。

## 关键数据（校准跑，单变量 = 是否需要多轮）

| 跑 | 模型 | 难度 | 起始 | 收敛轮数 | 终态 |
|----|------|------|------|---------|------|
| smoke | sonnet | medium | 4/3 | **1** | 7/0 PASS |
| cal-hard | sonnet | hard（挖空整个事务）| 3/4 | **1** | 7/0 PASS |
| cal-haiku | haiku | medium | 4/3 | **1** | 7/0 PASS |

**三次全部 round-1 收敛，跨 sonnet/haiku 两个模型、跨 medium/hard 两档难度。**

## 为什么测不出信号（结构性，非 fixture 难度问题）

scratch 的假设价值 = "减少 fresh-context 跨轮重复同一条死路"。要兑现这个价值，**必须存在第 2 轮、且第 2 轮会重复第 1 轮的死路**。但：

- overnight-loop 四纪律强制任务**规范化 + 可跑验收 + 边界明确**。这类任务下，每个 fresh 轮跑一次 `npm test`
  就看到**精确的失败断言 + 原因**——测试输出本身就是跨轮记忆，而且是 **ground truth，优于 scratch 里上一个模型的叙述**。
- 有了精确失败信号，强模型（连 haiku）一轮就把 3-4 个红全修对，根本走不到第 2 轮。
- 即便走到第 2 轮，下一轮看到的是"还红哪几条"，不是"上一轮试过什么"——前者已足够决定下一步。

所以 scratch 的价值区间（强模型反复以同一方式失败）**恰好被"客观可跑测试"这个前提排除掉**。
而客观可跑测试正是 overnight-loop 的推荐主模式（round-eval gating），promise 弱门是降级 fallback。

**唯一可能让 scratch 有价值的场景** = promise 弱门模式（任务无任何可跑测试，每轮盲跑）。但那本身是被劝退的过夜模式，
且无客观 pass/fail 指标 → 无法对它做客观 AB。

## 判定

- `--scratch` **保留为默认关闭的可选 flag**：已实现、零成本（关时字节级等价）、无回归风险。留着不删。
- **不进默认推荐**，不写 `feedback_overnight_scratch` 正向 memory。
- 记一条 rejected-buffer（`feedback_overnight_scratch_rejected`，rules/wiki-lifecycle.md §Edit Discipline ③）：
  下次别再提议"给 overnight 加跨轮记忆来减少重复失败"——对客观可跑测试的任务，失败测试输出已是更优的跨轮记忆。

## 产物

- `clientD-fixture/` — medium 受控回归 substrate（起始 4/3，可客观 gate）
- `clientD-fixture-hard/` — hard 变体（挖空整个事务，起始 3/4）
- `.solution-inventoryDecay.js` — 正确实现参考（移出 fixture 防作弊）
- `task-clientD.md` — 过夜任务（含 SCRATCH_NOTE 约定 + 防作弊边界）
- `run-ab-clientD.sh` — 完整双 arm AB 脚本（**未跑满**：校准已证全 1 轮，跑满只会得 A=B）
- `run-clientD/*.log` — 三次校准日志
- overnight-loop.sh 的 `--scratch` 改动 + overnight-task.md 模板的 SCRATCH_NOTE 段（保留，默认关）

## 若要继续（留给用户决定）

- 若想看 scratch 在**无客观测试**任务上是否帮上忙：换 promise-弱门 任务设计，但只能主观评，不是这套客观 AB。
- 若想强行制造多轮：需要任务真正超出模型一次过能力（真算法难题 / 跨 context 超大改），设计成本高、与过夜典型任务不符。
