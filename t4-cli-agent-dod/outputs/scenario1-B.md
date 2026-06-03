# scenario1-B — deployctl 接口设计（system-B，7 条契约）

## 命令结构

```
deployctl <subcommand> [flags]

Subcommands:
  deploy    部署到 staging 或 production
  list      列出历史部署记录
  rollback  回滚到指定版本
```

## 统一输出 schema（契约 1）

所有子命令输出同一结构，JSON 默认开：

```json
{
  "success": true | false,
  "data": { ... },     // 成功时的结果
  "error": null | {    // 失败时非空
    "code": "ERR_DEPLOY_FAILED",
    "message": "human-readable reason",
    "details": { ... } // 可选，结构化补充
  }
}
```

人读格式：`--format=text`（可选 flag，agent 不传）

---

## deploy

```
deployctl deploy --env <staging|production> --version <semver|git-sha>
                 [--dry-run] [--yes] [--format=json|text]
```

**破坏性安全（契约 6）**：
- 默认交互确认（human safe）
- `--dry-run`：输出将做什么，不实际部署
- `--yes`：agent 显式跳过确认

**幂等性（契约 5）**：
- 同一 `--env` + `--version` 已部署且状态为 active → 返回 `success:true`，`data.already_deployed: true`，no-op

```json
// 成功
{
  "success": true,
  "data": {
    "deployment_id": "dep_abc123",
    "env": "staging",
    "version": "1.4.2",
    "status": "active",
    "deployed_at": "2026-06-02T10:00:00Z",
    "already_deployed": false
  },
  "error": null
}

// dry-run
{
  "success": true,
  "data": {
    "dry_run": true,
    "env": "production",
    "version": "1.4.2",
    "would_replace": "dep_xyz999 (1.4.1)"
  },
  "error": null
}
```

---

## list

```
deployctl list [--env <staging|production>] [--limit <n>] [--format=json|text]
```

无破坏性，无幂等性约束。

```json
{
  "success": true,
  "data": {
    "deployments": [
      {
        "deployment_id": "dep_abc123",
        "env": "staging",
        "version": "1.4.2",
        "status": "active",
        "deployed_at": "2026-06-02T10:00:00Z"
      }
    ],
    "total": 12
  },
  "error": null
}
```

---

## rollback

```
deployctl rollback --env <staging|production> --to <deployment_id|version>
                   [--dry-run] [--yes] [--format=json|text]
```

**破坏性安全（契约 6）**：同 deploy，`--dry-run` + `--yes`。

**幂等性（契约 5）**：
- 目标版本已是当前 active → `success:true`，`data.already_active: true`，no-op

```json
// 成功
{
  "success": true,
  "data": {
    "deployment_id": "dep_old456",
    "env": "production",
    "version": "1.3.9",
    "status": "active",
    "rolled_back_from": "dep_abc123",
    "already_active": false
  },
  "error": null
}
```

---

## 错误处理（契约 2）

不 crash，不裸 stderr。所有失败路径统一走结构化错误：

```json
// 版本不存在
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERR_VERSION_NOT_FOUND",
    "message": "version '9.9.9' not found in registry",
    "details": { "requested_version": "9.9.9" }
  }
}

// 破坏性命令未传 --yes 且非 TTY（agent 环境）
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERR_CONFIRMATION_REQUIRED",
    "message": "destructive operation requires --yes in non-interactive mode",
    "details": { "hint": "pass --dry-run to preview or --yes to proceed" }
  }
}
```

退出码：`0` = success，`1` = structured error（agent 读 `success` 字段，不靠退出码）

---

## 分层 --help + Examples（契约 7）

```
deployctl --help          # 顶层：仅列 subcommands + 一行描述，不 dump 全手册
deployctl deploy --help   # 子命令展开，含真实例子：

Examples:
  # 部署到 staging（agent 调用模式）
  deployctl deploy --env staging --version 1.4.2 --yes

  # 预览 production 部署不实际执行
  deployctl deploy --env production --version 1.4.2 --dry-run

  # 回滚 production 到上一个版本
  deployctl rollback --env production --to dep_old456 --yes
```

---

## 自带可跑测试（契约 3）

```
deployctl test            # 内置测试套件，一条命令跑完

# 覆盖三类路径：
# - 正常：deploy staging → list → rollback
# - 边界：幂等（重复 deploy 同版本）、dry-run 无副作用
# - 错误：不存在的版本、非 TTY 无 --yes
```

---

## SKILL.md 发现入口（契约 4）

```markdown
# deployctl

Agent 调用规范：
- 所有输出为 JSON，读 `success` 字段判断成败，不解析 stdout 字符串
- 破坏性操作（deploy/rollback）必传 `--yes`，否则返回 ERR_CONFIRMATION_REQUIRED
- 先跑 `deployctl list` 获取 deployment_id，再用于 rollback
- `--dry-run` 可安全预览任何操作
- 运行 `deployctl test` 自验工具可用

Calling pattern:
  deployctl deploy --env staging --version <ver> --yes
  deployctl list --env production --limit 5
  deployctl rollback --env production --to <deployment_id> --yes
```
