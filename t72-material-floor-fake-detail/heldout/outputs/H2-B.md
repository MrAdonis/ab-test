已完成，全部 8 项测试通过。

- `/private/tmp/ho-H2-B-AY6krR/dirstat.py` — CLI 本体：`collect_stats()` 按扩展名（无扩展名归 `no_ext`）统计文件数和字节数；`run()` 返回统一 `{success, data|error}` 结构，目录不存在/不是目录时给结构化报错而非裸 traceback；`--json` 输出 JSON，默认输出对齐文本表格；`--help` 带可复制的调用示例
- `/private/tmp/ho-H2-B-AY6krR/test_dirstat.py` — 覆盖正常统计、空目录、嵌套子目录、路径不存在、路径是文件而非目录、CLI JSON 输出、CLI 无 JSON 参数文本输出、CLI 报错不带 traceback

跑测试：`cd /private/tmp/ho-H2-B-AY6krR && .venv/bin/python -m pytest test_dirstat.py -v`（当前环境是 PEP 668 externally-managed，已建 `.venv` 装了 pytest）。
