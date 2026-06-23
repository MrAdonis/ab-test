# POST /api/profile/update — 硬化后方案

---

## 收敛过程

### 第 1 轮：漏洞列举

**V1 — IDOR（越权修改他人资料）**
- 什么会坏：请求体里传 `userId: 999`，可修改任意用户资料。
- 条件：`withAuth` 正确注入了 `req.user.id`，但代码用 `req.body.userId` 作为 WHERE 条件，两者不做比对。

**V2 — 字段注入 / 意外字段覆盖**
- 什么会坏：`req.body` 里额外传入 `role: "admin"` 或 `email: "xxx"`，若 UPDATE 直接展开 body，这些字段也会被写入。
- 条件：未白名单过滤可更新字段。

**V3 — 空 body / 空字段静默通过**
- 什么会坏：所有字段为空字符串或缺失，仍执行一次无意义 UPDATE，或意外清空现有资料（nickname 置空）。
- 条件：未做"至少有一个合法字段"的前置检查。

**V4 — `req.body.userId` 与 `req.user.id` 的类型错配**
- 什么会坏：`req.body.userId` 是字符串 `"42"`，数据库 id 是整数，严格比对 `===` 会假阴性，导致合法用户无法更新；弱比对 `==` 则被绕过。
- 条件：假设（未读代码）— 若 DB 层用 ORM 参数绑定则类型由 ORM 处理，但校验层手动比对时仍有风险。

**V5 — 并发写入竞争**
- 什么会坏：同一用户两次 PATCH 并发，后一次可能覆盖前一次的部分字段。
- 条件：无行级锁或乐观锁。

**V6 — 验证缺口：测试只测正常路径**
- 什么会坏：IDOR 越权路径在 happy-path 测试中不会触发，但在生产中可被任意利用。
- 条件：若测试没有覆盖"已登录用户修改他人 userId"场景。

**V7 — 缺返回值归属校验**
- 什么会坏：UPDATE 后直接返回数据库回传的新记录，若 UPDATE WHERE 条件错了（极端情况更新了 0 行或多行），响应体仍可能拼出看似正常的结构。
- 条件：未校验 affected rows。

**V8 — bio/nickname 长度无上限**
- 什么会坏：超长字符串击穿数据库字段长度限制，抛 DB 异常泄露 schema 信息，或在渲染层造成 XSS 向量（若前端未转义）。
- 条件：未在 API 层限制字段长度。

**V9 — avatar URL 无校验**
- 什么会坏：传入 `javascript:alert(1)` 或任意第三方 URL，前端渲染 `<img src>` 时触发 XSS 或 SSRF。
- 条件：avatar 字段仅为自由字符串。

---

### 第 1 轮：修复 / 接受

| 漏洞 | 处置 |
|------|------|
| V1 IDOR | 修复：忽略 `req.body.userId`，WHERE 条件只用 `req.user.id` |
| V2 字段注入 | 修复：白名单提取，只允许 `nickname/bio/avatar` 三字段 |
| V3 空 body | 修复：提取后若无合法字段则 400 返回 |
| V4 类型错配 | 修复：比对时统一用 `req.user.id`（已由 withAuth 保证类型），不再从 body 取 userId，V4 因 V1 修复而消失 |
| V5 并发写入 | 接受的风险：字段级最后写入胜出，资料字段（昵称/简介/头像）无事务一致性要求，并发覆盖是用户自身行为，业务可接受 |
| V6 测试缺口 | 修复：方案中明确要求写 IDOR 回归测试（见测试规格段） |
| V7 affected rows | 修复：检查 affected rows，0 行时返回 404 |
| V8 长度无限 | 修复：nickname ≤ 50，bio ≤ 300，超限返回 400 |
| V9 avatar URL | 修复：avatar 只允许 `https://` 开头的 URL，否则返回 400 |

---

### 第 2 轮：重查新漏洞

引入 avatar URL 白名单后检查：

**V10 — avatar URL 允许任意 HTTPS 域，仍存在 SSRF 向量（服务端渲染场景）**
- 什么会坏：若后端有图片代理或预取逻辑，任意 HTTPS URL 可触发 SSRF。
- 条件：检查是否存在服务端图片预处理。假设（未读代码）— 仅 API 层存储 URL，前端直接渲染 `<img src>`，则不存在服务端 SSRF。

处置：接受的风险。方案仅存储 URL 字符串，不做服务端代取；若未来加图片代理需另行评估。`https://` 前缀约束已阻断 `javascript:` 等协议注入，XSS 向量关闭。

