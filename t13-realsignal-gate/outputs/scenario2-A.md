# edgepush 工具接口设计

## 命令结构

```
edgepush <subcommand> [options]

subcommands:
  deploy    发布构建产物到目标环境
  verify    验证已发布版本是否在目标环境生效
  status    查询当前部署状态（只读）
```

---

## `deploy` 命令

```
edgepush deploy --env <staging|production> --dir <build_dir> [--dry-run] [--yes]
```

**关键 flag：**
- `--env`（必填）：`staging` 或 `production`
- `--dir`（必填）：本地构建产物目录
- `--dry-run`：预览将上传的文件列表及目标 URL，不执行上传
- `--yes`：跳过 production 环境的人工确认提示（agent 调用时必传）
- `--wait`（默认 true）：上传完成后等待平台传播，完成后自动调用 verify

**触发条件契约：**
- **幂等性**：相同 content hash 二次上传返回 `already_deployed`，不重新推送
- **破坏性操作安全**：`--env production` 无 `--yes` 时交互确认；`--dry-run` 不触碰远端

---

## 输出 Schema（统一，所有路径）

```json
{
  "success": true | false,
  "command": "deploy | verify | status",
  "data": {
    "deployment_id": "dep_abc123",
    "env": "staging",
    "url": "https://my-app-staging.pages.dev",
    "content_hash": "sha256:a1b2c3...",
    "status": "deployed | already_deployed | propagating | live | failed",
    "verify": {
      "probed_url": "https://my-app-staging.pages.dev",
      "response_hash": "sha256:a1b2c3...",
      "hash_match": true,
      "latency_ms": 412,
      "checked_at": "2026-06-10T12:34:56Z"
    }
  },
  "error": null | {
    "code": "AUTH_FAILED | UPLOAD_TIMEOUT | HASH_MISMATCH | ENV_UNKNOWN | ...",
    "message": "human-readable description",
    "retryable": true | false
  }
}
```

**"做完了"的验收条件（deploy --wait）：**

`success: true` AND `data.status == "live"` AND `data.verify.hash_match == true`

---

## `verify` 命令（可独立调用）

```
edgepush verify --env <staging|production> --hash <content_hash> [--timeout 60]
```

探测逻辑：
1. HTTP GET 目标 URL（含 Cache-Buster header）
2. 计算响应体 hash
3. 与 `--hash` 比对，一致则 `hash_match: true`
4. 超时仍不一致返回 `success: false, error.code: VERIFY_TIMEOUT, error.retryable: true`

---

## 错误处理

```
# 所有错误走 JSON，不 crash，不裸 stderr
{
  "success": false,
  "command": "deploy",
  "data": null,
  "error": {
    "code": "HASH_MISMATCH",
    "message": "deployed hash a1b2c3 != probed hash d4e5f6 after 60s",
    "retryable": true
  }
}

# retryable=true  → agent 可以自动重试 verify
# retryable=false → agent 应上报人工介入（AUTH_FAILED / ENV_UNKNOWN 等）
```

---

## `--help` 入口（发现）

```
edgepush --help           # 顶层：subcommand 列表 + 核心 flag
edgepush deploy --help    # 分层展开，不一次 dump 全手册
```

**必含 Examples（可直接复制）：**

```bash
# staging 发布（agent 调用模式）
edgepush deploy --env staging --dir ./dist --yes

# production dry-run 预览
edgepush deploy --env production --dir ./dist --dry-run

# 独立验证（deploy 后补跑或失败重试）
edgepush verify --env staging --hash sha256:a1b2c3...

# 查当前状态（只读，不修改）
edgepush status --env production
```

---

## SKILL.md 关键声明（agent 发现入口）

```markdown
## Output
Always JSON. Never parse stdout as plain text.
Read `data.verify.hash_match` to confirm propagation—do NOT assume deploy == live.

## Done condition
success: true AND data.status == "live" AND data.verify.hash_match == true

## Agent flags
Always pass --yes to skip interactive prompts.
Pass --wait (default true) to block until verify completes.

## Retry guidance
error.retryable == true → retry verify with same --hash
error.retryable == false → escalate to human
```

---

## 自带可跑测试

```bash
edgepush test          # 跑内置测试套件，输出 JSON 结果

# 覆盖三类路径：
# 1. 正常：mock staging 发布 → verify hash_match == true
# 2. 边界：相同 hash 二次 deploy → status == already_deployed
# 3. 错误：hash 不一致 → verify 超时 → retryable=true
```
