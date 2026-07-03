## `gitsum` 接口设计

### 定位
只做一件事：统计当前 git 仓库「本周」的提交数与改动文件数，供 agent 程序化调用。无交互、无副作用、幂等。

### 命令结构

```
gitsum [flags]
```

不设子命令 —— 单一功能不需要动词分层。

### Flags

| flag | 默认值 | 说明 |
|---|---|---|
| `--path <dir>` | `.` | 目标仓库路径 |
| `--since <git-date-expr>` | 本周一 00:00（本地时区） | 覆盖起始时间，接受 git 原生日期表达式（如 `"7 days ago"`） |
| `--until <git-date-expr>` | now | 覆盖结束时间 |
| `--no-merges` | true（默认排除 merge commit） | 设为 false 则计入 merge |
| `--author <string>` | 空（全部作者） | 按 `git log --author` 过滤 |
| `--format json\|text` | `json` | agent 场景默认结构化输出；`text` 供人读 |

不加 `--branch`／`--author-breakdown` 等：超出「单一摘要」范围，需要时再加。

### 输出（stdout，`--format json`）

```json
{
  "repo": "/abs/path/to/repo",
  "branch": "main",
  "since": "2026-06-29T00:00:00+08:00",
  "until": "2026-07-03T18:42:00+08:00",
  "commits": 17,
  "files_changed": 42
}
```

- `files_changed`：本周所有提交涉及文件路径的去重并集（非逐次 diff 相加）。
- 字段固定、无嵌套可选块 —— agent 解析不需要处理 schema 分支。

`--format text`：

```
17 commits, 42 files changed (2026-06-29 → 2026-07-03, branch main)
```

### 错误处理

约定：**agent 先看 exit code，再决定要不要解析 stdout**。

| 场景 | exit code | stdout | stderr |
|---|---|---|---|
| 正常 | 0 | JSON/text 摘要 | 空 |
| 当前目录非 git 仓库 | 2 | 空 | `error: not a git repository: <path>` |
| 区间内无提交（合法状态） | 0 | `commits:0, files_changed:0` | 空 |
| git 命令不存在 | 127 | 空 | `error: git not found in PATH` |
| 参数非法（如 `--since` 无法解析） | 64 | 空 | `error: invalid --since value: "<raw>"` |

不用 JSON 包裹错误 —— 错误走 stderr + 非零 exit，成功走 stdout，两个通道分离，agent 判断逻辑更简单（`if exit==0: json.parse(stdout)`）。

### 核心逻辑（伪代码）

```
func main(args):
    repoPath = resolveGitRoot(args.path)      # `git -C <path> rev-parse --show-toplevel`
                                                # 失败 -> exit 2

    since = args.since or startOfThisWeekLocal()
    until = args.until or now()

    branch = run("git -C {repoPath} rev-parse --abbrev-ref HEAD").trim()

    commitArgs = ["--since", since, "--until", until]
    if args.author: commitArgs += ["--author", args.author]
    if not args.no_merges == false: commitArgs += ["--no-merges"]

    commitCount = run("git log {commitArgs} --pretty=format:%H").lines().count()

    changedFiles = run(
        "git log {commitArgs} --name-only --pretty=format:"
    ).lines()
     .filter(nonEmpty)
     .toSet()
     .size()

    result = {repo, branch, since, until, commits: commitCount, files_changed: changedFiles}

    print(format(result, args.format))
    exit(0)
```

`startOfThisWeekLocal()`：本地时区周一 00:00（ISO 周起点），非「过去滚动 7 天」—— 与「本周」语义对齐；若 agent 想要滚动 7 天，用 `--since "7 days ago"` 覆盖。

### 测试要点（行为契约，非实现细节）

- 非 git 目录 → exit 2，stderr 含 `not a git repository`。
- 空仓库（无提交）→ exit 0，两个计数均为 0。
- 同一文件在本周内被 3 次提交修改 → `files_changed` 记 1 次，不是 3 次。
- `--since`/`--until` 传入非法字符串 → exit 64，不 panic。
- `--format text` 与 `--format json` 数值一致，只是渲染不同。
- 跨平台：Windows 路径分隔符不影响文件去重（统一用 git 输出的正斜杠路径作 key）。

### 安全性

- 所有参数只用于构造 `git` 子进程的 **argv 数组**，不经过 shell 拼接／`sh -c`，避免命令注入（尤其 `--author`、`--since` 允许任意字符串输入）。
- `--path` 解析后仅用于 `git -C <path> ...`，不做 `cd` 或路径拼接读文件。