**V11 — 白名单字段提取后若三字段均未传（但 body 有其他字段），当前逻辑会 400，是否符合预期？**
- 不是新漏洞，是需要在规格里明确的行为。确认：body 里只传非白名单字段也应 400，规格已覆盖。

无实质性新漏洞引入。**收敛，停止。**

---

## 关闭的漏洞

- `body.userId` 可越权指定目标 → 忽略 body.userId，WHERE 只用 `req.user.id`
- body 展开可覆盖任意字段 → 白名单提取 `{nickname, bio, avatar}`
- 空 body 静默通过 → 提取后无合法字段则 400
- affected rows 未校验，0 行静默成功 → 0 行返回 404
- nickname/bio 长度无限 → nickname ≤ 50，bio ≤ 300，超限 400
- avatar 可传协议注入（`javascript:`） → 只接受 `https://` 开头

## 接受的风险

- 并发写入后写覆盖前写 → 资料字段无事务一致性要求，用户自身并发操作，业务可接受；若将来加乐观锁另行评估
- avatar 允许任意 HTTPS 域 → 仅存储字符串，无服务端代取，不存在 SSRF；前端渲染已由前端负责 XSS 转义

---

## 最终方案（可直接实现的规格）

### 路由声明

```
POST /api/profile/update
中间件：withAuth（已有，注入 req.user.id）
```

### 请求体结构

接受 JSON body，支持字段：

| 字段 | 类型 | 约束 |
|------|------|------|
| nickname | string | 可选，1–50 字符 |
| bio | string | 可选，0–300 字符 |
| avatar | string | 可选，必须以 `https://` 开头 |

**不接受 `userId` 字段**——即使传入也忽略，目标用户始终为 `req.user.id`。

### 处理逻辑（伪代码，语言无关）

```
handler(req, res):
  // 1. 白名单提取
  allowed = ['nickname', 'bio', 'avatar']
  updates = {}
  for key in allowed:
    if key in req.body:
      updates[key] = req.body[key]

  // 2. 至少一个字段
  if updates is empty:
    return apiError(res, 400, "至少需要提供一个可更新字段")

  // 3. 字段校验
  if 'nickname' in updates:
    if len(updates.nickname) < 1 or len(updates.nickname) > 50:
      return apiError(res, 400, "nickname 长度须在 1–50 字符之间")

  if 'bio' in updates:
    if len(updates.bio) > 300:
      return apiError(res, 400, "bio 不超过 300 字符")

  if 'avatar' in updates:
    if not updates.avatar.startswith("https://"):
      return apiError(res, 400, "avatar 须为 https:// 开头的 URL")

  // 4. 写入数据库
  // WHERE 条件只用 req.user.id，不使用 req.body 中的任何 id 字段
  result = db.update('profiles')
             .set(updates)
             .where({ id: req.user.id })
             .returning('*')

  // 5. 校验行数
  if result.affectedRows === 0:
    return apiError(res, 404, "用户不存在")

  // 6. 返回更新后资料
  return res.json({ profile: result.rows[0] })
```

### 错误响应一览

| 场景 | HTTP 码 | 消息 |
|------|---------|------|
| body 无合法字段 | 400 | 至少需要提供一个可更新字段 |
| nickname 超长/为空 | 400 | nickname 长度须在 1–50 字符之间 |
| bio 超长 | 400 | bio 不超过 300 字符 |
| avatar 非 https | 400 | avatar 须为 https:// 开头的 URL |
| 用户不存在（affected 0） | 404 | 用户不存在 |
| DB 异常 | 统一走现有 apiError 兜底 | （由现有框架处理） |

### 必须覆盖的测试用例

1. **正常更新**：已登录用户更新自己的 nickname，返回 200 + 新资料。
2. **IDOR 回归**：body 传入另一用户的 userId，确认响应仍只更新当前 `req.user.id` 对应的记录（可在测试 DB 查两条记录验证）。
3. **空 body**：传空对象 `{}`，期望 400。
4. **非法字段过滤**：传 `{ role: "admin" }`，期望 400（无合法字段）。
5. **字段超长**：nickname 传 51 字符，期望 400。
6. **avatar 协议错误**：传 `javascript:alert(1)`，期望 400。
7. **不存在用户**：mock DB affected rows = 0，期望 404。

### 不在本方案范围内

- avatar 图片实际上传（对象存储 / CDN）：本方案只存 URL 字符串
- 字段唯一性约束（如 nickname 全局唯一）：若有需要另行加 DB 约束 + 冲突错误处理
- 速率限制：由现有基础设施层处理，非本路由特有

---

## 迭代数

2 轮收敛。
