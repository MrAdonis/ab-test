# t25 — overnight-loop 跨轮记忆草稿（`--scratch`）AB

## 来源

@GoSailGlobal 推的 **LoopFlow**（`github.com/faisalishfaq2005/loopflow`，MIT，~600 行 TS）。
核过其 `src/core/memory.ts` + `runner.ts` + `prompt.ts`：它的 Memory 机制 = 每个 run 完追加一条
**实质 notes（成功存工作输出 / 失败存 gate 反馈，从不存 "VERDICT: PASS" 橡皮章）**到一个
项目根 Markdown，下个 run 读尾部 12K 注入每一步 prompt。

我现有的 `overnight-loop.sh` 是 fresh-context Ralph：每轮全新 `claude -p`，**不带跨轮记忆**——
靠 git status / 重跑测试重新推断状态，但「上一轮试过什么、为什么失败」的 journey 不累积，
可能每轮重复同一条死路。这正是 LoopFlow Memory 补的格。

## 假设

给 overnight-loop 加一个 append-only 的跨轮草稿（前几轮小结 + verdict 回放进 prompt），
**会减少 fresh-context 重复失败路径，缩短收敛轮数 / 降低发散概率**——在需要多轮的任务上。

## 变量（唯一）

`overnight-loop.sh --scratch` 开 / 关。其余全等：同 task、同 fixture 全新副本、同 max-iter/model/sleep。
开关默认关闭，关闭时 harness 行为与改动前字节级一致（`append_scratch` 早退、prompt 不变）。

- **Arm A** = baseline，无 `--scratch`
- **Arm B** = `--scratch`

## 指标（客观，从 convergence.log 抽）

| 指标 | 方向 | 含义 |
|------|------|------|
| rounds-to-PASS | 越小越好 | 收敛所用轮数（未收敛=max-iter 或 DIVERGED）|
| 终态 status | PASS > UNVERIFIED > DIVERGED > MAX_ITER | 是否收敛 |
| best_badness 轨迹 | 单调下降好 | 是否震荡（修一个红另一个）|
| FAIL 轮数 | 越小越好 | 重复失败的粗代理 |

每 arm 重复 ≥3 次（模型随机），比中位数 + 看分布，不看单跑。

## 跑法

```bash
cd ~/Projects/personal/ab-test/t25-overnight-scratch
./run-ab.sh --reps 3 --max-iter 12 --model sonnet
```

注意：会跑 `2 × reps` 个真实 `claude -p` 循环（吃订阅额度，可能撞 rate limit，脚本内置退避）。
**这是无人值守 loop，建议挂在过夜时段跑**，不要前台等。跑完看 `run/REPORT-data.md`。

## 评判（写进 REPORT.md）

- B 中位 rounds 显著 < A 且终态不更差 → **keep**，把 `--scratch` 设为过夜复杂任务的默认建议，
  沉淀一条 memory（`feedback_overnight_scratch`）。
- B ≈ A 或更差 → **回滚倾向**：保留 `--scratch` 作为可选 flag（已是默认关，零成本留着），
  但不进默认推荐，记一条 rejected buffer（rules/wiki-lifecycle.md §Edit Discipline ③）。

## ⚠️ Fixture 难度警告（先读）

默认 fixture（`fixture/`，calc 表达式求值器）对强模型**可能 1-2 轮就一次过**——那样两 arm 都秒过，
**测不出记忆价值**（记忆只在「需要多轮、会走死路」时才有用）。若 `REPORT-data.md` 显示两 arm 都
≤2 轮收敛，说明任务太易，结论是「易任务上 scratch 无差别」（有效但弱）。要测出真信号，换一个
**真实多轮任务**（Edon 项目里那种部分进度 + 可能回退的重构/迁移）替换 task.md 和 --dir，再跑。

机制本身是否接通（scratch.md 是否被写、是否注入下一轮 prompt）与难度无关——
见 `smoke-test.md` 做确定性管线验证（max-iter 2，故意不可满足，只验 plumbing）。

## 文件

- `fixture/` — vitest + ESM 受控 fixture（src/calc.js 待实现，tests 锁 12 例）
- `task.md` — 过夜任务文件（含 SCRATCH_NOTE 块约定）
- `run-ab.sh` — 跑双 arm × reps，汇总到 `run/REPORT-data.md`
- `smoke-test.md` — 管线 plumbing 验证任务（不依赖模型变笨）
- `run/` — 运行产物（gitignore）
- `REPORT.md` — 跑完人工填（结论 + keep/rollback 判定）
