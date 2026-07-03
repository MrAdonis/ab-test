# `deployctl` 接口设计

## 1. 命令结构

```
deployctl deploy <environment> --ref <git-ref> [flags]
deployctl list <environment> [flags]
deployctl rollback <environment> --to <version> [flags]
deployctl status <deployment-id> [flags]   # 查询单次部署/回滚的执行状态，供轮询
```

`<environment>` 为必填位置参数，取值枚举 `staging|production`，非法值直接报错退出，不做模糊匹配（避免 "prod" 之类的猜测导致误部署）。

## 2. 关键 Flag 设计

### `deploy`
```
--ref <string>        必填，git commit/tag/branch，禁止默认值（不允许"部署当前分支"这种隐式行为）
--yes                 显式确认破坏性操作；不带此 flag 且非 TTY 时直接失败退出（不阻塞等待输入）
--dry-run             只做校验+打印将执行的计划，不产生副作用
--wait                阻塞直到部署完成/失败，否则立即返回 deployment-id（异步）
--timeout <duration>  配合 --wait，默认 10m
--format json|table   默认 table（人看），agent 调用建议显式传 json
```

production 额外强制要求：`--ref` 必须是已存在的 tag（不接受任意分支名），在 flag 解析层就拒绝，不是运行时校验，防止"以为在部署某个commit,实际部署了分支最新值"的 TOCTOU。

### `list`
```
--limit <int>         默认 20
--since <duration>    如 --since 7d
--format json|table   默认 table
```
只读，无需 `--yes`。

### `rollback`
```
--to <version>        必填，必须是 list 输出中真实存在的 version id，不接受相对偏移(如 HEAD~1)，杜绝"数错了几步"的错误
--yes                 同 deploy
--dry-run             同 deploy，输出"当前版本 -> 目标版本"的 diff 摘要
--format json|table
```

## 3. 输出格式

统一 JSON schema（`--format json`，agent 调用方默认这个），核心字段：

```jsonc
// deploy / rollback 成功
{
  "status": "accepted" | "succeeded" | "failed",
  "deployment_id": "dep_01HXYZ",
  "environment": "production",
  "from_version": "v1.42.0",
  "to_version": "v1.43.0",
  "dry_run": false,
  "started_at": "2026-07-03T08:00:00Z"
}
```

```jsonc
// list
{
  "environment": "staging",
  "deployments": [
    {"version": "v1.43.0", "deployed_at": "...", "deployed_by": "...", "status": "succeeded"},
    ...
  ]
}
```

table 格式仅用于人类终端交互，两者字段一致，避免"两套信息模型"。

## 4. 错误处理

- **退出码**：`0` 成功；`1` 用户输入错误（非法 environment/version）；`2` 前置条件失败（缺 `--yes`、production 用了非 tag 的 ref）；`3` 执行期失败（部署脚本报错）；`4` 超时。区分清楚，避免调用方只能靠 stderr 文本判断。
- **错误输出**始终走 stderr，且 `--format json` 时错误也输出为 JSON（写到 stdout 还是 stderr 两边都保留一份结构化信息，方便脚本解析）：
  ```json
  {"error": "missing_confirmation", "message": "production deploy requires --yes", "code": 2}
  ```
- **幂等性**：`deploy`/`rollback` 支持 `--idempotency-key <string>`，重复提交同一 key 直接返回原 deployment 状态而不重新触发，防止网络重试/agent 重复调用造成二次部署。
- **无隐式确认**：任何破坏性操作缺少 `--yes` 时，不弹交互式 prompt 等待输入——直接失败退出并给出需要补充的 flag。这对人和 agent 调用方都是一致行为，不搞"检测到是否有 TTY 就分叉逻辑"的特殊路径。
- **dry-run 优先**：文档建议调用方（无论人还是 agent）执行 `deploy`/`rollback` 前先跑一次 `--dry-run`，把打印的计划展示给需要审批的人再决定是否补 `--yes` 重新执行。

## 5. 测试与文档要求（工程完成定义）

- 单元测试覆盖：非法 environment、缺 `--yes`、production 非 tag ref、幂等 key 重放、dry-run 不产生副作用。
- README 提供三条命令的完整 examples（含 json 输出样例）与退出码表。
- CI 中跑 `deployctl deploy staging --dry-run` 作为 smoke test，不允许直接对 production 跑集成测试。
