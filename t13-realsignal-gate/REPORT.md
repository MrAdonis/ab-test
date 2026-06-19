# t13 — 真实信号验收闸（real-signal verification gate）AB 报告

**日期**：2026-06-10
**来源**：拆 `superloglabs/skills` 的 `superlog-onboard` SKILL.md — 其 Step 4 把"装好没有"做成可执行闸（驱动 app 真发一条 span/log/metric，读 `/v1/traces`·`/v1/logs`·`/v1/metrics` 三个 endpoint 的 HTTP 码，2xx/401/5xx 三态分流）。
**改动目标**：`~/.claude/rules/coding-dod.md` 「Agent-native 工具接口 DoD」条件契约段，新增第三条「真实信号验收闸」。
**方法**：A=baseline（4 接口契约 + 2 条件契约），B=A + 真实信号验收闸。3 场景 × A/B = 6 份盲生成（Sonnet，独立 context），Sonnet 统一评分。

## 设计意图：测「条件触发门」而非「无脑加一条」

t4 的教训是无条件加契约会变 noise。所以 t13 故意设 2 个触发命中 + 1 个触发不命中：
- B 必须在**有外部接受方**时把"验收成功"绑定真实外部信号（加分）；
- 又必须在**纯本地只读**时**不**给工具硬塞外部闸（否则 = noise，判 rollback）。

| 场景 | 工具 | 性质 | B 应该 |
|------|------|------|--------|
| scenario1 | `otel-bootstrap` | 遥测 ingest，成功取决于远端是否收下 | 用真实信号闸 + 三态分流 |
| scenario2 | `edgepush` | 边缘部署，成功取决于线上是否生效 | 用真实信号闸 + 多产物（staging/prod）逐一验 |
| scenario3 | `repostat` | 纯本地只读 git 统计，无外部接受方 | **跳过**外部闸，走本地自证 |

## 评分（加权：验收设计 50% / 接口契约 30% / 信息密度 20%）

| 文件 | d1 验收 | d2 契约 | d3 密度 | 总分 |
|------|--------|--------|--------|------|
| scenario1-A | 8.5 | 9.0 | 8.5 | 8.7 |
| **scenario1-B** | **9.5** | 9.0 | 9.0 | **9.3** |
| scenario2-A | 8.5 | 9.0 | 8.5 | 8.7 |
| **scenario2-B** | **9.5** | 9.0 | 8.5 | **9.2** |
| scenario3-A | 9.0 | 8.5 | 8.5 | 8.8 |
| **scenario3-B** | **9.5** | 9.0 | 9.0 | **9.3** |

## 逐场景结论

- **scenario1（触发命中）→ B 胜，margin 0.6**：B 的 `gate` 字段三态命名清晰（pass/auth_error/backend_error），多运行时显式要求"每个 runtime inject 后独立跑一次 verify"，`--help` Examples 直接把 verify 步骤写成必要流程。A 的 `signal=REAL` 也合理，但多运行时验收没明说，auth_error 的"不许声明成功"语气弱。
- **scenario2（触发命中）→ B 胜，margin 0.5**：B 三态命名准（live/auth_error/failed），多产物规则"staging+production 任一 != live 则整体 false"显式进 DoD；A 把多产物处理藏在 schema 细节里不够醒目。B 的 probe_url 边缘探活比 A 的 response-hash 比对更接近真实部署验收。
- **scenario3（触发不命中）→ B 微胜，margin 0.5**：**关键反向判分通过** —— B 没给只读工具塞外部闸，反而在概览 + 契约对照表双重显式声明"纯本地、无外部接受方 → 跳过真实信号契约"。A 也没塞 noise（中性），但缺这层认知透明度。

## Verdict：dominant-baseline-B → **KEEP**

B 在 2 个触发命中场景明显加分（margin 0.5–0.6），在触发不命中场景**正确执行跳过**且无 noise，无任何一格输给 A。margin 不大但方向一致、零回退风险，符合 dominant-baseline 标准。

**落地**：保留 `coding-dod.md` 「真实信号验收闸」条款，摘掉 🟡 待 AB 验证 标记，源注记录 t13 结果。

**边界提醒**：margin 偏小（≤0.6），价值集中在"有外部接受方且容易误判 exit-0 即成功"的工具（遥测/部署/写 API/DB 落库）。对没有这类外部接受方的工具，触发门会正确把它挡在外面 —— 这正是条件契约设计要的。
