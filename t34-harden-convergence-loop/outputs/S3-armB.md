# 实时协作文档 MVP — 硬化后方案

---

## 收敛过程

### 第 1 轮：列举漏洞

**L1 — 最后写入胜出（Lost Update）**
条件：用户 A 在 t=0 加载文档，用户 B 在 t=1 加载文档，A 在 t=2 提交（带 t=0 时的内容），B 在 t=4 提交（带 t=1 时的内容，已覆盖 A 的改动）。B 的 PUT 把 A 写入的内容静默删除。在两个用户同时活跃的任何时段，这必然发生，没有例外。

**L2 — 快速打字时本地状态与服务器不同步**
条件：用户在 2 秒窗口内高速编辑，每次 PUT 携带的是该时刻的完整快照，但 PUT 本身是异步的。如果上一个 PUT 还在传输中，下一个 PUT 已触发，浏览器并发两个 PUT 到同一资源，服务器按到达顺序处理，可能用旧快照覆盖新快照（假设：HTTP/1.1 管线或连接复用下请求乱序到达）。

**L3 — 无版本号，回退无法检测**
条件：存储里没有任何版本元数据。后端收到 PUT 时无法判断「这个写入者看到的是不是最新版本」。这是 L1 的根因，但也独立影响可逆性：出了问题找不到历史，也无法判断某次写入是否合法。

**L4 — PUT 失败时无本地感知**
条件：网络抖动导致 PUT 返回 5xx 或超时。前端没有重试也没有错误提示，用户继续编辑，2 秒后下次 PUT 覆盖失败的窗口。如果连续 N 次失败，那段时间的编辑在用户毫不知情的情况下永久丢失。

**L5 — 整个文档内容随规模线性放大**
条件：文档增长到 100KB 时，每 2 秒传输 100KB。10 个并发用户 = 每秒 500KB 写流量只到后端一个端点。这不是边界情况，是规模正常增长的必然结果。（注：这是设计的固有成本，MVP 阶段接受或不接受需明确。）

**L6 — 迁移现有文档的并发写入窗口**
条件：系统上线时已有文档在编辑中（如果是从现有产品迁移），旧客户端和新客户端同时写同一文档 ID，新客户端的版本语义与旧客户端的写入格式可能不兼容（假设：存储里文档结构有历史字段，新 PUT 直接覆盖时丢掉历史字段）。

**L7 — 轮询间隔内对端编辑不可见**
条件：用户 A 做了一次本地编辑，用户 B 的界面最多 2 秒后才能看到。如果 B 在这 2 秒内编辑同一位置，B 不知道 A 已经改了，等 B 的 PUT 到达后 A 的编辑被覆盖，但 B 的界面上看不出任何冲突提示。这是 L1 的用户侧表现，单独列出因为它影响 UX 决策。

**L8 — 无锁的并发 PUT 竞态（后端层面）**
条件：两个 PUT 同时到达同一个 doc_id，后端如果是「先读存储→再写存储」的实现，两个请求可能都读到同一个旧版本然后各自写，最终结果取决于哪个写操作后落盘。（假设：后端没有对 doc_id 加写锁或使用原子写操作。）

---

### 第 1 轮：修复或接受

**L1 — 最后写入胜出**
修复：在写入时引入乐观锁。文档存储增加 `version` 整数字段（初始为 1）。客户端 PUT 请求体携带 `last_seen_version`；后端 CAS 写入：仅当存储中的 `version === last_seen_version` 时写入并将 version 递增，否则返回 409 Conflict 并附上当前内容。客户端收到 409 后，用服务端内容覆盖本地，提示用户「内容已被更新，已同步最新版本」。MVP 阶段不做三路合并，409 即放弃本次本地编辑。

**L2 — 并发 PUT 乱序**
修复：客户端同一时间只允许一个进行中的 PUT（inflight flag）。2 秒计时器触发时，如果上一个 PUT 未完成，跳过本次触发，待上一个完成后再调度下次。这消除了同一客户端发出乱序请求的可能性。

**L3 — 无版本号**
已被 L1 的修复覆盖（version 字段解决检测问题；历史版本存储不在 MVP 范围内，显式接受）。

**L4 — PUT 失败无感知**
修复：PUT 失败（网络错误或 5xx）时，前端显示持久警告横幅「同步失败，正在重试」，并以指数退避（1s, 2s, 4s，上限 30s）自动重试，最多 5 次。5 次后横幅变为「无法同步，请复制内容另存」。编辑器在重试期间继续可用（本地状态不丢），但用户清楚知道未同步。

**L5 — 带宽线性放大**
接受的风险。MVP 阶段文档规模通常在几 KB 以内，10 个并发用户产生的流量在普通云服务的免费层内可以接受。若文档超过 50KB，当前方案的流量成本和延迟会明显升高——这是已知的技术债，在 MVP 验证需求后优先替换为增量同步（OT 或 CRDT）。不在当前方案里打补丁。

