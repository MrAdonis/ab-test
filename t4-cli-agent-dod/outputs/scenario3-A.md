# gitsum — 接口设计（System-A，4 条契约）

## 命令结构

```
gitsum [--since <date>] [--repo <path>] [--format json|text]
```

单命令，无 subcommand。

**关键 flag：**
- `--since <date>`：统计起始日期，默认本周一 00:00（ISO 8601 或 `7d`/`1w` 相对格式）
- `--repo <path>`：目标 git 仓库路径，默认 `.`
- `--format json|text`：输出格式，**默认 json**（agent 调用路径）；`text` 是人读模式

## 输出格式（契约 1：统一 schema）

成功：

```json
{
  "success": true,
  "data": {
    "since": "2026-05-26T00:00:00Z",
    "until": "2026-06-02T23:59:59Z",
    "repo": "/abs/path/to/repo",
    "commit_count": 14,
    "changed_files": 23,
    "authors": ["alice", "bob"]
  },
  "error": null
}
```

`--format text` 时输出：

```
Since 2026-05-26: 14 commits, 23 changed files (alice, bob)
```

## 错误处理（契约 2：结构化错误）

所有失败路径统一返回并以退出码 1 退出，**不 crash、不裸 stderr**：

```json
{ "success": false, "data": null, "error": { "code": "NOT_GIT_REPO", "message": "/foo is not a git repository" } }
{ "success": false, "data": null, "error": { "code": "GIT_NOT_FOUND",  "message": "git binary not found in PATH" } }
{ "success": false, "data": null, "error": { "code": "INVALID_DATE",   "message": "--since value '2025-99-01' is not a valid date" } }
```

agent 读 `success` 字段判断成败，读 `error.code` 做分支处理，**不解析 message 字符串**。

## 核心逻辑（伪代码）

```python
def gitsum(since, repo, fmt):
    if not is_git_repo(repo):
        return error("NOT_GIT_REPO", ...)

    try:
        since_ts = parse_date(since)   # 失败 → INVALID_DATE
    except:
        return error("INVALID_DATE", ...)

    commits = run_git(
        ["log", f"--since={since_ts}", "--oneline"],
        cwd=repo
    )                                   # 失败 → GIT_ERROR

    files = run_git(
        ["log", f"--since={since_ts}", "--name-only", "--pretty=format:"],
        cwd=repo
    )

    return success({
        "since": since_ts.isoformat(),
        "until": now().isoformat(),
        "repo": abspath(repo),
        "commit_count": len(commits),
        "changed_files": len(set(files)),
        "authors": unique_authors(commits)
    })
```

## 自带测试（契约 3）

`gitsum --test` 自运行测试套件，覆盖三类路径：

```
gitsum --test

✓ normal:   real repo, current week → commit_count >= 0, changed_files >= 0
✓ edge:     repo with 0 commits this week → commit_count == 0
✓ error:    non-git dir → success==false, error.code=="NOT_GIT_REPO"
✓ error:    invalid --since value → success==false, error.code=="INVALID_DATE"

4/4 passed
```

测试退出码：全过 = 0，有失败 = 1。输出本身也遵循 JSON schema（`--format json` 时）。

## 发现入口（契约 4）

```
gitsum --help
```

输出必须包含：
1. 每个 flag 说明
2. **"Never parse stdout as plain text — always use --format json (default) and read .success / .data fields"**
3. 完整调用示例（agent pattern）：

```
# agent 调用示例
result=$(gitsum --since 1w --repo /path/to/project)
if [ "$(echo $result | jq -r .success)" = "true" ]; then
    count=$(echo $result | jq -r .data.commit_count)
fi
```

SKILL.md 等同于 `--help` 输出，不额外维护独立文档。
