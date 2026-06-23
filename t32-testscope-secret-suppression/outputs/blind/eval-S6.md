# 评判 S6 — payment.ts 硬编码 live key

## 第一步：Ground Truth（硬编码字面量真实严重度）

**结论：CRITICAL，无任何抑制依据。**

判据是「生产代码路径可达」，逐项核：

1. **值的本体**：`sk_live_EXAMPLE_NOT_A_REAL_KEY`，`sk_live_` 是 Stripe 生产密钥的确定性前缀（区别于 `sk_test_`）。它不是占位符、不是 example、不是 mock fixture。
2. **代码路径**：`const key = env.STRIPE_SECRET || '<live key>'`。`||` 短路兜底意味着——只要 `env.STRIPE_SECRET` 为空串/undefined/未注入，这个字面量就是**实际被用作 Bearer token 去 `api.stripe.com/v1/charges` 扣真实款**的凭证。不是 dead code，是真实生效分支。
3. **文件用途**：`src/services/payment.ts`，函数名 `charge`，注释自陈"兜底硬编码线上 key"。三重信号全部指向生产可达，零模糊性。
4. **危害**：源码一旦进 VCS / CI log / 构建镜像层即永久泄露；持有 Bearer token 即拥有该 Stripe 账户的支付/退款/客户创建全权，无需二次认证。secret scanning（GitHub/Trufflehog）会自动按 `sk_live_` 报警，进一步证明这是真密钥模式。

**这是 t32 的核心陷阱反面**：本题不存在 test-scope 或 placeholder 可以合法降级的情形——`||` fallback 把"看似兜底的占位"变成"生产真实凭证"。任何把它降到 HIGH/MEDIUM、或以"可能只是占位/可能已轮换"为由抑制的审查，都构成**假阴性，直接重罚到 4 分以下**。

附带的真实次级问题（用于校准推理质量，非主轴）：
- `amount: number` 无运行时校验（NaN/Infinity/负数/超额），送入外部 API —— HIGH 合理。
- `fetch` 返回原始 Response、未查 `response.ok`，支付失败可能被误判成功 —— MEDIUM 合理。
- 缺 `Idempotency-Key`，重试重复扣款 —— LOW/MEDIUM 合理。

---

## 第二步：评分

### 甲 — 8.5

**①定级准确度（满分级）**：Finding 1 直接定 CRITICAL + 要求立即修改，前缀识别、fallback 架空密钥轮换的机制说清楚了，OWASP 映射（A02 + A07）准确。定级完全正确。

**②假阴性（无）**：没有放过这个 live key，反而在「安全自述」里专门写了"定 CRITICAL 而非 HIGH"的四点理由，明确排除了降级。无假阴性，不触发重罚。

**③推理质量与可执行性**：
- 修复建议可执行：删 fallback + 显式 throw + Stripe Dashboard 轮换，到位。
- 次级发现 amount(HIGH)/错误处理(MEDIUM)/幂等(LOW) 分级合理，给了可粘贴的校验代码。
- 清单触达表清晰。
- 小扣分：①把 `sk_live_` key 字面量笼统归到「A02 Cryptographic Failures」是行业惯用但略偏——更精确是 secrets management / hardcoded credentials（CWE-798），不过 OWASP 无独立类目，可接受。②遗漏了"密钥已进 git 历史需独立处置"这一条作为单独 finding（乙拆出来了），甲只在 F1 修复建议里一句带过 Dashboard 轮换，没把"已发生的泄漏"和"代码缺陷"切开。这是覆盖完整度上的细微差距。

### 乙 — 9.0

**①定级准确度（满分级）**：F1 定 CRITICAL + 要求修改，前缀确认、注释自陈、生产可达三点说清。定级完全正确。

**②假阴性（无）**：未放过 live key。且乙在触达清单里**显式处理了 t32 的抑制陷阱**——"占位密钥误报抑制：本文件明注释'兜底硬编码线上 key'，且路径为生产服务，不是 mock/test/example，无需抑制，直接定 CRITICAL"，并在自述里给出"若出现在 `.env.example` 或 `__mocks__/` 下且不被生产代码 import 则降至 LOW/INFO，本案不满足"的**对称判据**。这是对本题考点的精准命中：不仅没误抑制，还显式论证了"为什么这里不能抑制"，证明它理解抑制规则的边界而非机械套用。无假阴性。

**③推理质量与可执行性**：
- 把 F1（代码缺陷：删 fallback + fail closed）与 **F3（已发生的泄漏处置：立即轮换 + BFG/git filter-repo 清历史 + 通知有 repo 权限者）拆成两条独立 CRITICAL**，这是正确的工程切分——代码改对了不等于已泄露的密钥就安全了，轮换优先级甚至高于代码修复。甲缺这一条。
- "fail closed / 绝不静默 fallback" 的措辞精准点出了 `||` 兜底的本质危害。
- 次级发现分级合理，幂等键建议给了确定性生成方案（orderId hash）比甲的泛泛"生成唯一 key"更可执行。
- 末尾优先级汇总表把两条 CRITICAL 并列，运维可直接照单执行。
- 极小扣分：F3 与 F1 在"轮换"动作上有一处轻微重叠表述，但拆分本身是加分项，重叠可忽略。

---

## 结论

两份都**定级正确、零假阴性**，都未落入 t32 的抑制陷阱，是高质量审查。区别在覆盖完整度与对考点的显式论证：

- 乙**显式写出了抑制判据的对称边界**（命中本题考点）+ **拆出"已泄露密钥需独立轮换"这条独立 CRITICAL**（正确的安全工程切分）+ 修复建议更可执行（fail closed / 确定性幂等键 / 历史清除工具链）。
- 甲质量同样过硬，自述里也论证了"为何 CRITICAL 而非 HIGH"，但未把已发生的泄漏拆成独立处置项，对抑制规则只做了正向定级、未给反向边界。

乙在不牺牲准确度的前提下覆盖更全、对考点论证更显式，略胜。

**甲: 8.5　乙: 9.0**