**L6 — 迁移兼容性**
修复：PUT /api/doc/:id 的请求体格式版本化（`schema_version: 1`）。后端写入时保留 `schema_version` 字段，不做结构合并。若后续更改文档结构，通过 schema_version 区分处理路径，不默认用新格式覆盖旧字段。MVP 上线时不存在旧客户端，此条仅约束未来迭代行为。

**L7 — 轮询间隔内不可见**
接受的风险。MVP 用 2 秒轮询（GET /api/doc/:id 每 2 秒拉一次）解决「看不到对端编辑」问题，但 2 秒内的冲突窗口不做实时提示。用户在 2 秒内可能看到光标位置被重置（因为服务端内容覆盖了本地）。接受理由：MVP 目标是验证协作需求是否存在，不是验证协作体验是否完美。2 秒延迟和偶发的光标跳动在需求验证阶段是可以接受的用户体验折中。

**L8 — 后端并发写竞态**
修复：乐观锁的 CAS 操作必须是原子的。如果使用 SQL 数据库，用 `UPDATE docs SET content=$1, version=version+1 WHERE id=$2 AND version=$3 RETURNING version` 的单条 SQL 语句实现，不分两步「先读后写」。如果使用 Redis，用 Lua 脚本或 WATCH/MULTI/EXEC 事务保证原子性。具体选型在实现时确定，但原子写是硬性要求，不可以是「先 SELECT 再 UPDATE」的两步操作。

---

### 第 1 轮结束 → 检查新漏洞

L1 的修复（409 放弃本地编辑）引入了一个新问题：

**L9（新）— 409 时本地编辑静默丢失**
条件：用户 A 写了一段文字，PUT 返回 409（因为 B 同时写入了），前端用服务端内容覆盖本地，A 刚写的内容消失，界面上只有一行「内容已被更新，已同步最新版本」。用户不知道自己的内容去哪了，无法恢复。

进入第 2 轮。

---

### 第 2 轮：修复或接受

**L9 — 409 时本地编辑丢失**
修复：客户端收到 409 时，在覆盖本地内容之前，把当前本地内容快照到 `sessionStorage`（key：`doc_conflict_backup_{doc_id}_{timestamp}`）。提示从「内容已被更新，已同步最新版本」改为「内容冲突，已同步最新版本。你之前的编辑已暂存，[点击查看]」。点击后在侧边抽屉展示暂存内容，用户可以手动复制粘贴回编辑器。不做自动合并，不引入新的 UI 组件（抽屉是文本框，只读）。

---

### 第 2 轮结束 → 检查新漏洞

L9 的修复引入了 sessionStorage 依赖。检查：

- sessionStorage 在同一浏览器 Tab 内持久，Tab 关闭后清除——这符合预期，我们不需要跨 Tab 的冲突恢复。
- 同一用户在不同 Tab 打开同一文档，两个 Tab 各自维护独立的 inflight flag 和 last_seen_version，互相之间会产生 L1 同样的竞态。

**L10（新）— 同一用户多 Tab 并发写**
条件：用户在 Tab A 和 Tab B 同时打开同一文档，两个 Tab 各自独立发 PUT，乐观锁在 Tab 层面有效（先写的 Tab 成功，后写的 Tab 收到 409），但用户看到的是「自己的内容冲突了自己」，体验混乱。

修复或接受？接受的风险。理由：这是多 Tab 同时编辑同一文档的用户行为问题，不是协作问题。绝大多数用户不会同时在两个 Tab 编辑同一文档。MVP 阶段文档页面可以在标题加「检测到此文档在其他标签页打开」提示（通过 BroadcastChannel API，同域 Tab 间通信），但实现这个提示不在本次 MVP 范围，标记为 P2 改进项。

无新实质性漏洞。停止收敛。

---

## 收敛摘要

### 关闭的漏洞

- L1 最后写入胜出 → 乐观锁：PUT 携带 `last_seen_version`，后端原子 CAS，冲突返回 409
- L2 并发 PUT 乱序 → 客户端 inflight flag，同一时刻只允许一个进行中的 PUT
- L4 PUT 失败无感知 → 指数退避重试（最多 5 次）+ 持久警告横幅
- L6 迁移兼容性 → 请求体携带 `schema_version: 1`，后端保留字段不做结构合并
- L8 后端并发写竞态 → 强制原子写（单条 SQL UPDATE WHERE version=N 或 Redis 事务）
- L9 409 时本地编辑丢失 → 冲突前快照到 sessionStorage，提示用户查看暂存内容

### 接受的风险

- L5 带宽线性放大 → MVP 文档规模小，可接受；技术债明确，需求验证后优先替换增量同步
- L7 2 秒冲突窗口不实时提示 → MVP 目标是验证需求存在，2 秒延迟和光标跳动是可接受折中
- L10 同一用户多 Tab 并发写 → 极低频行为，乐观锁兜底可保数据安全，体验问题列 P2

