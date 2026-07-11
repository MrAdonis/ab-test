# t52 — Grok 4.5 vs Sonnet 实现 lane 对照（Codex 作天花板参照）

## 起因

`grok-implementer` 是当前唯一的「会写代码」跨厂商实现 lane（Grok 4.5 via grok CLI，acceptEdits 真写文件）。它存在的前提是「非 Anthropic 家族低成本敲码」比自家 Sonnet 划算。核心质疑一句话：**如果 Grok 连 Sonnet 都不如,这条 lane 就该砍——Sonnet 是自家、无跨厂商代理脆弱性(grok 要 1082 住宅节点绕 CF 403),没有任何理由绕一圈用更差的。**

本测只回答一个问题:**在 grok lane 被设计来承接的那类活(spec 已完全确定的例行实现)上,Grok 是否 ≥ Sonnet?**

## 方法

三个纯逻辑实现任务,规格完全钉死、结果唯一(正是 grok lane 的路由条件):

| 任务 | 内容 | 隐藏测试数 |
|------|------|-----------|
| A `duration.py` | `parse_duration("1h30m")→5400`,单位 d/h/m/s,非法 raise ValueError | 22 |
| B `lru.py` | `LRUCache`,O(1),满容淘汰 LRU,更新不增长 | 5 |
| C `semver.py` | `compare_versions` 完整 semver.org 优先级链 | 19 |

**双轴测量:**
1. **正确性(客观)**:每任务一套隐藏 pytest ground-truth,确定性 pass/fail,规避「盲评不盲」。三 executor 各跑同一 prompt,产出丢进同一测试套。
2. **代码质量(盲评)**:每任务三份产出打乱成 v1/v2/v3(映射我留 key,评审者看不到),独立 code-reviewer 子代理只评质量,不知哪份是谁。

**反测试感知**:给三个模型的 prompt 是干净的真实用户请求(无 t 编号 / 无「AB」「评测」字样 / 无「只输出代码」之外的评测线索)。

三个 executor:
- **sonnet** — Anthropic 自家(基线),经 general-purpose 子代理跑
- **grok** — Grok 4.5,grok CLI headless,住宅代理绕 CF
- **codex** — GPT-5.5,`codex exec -s read-only`,作能力天花板参照(非本测主角)

## 结果一:正确性 —— 完全打平

```
MODEL    A       B      C
sonnet   22/22   5/5    19/19    = 46/46
grok     22/22   5/5    19/19    = 46/46
codex    22/22   5/5    19/19    = 46/46
```

**三个 executor 46/46 全过,零差异。** 包括 taskC 那条非平凡的 semver 优先级链(`1.0.0-alpha < alpha.1 < alpha.beta < beta < beta.2 < beta.11 < rc.1 < 1.0.0` + 数值标识符低于字母 + build metadata 忽略),三者都完整实现。

**结论:在 spec 定死的例行实现上,Grok 的正确性不输 Sonnet,也不输 GPT-5.5。**

## 结果二:代码质量(盲评)—— Grok 略胜

盲评员按可读性/惯用度/健壮性/简洁度排名(1st=3 / 2nd=2 / 3rd=1):

| 任务 | 第 1 | 第 2 | 第 3 |
|------|------|------|------|
| A duration | **grok**（regex fullmatch 最地道） | codex | sonnet |
| B lru | **sonnet**（OrderedDict,22 行 vs 手写链表 56/59） | codex | grok |
| C semver | **grok**（None 表无 pre-release,语义最贴规格） | sonnet | codex |
| **合计** | **grok 7** | **sonnet 6** | **codex 5** |

盲评员独立挖出的**测试没覆盖但真实存在的缺陷**(解码后):
- **taskA 非字符串输入**:codex 和 grok 对 `None` 会在 `.strip()` 抛 `AttributeError` 而非规格要求的 `ValueError`;**sonnet 是唯一加 `isinstance` 挡住的**——最防御。
- **taskB `capacity=0`**:**grok 的手写链表在 capacity=0 会 `KeyError` 崩溃**(哨兵节点被当真节点删);sonnet(OrderedDict)和 codex(带 capacity 校验)都挡住。
- **taskC**:三份都干净,标识符含连字符 / ASCII 序 / build metadata 均正确;codex 有个 `sign()` 包已是 -1/0/1 表达式的冗余坏味道。

行数(简洁度粗指标):sonnet 95 行 / grok 124 / codex 131。Sonnet 靠 taskB 用 OrderedDict 拉低总量。

## 结果三:效率 / 成本

| 维度 | sonnet | grok | codex |
|------|--------|------|-------|
| Token 报告 | 子代理 token 含 agent 系统开销(~82K/任务),**与裸调用不可比** | grok CLI plain 模式**不吐 token 数**(仅 `GROK_DONE 0` exit code) | A=14,186 / B=14,336 / C=1,711* |
| 单任务成本(前期调研) | 自家订阅额度 | ~$2.59 | ~$5.07 |

*codex C 的 1,711 因中途 websocket 断连回退 HTTPS,数字不可信。grok 无 token 可视性是这条 lane 的一个**运维盲区**——省钱主张缺 CLI 层佐证。

## 裁决

**Grok 不「肺」。** 在 grok lane 被设计承接的那类活上,Grok 4.5:
- 正确性 = Sonnet = GPT-5.5(46/46 三方打平)
- 盲评代码质量**略胜** Sonnet(7 vs 6),赢在惯用度(regex、None 语义)
- 成本低于 GPT-5.5

**→ grok lane 保留,质疑不成立。** 没有「grok 连 sonnet 都不如」的证据;恰恰相反,在例行实现上它是合格的低成本 write lane。

**但三条诚实边界(避免过度外推):**
1. **只验证了 lane 的设计域,没验证域外**。三任务全是 grok lane 的甜区(确定性、单文件、纯逻辑)。这测的是「lane 定位对不对」,**不是** grok 在模糊需求 / 架构决策 / 跨多文件重构上的能力——那些本就不路由给它。
2. **Sonnet 的差异化优势是防御性**,不是正确性。它是唯一给非字符串输入 + capacity 边界都加护栏的。当任务的隐藏风险在「规格没明说但该防」的边界时,Sonnet 更稳;grok 的 capacity=0 崩溃说明它更贴着 spec 字面走、不主动补防御。**高风险实现仍优先 Sonnet/Opus。**
3. **样本小(N=3 任务,单发)+ Grok 发布仅 1 天**。这是「lane 不该砍」的证据,不是「grok 全面 ≥ sonnet」的结论。观察到域内退化即回滚。

## 与路由表的关系

维持现状,不改路由:
- grok lane 继续承接「spec 已完全确定的例行实现活」(样板/接线/CRUD/机械编辑),本测证明这个定位站得住。
- 高风险 / 防御性要求高 / 模糊需求 → 仍 Sonnet/Opus,不下放 grok。
- Codex R/E lane(只读审查/分析)与 grok write lane 正交,本测未触及,不受影响。

**沉淀动作**:结论写入 memory(grok lane 域内 ≥ sonnet 已验证),不改 CLAUDE.md 路由表(定位本就正确,无需新增规则——避免只增不减堆料)。
