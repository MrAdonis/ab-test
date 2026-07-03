# `gitsum` 接口设计

单一只读命令：统计当前 git 仓库本周（周一 00:00 至今）提交数与改动文件数。

## 触发判定

- 是 agent-native 工具（明确"给 agent 调"）→ 四条硬契约全加
- 只读、无副作用 → 幂等性、破坏性操作安全 两条跳过（noise）

## 命令结构

```
gitsum [flags]
gitsum --help
gitsum --self-test
```

单命令，不设 subcommand——功能单一，不需要分层。

### Flags

| flag | 说明 | 默认 |
|---|---|---|
| `--json` | 结构化输出 | **true（默认开）** |
| `--human` | 人读格式（表格/彩色文本） | false |
| `--since <date>` | 覆盖"本周"，接受 `YYYY-MM-DD` 或 git 相对时间（`7.days.ago`） | 本周一 00:00（本地时区） |
| `--path <dir>` | 指定仓库路径 | cwd |
| `--self-test` | 跑内置测试套件，输出结果后退出 | — |
| `--help` | 输出分层 help | — |

不设 `--dry-run` / `--yes`：无写副作用，条件契约不触发。

## 输出 Schema（统一，所有路径同构）

```jsonc
// 成功
{
  "success": true,
  "data": {
    "since": "2026-06-29T00:00:00+08:00",
    "commits": 14,
    "files_changed": 23,
    "insertions": 512,
    "deletions": 88,
    "branch": "main"
  },
  "error": null
}

// 失败
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_A_GIT_REPO",   // 枚举，见下
    "message": "cwd is not inside a git working tree"
  }
}
```

- `--human` 时把同一份 `data`/`error` 渲染成文本表格，字段名不变，仅换渲染层——不是另一套结构。
- 退出码仅作辅助信号，**不是**判断依据：`0` = success:true，`1` = success:false。调用方必须读 `success` 字段，不解析 stderr / 猜 exit code（对应契约②）。
- stdout 只输出这个 JSON（或 `--human` 渲染），不掺日志；日志/调试信息一律走 stderr。

## 错误码枚举

```
NOT_A_GIT_REPO       // 当前路径非 git 仓库
NO_COMMITS_IN_RANGE  // 仓库正常，只是本周无提交（success:true, commits:0，不算错误——单独列出防止误判）
GIT_BINARY_NOT_FOUND // PATH 里找不到 git
INVALID_SINCE        // --since 传的日期解析失败
PERMISSION_DENIED     // 无权限读取 .git
INTERNAL_ERROR        // 兜底，附带原始 stderr 片段
```

不做 crash / 抛异常 / 裸 traceback——任何失败路径都落到上面某个 code，`message` 给人看，`code` 给程序判断分支（对应契约②：调用方按字段分支，不用字符串匹配 message）。

## 接口签名（伪代码）

```python
def gitsum(since: str | None, path: str, json_mode: bool) -> Result:
    repo = resolve_repo(path)          # 失败 -> Result.err(NOT_A_GIT_REPO / PERMISSION_DENIED)
    since_dt = parse_since(since)      # 失败 -> Result.err(INVALID_SINCE)
    commits = git_log_count(repo, since_dt)      # git rev-list --count --since=...
    stat = git_diff_stat(repo, since_dt)         # git log --since=... --numstat 聚合
    return Result.ok({
        "since": since_dt.isoformat(),
        "commits": commits,
        "files_changed": stat.files,
        "insertions": stat.ins,
        "deletions": stat.del_,
        "branch": current_branch(repo),
    })

class Result:
    success: bool
    data: dict | None
    error: {"code": str, "message": str} | None
```

## 自带测试（契约③）

```
gitsum --self-test
```

内置固定场景，跑完直接打印同构 Result 汇总，退出码反映是否全过：

- **正常路径**：临时初始化一个 git repo，造 3 个 commit（跨"本周/上周"边界），断言 `commits`/`files_changed` 数值正确
- **边界路径**：全新空仓库（0 commit）→ 断言 `success:true, commits:0`（走 `NO_COMMITS_IN_RANGE` 语义但非错误）；`--since` 传未来日期 → 0 结果
- **错误路径**：在非 git 目录跑 → 断言 `error.code == NOT_A_GIT_REPO`；`--since bad-date` → 断言 `INVALID_SINCE`

测试用临时目录 + 临时 git repo，不碰用户当前仓库，跑完自清理。

## 自描述 / 发现入口（契约④）

`--help` 分层，不一次 dump 全部：

```
$ gitsum --help
gitsum — summarize this week's git commit activity for agent consumption.

Usage:
  gitsum [--json|--human] [--since DATE] [--path DIR]
  gitsum --self-test
  gitsum --help

Output: always a JSON object {success, data, error} on stdout.
  - success:true  -> read fields from `data`
  - success:false -> read `data.error.code`; DO NOT parse message text or stderr
  - never parse stdout as plain prose — data is structured, always.

Examples:
  gitsum
    -> {"success":true,"data":{"commits":14,"files_changed":23,...},"error":null}

  gitsum --since 2026-06-01
    -> commits/files since a custom date instead of this Monday

  gitsum --path ../other-repo --human
    -> human-readable table for terminal display, same fields

  gitsum --self-test
    -> runs built-in test suite, verifies tool works before you rely on it

Error codes: NOT_A_GIT_REPO, NO_COMMITS_IN_RANGE, GIT_BINARY_NOT_FOUND,
             INVALID_SINCE, PERMISSION_DENIED, INTERNAL_ERROR
```

若打包为 skill 形式，同一内容落一份 `SKILL.md`，`--help` 与 `SKILL.md` 内容保持同源（一处维护，两处引用），避免漂移。

## 明确跳过项（及理由）

- **幂等性**：只读命令，天然幂等，重复跑无副作用可言——不写多余保证代码
- **`--dry-run` / `--yes`**：无破坏性操作，不适用
- **subcommand 分层**：功能单一到不需要 subcommand，`--help` 本身已分层（概览 vs 完整 flag 列表可用 `--help --full` 二级展开，非必需可先不做）
