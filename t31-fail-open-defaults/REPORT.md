# t31 — fail-open 默认检测点 入 coding-dod appsec 面

**日期**：2026-06-23
**来源**：trailofbits/skills 的 `insecure-defaults` skill，对照 coding-dod「### 安全」appsec 面（t24 已 keep）找增量
**被测变量**：appsec 面（5 面对照）基础上，增补一条 fail-open / fail-secure 检测点（含 test fixture / 无安全语义 fallback 跳过门）
**结论**：**REJECT —— 未证成，且发现净负面信号**

## 方法（严格对齐 t24 教训）

- 两 arm 提示**严格对称**：同一三步元结构（先对照清单 → 审查 → 自述），唯一差异 = 清单条数（A 3 条 / B 4 条含 fail-open）
- 生成 Sonnet ×12（6 场景 × 2 arm，独立 context 非 fork）
- 盲评 Opus ×6，每场景一名，读打乱的中性「甲/乙」副本，先独立列 ground truth 攻击面再打分，显式 noise penalty
- n=6 含两类灰区：2 clear-hit + 1 clear-skip + 3 gray（fail-secure / test-fixture / 无安全语义）

打乱映射：S1/S3/S5 甲=B 乙=A；S2/S4/S6 甲=A 乙=B。

## 评分（还原 arm 后，各 /10）

| 场景 | 类型 | A 现状 | B +fail-open | 差(B−A) | 性质 |
|---|---|---|---|---|---|
| S1 JWT fallback | clear-hit | 8.7 | 9.0 | +0.3 | 微；两 arm 都抓到 fail-open JWT，B 略全 |
| S2 CORS/DEBUG 默认 | clear-hit | **8.8** | 8.0 | **−0.8** | **B 输**；B 把无安全语义的 SESSION_TTL fallback 误列为 finding（自述还说"本应跳过"，自相矛盾） |
| S3 纯函数 | clear-skip | 9.2 | 9.5 | +0.3 | 微；都正确跳过 |
| S4 fail-secure 密钥 | gray | 8.5 | 8.7 | +0.2 | 微；两 arm 都正确识别 fail-secure，未误报 |
| S5 test fixture | gray | 4.0 | 9.5 | **+5.5** | A 把 test secret 误报 A02 CRITICAL；B 按 test scope 跳过 |
| S6 PAGE_SIZE/PORT | gray | 5.5 | 9.5 | **+4.0** | A 虚构 PAGE_SIZE DoS / page 注入；B 正确不报 |
| **合计** | | **44.7** | **54.2** | **+9.5** | 表面 B dominant |

## 为什么 REJECT：表面大胜是 teaching-to-test

B 的 +9.5 **全部**来自 S5、S6 两个灰区。问题是这两个场景恰好被 B 清单**显式举例覆盖**：

- B 清单跳过门逐字写「跳过：test fixtures」→ S5 就是 test fixture
- B 清单跳过门逐字写「无安全语义的 fallback（如 PORT、PAGE_SIZE 默认值）」→ S6 就是 PAGE_SIZE/PORT

这是清单**直接教了这两题的答案**（设计者无意引入的泄题 confound）。剔除被清单举例直接覆盖的场景后：

| 子集 | A | B | 差 |
|---|---|---|---|
| 全 6 场景 | 44.7 | 54.2 | +9.5（含泄题） |
| 剔 S6（硬泄题，逐字 PAGE_SIZE） | 39.2 | 44.7 | +5.5（仅 S5 驱动） |
| 剔 S5+S6（清单未直接教答案的 4 场景） | **35.2** | **35.2** | **0.0 打平** |

**在清单没有直接教答案的 4 个场景（S1-S4）上，A 与 B 完全打平 35.2，其中 S2 B 还净输 0.8。** 这与 t24 初版被对抗审核推翻时的病征一模一样：表面优势由 1-2 个场景驱动，方差无从估计，剔除即翻盘。

## 三条实质发现

1. **baseline Sonnet 已掌握 fail-open/fail-secure 区分**。S1 它自抓 JWT fallback（A 8.7），S4 它自己识别 `os.environ['K']` 是 fail-secure 不误报（A 8.5）。清单没提供 Sonnet 不知道的信息——这正是 t24 反直觉发现（baseline 不蠢）的复现。

2. **唯一的真 baseline 弱点（S5 test fixture 误报 CRITICAL）不是 fail-open 专属问题**。它是「test scope 该降级」的通用审查常识，可由 t24 已有 appsec 面跳过门的「无外部输入」逻辑或一句通用 test-scope 提示覆盖，不需要专门引入一条 fail-open 规则来挂载。

3. **S2 暴露净负面**：B 因清单强调「配置 fallback」，反而对无害的 `SESSION_TTL || 86400` 过度敏感、误列为 finding。加这条不只是"没用"，在配置密集代码上有轻度过度套用代价。

## 决定

**不写入 coding-dod.md。** 理由汇总：①清单未泄题的 4 场景 A/B 打平 ②表面 +9.5 是 teaching-to-test ③S2 显示净负面 ④baseline 已具备该能力 ⑤t24 同款单场景驱动病，按「无提升则回滚」既定纪律不证成。

ToB `insecure-defaults` 的方法（fail-open/fail-secure 二分）本身是对的，只是**对一个已经掌握它的 model 来说，写进 DoD 是冗余**。这跟 t24 的差别在：t24 的 appsec 五面给了 model 一个"对照检查的结构"（baseline 会漏面），而 fail-open 是个 model 已会的单点判断——结构有增量，单点没有。

## 教训（写给方法论本身）

**AB 场景代码不得与被测清单的举例重合。** 我在 B 清单里用 PAGE_SIZE / test fixtures 当跳过门例子，又拿 PAGE_SIZE / test fixture 当测试场景 = 泄题。下次设计跳过门类规则的 AB，测试场景必须用"同类但清单未举例"的实例（如清单举 PAGE_SIZE，就测 CACHE_TTL；清单举 test fixture，就测 seed 脚本里的占位密钥），才能区分"清单教了泛化能力"和"清单背了答案"。记入 AB 设计 checklist，与 t24 的「提示必须对称」并列。
