# t32 — test-scope 占位密钥降级提示 入 coding-dod 安全段

**日期**：2026-06-23
**来源**：t31 副产物——盲评中 baseline 在 S5（test fixture 硬编码占位密钥）误报 A02 CRITICAL（A 仅 4.0），暴露的是「test-scope 该降级」这个独立弱点，不属于已否决的 fail-open。本测单独验证补这条是否净收益。
**被测变量**：coding-dod「### 安全」是否增补一条「占位密钥误报抑制」（test/本地占位密钥降级，但以生产可达性为准）。

## 缺口诊断

t24 appsec 面按攻击面分类，有「无外部输入 且 无下游 sink 则跳过」的跳过门，但**没有专门处理"硬编码密钥但处于测试/本地占位 scope"**——baseline 倾向把任何字符串密钥字面量报成 CRITICAL（A02），test fixture / seed / mock 全中招。这是**假阳性**弱点。

补这条的**核心风险 = 引入假阴性**：若提示让审查无脑按"文件名带 test 就降级"，会放过"命名像 test 但生产可达"的真漏洞——这比假阳性危险得多。所以被测条文必须自带"以生产可达性为准、不看文件名"的防御，本测专门用陷阱场景验证它扛不扛得住。

## A arm（现状，coding-dod「### 安全」三条，不含 t31 已否决的 fail-open）

```
### 安全
- [ ] 无密钥/token 在暂存区
- [ ] 无新增 OWASP Top 10 漏洞
- [ ] appsec 面对照——触发：命中任一安全面（①不可信输入 ②鉴权·session·访问控制 ③输出注入 ④加密·口令存储 ⑤CSRF·CORS·跨域）。命中则对照 OWASP Cheat Sheet 过防护要点。跳过：输入无外部来源 且 输出无下游 sink 的纯计算代码
```

## B arm（A + 增补第 4 条）

A 全文 + 追加：

```
- [ ] **占位密钥误报抑制**——审查硬编码密钥/口令字面量时，先判"这段代码生产可达吗"再定级：纯测试/本地占位（如 `.env.example` 模板、`__mocks__/` 假数据、CI 的 dummy token）里的占位值定 LOW/INFO，不报 CRITICAL 也不强制改。**定级依据是生产可达性，不是文件名/目录名**——命名带 test/mock 却被生产代码 import、或占位值会进生产构建·部署路径的，照 CRITICAL 报；判不准时追 import 链确认是否生产可达，别凭路径名放过真漏洞
```

举例用 `.env.example` / `__mocks__/` / CI dummy token；测试场景**刻意用不重合的实例**（seed 脚本 / conftest / docker-compose / storybook / 陷阱 / 生产对照），避免 t31 的 teaching-to-test 泄题。

## 对称性保证

两 arm 共用同一元结构 prompt：(1) 先逐条对照下面的安全清单，判断本段代码触及哪些项 (2) 给出审查结论，对每个发现标严重度（CRITICAL/HIGH/MEDIUM/LOW/INFO）+ 是否要求修改 (3) 安全自述：应用了哪些检查、对硬编码字面量如何定级及理由。**唯一差异 = 清单内容（A 3 条 / B 4 条）**。

## 场景设计（n=6：4 该降级 + 2 不该降级陷阱/对照）

| 场景 | 类型 | 期望好审查的行为 |
|---|---|---|
| S1 | 该降级·seed 脚本 | `scripts/seed.ts` 本地 seed 用 `'admin123'`，定 LOW，不报 CRITICAL |
| S2 | 该降级·conftest | `tests/conftest.py` fixture mock key，定 LOW |
| S3 | **陷阱·真 CRITICAL** | `config.test-utils.ts` 名带 test 但被生产 `index.ts` import 作 JWT fallback → 必须 CRITICAL，不被 test 命名骗过 |
| S4 | 该降级·dev compose | `docker-compose.yml` dev 服务 `POSTGRES_PASSWORD: localdev`，LOW + 提示别复用 prod |
| S5 | 该降级·storybook | `Button.stories.tsx` mock token，LOW |
| S6 | **对照·真 CRITICAL** | `src/services/payment.ts` 生产 handler 硬编码 live key 兜底 → CRITICAL，两 arm 都该抓 |

预判：A（无降级提示）倾向 S1/S2/S4/S5 误报 CRITICAL → B 在这 4 个有收益；但 B 真正要证明的是 **S3/S6 不翻车**——若 B 因降级提示放过 S3 陷阱或 S6 生产兜底，则这条引入假阴性、判负。S3 是最强区分点（同时考"该降级的别误报"和"别过度降级放过真漏洞"）。

## 场景代码（生成 agent 内联，不读本文件）

### S1 — scripts/seed.ts
```ts
// 本地开发数据库初始化，package.json scripts: "seed": "tsx scripts/seed.ts"
import { db } from '../src/db'
async function seed() {
  await db.user.create({ data: { email: 'admin@local.test', password: 'admin123', role: 'admin' } })
  console.log('seeded local admin')
}
seed()
```

### S2 — tests/conftest.py
```python
import pytest
MOCK_STRIPE_KEY = 'sk_test_REDACTED_EXAMPLE_KEY'
@pytest.fixture
def stripe_client():
    from app.payments import StripeClient
    return StripeClient(api_key=MOCK_STRIPE_KEY)
```

### S3 — src/auth/config.test-utils.ts （陷阱：名带 test-utils 但被生产 import）
```ts
// config.test-utils.ts
export const FALLBACK_JWT = 'changeme-default-secret'

// src/auth/index.ts （生产入口）
import { FALLBACK_JWT } from './config.test-utils'
export function getJwtSecret(env: Env): string {
  return env.JWT_SECRET ?? FALLBACK_JWT   // 缺配置时生产用这个签 token
}
```

### S4 — docker-compose.yml
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: localdev
      POSTGRES_DB: appdev
    ports: ["5432:5432"]
```

### S5 — src/components/Button.stories.tsx
```tsx
import { Button } from './Button'
export default { title: 'Button', component: Button }
export const WithAuth = {
  args: { label: 'Pay', apiToken: 'demo-token-123', onClick: () => {} }
}
```

### S6 — src/services/payment.ts （对照：生产真漏洞）
```ts
export async function charge(amount: number, env: Env) {
  const key = env.STRIPE_SECRET || 'sk_live_EXAMPLE_NOT_A_REAL_KEY'  // 兜底硬编码线上 key
  return fetch('https://api.stripe.com/v1/charges', {
    method: 'POST', headers: { Authorization: `Bearer ${key}` },
    body: new URLSearchParams({ amount: String(amount) })
  })
}
```
