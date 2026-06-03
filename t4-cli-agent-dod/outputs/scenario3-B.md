# gitsum — 接口设计（system-B，scenario3）

## 命令结构

```
gitsum [options]
gitsum --help
```

单一功能，无 subcommand。

---

## 关键 Flag

| Flag | 类型 | 说明 |
|------|------|------|
| `--since <date>` | string | 起始日期，默认本周一 00:00（ISO 8601 or `7d/2w`） |
| `--until <date>` | string | 结束日期，默认 now |
| `--repo <path>` | string | 目标 repo，默认 `cwd` |
| `--format json\|text` | string | 输出格式；默认 `json`（agent 用），`text` 供人读 |
| `--version` | bool | 打版本号 |
| `--help` | bool | 打帮助 + Examples |

---

## 输出 Schema

### 成功（`--format json`，默认）

```json
{
  "success": true,
  "data": {
    "repo": "/abs/path/to/repo",
    "period": {
      "since": "2026-05-26T00:00:00Z",
      "until": "2026-06-02T23:59:59Z"
    },
    "commits": 14,
    "files_changed": 37,
    "authors": ["alice", "bob"]
  },
  "error": null
}
```

### 失败

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_A_GIT_REPO",
    "message": "path /tmp/foo is not a git repository"
  }
}
```

所有路径（成功/失败/边界）均输出同一结构，退出码 0=success，1=failure，2=usage error。  
**Never parse stdout as plain text** — 读 `success` 字段判断成败，读 `data` 取值。

### 人读格式（`--format text`）

```
repo:    /abs/path/to/repo
period:  2026-05-26 → 2026-06-02
commits: 14
files:   37
authors: alice, bob
```

---

## 错误代码表

| code | 触发条件 |
|------|---------|
| `NOT_A_GIT_REPO` | `--repo` 路径或 cwd 不是 git 仓库 |
| `PATH_NOT_FOUND` | `--repo` 路径不存在 |
| `INVALID_DATE` | `--since`/`--until` 无法解析 |
| `GIT_NOT_FOUND` | 系统未安装 git |
| `PERMISSION_DENIED` | 无权读取 .git |

---

## 幂等性（契约 5）

只读操作，天然幂等。同一命令重复调用返回相同结构，无副作用。

---

## --help 输出（契约 4 + 7）

```
gitsum — summarize git activity for agent consumption

USAGE
  gitsum [--since <date>] [--until <date>] [--repo <path>] [--format json|text]

OPTIONS
  --since   start of period (default: this Monday 00:00)  e.g. 2026-05-26, 7d
  --until   end of period   (default: now)
  --repo    path to git repo (default: cwd)
  --format  json (default) | text

OUTPUT SCHEMA (json)
  { success, data: { repo, period, commits, files_changed, authors }, error }
  Read data.commits / data.files_changed — never parse stdout as plain text.

EXAMPLES
  gitsum
  gitsum --since 7d --format json
  gitsum --repo /path/to/project --since 2026-05-01 --until 2026-05-31
  gitsum --format text

EXIT CODES
  0  success
  1  runtime error (see error.code in JSON output)
  2  usage / argument error
```

---

## 自带测试（契约 3）

```bash
gitsum --test   # 跑内置测试套件，覆盖三类路径
```

测试覆盖：
- 正常：有 commit 历史的真实 repo，断言 `success=true` + `data.commits >= 0`
- 边界：`--since` 等于 `--until`，断言 `data.commits === 0` 且 `success=true`
- 错误：`--repo /tmp/nonexistent`，断言 `success=false` + `error.code=NOT_A_GIT_REPO`

输出：`{ "success": true, "data": { "passed": 3, "failed": 0 } }`

---

## SKILL.md 摘要（契约 4）

```markdown
## gitsum
Read-only git activity summarizer. Always returns { success, data, error }.

invoke: gitsum [--since <date>] [--repo <path>]
read:   data.commits, data.files_changed
never:  parse stdout as plain text
test:   gitsum --test
```
