# `deployctl` 接口设计

## 命令结构

```
deployctl deploy   <env> <version>  [flags]   # 破坏性
deployctl rollback <env> <version>  [flags]   # 破坏性
deployctl list     [--env <env>] [--limit N]  # 只读
deployctl status   <env> <deployment-id>      # 只读
deployctl selftest                            # 自带测试
deployctl --help / deploy --help / ...        # 分层帮助
```

`env` ∈ `{staging, production}`；`version` 为 git sha 或 tag。

## 统一输出 schema

所有命令、所有路径（成功/失败/异常）输出同一结构，**JSON 默认开**，`--human` 才切人读格式：

```json
{
  "success": true,
  "data": { "...命令相关字段..." },
  "error": null
}
```

失败：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VERSION_NOT_FOUND",
    "message": "version abc123 not found in staging deploy history",
    "retryable": false
  }
}
```

- 退出码仍设置（0/1），但 agent 不应依赖它判断业务成败，只看 `success` 字段
- 永不裸抛 stack trace 到 stdout；未捕获异常也要落进 `error.code = INTERNAL_ERROR`

## 关键 flag（破坏性命令）

```
deployctl deploy production v2.3.1 \
  --dry-run          # 预览：打印将执行的变更 + 影响范围，不落地
  --yes               # 跳过交互确认（agent 必传，否则报错要求确认）
  --idempotency-key <key>   # 可选；同 key 重试直接返回上次结果，不重复部署
  --timeout 300s
```

```
deployctl rollback production --to v2.3.0 --yes [--dry-run]
```

- 人类默认不传 `--yes` → 走终端交互确认；agent 场景必须显式传 `--yes`，否则返回结构化错误 `error.code=CONFIRMATION_REQUIRED`，不阻塞等待 stdin（agent 卡死的常见坑）
- `--dry-run` 输出 `data.plan`：目标版本、当前版本、影响的服务列表、预估耗时,不产生真实副作用

## 幂等性设计

deploy/rollback 都是有写副作用的破坏性操作，agent 可能因超时重试，必须幂等：

- 同一 `(env, version, idempotency-key)` 组合：若已有进行中/已完成的部署，直接返回该次结果（`data.deduped: true`），不重新触发
- 未传 `idempotency-key` 时，用 `env+version+调用方指纹` 做默认去重窗口（如 5 分钟内相同请求视为重试）
- 目标状态已是当前版本时，deploy 视为 no-op 成功，返回 `data.noop: true`，而非报错

## 各命令输出示例

**deploy 成功**
```json
{"success":true,"data":{"deployment_id":"dep_9f3","env":"production","version":"v2.3.1","status":"completed","noop":false},"error":null}
```

**list**
```json
{"success":true,"data":{"deployments":[
  {"id":"dep_9f3","env":"production","version":"v2.3.1","status":"completed","deployed_at":"2026-07-03T08:00:00Z"}
]},"error":null}
```

**rollback 失败（版本不在历史内）**
```json
{"success":false,"data":null,"error":{"code":"VERSION_NOT_FOUND","message":"v9.9.9 not in last 50 deployments for production","retryable":false}}
```

## 错误码集合（结构化，供 agent 分支判断）

`CONFIRMATION_REQUIRED` `VERSION_NOT_FOUND` `ENV_LOCKED`（有部署正在进行）`DEPLOY_FAILED`（构建/健康检查失败，`retryable:true`）`INTERNAL_ERROR`

## 自带可跑测试

```
deployctl selftest [--json]
```

- 内部起本地 mock backend，跑三类路径：正常部署→list 可见、边界（重复 idempotency-key 去重、rollback 到不存在版本）、错误（未传 --yes 的破坏性调用被拒绝）
- 输出同一 schema：`{"success":true,"data":{"passed":12,"failed":0,"cases":[...]}}`
- CI 与 agent 都用它做“工具本身是否可用”的自证，不依赖外部环境

## 自带发现入口

- 顶层 `deployctl --help` 只列 subcommand 一览 + 1 行用途，不 dump 全部 flag
- `deployctl deploy --help` 才展开该子命令的完整 flag 与 **Examples**：
  ```
  Examples:
    deployctl deploy staging v2.3.1 --yes
    deployctl deploy production v2.3.1 --dry-run
    deployctl rollback production --to v2.3.0 --yes --idempotency-key rb-2026-07-03-01
  ```
- 配套 `SKILL.md`：开头即写明「所有输出为 JSON，读 `success`/`error.code` 字段，禁止 parse stdout 文本」，并给出上面这几条真实调用样例

## 边界说明

`list`/`status` 是只读，不加 dry-run/幂等（天然幂等，加了是噪音）。`deploy`/`rollback` 因不可逆且 agent 可能重试，是本设计中唯一需要幂等 + dry-run + 显式确认三件套的命令。
