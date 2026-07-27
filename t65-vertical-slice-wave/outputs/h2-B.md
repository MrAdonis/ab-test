Works as expected — structured JSON error (not a traceback), correct exit code, and both output modes function correctly.

完成。已创建两个文件：

- **`dirstat.py`**：CLI 工具，统计目录下各扩展名文件数和总字节数
  - `collect_stats(root)` — 核心逻辑，可被其他脚本导入调用
  - `--json` 输出结构化 JSON，默认输出人类可读文本
  - 目录不存在 / 路径非目录时抛 `DirstatError`（带 `code`/`message`），CLI 层捕获后输出结构化错误到 stderr 并返回 exit code 1，不会有裸 traceback
  - 无扩展名文件归入 `"(no extension)"` 类别

- **`test_dirstat.py`**：10 个 pytest 用例，覆盖核心统计逻辑、空目录、缺失路径、非目录路径、JSON/文本输出、错误处理，以及两个通过 `subprocess` 实际调用 CLI 脚本的端到端测试。全部通过（用 `/usr/bin/python3 -m pytest` 运行，因为默认 `python3` 环境没装 pytest）。
