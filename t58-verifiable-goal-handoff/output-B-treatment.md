# 组B · treatment（现状配置 + Goal 编译器模板注入）

subagent_tokens: 99855 | tool_uses: 3

---

# HANDOFF — Express + Prisma 待办 API

## 0. 使用说明
接手者（新对话窗口）拿到此文档后不需要读任何聊天记录。顺序：确认 Current State 起点 → 按 Completion Criteria 补齐缺口 → 每完成一项跑对应验证命令 → 全部通过后按 Verification 的报告格式回报。

> 本文档写作时无法在本机定位到该项目的实际路径，接手者第一步先 `pwd` 确认项目根目录绝对路径，下文 `<项目根目录>` `<port>` 等占位符需自行替换为实际值，不要假设。

## 1. Goal（交付什么）

把 Express + Prisma 的待办事项 API 补完成一个可用、鉴权保护的 CRUD 服务：
- 用户注册、登录（JWT）——已完成
- 登录用户可对**自己的**待办事项执行完整 CRUD：GET / POST / PUT / DELETE
- `/todos` 全部路由必须要求鉴权，未登录请求一律 401

## 2. Current State（现状）

### 已完成且已测试
- `POST /auth/register`
- `POST /auth/login`（返回 JWT）
- `requireAuth` 中间件已实现，逻辑正确，**但尚未挂载到任何 /todos 路由**
- `GET /todos`
- `POST /todos`
- 数据库 schema 已定稿（Prisma schema），**本次任务不允许修改**

### 已知缺口（本次要做的事，不是意外发现的 bug）
- `PUT /todos/:id` 未实现
- `DELETE /todos/:id` 未实现
- `/todos` 当前是公开路由（无鉴权保护）——已知问题，必须修

### 未验证/未知（接手者需先自行确认，不要假设）
- `requireAuth` 中间件的具体文件路径和导出方式
- 现有 `GET`/`POST /todos` 实现里 todo 和 userId 的关联方式（POST 时是否已把 todo 绑定到当前用户；GET 是否已按当前用户过滤，还是任何登录用户能看到全部 todo）——这直接决定 PUT/DELETE 的越权检查怎么写
- 现有测试框架（Jest/Vitest/Supertest 等）和测试文件位置
- 项目根目录绝对路径、本地启动端口

## 3. Completion Criteria（怎么算做完，逐项可判断）

| # | 条件 | 判断方法 | 状态 |
|---|------|---------|------|
| C1 | `requireAuth` 已挂载到全部 `/todos` 路由（GET/POST/PUT/DELETE） | 读路由源码，确认每个 handler 前有 `requireAuth`（或路由级 `router.use(requireAuth)`） | not done |
| C2 | 未带 JWT 访问任意 `/todos` 端点一律返回 401 | curl 不带 Authorization header 打四个端点，实收 401 | not done |
| C3 | `PUT /todos/:id` 已实现，只能更新当前用户自己的 todo | 代码 review + 用 A 的 token 改 B 的 todo，应被拒绝（403/404），不应成功 | not done |
| C4 | `DELETE /todos/:id` 已实现，只能删除当前用户自己的 todo | 同上，越权删除必须被拒绝 | not done |
| C5 | 原有 GET/POST 行为不回归 | 跑现有测试，之前通过的用例仍通过 | not done（先确认现状） |
| C6 | 新增行为有对应测试（PUT/DELETE 正常路径 + 越权路径 + 未鉴权路径） | 测试文件中能看到这些用例且执行通过 | not done |
| C7 | 数据库 schema 未被改动 | `git diff` 中 schema 文件零改动 | not done（持续约束） |

全部为 done 才算完成，不允许"大部分做完"当结束状态。

## 4. Constraints（不做什么、不能碰什么）

- **不改数据库 schema**——已定稿。若实现 PUT/DELETE 时发现 schema 缺字段（如缺 userId 外键），停下报告，不擅自加字段/迁移
- **不重写 GET/POST**，除非是为 PUT/DELETE 抽取一个共享的"确认 todo 属于当前用户"辅助函数所需的最小改动；已通过测试的代码不动
- **不引入新依赖**，除非现有实现已依赖同类工具且只是复用
- **不做范围外的事**：不加分页、不加排序、不加软删除、不加角色分级——即使顺手能做也不做
- **能否提交**：本地 C1-C7 全部 done、测试全过、`git status` 干净后可以 commit（不要求 push）。改动分两个 commit：先 `fix:`（挂载鉴权，修已知安全缺口），再 `feat:`（新增 PUT/DELETE），不混在一个 commit 里
- 不跳过 git hooks，不用 `--no-verify`

## 5. Verification（验证）

### 5.1 自动化命令

```bash
cd <项目根目录>
npm run build 2>&1 | tail -50   # TS 项目才有；纯 JS 跳过
npm run lint
npm test
```

三条全部 exit code 0 才算通过。任一失败，贴完整报错，不因为"看起来应该没问题"跳过。

### 5.2 手动行为验证（curl，防测试漏测造成假阳性）

```bash
# 1. 登录拿 token
TOKEN=$(curl -s -X POST http://localhost:<port>/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"..."}' | jq -r '.token')

# 2. 不带 token 访问四个端点，期望全部 401
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<port>/todos
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:<port>/todos
curl -s -o /dev/null -w "%{http_code}\n" -X PUT http://localhost:<port>/todos/1
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://localhost:<port>/todos/1

# 3. 带 token 走一遍正常 CRUD
curl -s -X POST http://localhost:<port>/todos -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"title":"test todo"}'
# 记下返回 id，再:
curl -s -X PUT http://localhost:<port>/todos/<id> -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"title":"updated"}'
curl -s -X DELETE http://localhost:<port>/todos/<id> -H "Authorization: Bearer $TOKEN"
# 期望：POST 201、PUT 200、DELETE 200/204，且改动真实生效（GET 复查）

# 4. 越权检查：用 A 用户 token 操作 B 用户的 todo id，期望 403/404，不能成功
```

### 5.3 证据看哪
- 自动化命令的完整终端输出（不截断，尤其报错部分）
- curl 验证的实际 HTTP 状态码（跑出来的数字，不是推测）
- `git diff --stat`（确认 schema 文件零改动）
- `git log --oneline -5`（确认 commit 按 Constraints 拆成了两个）

### 5.4 什么算失败
- 任一自动化命令 exit code 非 0
- curl 验证中任一未鉴权/越权请求没被正确拒绝
- schema 文件出现在 `git diff` 里
- 测试数量比接手前更少（说明删测试而非修代码——古德哈特陷阱，禁止这么做）

### 5.5 结果回报格式

```
## 完成情况
C1-C7 逐项：done / not done，各一句话依据

## 验证证据
- npm test 输出关键行（通过数量或失败详情）
- curl 验证结果：四个未鉴权请求状态码 + 越权请求状态码
- git diff --stat 结果
- git log 结果（两个 commit 的 hash + message）

## 遗留问题
[若有 not done 项，说明卡在哪、缺什么信息]
```
