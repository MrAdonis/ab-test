`__pycache__` 是 Python 运行时自动生成的缓存目录,不影响交付,不必删。

已完成 `/tmp/t69h-h2-cli-C-j2aLwY/dirstat.py` 和 `/tmp/t69h-h2-cli-C-j2aLwY/test_dirstat.py`,10 个 pytest 用例全部通过。

要点:
- `collect_stats()` 递归统计各扩展名(小写,无扩展名归为 `<no ext>`)的文件数与总字节数,单文件读取失败(权限/损坏软链)会静默跳过而不中断整体统计
- 路径不存在或不是目录时抛 `DirStatError`(带 `code` 字段:`path_not_found` / `not_a_directory`),不会冒出裸 traceback
- CLI 支持 `--json`:成功输出 `{"success": true, "data": {...}}`,失败输出 `{"success": false, "error": {"code", "message"}}` 到 stdout;不带 `--json` 时成功打印表格,失败打印简短 `error: ...` 到 stderr,exit code 均为 0/1,可被脚本按退出码 + JSON 字段消费
- 跑测试:`python3 -m pytest test_dirstat.py -v`(需要 pytest,环境是 externally-managed,建议用 venv 装)
