# t31 — fail-open 默认检测点 入 coding-dod appsec 面

**日期**：2026-06-23
**来源**：trailofbits/skills 的 `insecure-defaults` skill,对照 coding-dod「### 安全」appsec 面（t24 已 keep）找增量
**被测变量**：在现有 appsec 面（5 面对照）基础上，是否增补一条 fail-open/fail-secure 检测点

## 缺口诊断

t24 后 appsec 面按「攻击面类型」分（不可信输入 / 鉴权 / 输出注入 / 加密 / CSRF·CORS）。
ToB insecure-defaults 是正交的另一维度——按「配置缺失时的失败方向」分：

- fail-open（CRITICAL）：`SECRET = env.get('K') or 'default'` → 缺配置时带弱密钥/关认证裸奔上线
- fail-secure（SAFE）：`SECRET = env['K']` → 缺配置即崩，不会不安全地跑

现有 appsec 面的「④加密·口令存储」会覆盖"用了弱算法"，但不专门盯"fallback 默认值让安全机制失效"这个失败方向，也没有配套跳过门（test fixture / 无安全语义的 `or default` 不算 finding）。

## A arm（现状，coding-dod「### 安全」全文）

```
### 安全
- [ ] 无密钥/token 在暂存区
- [ ] 无新增 OWASP Top 10 漏洞
- [ ] **appsec 面对照**——触发：本次代码命中任一安全面（①不可信输入：表单/URL 参/上传文件/反序列化/SSRF（服务端代取 URL）②鉴权·session·访问控制（含归属校验/IDOR）③输出注入：HTML/SQL/shell/模板 ④加密·口令存储 ⑤CSRF·CORS·跨域）。命中则写之前对照 OWASP 对应 Cheat Sheet 过防护要点，不靠"无 OWASP Top 10 漏洞"这句空话兜底。**跳过**：输入无外部来源 且 输出无下游 sink 的代码（如纯计算）
```

## B arm（A + 增补第 4 条）

A 全文 + 追加：

```
- [ ] **fail-open 默认检测**——读配置/密钥时盯"缺失时的失败方向"：`x = env.get('K') or 'default'` / `env.get('K','false')` 这类 fallback 让 app 带弱密钥·关认证·开调试裸奔上线（fail-open，按 CRITICAL 处理）；fail-secure 形态是 `env['K']`（缺失即崩，安全）。高发点：JWT/session secret fallback、CORS `*`、DEBUG/AUTH_REQUIRED 默认开/关、MD5·SHA1 用于 auth。**跳过**：test fixtures / `.example`·`.sample` 模板 / 构建期注入替换的占位 / 无安全语义的 fallback（如 PORT、PAGE_SIZE 默认值）——这些有默认值不算 finding，追到生产可达路径再判
```

## 对称性保证（t24 核心教训）

两 arm 共用同一元结构 prompt：(1) 先逐条对照下面的安全清单，判断本段代码触及哪些项 (2) 给出审查/修复要点 (3) 安全自述：应用了哪些检查、跳过了哪些及原因。**唯一差异 = 清单内容（A 3 条 / B 4 条）**。

## 场景设计（n=6，含两类灰区）

| 场景 | 类型 | 代码要点 | 期望好审查的行为 |
|---|---|---|---|
| S1 | clear-hit | CF Workers 登录，`const secret = env.JWT_SECRET \|\| 'dev-secret-change-me'` | 抓 fail-open JWT fallback，CRITICAL |
| S2 | clear-hit | 配置模块，`CORS = env.CORS \|\| '*'` + `DEBUG = env.DEBUG ?? true` | 抓 CORS 通配 + 默认开调试 |
| S3 | clear-skip | 期权 payoff 纯计算，无 IO 无配置 | 正确跳过，不堆密钥/配置戏码 |
| S4 | gray-fail-secure | Python `SECRET = os.environ['JWT_SECRET']`（无 fallback，缺失即 KeyError 崩） | 识别为 fail-secure=安全，不误报"密钥处理需注意" |
| S5 | gray-test-fixture | `tests/auth.test.ts` 里 `const TEST_SECRET = 'test-key-123'` | 按 test scope 跳过/降级，不误报 CRITICAL 硬编码密钥 |
| S6 | gray-无安全语义 | `const PAGE_SIZE = env.PAGE_SIZE \|\| 20` + `const PORT = env.PORT \|\| 3000` | 不报——`or default` 模式但无安全含义 |

预判：S1/S2（明显 fail-open）baseline 可能自抓 → B 增量小；价值若有集中在 S4/S5/S6（防误报/防过度套用）。
