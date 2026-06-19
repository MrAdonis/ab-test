# otel-bootstrap — 接口设计文档

## 命令结构

```
otel-bootstrap <subcommand> [options]

subcommands:
  inject      把 OTel SDK 注入到目标项目
  verify      发一条 test span，确认 traces 真的到达远端
  status      只读：读已注入的配置并报告状态
  remove      撤销注入（破坏性，需 --yes）
```

## 关键 Flag

```
inject:
  --project-dir <path>    目标项目根目录（默认 cwd）
  --endpoint <url>        OTLP HTTP/gRPC 推送地址（必填）
  --token <str>           ingest token，优先读 OTEL_AUTH_TOKEN 环境变量
  --runtime <node|python|go>  自动检测，可手动指定
  --dry-run               打印将要修改的文件，不实际写入
  --yes                   跳过确认，供 agent 调用

verify:
  --endpoint <url>        同 inject；可复用注入后写入的 .otelrc
  --token <str>
  --timeout-ms <n>        等待 ack 的超时（默认 10000ms）

status:
  --project-dir <path>

remove:
  --project-dir <path>
  --dry-run
  --yes
```

## 统一输出 Schema（JSON 默认开）

所有 subcommand 输出同一结构：

```json
{
  "success": true | false,
  "command": "inject | verify | status | remove",
  "data": { ... },       // 成功时的负载（见各命令细节）
  "error": null | {
    "code": "CONNECT_FAILED | AUTH_REJECTED | RUNTIME_UNSUPPORTED | ...",
    "message": "人读描述",
    "detail": "原始错误或 HTTP 状态"
  }
}
```

加 `--human` flag 输出纯文本，JSON 是默认；agent 调用 **不加** `--human`，直接读字段。

### inject data 负载

```json
{
  "runtime": "node",
  "files_modified": ["src/instrumentation.ts", "package.json"],
  "env_vars_added": ["OTEL_EXPORTER_OTLP_ENDPOINT", "OTEL_AUTH_TOKEN"],
  "idempotent": false,     // true = 已注入过，本次 no-op
  "next_step": "run `otel-bootstrap verify` to confirm live signal"
}
```

### verify data 负载

```json
{
  "trace_id": "abc123...",
  "latency_ms": 342,
  "backend_ack": true,     // 关键字段：false = 推出去但没收到 ack
  "signal": "REAL"         // REAL | SYNTHETIC | NONE
}
```

`signal: REAL` = 真实 trace 到达远端，**这是"装好了"的判据**。

### status data 负载

```json
{
  "injected": true | false,
  "endpoint": "https://...",
  "runtime": "node",
  "last_verify": "2026-06-10T12:34:56Z" | null
}
```

## 错误处理

失败一律 `success: false`，不 crash，不裸 exit(1) without JSON：

```json
{ "success": false, "command": "verify", "data": null,
  "error": { "code": "CONNECT_FAILED",
             "message": "无法连接 endpoint，检查 URL 和网络",
             "detail": "connect ECONNREFUSED 4318" } }
```

错误码枚举（agent 按 code 分支，不解析 message）：
- `CONNECT_FAILED` — TCP 连不上
- `AUTH_REJECTED` — token 错误（HTTP 401/403）
- `BACKEND_NO_ACK` — 推出去但没收到 ack（backend 可能在吃数据但不回应）
- `RUNTIME_UNSUPPORTED` — 项目运行时无法识别
- `ALREADY_INJECTED` — inject 时已存在注入（非错误，`success:true` + `idempotent:true`）
- `PROJECT_NOT_FOUND` — `--project-dir` 不存在

## 幂等性（inject 有写副作用）

`inject` 同一目录跑两次：
- 检测到已注入 → `success:true`, `data.idempotent:true`，文件不重复修改
- agent 重试安全，无重复 SDK 注册

## 破坏性操作安全（remove）

```bash
# 人类默认走确认提示
otel-bootstrap remove --project-dir ./myapp
# → "将删除 instrumentation.ts，移除 3 个环境变量。继续？[y/N]"

# agent 调用加 --yes 跳过
otel-bootstrap remove --project-dir ./myapp --yes

# dry-run 预览
otel-bootstrap remove --project-dir ./myapp --dry-run
```

## "装好了"验收定义（DoD）

**充分条件（全部满足）：**

```
1. inject 返回 success:true, idempotent:false（或幂等第二次 idempotent:true）
2. verify 返回 success:true AND data.backend_ack:true AND data.signal:"REAL"
```

只有 inject 成功而 verify 失败 = **未完成**，coding agent 应报 blocked 状态。

```bash
# agent 调用示例（两步验收）
otel-bootstrap inject --endpoint https://ingest.example.com/otlp \
  --token $OTEL_AUTH_TOKEN --yes
otel-bootstrap verify --timeout-ms 15000
# 读 .data.signal === "REAL" 才算 done
```

## 自带可跑测试

```bash
otel-bootstrap test            # 跑全套内置测试
otel-bootstrap test --suite unit|integration|e2e
```

覆盖三类：
- **正常路径**：mock backend ack → inject+verify 全流程 success
- **边界**：已注入目录重跑 inject → idempotent:true
- **错误路径**：endpoint 不可达 → CONNECT_FAILED；token 错误 → AUTH_REJECTED

---

> **Agent 使用须知**：永远不要解析 stdout 纯文本——读 `.success` / `.error.code` / `.data.signal` 字段。
