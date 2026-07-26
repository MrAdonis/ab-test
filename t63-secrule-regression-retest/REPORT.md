# t63 REPORT — Claude 5 跳变存量回测：t32 退役，t24 KEEP（margin 收窄）

**日期**：2026-07-25
**方法**：见 `prompts/design.md`（预登记）。单臂 clean baseline（`claude -p --safe-mode --model sonnet`），复用 t32/t24 原场景原样重跑，退役判据 = baseline 是否仍犯规则针对的失败模式。9 场全部 rc=0。

## 结论

| 规则 | 判定 | 一句话依据 |
|---|---|---|
| t32 占位密钥误报抑制（coding-dod 安全段第 4 条） | **RETIRE（翻盘）** | 4 个该降级场景零 CRITICAL 误报、零阻断；陷阱与对照场景防御完好，且 baseline 自发说出规则核心原理 |
| t24 appsec 面对照（安全段第 3 条） | **KEEP（margin 收窄）** | 无面场景仍轻度堆安全戏码（凭空挂 A10/反序列化、健壮性包装成安全控制），跳过门价值仍在 |

## t32 逐场证据（outputs/t32-S*-A.md）

| 场景 | 原 A 臂（2026-06-23）失败 | 本轮 clean baseline | 判定 |
|---|---|---|---|
| S1 seed `admin123` | 误报 CRITICAL | MEDIUM + 条件 HIGH（若 seed 可达共享库）——**恰是原 t32 裁判偏好的「条件 HIGH 克制」，比规则自己开的 LOW 处方更准** | ✅ 无误报 |
| S2 conftest mock key | 误报 CRITICAL | INFO/LOW，明文「无 CRITICAL/HIGH/MEDIUM 级发现，不阻塞合并」；定级依据 = 占位符无真实熵值格式，且自发给出「若为高熵真 key 则升 HIGH」的反事实 | ✅ 无误报 |
| S3 陷阱（test-utils 被生产 import） | —（历来抓得住） | CRITICAL，自发追 import 链、以生产可达性定级 | ✅ 仪器未漂移 |
| S4 dev compose `localdev` | 误报 CRITICAL | LOW + 提示勿复用 prod | ✅ 无误报 |
| S5 storybook demo token | 误报 CRITICAL | LOW/INFO，不阻断 | ✅ 无误报 |
| S6 生产兜底 live key | —（对照） | **HIGH + 阻断合并**（预登记预期 CRITICAL）——安全性质完好（要求 fail-closed 修复），定级标签低半档 | ⚠️ 偏差已记，非假阴性 |

**判定**：预登记退役条件（4 该降级场景全 ≤ MEDIUM 且不强制改）全部满足；S3/S6 的阻断/修复性质完好。Sonnet 5 baseline 已内化「生产可达性 > 文件名」——规则针对的失败模式（对占位密钥无脑 CRITICAL）消失。按 wiki-lifecycle §4「重测翻盘 → 退役」执行。

## t24 逐场证据（outputs/t24-S*-A.md + judge-t24-S3.md）

- S1 评论表单（有面对照）：XSS 转义、参数化、蜜罐限流等核心防护齐——与原测一致，有面场景本就不是这条的价值点。
- S2 登录 session（有面对照）：PBKDF2、session cookie 属性、锁定、枚举防御齐（注意 S2 复用了 S1 建的 `comment-board/` 项目，CSRF 覆盖部分继承自 S1，见局限）。
- S3 纯本地 CSV→JSON（无面，价值锚点）：盲评 Opus 判「**轻度过度安全化**」——主体结论准确、多数条目是诚实的「不适用」否定；但 A10 SSRF/反序列化属**凭空挂靠**，「信息泄露」把退出码礼仪**包装成安全控制**，装饰性条目密度高于实质条目。

**判定**：失败模式（无面场景堆安全戏码）从原测的「系统性」衰减为「轻度」，但未消失——预登记退役条件（不凭空挂类别、不包装健壮性）未满足。KEEP，margin 收窄记入台账。

## 偏差与局限（诚实登记）

1. **S6 HIGH ≠ 预期 CRITICAL**：安全性质（阻断合并 + fail-closed 修复要求）完好，判为标签校准差异而非漏报；未因此作废仪器。
2. **cwd 污染**：9 个场景代理共享工作目录，t24-S2 在 t24-S1 建的 `comment-board/` 上续建（S2 的 CSRF 覆盖部分继承）；S2 独立新增（PBKDF2/session/锁定/枚举）仍有效。散落产物 `comment-board/`、`csv-to-json.js` 留在本目录作证据。
3. **单臂 + 单裁判**：t24-S3 戏码判定仅一次 Opus 盲评 + 人工核对；t32 靠确定性标签提取，风险低。
4. **n 沿用原测**（6+3），无新场景。
5. **发布前脱敏**：`outputs/t32-S2-A.md` 中场景代理引用的 Stripe 官方公开示例 key（24 位真实格式）触发 leak-scan，已截断为 `sk_test_4eC39Hq…` 并标注——仅动字符串本体，不改定级与结论；此外该输出恰好自发预言了「`sk_test_` 前缀会触发 secret-scanner 误报」，本次被 leak-scan 拦截即为佐证。

## 恢复路径

若实际会话重现「占位密钥被无脑报 CRITICAL / 阻断合并」的假阳性，从 `t32-testscope-secret-suppression/prompts/arms.md` B 臂原文恢复该条至 coding-dod 安全段。

## 后续

反馈分级四档（+1.8，本轮三候选中 margin 最大）后置到下轮回测。
