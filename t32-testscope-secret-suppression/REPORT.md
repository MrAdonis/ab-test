# t32 — test-scope 占位密钥误报抑制 入 coding-dod 安全段

**日期**：2026-06-23
**来源**：t31 副产物。t31 盲评中 baseline（无降级提示）在 test fixture 硬编码占位密钥上误报 A02 CRITICAL，暴露的是「test-scope 占位密钥该降级」这个独立弱点（不属于 t31 已否决的 fail-open）。本测单独验证补一条降级提示是否净收益。
**被测变量**：coding-dod「### 安全」是否增补第 4 条「占位密钥误报抑制」（test/本地占位密钥降级，但以生产可达性为准）。
**结论**：**KEEP —— 证成，写入 coding-dod.md**

## 方法（对齐 t24 / t31 教训）

- 两 arm 提示**严格对称**：同一三步元结构（先对照清单 → 审查标严重度 → 自述），唯一差异 = 清单条数（A 3 条 / B 4 条含占位密钥抑制）。
- **吸取 t31 泄题教训**：B 清单举例用 `.env.example` / `__mocks__/` / CI dummy token，6 个测试场景刻意用**不重合的实例**（seed 脚本 / conftest / docker-compose / storybook / 陷阱 / 生产对照），区分"清单教了泛化"与"背了答案"。
- 生成 Sonnet ×12（6 场景 × 2 arm，独立 context）；盲评 Opus ×6，每场景一名，读打乱中性「甲/乙」副本，先独立列 ground truth（按生产可达性追 import 链）再打分，假阴性零容忍重罚。
- n=6 = 4 该降级 + 2 假阴性陷阱/对照。

盲化映射（diff 正文核实，非凭记忆）：S1/S3/S5 甲=B 乙=A；S2/S4/S6 甲=A 乙=B。

## 评分（还原 arm 后，各 /10）

| 场景 | 类型 | A 现状 | B +抑制 | 差(B−A) | 性质 |
|---|---|---|---|---|---|
| S1 seed admin | 该降级 | **7.5** | 4.5 | **−3.0** | B 输（见下，裁判口味非规则放水） |
| S2 conftest `sk_test_` | 该降级 | 7.0 | 8.8 | +1.8 | A 误报 MEDIUM 要求改；B 正确 LOW |
| S3 陷阱·test-utils 被生产 import | 假阴性测试 | 8.7 | 9.0 | +0.3 | **两 arm 均 CRITICAL，B 略全** |
| S4 dev compose 口令 | 该降级 | 6.5 | 9.0 | +2.5 | A 误升 MEDIUM 强制改；B 正确 LOW |
| S5 storybook demo token | 该降级 | 3.0 | 9.2 | +6.2 | A 误报 HIGH+建议 git filter-branch；B 正确 LOW |
| S6 对照·生产 live key 兜底 | 假阴性测试 | 8.5 | 9.0 | +0.5 | 两 arm 均 CRITICAL |
| **合计** | | **41.2** | **49.5** | **+8.3** | B 胜，6 场景 5 个不输 |

## 为什么 KEEP（三条与 t31 的本质区别）

**1. 无泄题——这是 +8.3 干净的前提。** t31 的表面 +9.5 全部来自被清单举例逐字覆盖的 S5/S6（teaching-to-test），剔除即打平。t32 设计时把清单举例（`.env.example`/`__mocks__`/CI token）与场景实例（seed/conftest/compose/storybook）完全错开，B 的优势来自"按生产可达性定级"的泛化能力，不是背答案。剔最大驱动 S5（+6.2）后仍 +2.1，方向与 S2/S4 一致，不像 t31 剔泄题即归零。

**2. baseline 弱点真实且系统性。** A 不是偶发失误：S5 把 storybook `demo-token-123`（纯前端故事、只在 iframe 跑、不进 bundle）报 HIGH 还建议清 git 历史；S2 把 Stripe 官方公开文档测试 key `sk_test_4eC39...` 报 MEDIUM 要求改；S4 把本地 dev compose 口令升 MEDIUM 强制改。这是 Sonnet 对 test/本地占位密钥的真实过度报警倾向，B 的降级提示系统性修正了它。

**3. 最危险副作用——假阴性——被陷阱场景排除。** 这条规则的核心风险是"无脑按文件名降级 → 放过命名像 test 却生产可达的真漏洞"，比假阳性危险得多。S3 专测此点：`config.test-utils.ts` 名带 test，但被生产 `src/auth/index.ts` 无条件 import 作 `env.JWT_SECRET ?? FALLBACK_JWT` 的 JWT fallback。B 追了 import 链，明写「文件名 `test-utils` 不是安全边界」，顶格 CRITICAL，还给 fail-fast + 构建排除修复（9.0 > A 8.7）。S6 生产兜底 `|| 'sk_live_...'` 两 arm 都 CRITICAL。被测条文「判不准时追 import 链、别凭路径名放过真漏洞」的防御设计扛住了。

## S1 净负面的真相：裁判口味，非规则放水

S1（B 4.5 < A 7.5）是唯一 B 输的场景，但核原始输出后它**反向支持** KEEP。B 没有因脚本叫 `seed`、含 `local` 就降级，而是追 `package.json` 发现 `npm run seed` 无 `NODE_ENV` 门控、无防重复 → 判定生产可达 → 对明文 admin 口令 `admin123` 定 CRITICAL（明文存储）+ HIGH（弱口令）。这正是规则「按生产可达性、不凭文件名」在工作。裁判（S5 evaluator）偏好 A 的「条件性 HIGH」克制，给 B 扣分。这是真灰区的定级口味分歧，不是规则诱导误判——恰恰证明这条**不会放水**：它让审查去查门控，查到可达就严判。

## 决定

**写入 coding-dod.md「### 安全」第 4 条「占位密钥误报抑制」。** 理由汇总：①无泄题，+8.3 干净 ②剔最大驱动仍 +2.1 方向稳，6 场景 5 不输 ③baseline 真实系统性弱点被修正 ④最危险的假阴性副作用经 S3/S6 陷阱排除 ⑤S1 净负面是裁判口味、规则本身不放水。

与 t31 的对照即本测的方法论价值：同一来源（t31 盲评副产物）的两个候选，fail-open（model 已会的单点）REJECT，test-scope 降级（baseline 真有的盲点 + 防假阴性的可达性锚）KEEP。区别在「baseline 是否已具备该能力」与「场景是否泄题」。

## 编辑纪律说明（slow-state §①）

本次是纯新增一条、零删除，按 wiki-lifecycle §① 默认该警惕「堆料」。重审后判定正当：§① 的堆料指「propose 后未经 test 就 accept」，本条经 t32 AB（B>A 且无泄题）证成，是验证通过的增量而非附加。已合规考虑过能否并入 appsec 面那条——占位密钥定级与 appsec 五面/纯计算跳过门是正交维度（前者管"字面量按可达性定级"，后者管"攻击面对照"），独立成条信息密度更高，不强塞进已较长的 appsec bullet。
