# repostat 工具接口设计

## 概览

只读、纯本地、单一功能。无写副作用，不触发幂等/破坏性/真实信号契约条件——这三条条件契约全部跳过。

---

## 命令结构

```
repostat [--since <date>] [--repo <path>] [--format json|text] [--help]
```

**flags：**
- `--since <date>`：统计起点，默认 `1 week ago`（git date 格式）
- `--repo <path>`：目标仓库路径，默认当前目录
- `--format json|text`：输出格式，默认 `json`（agent 调用用 json，人读用 text）

---

## 输出 schema（统一，所有路径同一结构）

```json
{
  "success": true,
  "data": {
    "period": {
      "since": "2026-06-03T00:00:00Z",
      "until": "2026-06-10T23:59:59Z"
    },
    "stats": {
      "commit_count": 12,
      "changed_files": 34
    },
    "recent_commits": [
      {
        "hash": "a1b2c3d",
        "date": "2026-06-10T14:22:00Z",
        "author": "edon",
        "subject": "fix: correct token budget threshold"
      }
      // ...最近 5 条
    ]
  },
  "error": null
}
```

失败时：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_A_GIT_REPO",   // 枚举值，见下方错误码表
    "message": "path /foo is not a git repository"
  }
}
```

**错误码枚举：**

| code | 触发条件 |
|------|---------|
| `NOT_A_GIT_REPO` | 目标路径无 `.git` |
| `GIT_NOT_FOUND` | 系统找不到 `git` 可执行文件 |
| `INVALID_DATE` | `--since` 值 git 无法解析 |
| `REPO_EMPTY` | 仓库无任何 commit |

不 crash、不裸 exit 1——任何异常走结构化 error 字段返回，exit code 统一为 0（调用方读 `success` 字段判断成败，不靠 exit code）。

---

## 实现骨架

```python
def run(since="1 week ago", repo=".", fmt="json"):
    result = {"success": False, "data": None, "error": None}
    try:
        validate_git_repo(repo)           # 抛 NotGitRepo / GitNotFound
        commits = git_log(repo, since)    # 抛 InvalidDate / RepoEmpty
        files   = git_changed_files(repo, since)
        result["success"] = True
        result["data"] = build_data(commits, files, since)
    except KnownError as e:
        result["error"] = {"code": e.code, "message": str(e)}
    except Exception as e:
        result["error"] = {"code": "UNKNOWN", "message": str(e)}
    output(result, fmt)
    sys.exit(0)   # 统一 exit 0，不依赖 exit code 传达失败
```

---

## 自带可跑测试（自证方式）

```
repostat --test
```

单命令跑内建测试套件，覆盖三类路径，退出前打印摘要：

```
repostat self-test:
  [PASS] normal: valid git repo returns commit_count >= 0
  [PASS] edge:   --since far future yields commit_count = 0, success = true
  [PASS] error:  non-repo path returns success=false, code=NOT_A_GIT_REPO
  [PASS] error:  bad --since value returns success=false, code=INVALID_DATE
  ALL 4 PASSED
```

输出同样是 json schema（`success`, `data.results[]`, `error`），agent 可机读。

**"做完了 / 装好了"的判定：**

```bash
repostat --test
# 读 .success == true AND .data.results 全部 passed == true
# 则视为安装验证通过
```

无外部依赖，纯本地执行，无需 mock、无需网络——自测即验收闸。

---

## 发现入口（SKILL.md 摘要 / --help 关键段）

```
NEVER parse stdout as plain text.
Always pass --format json (default). Read .success first; if false, read .error.code.

CALLING PATTERN (agent):
  result = json.loads(run("repostat --repo /path/to/repo"))
  if not result["success"]:
      handle_error(result["error"]["code"])
  stats = result["data"]["stats"]

INSTALL VERIFY:
  repostat --test   # all tests pass = ready

SUBCOMMANDS:
  repostat           # run report (default)
  repostat --test    # self-test
  repostat --help    # this message
```

---

## 约束契约对照

| 契约 | 本工具 | 满足/跳过 |
|------|--------|---------|
| 统一输出 schema | 所有路径同 `{success,data,error}` | ✅ 满足 |
| 结构化错误 | 枚举 code + message，exit 0 | ✅ 满足 |
| 自带可跑测试 | `--test` 覆盖正常/边界/错误 | ✅ 满足 |
| 发现入口 | `--help` + SKILL.md，含 Examples | ✅ 满足 |
| 幂等性 | 只读，天然幂等 | ⏭ 跳过（无写副作用） |
| 破坏性操作安全 | 只读 | ⏭ 跳过 |
| 真实信号验收闸 | 纯本地计算，无外部接受方 | ⏭ 跳过 |
