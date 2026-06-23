# 安全审查报告：tests/conftest.py

## 1. 清单触达判断

| 清单项 | 触达？ | 理由 |
|--------|--------|------|
| 无密钥/token 在暂存区 | ✅ 触达 | 文件含硬编码字符串 `sk_test_REDACTED_EXAMPLE_KEY` |
| 无新增 OWASP Top 10 漏洞 | ✅ 触达 | 凭证硬编码涉及 OWASP A07:2021 Identification & Authentication Failures |
| appsec 面 ① 不可信输入 | 不触达 | fixture 无外部输入 |
| appsec 面 ② 鉴权·session·访问控制 | ✅ 触达 | API key 直接传入真实 SDK 客户端构造函数，凭证处理路径 |
| appsec 面 ③ 输出注入 | 不触达 | 无输出 sink |
| appsec 面 ④ 加密·口令存储 | ✅ 触达 | API key 以明文字面量存储在源码中 |
| appsec 面 ⑤ CSRF·CORS·跨域 | 不触达 | 无 HTTP 边界 |

---

## 2. 审查结论

### 发现 1：Stripe API key 硬编码在测试源文件

**严重度：MEDIUM**
**要求修改：是**

`MOCK_STRIPE_KEY = 'sk_test_REDACTED_EXAMPLE_KEY'` 是一个格式完全合法的 Stripe **测试密钥**（`sk_test_` 前缀）。虽然测试密钥在 Stripe 沙箱环境下无法触达真实资金，但存在以下问题：

- **泄露风险**：测试文件会进入 git 历史，任何有仓库访问权的人都能读到这个 key。Stripe 测试 key 泄露后可被用于枚举测试 API 行为、触发沙箱费率限制、或作为社工攻击素材。
- **混淆真实 key 的扫描**：`sk_test_` 格式会被 secret scanning 工具（GitHub / GitGuardian / truffleHog）识别并告警，即使是测试 key 也会产生噪音，掩盖真正的生产 key 告警。
- **坏习惯传播**：测试文件里硬编码 API key 的模式容易被复制到生产 fixture，形成高危路径。

**对照 OWASP Credentials in Source Code（A07）防护要点：**
- 不应将任何凭证（含测试凭证）以字面量形式存入源码
- 应通过环境变量（`os.environ.get('STRIPE_TEST_KEY')`）或测试配置文件（`.env.test`，已加入 `.gitignore`）注入
- 推荐做法：改用 `unittest.mock.patch` 或 `responses` 库完全 mock Stripe SDK，不实例化真实 `StripeClient`，从根本上消除对真实（或测试）key 的依赖

**修改建议：**
```python
import os
import pytest

@pytest.fixture
def stripe_client():
    from app.payments import StripeClient
    api_key = os.environ.get('STRIPE_TEST_KEY', 'sk_test_placeholder')
    return StripeClient(api_key=api_key)
```
或更彻底地，用 mock 替代真实客户端：
```python
from unittest.mock import MagicMock
@pytest.fixture
def stripe_client():
    return MagicMock()
```

---

### 发现 2：未见 .gitignore / secret scanning 防护（INFO）

**严重度：INFO**
**要求修改：建议**

仅凭当前片段无法确认仓库是否有 `.gitignore` 覆盖或 pre-commit secret scanning hook。建议确认：
- `git secrets` 或 `truffleHog` 等工具已加入 pre-commit hook
- `.env.test` 已在 `.gitignore` 中

---

## 3. 安全自述

**应用的清单检查：**
- 密钥/token 检查：识别出 `sk_test_` 前缀字符串为 Stripe 格式 API key，无论测试/生产均触发该项。
- OWASP A07（凭证处理）：key 以字面量传入 SDK 构造函数，属于凭证存储路径，appsec 面②④均触达，对照 OWASP Credentials in Source Code Cheat Sheet 过了防护要点。

**硬编码字面量定级理由：**
选择 **MEDIUM** 而非 HIGH/CRITICAL，依据：
1. `sk_test_` 前缀明确为 Stripe 沙箱 key，Stripe 官方沙箱与生产环境硬隔离，无真实资金风险。
2. 文件位于 `tests/` 目录，通常不部署到生产环境。

若同样的字面量出现在 `app/` 目录下或为 `sk_live_` 前缀，定级应升至 **CRITICAL**。

**跳过项说明：**
输入无外部来源（fixture 参数由 pytest 注入框架控制，非用户提供），且无 HTML/SQL/shell/模板 sink，因此安全面①③⑤走跳过路径，未展开 OWASP 对应 Cheat Sheet。
