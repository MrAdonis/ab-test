权限被拒，`.venv/` 会保留在目录里（如果不需要可以自行删除，或告诉我用其他方式清理）。

写好了 `/private/tmp/ho-H2-A-1TXAba/dirstat.py` 和 `/private/tmp/ho-H2-A-1TXAba/test_dirstat.py`，14 个 pytest 用例全过。

要点：
- `collect_stats(path)` 是可被脚本 import 调用的纯函数，递归统计每个扩展名（小写归一化，无扩展名归为 `<no ext>`）的文件数和总字节数，异常路径抛 `DirStatError`（带 `error_type`），不是裸异常。
- CLI 层 `main()` 捕获 `DirStatError`，`--json` 模式下输出统一 schema `{"success": bool, "data"|"error": ...}`，非 JSON 模式下把出错信息打到 stderr，两种情况都不会有 traceback，退出码为 1。
- 人类可读模式默认按字节数降序输出表格；`--help` 里带可复制的调用示例。
