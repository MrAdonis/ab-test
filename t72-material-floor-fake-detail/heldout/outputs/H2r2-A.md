Works correctly — human-readable table, JSON output, and structured error (exit 1, no traceback) all verified. All 10 pytest cases pass.

`/private/tmp/ho2-H2-A-LaKQ06/dirstat.py`（CLI 本体）和 `/private/tmp/ho2-H2-A-LaKQ06/test_dirstat.py`（10 条 pytest 用例）已写好并跑通。

要点：
- `collect_stats()` 是核心函数，目录不存在抛 `PathNotFoundError`、路径不是目录抛 `NotADirectoryStatError`，都带 `code`/`message`/`path` 结构化字段
- `main()` 捕获这些异常后按 `--json` 分支输出到 stderr（JSON 或 `Error: ...`），退出码 1，不会有裸 traceback
- `--json` 成功时输出 `{"success": true, "path": ..., "data": {ext: {count, total_bytes}}}`，扩展名统一转小写合并（`.py`/`.PY` 算一类），无扩展名归到 `<no-ext>`
- 测试覆盖：统计正确性、递归子目录、空目录、缺失路径报错、非目录报错、JSON/人类可读两种错误输出、以及用 `subprocess` 真实调用 CLI 验证退出码和无 traceback

我用 `.venv` 装了 pytest 跑测试（没碰系统 Python），仓库根目录多了个 `.venv/` 和 `.pytest_cache/`，需要的话可以删掉。