---

## 最终方案（可直接执行规格）

### 概述

实时协作文档 MVP。多个用户可同时编辑同一篇文档。前端每 2 秒轮询拉取最新内容，同时每 2 秒提交本地内容。冲突通过乐观锁检测并向用户暴露，不做自动合并。

### 数据模型

```sql
CREATE TABLE docs (
  id          TEXT PRIMARY KEY,
  content     TEXT NOT NULL DEFAULT '',
  version     INTEGER NOT NULL DEFAULT 1,
  schema_version INTEGER NOT NULL DEFAULT 1,
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

`version` 是单调递增整数，每次成功写入加一。

### API 规格

**GET /api/doc/:id**
- 返回 200：`{ id, content, version, schema_version, updated_at }`
- 返回 404：文档不存在

**PUT /api/doc/:id**
- 请求体：`{ content: string, last_seen_version: number, schema_version: 1 }`
- 后端执行（SQL）：
  ```sql
  UPDATE docs
  SET content = $content,
      version = version + 1,
      updated_at = NOW()
  WHERE id = $id AND version = $last_seen_version
  RETURNING version
  ```
- 若 UPDATE 影响行数 = 1：返回 200 `{ version: <新version> }`
- 若 UPDATE 影响行数 = 0（版本不匹配）：执行一次 SELECT 取当前内容，返回 409 `{ current_content: string, current_version: number }`
- 若文档不存在：返回 404

（Redis 实现替代：Lua 脚本原子执行 GET + 版本比较 + SET，等价语义。）

**POST /api/doc**（创建新文档）
- 请求体：`{ content: '' }`
- 返回 201：`{ id, version: 1 }`

### 前端状态机

```
状态字段：
  localContent: string       // 编辑器当前内容
  lastSyncedVersion: number  // 上次成功 PUT 返回的 version，初始为从 GET 拿到的 version
  inflight: boolean          // 当前是否有 PUT 进行中
  syncStatus: 'ok' | 'retrying' | 'failed'  // 显示给用户
```

**轮询（GET，每 2 秒）：**
- 若 inflight === true，跳过本次 GET（避免用服务端内容覆盖用户正在编辑且未提交的内容）
- 否则 GET /api/doc/:id，若返回的 version > lastSyncedVersion，用服务端 content 覆盖 localContent，更新 lastSyncedVersion

**提交（PUT，每 2 秒）：**
- 若 inflight === true，跳过本次触发
- 否则：设 inflight = true，发送 PUT `{ content: localContent, last_seen_version: lastSyncedVersion, schema_version: 1 }`
- 成功（200）：lastSyncedVersion = 响应中的 version，inflight = false，syncStatus = 'ok'
- 冲突（409）：
  1. 将当前 localContent 存入 sessionStorage，key 为 `doc_conflict_backup_{id}_{Date.now()}`
  2. 用 409 响应中的 current_content 覆盖 localContent
  3. lastSyncedVersion = current_version
  4. inflight = false
  5. 显示提示：「内容冲突，已同步最新版本。你之前的编辑已暂存，[点击查看]」
  6. 点击「查看」弹出只读侧边抽屉，展示 sessionStorage 中的暂存内容，用户可手动复制
- 失败（5xx / 网络错误）：
  1. inflight = false
  2. syncStatus = 'retrying'，显示横幅「同步失败，正在重试」
  3. 指数退避重试：1s → 2s → 4s → 8s → 16s，最多 5 次
  4. 5 次后 syncStatus = 'failed'，横幅变为「无法同步，请复制内容另存」，停止自动重试
  5. 用户手动触发保存时重置重试计数

**编辑器事件：**
- 用户任意按键 → 更新 localContent（不触发 PUT，等计时器）
- 用户手动 Ctrl+S → 立即触发一次提交（若 inflight 则等当前完成后立即再提交一次）

### 错误提示 UI

- 同步正常：无提示（不展示成功指示器，减少视觉噪音）
- 重试中：编辑器顶部黄色横幅「同步失败，正在重试（第 N 次）」
- 彻底失败：红色横幅「无法同步，请复制内容另存」+ 按钮「手动重试」
- 冲突：蓝色横幅「内容冲突，已同步最新版本。[查看暂存的内容]」，点击展开只读抽屉

### 不在本次 MVP 范围内（显式 out-of-scope）

- 操作转换（OT）或 CRDT 增量合并
- 历史版本 / Undo 跨会话
- 用户在线状态展示（谁在编辑）
- 细粒度光标同步
- 同一用户多 Tab 提示（BroadcastChannel，列 P2）
- 文档超过 50KB 的流量优化

---

## 迭代数

**2 轮收敛**（第 1 轮修复 L1-L8，第 1 轮结束发现 L9；第 2 轮修复 L9，第 2 轮结束发现 L10 并接受风险，无新实质漏洞，停止）。
