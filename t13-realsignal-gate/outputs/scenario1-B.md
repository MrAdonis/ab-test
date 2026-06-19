# otel-bootstrap 接口设计

## 命令结构

```
otel-bootstrap <subcommand> [flags]

subcommands:
  inject    向项目注入 OTel SDK 依赖与初始化代码
  verify    向远程后端发一条 smoke trace，读回 ingest 状态码做三态分流
  status    只读检查：SDK 文件是否已注入（不发网络请求）
```

## 关键 Flag

```
inject:
  --endpoint <url>       遥测后端 OTLP endpoint（必填）
  --token <token>        ingest token（必填，也可走 OTEL_TOKEN 环境变量）
  --runtime <node|go|python>  目标运行时（必填）
  --project-dir <path>   目标项目根目录（default: cwd）
  --dry-run              打印将写入的文件清单，不实际写入
  --yes                  跳过破坏性确认（覆盖已有 otel 配置时触发）

verify:
  --endpoint <url>
  --token <token>
  --timeout <sec>        等待 ingest 响应的超时（default: 10s）
```

## 统一输出 Schema

所有命令、所有路径统一返回同一 JSON 结构（--human flag 转可读格式）：

```json
{
  "success": true | false,
  "command": "inject | verify | status",
  "data": { /* 命令特有字段，见下 */ },
  "error": null | { "code": "...", "message": "...", "hint": "..." }
}
```

### inject data 字段
```json
{
  "files_written": ["src/telemetry.ts", "package.json"],
  "dry_run": false,
  "already_done": false   // 幂等：已注入时为 true，不重写
}
```

### verify data 字段（真实信号验收闸）
```json
{
  "gate": "pass | auth_error | backend_error",
  "http_status": 200,
  "trace_id": "abc123",
  "latency_ms": 42
}
```

### status data 字段
```json
{
  "injected": true,
  "files_found": ["src/telemetry.ts"],
  "endpoint_configured": "https://ingest.example.com"
}
```

## 错误处理

```json
// 401/403 → gate: "auth_error"，不声明成功，提示补 token
{
  "success": false,
  "command": "verify",
  "data": { "gate": "auth_error", "http_status": 401 },
  "error": {
    "code": "AUTH_FAILED",
    "message": "ingest endpoint returned 401",
    "hint": "check --token or OTEL_TOKEN; token may be expired"
  }
}

// 5xx / 超时 → gate: "backend_error"，归 bug 类
{
  "success": false,
  "data": { "gate": "backend_error", "http_status": 503 },
  "error": { "code": "BACKEND_ERROR", "message": "503 from endpoint", "hint": "retry or check endpoint health" }
}

// inject 覆盖已有配置但未带 --yes → 报错不写入
{
  "success": false,
  "error": { "code": "NEEDS_CONFIRM", "message": "existing otel config found", "hint": "re-run with --yes to overwrite" }
}
```

## "装好了"的定义（DoD）

inject + verify 两步都必须过闸，缺一不算完成：

```
Step 1: inject --dry-run          → 检查写入清单无误
Step 2: inject --yes              → success:true, already_done:false/true
Step 3: verify                    → gate:"pass", http_status:2xx, trace_id 非空
```

三态分流（verify 必须走，不信"inject 没报错"）：
- gate=pass           → 完成，trace_id 可作 audit log
- gate=auth_error     → 前置未满足，回补 token，重跑 verify
- gate=backend_error  → 真 bug，debug endpoint 再继续

多运行时项目：每个 runtime inject 后独立跑一次 verify，不允许批量 inject 后只验一条。

## 幂等性（inject 有写副作用）

同一 inject 命令执行两次：
- 文件内容 hash 不变 → no-op，data.already_done=true
- 文件已存在但内容不同 → 报 NEEDS_CONFIRM，不覆盖

## 自带测试入口

```
otel-bootstrap test [--endpoint <mock-url>]
```
覆盖三类路径（一条命令，输出标准 JSON，exit 0=全过）：
- 正常：mock endpoint 返回 200，verify gate=pass
- 边界：inject 两次，第二次 already_done=true
- 错误：mock endpoint 返回 401，verify success=false, gate=auth_error

## --help 分层示例（inject 子命令）

```
otel-bootstrap inject --help

Inject OTel SDK into target project.

Usage:
  otel-bootstrap inject --endpoint <url> --token <token> --runtime node [flags]

Examples:
  # dry run first
  otel-bootstrap inject --endpoint https://ingest.ex.com --token $OTEL_TOKEN --runtime node --dry-run

  # actual inject
  otel-bootstrap inject --endpoint https://ingest.ex.com --token $OTEL_TOKEN --runtime node --yes

  # then verify the real signal gate
  otel-bootstrap verify --endpoint https://ingest.ex.com --token $OTEL_TOKEN

Output: JSON {success, command, data:{files_written, already_done}, error}
Never parse stdout as plain text — read .success and .data fields.
```
