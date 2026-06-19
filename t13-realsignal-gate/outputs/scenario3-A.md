# repostat 工具设计

## 命令结构

```
repostat [--since <date>] [--json] [--help]
```

只读、单一功能、无子命令。

**Flag 说明**

| Flag | 说明 |
|------|------|
| `--since <date>` | 统计起始日期，默认本周一（Monday 00:00 本地时间） |
| `--json` | 强制 JSON 输出（默认开，供 agent 调用）；`--no-json` 输出人读文本 |
| `--help` | 分层帮助，仅显示本命令手册 |

---

## 输出 Schema（JSON 默认）

```jsonc
// 成功
{
  "success": true,
  "data": {
    "since": "2026-06-09T00:00:00+08:00",   // ISO 8601
    "commit_count": 12,
    "changed_files": 34,
    "recent_commits": [
      {
        "hash": "a1b2c3d",
        "author": "Edon",
        "date": "2026-06-10T14:22:00+08:00",
        "message": "fix: correct typo in README"
      }
      // ...最多 5 条，按时间倒序
    ]
  },
  "error": null
}

// 失败
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_A_GIT_REPO",   // 机器可读
    "message": "Current directory is not a git repository"
  }
}
```

**错误码枚举**

| code | 触发条件 |
|------|---------|
| `NOT_A_GIT_REPO` | cwd 无 `.git`，`git rev-parse` 失败 |
| `GIT_NOT_FOUND` | `git` 二进制不在 PATH |
| `GIT_COMMAND_FAILED` | git 子命令非零退出，`message` 含 stderr |

不 crash、不裸 stderr。所有错误走 `{success:false, error}` 结构，退出码 0（调用方读 `success` 字段，不靠退出码）。

---

## 条件契约评估

- **幂等性**：只读工具，天然幂等，**不加**。
- **破坏性操作安全**：无写副作用，**不加** `--dry-run`。

---

## --help 输出（可复制调用示例）

```
repostat — Git repository weekly stats (read-only)

USAGE
  repostat [--since <date>] [--json] [--help]

FLAGS
  --since <date>   Start date for stats. Default: this Monday 00:00 local time.
                   Accepts: ISO 8601 date, e.g. 2026-06-09
  --json           JSON output (DEFAULT). Never parse stdout as plain text.
  --no-json        Human-readable text output
  --help           Show this help

OUTPUT SCHEMA (JSON)
  { success, data: { since, commit_count, changed_files, recent_commits[] }, error }
  On failure: { success: false, data: null, error: { code, message } }
  Always read the `success` field first.

EXAMPLES
  repostat
  repostat --since 2026-06-01
  repostat --no-json
```

---

## 自带可跑测试

单入口，一条命令跑完：

```bash
repostat --test
# 或
npm test   # / pytest / go test
```

**覆盖三类路径**

```
[正常] cwd = 真实 git repo
  → success=true, commit_count 为整数, recent_commits.length ≤ 5
  → 每条 commit 有 hash/author/date/message 字段

[边界] cwd = 无任何提交的空 repo（git init 后未 commit）
  → success=true, commit_count=0, changed_files=0, recent_commits=[]

[错误] cwd = 非 git 目录（/tmp 空目录）
  → success=false, error.code="NOT_A_GIT_REPO"
  → 进程退出码 = 0（不 crash）
```

---

## 怎么算"做完了 / 装好了"（验收）

**安装自证**（agent 可一条命令跑）：

```bash
repostat --test && echo "READY"
# 期望输出末行：READY
# 任一 case 失败则 success=false，输出 FAILED: <case_name>
```

**功能验收**（在任意 git repo 内）：

```bash
out=$(repostat)
# 必须满足：
jq -e '.success == true' <<< "$out"
jq -e '.data.commit_count | type == "number"' <<< "$out"
jq -e '(.data.recent_commits | length) <= 5' <<< "$out"
```

**错误路径验收**（在 /tmp 空目录内）：

```bash
out=$(cd /tmp && repostat)
jq -e '.success == false' <<< "$out"
jq -e '.error.code == "NOT_A_GIT_REPO"' <<< "$out"
```

三组 jq 命令全部返回 0 = 工具达 agent-native 标准。
