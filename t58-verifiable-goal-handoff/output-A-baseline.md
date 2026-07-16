# 组A · baseline（现状配置，无 Goal 编译器模板）

subagent_tokens: 90285 | tool_uses: 0

---

# 待办 API 交接文档

## 项目状态

Express + Prisma 待办事项 API。数据库 schema 已定稿，**不要改动**。

## 已完成

- 用户注册 / 登录（JWT），已写测试并通过
- `GET /todos`、`POST /todos` 已实现
- `requireAuth` 鉴权中间件已实现（具体实现细节需重新打开中间件文件确认，未在此记录）

## 待完成

1. **`PUT /todos/:id`**：更新指定待办事项
2. **`DELETE /todos/:id`**：删除指定待办事项
3. **把 `requireAuth` 挂到 `/todos` 路由**：这是已知问题，当前 `/todos` 路由完全公开、无鉴权

## 已知问题（未修复）

`/todos` 路由（包括已写好的 GET 和 POST）目前没有挂载 `requireAuth` 中间件，任何人不登录也能访问。这个问题必须在新增 PUT/DELETE 之前或同时修复，不要先补完 PUT/DELETE 再回头补鉴权——否则新路由也会重复同一个漏洞。

## 下一步具体顺序

1. 打开 todos 路由文件，确认 `requireAuth` 中间件的导出方式和签名
2. 把 `requireAuth` 挂到整个 `/todos` 路由（router-level `router.use(requireAuth)`，或逐个路由加，取决于是否所有 todos 操作都要求登录——按当前设计应该是全部都要）
3. 实现 `PUT /todos/:id`：校验请求体、确认该 todo 属于当前登录用户（不能改别人的待办）、更新后返回
4. 实现 `DELETE /todos/:id`：同样先确认所有权，再删除
5. 补测试：
   - 未登录访问 `/todos` 任意方法应返回 401
   - PUT/DELETE 操作别人的 todo 应返回 403 或 404（按现有设计习惯选一种，两者不要混用）
   - PUT/DELETE 正常路径应通过

## 验收标准

- 全部 `/todos` 路由在未登录时返回 401
- PUT /todos/:id、DELETE /todos/:id 均已实现并有对应测试
- 已有测试（注册/登录）仍然全部通过
- 不修改 Prisma schema

## 不要做的事

- 不要改数据库 schema，已定稿
- 不要在补鉴权之外顺手重构已经写好的 GET/POST 逻辑
