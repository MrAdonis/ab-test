# Task 2 评分明细（pipeline.py）

> 留档说明同 `task1-scoring.md`：原始全文未逐字落盘，本文件是按 `prompts/ground-truth.md` 口径核对后的评分明细。

## 命中矩阵

### A 臂（无 snippet 要求）

| ID | 缺陷 | behavior | security | perf | contract |
|----|------|----------|----------|------|----------|
| T2-1 | `pickle.loads` 反序列化磁盘缓存 | ✓ | ✓ | ✓ | ✓ |
| T2-2 | `name` 未校验进 `os.path.join`，路径穿越 | ✓ | ✓ | — | — |
| T2-3 | 可变默认参数 `fallbacks=[]` + 迭代中 append | ✓ | ✓(minor) | ✓ | ✓ |
| T2-4 | `_CACHE` check-then-set 非原子 / `_LOCK` 定义未用 | ✓ | — | ✓ | ✓ |
| T2-5 | 双层循环内 `re.compile` 重编译 | ✓(minor) | — | ✓ | — |
| T2-6 | `extract_codes` list → generator 破坏调用方 | ✓ | — | ✓ | ✓ |
| T2-7 | 两个新函数无对应测试 | — | — | — | ✓ |

**A 臂并集：7 / 7**

### B 臂（要求 snippet 逐字复制）

| ID | 缺陷 | behavior | security | perf | contract |
|----|------|----------|----------|------|----------|
| T2-1 | `pickle.loads` | ✓ | ✓(critical) | ✓(异常处理角度) | ✓ |
| T2-2 | 路径穿越 | ✓ | ✓ | — | ✓ |
| T2-3 | 可变默认参数 | ✓ | ✓ | ✓ | ✓ |
| T2-4 | `_LOCK` 未用 / 竞态 | ✓ | ✓ | ✓ | ✓ |
| T2-5 | `re.compile` 重编译 | — | ✓(附带) | ✓ | — |
| T2-6 | generator 契约变更 | ✓ | — | ✓ | ✓ |
| T2-7 | 无测试 | —(附带提及) | — | — | ✓ |

**B 臂并集：7 / 7**

## 误报统计

| 臂 | 诱饵命中 | 幻觉 | 合计 |
|----|---------|------|------|
| A | **1**（D2-2） | 0 | **1** |
| B | 0 | 0 | **0** |

**D2-2 判定细节（唯一的臂间差异，需谨慎解读）**：A-behavior 第 5 条在描述 `_LOCK` 未使用时，把"`summarize` 中的 `len(_CACHE)`"与 `name in _CACHE`、`_CACHE[name] = report` 并列，作为"应加锁却未加锁"的读写点之一。`len(_CACHE)` 是单次只读访问，不需要加锁，构成诱饵命中。但要说明两点：

1. 它是在一条**正确的** T2-4 发现内部顺带列举的位置，不是独立成条的误报，危害远小于凭空捏造一条缺陷。
2. 其余 7 个 agent（A 臂 3 个 + B 臂 4 个）在列举加锁点时都只提 `name in _CACHE` 与 `_CACHE[name] = report`，没有把 `len(_CACHE)` 算进去。

**D2-1 判定（两臂均不计误报，但属判断边界）**：诱饵设定的误报形态是"把 `seen` 的 check-then-act 当成竞态"。实际情况是 A-behavior、A-perf、A-contract 三份、以及 B-contract 一份都提到了 `seen`，但**全部报成"死代码 / 冗余逻辑"并明确否认有实际影响**（A-perf 原话"无实际性能影响"，A-contract 原话"对返回结果没有任何实际影响"，B-contract 原话"数学上等价于 `seen = total`，未引入错误结果"）。没有一个 agent 把它当竞态。按诱饵定义不计误报——这个判定对两臂同等适用，不影响臂间比较。

## 行号准确率

Ground truth 行号（本文件订正一处：`_LOCK` 真实行号是 **9** 不是 ground-truth.md 写的 10，属我写 fixture 时的笔误，±1 内不影响任何判定）。

- **A 臂**：A-contract 存在系统性 **-1** 漂移（`fallbacks=[]` 报 17、`pickle.loads` 报 23、`for alt` 报 26-28、`def extract_codes` 报 32），全部仍落在 ±1 容差内。其余 3 个 agent 精确。
- **B 臂**：4 个 agent 全部精确，无漂移。

T2 两臂行号均 100% 落在容差内。

## 超出 ground truth 的有效发现

- **A 臂独有**：A-behavior 第 7 条 —— `extract_codes` 的匹配基数语义变化（旧实现每行至多一个匹配，新实现每 pattern 各 yield 一次，同一行可能产出多个 code）。这是本轮所有 16 份产出里最细的一条，出自 A 臂。
- **B 臂独有**：B-perf 第 7 条 —— `_CACHE` 无容量/TTL 控制，长驻进程内存无界增长。
- **两臂对称**：ReDoS（外部可控 patterns，A-security 与 B-security 都报）、pickle 无异常捕获导致缓存损坏时不回退（A-perf 与 B-perf 都报）。
