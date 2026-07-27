完成。目录下只保留了两个文件：

- **`dirstat.py`**：核心逻辑封装为 `collect_stats(root)`（可被脚本/库调用，返回按字节数降序的 `{ext: {count, bytes}}`），CLI 支持 `--json`。目录不存在或不是目录时抛出 `DirStatError`（带 `code`/`message`），`main()` 捕获后输出结构化错误（JSON 模式写 `{"error": ..., "message": ...}` 到 stderr，非 JSON 模式写可读文本），退出码 1，不会有裸 traceback。
- **`test_dirstat.py`**：11 个 pytest 用例，覆盖多扩展名统计、无扩展名文件、空目录、按字节排序、目录不存在/路径非目录两种错误、以及 CLI 的 JSON/表格输出与错误路径（包括验证 stderr 中没有 `Traceback`）。

已用临时 venv 跑通 `pytest test_dirstat.py -q`（11 passed）并手动验证了 CLI 的表格输出、JSON 输出和错误场景，随后清理了 venv 和缓存文件。
