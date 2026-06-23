# 评判：S1 — scripts/seed.ts 安全审查（甲 vs 乙）

## 第一步：Ground Truth

**代码性质**：`scripts/seed.ts` 是本地开发数据库初始化脚本（`package.json` "seed": "tsx scripts/seed.ts"）。硬编码 `password: 'admin123'`、`email: 'admin@local.test'`、`role: 'admin'`。

**核心判据 — 生产可达性**（按 brief：看实际用途和调用关系，不凭文件名）：

1. **不在生产代码路径**。seed 脚本的全部用途是本地 dev DB 初始化。它不被 `src/` 运行时代码 import，不参与请求处理、不服务生产流量、不认证真实用户。它只能由人**显式手动调用** `npm run seed` 才执行。"脚本可被运行" ≠ "字面量处于生产可达的攻击面上"。
2. **`admin123` 不是 secret/token/API key**，是一个**本地 dev fixture 占位口令**。`admin@local.test` 的 `.test` 是 RFC 6761 保留的不可路由 TLD —— 这是一个明确的"一次性本地测试账户"信号，不是真实凭据。
3. **真实风险是条件性/运维性的**：若有人误把此脚本对着生产 DB 跑，会创建一个已知口令的 admin 账户。这是真实但**有前提**的风险（misrun against prod），不是"密钥泄漏在生产代码里"的 CRITICAL。前提（误跑到 prod）是假设性的。
4. **明文 vs 哈希是未知项**：是否明文落库取决于未给出的 ORM/schema hook。把它当"待核实风险"标出来是对的；**断言 CRITICAL 明文存储是越权下结论**，因为存储层根本没在代码里。

**正确严重度**：这是一个**非生产可达的本地 dev fixture 占位口令**。正确定级应在 **LOW–MEDIUM**：标出硬编码弱口令 + 缺环境门控（防误跑 prod）+ 提醒核实哈希，但**不应定 CRITICAL**。把 `admin@local.test`/`admin123` 升到 CRITICAL 属于过度升级（false positive）—— 正是 brief 警告的失败模式「不构成生产风险的占位值被误报成 CRITICAL」。

**假阴性检查**：本代码不存在真正生产可达的高危密钥，故无"放过真漏洞"问题，两方都不触发假阴性重罚。

---

## 第二步：评分

### 甲：4.5 / 10

- **定级准确度（差）**：定 **CRITICAL**，并显式拒绝占位抑制规则、把 `admin123`/`admin@local.test` 升到 CRITICAL。这是 brief 明确惩罚的误报。
- **关键推理瑕疵**：用"npm script 无环境门控 → `npm run seed` 即写入生产 DB → 完全生产可达"来论证 CRITICAL。这把"可被误跑"偷换成"生产可达的代码路径"。seed 脚本可运行不等于它在生产攻击面上 —— 这正是 brief 要求识破的混淆。还把存储层未知的"明文存储"直接断言成既成事实（"完全生产可达"+CRITICAL），越过了证据。
- **可取之处**：appsec 面对照结构清晰，env-guard 修复建议正确且可执行，弱口令/版本历史泄漏的识别都对。问题集中在**头条定级错了**。
- 因属过度升级误报（非假阴性），不触发 4 分以下重罚，但误报实质性拉低准确度分。

### 乙：7.5 / 10

- **定级准确度（好）**：最高定 **HIGH** 且**带条件**（"若 ORM 无 hash hook"），并显式说明"CRITICAL 保留给生产凭据泄漏或 RCE 路径""若误跑生产可升 CRITICAL"。把 misrun-on-prod 正确处理成**条件性升级路径**而非既成事实。这与 ground truth 高度一致。
- **推理质量**：明文存储发现保持条件性（承认存储层未知，给出"若已有 hook 则降为 MEDIUM/INFO"的分支），不越权断言。finding 4（环境门控缺失）正确指向真正可执行的根因项。`admin@local.test` 正确归为公开标识符、不单列 CRITICAL。
- **轻微偏热**：对一个纯本地 fixture，HIGH 仍略高于更稳妥的 LOW–MEDIUM；finding 数略冗（5 条，role:admin 那条 INFO 偏凑数）。但方向对、克制、有分支判断，未踩误报雷。
- 修复建议（bcrypt 示例、env 读取、NODE_ENV 断言）具体可执行。

---

## 结论

乙明显更准。乙把核心判据（生产可达性 = 看代码实际用途而非可运行性）落实成了"条件性 HIGH + 把 misrun 当假设升级路径"，避免了误报；甲在同一判据上栽了跟头，把"脚本可被误跑"升级成"完全生产可达"从而误报 CRITICAL，正中 brief 警示的占位值过度升级。两方都没有假阴性。

**甲: 4.5　乙: 7.5**
