写好了两个文件：

- **`dirstat.py`** — 核心逻辑 `collect_stats()` 递归遍历目录，按扩展名（小写，含点；无扩展名归为 `""`）统计文件数和总字节数；`main()` 是 CLI 入口，支持位置参数 `path` 和 `--json`。错误统一走 `DirStatError`（`path_not_found` / `not_a_directory`），非 JSON 模式打印 `Error: ...` 到 stderr，`--json` 模式打印结构化 JSON 错误对象到 stderr，两种情况都是 exit code 1，不会有裸 traceback。
- **`test_dirstat.py`** — 8 个 pytest 用例，覆盖：递归统计正确性、缺失目录/路径是文件时抛出结构化错误、JSON 输出格式与排序、CLI 端到端（表格/JSON/退出码/无 traceback）。

用临时 venv 跑通了全部 8 个测试，并手动验证了 CLI 三种场景（表格输出、`--json`、目录不存在时两种模式的报错）。测试完已清理 `.venv`，仓库里只留下这两个文件。
