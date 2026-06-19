# edgepush 工具接口设计

## 命令结构

```
edgepush deploy <dist-dir> --env <staging|production> [--project <name>] [--dry-run] [--yes]
edgepush status <deployment-id>
edgepush verify <deployment-id> --url <probe-url>
```

## 关键 Flag

| Flag | 说明 |
|------|------|
| `--env staging\|production` | 必填，目标环境 |
| `--project <name>` | 项目名，默认读 `edgepush.json` |
| `--dry-run` | 预览将上传的文件列表和目标 URL，不实际发布 |
| `--yes` | 跳过 production 确认提示（agent 调用必须带） |
| `--wait` | 等待部署就绪后再返回（默认 true） |
| `--timeout <sec>` | 等待超时，默认 120s |
| `--format json\|human` | 输出格式，默认 json |

## 统一输出 Schema

**成功：**
```json
{
  "success": true,
  "data": {
    "deployment_id": "dep_abc123",
    "env": "staging",
    "url": "https://staging.example.pages.dev",
    "files_uploaded": 42,
    "gate": {
      "status": "live",           // "live" | "auth_error" | "failed"
      "http_status": 200,
      "probe_url": "https://staging.example.pages.dev/_edge_probe",
      "asset_hash_match": true,   // 探针返回的 etag 与上传清单一致
      "latency_ms": 340
    }
  },
  "error": null
}
```

**失败：**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "GATE_AUTH_ERROR",    // 见错误码表
    "message": "API token rejected (403): check EDGEPUSH_TOKEN",
    "retry": true                 // agent 是否可自动重试
  }
}
```

## 验收闸（真实信号，三态分流）

deploy 命令返回前必须跑完闸，不信"上传没报错"：

```
step 1: 上传产物 → 拿到 deployment_id
step 2: 轮询平台部署状态 API → 等待 status == "active"（非 pending/building）
step 3: HTTP GET probe_url（平台 CDN 边缘节点）
         ├─ 2xx + asset_hash 匹配 → gate.status = "live"  → success: true
         ├─ 401/403              → gate.status = "auth_error" → success: false, retry: true
         └─ 5xx / timeout / DNS  → gate.status = "failed"    → success: false, retry: false
```

probe_url 默认是 `<env_url>/_edge_probe`（构建时注入的哈希端点），
fallback 到 `<env_url>/index.html` + 校验 ETag。

**多产物规则**：staging + production 同时发布时，每个环境独立过闸，
任一 `gate.status != "live"` 整体 `success: false`。

## 幂等性（有写副作用，触发条件满足）

相同 dist-dir + 相同 env 重复调用：
- 平台返回"内容未变"（hash 一致）→ 跳过上传，返回已有 deployment_id，`data.skipped: true`
- 平台不支持检测时：上传覆盖（幂等），gate 仍走三态闸

## 破坏性操作安全（production 触发）

- `--env production` 且无 `--yes`：打印变更摘要后 stdin 等确认，不自动执行
- `--dry-run`：只输出文件列表 + 目标 URL，不上传，`data.dry_run: true`

## 错误码表

| code | 含义 | retry |
|------|------|-------|
| `GATE_AUTH_ERROR` | token 无效或权限不足（401/403） | true（补配置后） |
| `GATE_FAILED` | 边缘节点 5xx 或超时 | false |
| `DEPLOY_TIMEOUT` | 平台侧部署超过 timeout 仍 pending | false |
| `UPLOAD_ERROR` | 文件上传失败 | true |
| `CONFIG_MISSING` | edgepush.json 或必填 flag 缺失 | false |

## 自带测试（一条命令跑）

```bash
edgepush test
# 覆盖三类路径：
# - 正常：mock dist + mock API → gate 返回 200 → success: true
# - 边界：空 dist-dir → CONFIG_MISSING
# - 错误：mock API 返回 403 → GATE_AUTH_ERROR, retry: true
```

## --help 入口（分层，不 dump 全手册）

```
edgepush --help          # 子命令列表
edgepush deploy --help   # deploy 完整 flag + Examples
edgepush status --help   # 查询 deployment_id 状态

Examples:
  # staging 发布（agent 调用）
  edgepush deploy ./dist --env staging --yes

  # production 发布，带 dry-run 预览
  edgepush deploy ./dist --env production --dry-run
  edgepush deploy ./dist --env production --yes

  # 单独补跑验收闸
  edgepush verify dep_abc123 --url https://staging.example.pages.dev

  # 自测
  edgepush test
```

## SKILL.md 关键声明（agent 调用须知）

```
- 所有命令输出均为 JSON，读 .success 判断成败，不 parse stdout 纯文本
- gate.status 是验收真值，success:true 但 gate.status != "live" 不存在
- production 部署 agent 必须带 --yes，否则阻塞等 stdin
- retry: true 的错误 = 前置未满足（补 token/配置），retry: false = 需人工介入
```
