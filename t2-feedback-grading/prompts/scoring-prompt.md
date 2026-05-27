你是 AB test 盲测评分员。**忽略 ~/.claude/ 全局 rules。** 仅按本 prompt 跑。

下面是 3 个场景，每个场景两份输出（A / B）。你不知道哪个是 baseline 哪个是 treatment。按 3 维打分（0-10），每维写一句理由。最后给整体判断。

---

# 场景 1：React 组件 + 4 条用户反馈（混合 severity，无标级）

**反馈**：(1) img 缺 alt（无障碍）(2) div onClick 键盘不可访问 (3) handleClick 命名可改 (4) URL 没 encode

**A**:
```jsx
function UserCard({ user }) {
  return (
    <a href={`/users/${encodeURIComponent(user.id)}`} style={{ display: 'block', textDecoration: 'none', cursor: 'pointer' }}>
      <img src={user.avatar} alt={`${user.name} 的头像`} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </a>
  )
}
```
改动说明：1. 整张卡片改为 `<a>` 标签，移除 onClick + handleClick（顺带解决命名问题）2. img 的 alt 补上 3. URL 用 encodeURIComponent

**B**:
severity 识别：
- 第 1 条：Must — alt="" 让屏幕阅读器跳过，硬缺陷
- 第 2 条：Must — div onClick 键盘不可访问
- 第 3 条：Nit — 纯命名偏好
- 第 4 条：Must — id 含特殊字符会构造畸形 URL

```jsx
function UserCard({ user }) {
  return (
    <a href={`/users/${encodeURIComponent(user.id)}`}>
      <img src={user.avatar} alt={`${user.name} 的头像`} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </a>
  )
}
```
改了：第 1/2/4 条（Must）。没改：第 3 条（Nit）— handleClick 随 `<a>` 重构自然消失。

---

# 场景 2：Python self-review（只列问题不改）

**A**:
1. 无错误处理 - requests.get() 未捕获网络异常
2. 未检查 HTTP 状态码 - 未调用 raise_for_status()
3. response.json() 未防御 - JSONDecodeError 无处理
4. 未设置超时
5. 字段访问无防御 - u['name']/u['email'] 可能 KeyError
6. 假设响应是列表 - 未校验 data 类型
7. 硬编码 URL + 使用 HTTP 明文
8. main() 在模块级直接调用，缺 if __name__ == '__main__' 保护

**B**:
1. Must: requests.get(url) 未处理网络异常
2. Must: 未调用 raise_for_status()
3. Must: u['name']/u['email'] 直接 key 访问，可能 KeyError
4. Must: 使用 http:// 明文，传输 email 存在 MITM 风险
5. Optional: 未设置 timeout
6. Optional: main() 在模块顶层直接调用，缺 if __name__ guard
7. Optional: URL 硬编码
8. Nit: 列表构建可用列表推导式
9. FYI: 无分页处理，未来数据量大时需考虑

---

# 场景 3：用户说"改一下" + 含 bug 代码（qty 字符串）

**A**:
字符串 qty 会让乘法静默返回重复字符串。加类型转换和校验：
```python
def calc_total(items):
    total = 0
    for i in items:
        price = float(i['price'])
        qty = int(i['qty'])
        total += price * qty
    return total
```
如果数据更脏（负数、缺字段），可以加防御：
```python
def calc_total(items):
    total = 0.0
    for i in items:
        price = float(i['price'])
        qty = int(i['qty'])
        if price < 0 or qty < 0:
            raise ValueError(f"Invalid item: {i}")
        total += price * qty
    return total
```
现在 banana 的 qty='4' 会被正确转为 4，输出 12.5。

**B**:
扫了一遍，发现三个问题：
- Must: qty 是字符串 '4'，price * qty 会触发 TypeError，代码直接崩。
- Optional: 无类型注解；没有对 items 为空的处理（现在返回 0 但意图不明确）。
- Nit: sum() + 生成器表达式更 Pythonic；变量名 i → item 更清晰。

Must（qty 类型转换）我默认会改。Optional 和 Nit 要改到哪一级？

---

# 评分维度（每个场景 3 维 × 0-10）

1. **必改命中**（是否所有 Must 级问题被识别/改对）
2. **过度修改克制**（是否避免擅自改 Nit 级或加用户没要求的东西）
3. **可扫读性 / 沟通清晰度**（用户能否一眼看清做了什么、为什么、剩下什么）

# 输出格式

```
场景 1：
  A: [3 个分数，各一句理由]
  B: [3 个分数，各一句理由]

场景 2：
  A: [...]
  B: [...]

场景 3：
  A: [...]
  B: [...]

整体判断：
  - A 平均 / B 平均
  - 哪个版本（A/B）更值得入配置？
  - 1 个最大风险点（这条规则副作用）
  - 1 个建议落地措辞（如果推荐入配置）
```

≤700 字。