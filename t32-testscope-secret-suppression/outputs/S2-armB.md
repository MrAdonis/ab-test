# 安全审查报告：tests/conftest.py

## 1. 清单项触达判断

- **无密钥/token 在暂存区**：代码中存在硬编码字符串 `sk_test_REDACTED_EXAMPLE_KEY`，形式上是 Stripe 测试密钥。触达此项。
- **无新增 OWASP Top 10 漏洞**：本文件无 HTTP 层、数据库操作、模板渲染等常见 OWASP sink，不直接触达。
- **appsec 面对照**：代码实例化 `StripeClient(api_key=MOCK_STRIPE_KEY)`，传入外部服务凭据，触达②鉴权·访问控制面。但这是测试 fixture 语境，见下方定级分析。
- **占位密钥误报抑制**：直接命中。需追 import 链判断生产可达性。

---

## 2. 生产可达性追踪

关键判断链：

1. `MOCK_STRIPE_KEY = 'sk_test_REDACTED_EXAMPLE_KEY'` 定义在 `tests/conftest.py`。
2. pytest conftest.py 文件由测试框架自动加载，**仅在测试运行时执行**，不会被生产应用的模块导入系统（`import`）触达。
3. `stripe_client` fixture 通过 `@pytest.fixture` 装饰，fixture 机制保证其只注入测试函数，不暴露于生产运行时。
4. 密钥值本身为 Stripe 官方文档示例格式（`sk_test_` 前缀），属于 Stripe 的测试模式密钥命名空间。Stripe 的测试密钥与生产密钥（`sk_live_`）由平台隔离，即使密钥值本身有效，也无法在 Stripe 生产环境执行真实扣款。
5. 该 fixture 调用 `from app.payments import StripeClient`，意味着测试会 import 生产代码路径，但 `MOCK_STRIPE_KEY` 本身不会被 `app/` 下任何模块引用，生产构建/部署不会打包 `tests/` 目录。

**结论**：该密钥字面量不生产可达，属于测试占位值，不应报 CRITICAL。

---

## 3. 审查结论

### 发现 F1：硬编码 Stripe 测试密钥

| 项目 | 内容 |
|------|------|
| 位置 | `tests/conftest.py`，`MOCK_STRIPE_KEY = 'sk_test_REDACTED_EXAMPLE_KEY'` |
| 严重度 | **LOW** |
| 是否要求修改 | 否（建议改进，非强制） |

**定级理由**：密钥位于 pytest conftest 文件，仅测试框架可达，不进生产构建路径。`sk_test_` 前缀为 Stripe 测试模式密钥，即使泄露也无法操作生产资金。生产可达性判断为否，按清单规则降级为 LOW/INFO，不报 CRITICAL。

**建议改进（可选）**：从环境变量读取可减少误报噪音，并与真实 CI 密钥注入保持一致的风格，例如：

```python
import os
MOCK_STRIPE_KEY = os.getenv('STRIPE_TEST_KEY', 'sk_test_REDACTED_EXAMPLE_KEY')
```

但这属于代码整洁度改进，不是安全强制项。

### 发现 F2：StripeClient 实例化传入凭据（appsec 面②）

| 项目 | 内容 |
|------|------|
| 位置 | `stripe_client` fixture，`StripeClient(api_key=MOCK_STRIPE_KEY)` |
| 严重度 | **INFO** |
| 是否要求修改 | 否 |

**定级理由**：凭据传入路径是测试 fixture 到测试函数的内部注入，不经过任何不可信外部输入，也不暴露于 HTTP 请求处理链。鉴权面触达仅限测试沙箱，不构成实际访问控制风险。

---

## 4. 安全自述

**应用的清单检查**：

- 密钥/token 检查：识别到硬编码字符串，未直接通过，进入下一步追踪。
- 占位密钥误报抑制：这是本次审查的核心判断路径。依据"生产可达性"而非路径名/文件名定级——追踪了 conftest.py 的加载机制（pytest 专属）、fixture 的注入边界（仅测试函数）、目录隔离（tests/ 不进生产构建）、以及 Stripe `sk_test_` 前缀的平台级隔离语义，综合判定为不生产可达，定 LOW 而非 CRITICAL。
- appsec 面对照（面②鉴权）：凭据传入路径在测试沙箱内封闭，不存在跨越测试/生产边界的访问控制问题，定 INFO。
- OWASP Top 10：本文件无 HTTP、数据库、模板 sink，不触达，跳过。

**对硬编码字面量的定级依据**：定级轴是"生产可达性"而非"是否看起来像密钥"。`sk_test_REDACTED_EXAMPLE_KEY` 在形式上符合 Stripe 密钥格式，但生产可达性为否（pytest conftest 机制 + tests/ 目录隔离 + Stripe 测试/生产命名空间隔离三重屏障），因此定 LOW 而非误报 CRITICAL，符合清单"占位密钥误报抑制"原则。
