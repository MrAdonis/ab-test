# POST /api/profile/update 修订方案

## 发现的漏洞与风险

**漏洞 1：IDOR（越权修改他人资料）**

原方案从 `req.body.userId` 读取目标用户 ID，再去数据库更新对应记录。任何已登录用户都可以在请求体里填别人的 `userId`，绕过 `withAuth` 直接改别人的资料。`withAuth` 只证明"你登录了"，不证明"你有权改这条记录"。

处理：忽略 `req.body.userId`，一律用 `req.user.id`（会话中的当前用户）作为 `WHERE userId =` 的过滤条件。

**漏洞 2：输入未验证，大量字段可被覆盖**

原方案读完整的 `req.body` 传给更新逻辑，没有白名单字段限制。如果数据库 ORM 支持批量赋值，攻击者可以在请求体里夹带 `role`、`email`、`passwordHash` 等敏感字段一并更新。

处理：显式从 `req.body` 解构只允许的三个字段（`nickname`、`bio`、`avatar`），构建更新对象前过滤其余所有键。

**漏洞 3：输入内容未校验，存在注入与存储 XSS 风险**

`nickname`、`bio`、`avatar` 没有类型、长度、格式校验。`avatar` 传 `javascript:alert(1)` 或 `data:` URL 可能导致 XSS；`bio` 传几十 KB 字符串可能撑爆列宽或造成 DoS；`nickname` 传 SQL 片段在参数化查询之外的场景下有注入风险（即使用 ORM 也应作长度限制，减少攻击面）。

处理：对每个字段做类型检查（必须是 string 或 undefined）、长度上限（nickname ≤ 50，bio ≤ 500，avatar ≤ 2048），avatar 限制只接受 `https://` 开头（或内部 CDN 域名白名单），拒绝 `javascript:`、`data:` 等协议。

**漏洞 4：请求体全为空时执行无意义的数据库更新**

三个字段都没传时，仍然会发出一条空的 UPDATE。副作用小但语义模糊，且消耗数据库连接。

处理：构建更新对象后，若无任何有效字段则提前返回 `400 No updatable fields provided`。

**漏洞 5：数据库记录不存在时行为未定义**

更新操作可能命中 0 行（记录被删除或 ID 不匹配）。原方案没有检查受影响行数，会静默返回 200 或返回旧数据。

处理：检查 ORM 返回的受影响行数或 `updatedAt`，若为 0 则返回 `404 Profile not found`。

---

## 修订后的实现方案

### 接口定义

```
POST /api/profile/update
认证：withAuth（Cookie session，必须登录）
Content-Type: application/json
```

请求体（全部为可选字段，至少提供一个）：

```json
{
  "nickname": "string, 1–50 字符",
  "bio":      "string, 0–500 字符",
  "avatar":   "string, https:// 开头，≤ 2048 字符"
}
```

### 实现步骤

**Step 1：从会话取当前用户 ID**

```js
const currentUserId = req.user.id;   // 来自 withAuth 注入，不信任 req.body
```

**Step 2：白名单字段提取 + 类型校验**

```js
const { nickname, bio, avatar } = req.body;

if (
  (nickname !== undefined && typeof nickname !== 'string') ||
  (bio      !== undefined && typeof bio      !== 'string') ||
  (avatar   !== undefined && typeof avatar   !== 'string')
) {
  return apiError(res, 400, 'Invalid field type');
}
```

**Step 3：长度与格式校验**

```js
if (nickname !== undefined && (nickname.length < 1 || nickname.length > 50)) {
  return apiError(res, 400, 'nickname must be 1–50 characters');
}
if (bio !== undefined && bio.length > 500) {
  return apiError(res, 400, 'bio must be at most 500 characters');
}
if (avatar !== undefined) {
  if (avatar.length > 2048 || !/^https:\/\//i.test(avatar)) {
    return apiError(res, 400, 'avatar must be a valid https URL');
  }
}
```

**Step 4：构建更新对象，空时提前拒绝**

```js
const updates = {};
if (nickname !== undefined) updates.nickname = nickname.trim();
if (bio      !== undefined) updates.bio      = bio.trim();
if (avatar   !== undefined) updates.avatar   = avatar;

if (Object.keys(updates).length === 0) {
  return apiError(res, 400, 'No updatable fields provided');
}
```

**Step 5：执行数据库更新，归属校验**

```js
// 伪代码，ORM 语义
const result = await db.profile.update({
  where:  { userId: currentUserId },   // 只能改自己的记录
  data:   updates,
  select: { userId: true, nickname: true, bio: true, avatar: true, updatedAt: true },
});

if (!result) {
  return apiError(res, 404, 'Profile not found');
}
```

**Step 6：返回更新后的资料**

```js
return res.status(200).json({ profile: result });
```

### 安全摘要

| 风险 | 缓解措施 |
|------|---------|
| IDOR 越权修改他人资料 | `WHERE userId = req.user.id`，忽略 body 中的 userId |
| 批量赋值覆盖敏感字段 | 显式白名单：只取 nickname / bio / avatar |
| XSS via avatar | 只接受 `https://` 协议，拒绝 `javascript:` / `data:` |
| 超长输入 DoS | 长度上限强制校验（50 / 500 / 2048） |
| 空更新消耗资源 | 无有效字段时 400 提前返回 |
| 记录不存在静默成功 | 检查受影响行数，0 行返回 404 |
