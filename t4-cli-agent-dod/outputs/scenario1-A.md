# deployctl — 接口设计（system-A / 4条契约）

## 命令结构

```
deployctl deploy   --env <staging|production> --version <tag|sha>  [--dry-run] [--force]
deployctl list     [--env <staging|production>] [--limit <n>]
deployctl rollback --env <staging|production>  --to <deployment-id>  [--dry-run] [--force]
deployctl test     # 自带可跑测试（契约3）
```

关键 flag：
- `--dry-run`：预检，不执行破坏性操作，返回 `data.plan`
- `--force`：跳过确认门（production 默认拦截，agent 调用须显式传入）
- `--json` / `--no-json`：默认 JSON 输出，`--no-json` 切人读格式

---

## 统一输出 schema（契约1）

所有命令输出同一根结构，JSON 默认开：

```typescript
interface Output {
  success: boolean
  command: string          // "deploy" | "list" | "rollback"
  data:    DeployResult | ListResult | RollbackResult | DryRunPlan | null
  error:   ErrorPayload | null
  meta: {
    duration_ms: number
    timestamp:   string    // ISO 8601
    env:         string | null
  }
}

interface ErrorPayload {
  code:    string          // 机器可读，见下方错误码表
  message: string          // 人读摘要
  detail:  string | null   // stack / 上游错误原文
}
```

`deploy` data：
```typescript
interface DeployResult {
  deployment_id: string
  env:           "staging" | "production"
  version:       string
  url:           string
  status:        "ok" | "partial"
}
```

`list` data：
```typescript
interface ListResult {
  deployments: Array<{
    deployment_id: string
    env:           string
    version:       string
    deployed_at:   string
    status:        "active" | "superseded" | "rolled_back"
  }>
  total: number
}
```

`rollback` data：同 `DeployResult`，加 `rolled_back_from: string`。

`dry-run` data：
```typescript
interface DryRunPlan {
  dry_run: true
  steps:   string[]        // 将执行的步骤列表
  risk:    "low" | "medium" | "high"
}
```

---

## 错误处理（契约2）

**不 crash，不裸 stderr，退出码只做信号**：

| code                     | 场景                              | exit |
|--------------------------|-----------------------------------|------|
| `ENV_INVALID`            | `--env` 不是 staging/production   | 1    |
| `VERSION_NOT_FOUND`      | tag/sha 不存在                    | 1    |
| `DEPLOYMENT_NOT_FOUND`   | rollback `--to` 的 id 不存在      | 1    |
| `PRODUCTION_GUARD`       | production 操作缺 `--force`       | 2    |
| `DEPLOY_FAILED`          | 部署过程失败（上游）              | 3    |
| `ROLLBACK_FAILED`        | 回滚过程失败                      | 3    |
| `AUTH_ERROR`             | 凭证缺失或过期                    | 4    |

示例失败输出（`deployctl rollback --env production --to abc123`，无 `--force`）：
```json
{
  "success": false,
  "command": "rollback",
  "data": null,
  "error": {
    "code": "PRODUCTION_GUARD",
    "message": "production rollback requires --force flag",
    "detail": null
  },
  "meta": { "duration_ms": 12, "timestamp": "2026-06-02T10:00:00Z", "env": "production" }
}
```

---

## 自带可跑测试（契约3）

```bash
deployctl test
# 覆盖：
#   normal  — staging deploy + list + rollback（dry-run 模式，不打真环境）
#   edge    — --limit 0、版本 sha 极长串、回滚到最新版本自身
#   error   — 缺 --env、错误 deployment-id、production 无 --force
# 退出码 0 = 全过；非零 = 有失败，输出同统一 schema
```

---

## 自带发现入口（契约4）

`deployctl --help` 输出包含：

```
OUTPUT FORMAT
  All commands return JSON by default:
    { success, command, data, error, meta }
  Never parse stdout as plain text — read `data` on success, `error.code` on failure.

AGENT CALLING PATTERN
  1. deployctl deploy --env staging --version <tag>
     → check success; read data.deployment_id for reference
  2. deployctl list --env staging --limit 5
     → read data.deployments[].deployment_id
  3. deployctl rollback --env staging --to <deployment_id>
     → for production, always pass --force after human confirmation
  4. deployctl deploy --dry-run to inspect plan before committing
```

---

## 破坏性操作保护小结

- `deploy` + `rollback` 在 `--env production` 时，缺 `--force` 返回 `PRODUCTION_GUARD` 错误，不执行。
- Agent 编排建议：先 `--dry-run` 取 `data.plan`，确认 risk 级别后再带 `--force` 真跑。
- `list` 是只读操作，无保护门。
