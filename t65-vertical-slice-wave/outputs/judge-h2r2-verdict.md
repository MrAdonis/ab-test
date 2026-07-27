## 评分表

| 维度 | 甲 | 乙 |
|---|---|---|
| 1. 统一输出 schema | **9** | 5 |
| 2. 结构化错误 | 8 | **8** |
| 3. 测试质量 | 8 | **9** |
| 4. --help 自描述 | **5** | 4 |
| 5. 代码质量综合 | **9** | 7 |
| **总分** | **39 / 50** | **33 / 50** |

## 各维度依据

**1. 输出 schema（差距最大）**
甲的 JSON 是带信封的稳定契约：`{path, extensions:[{extension,count,bytes}], total_files, total_bytes}`，表格与 JSON 共用 `_stats_to_rows()`，两条路径不可能漂移；排序结果放在**数组**里，顺序对消费者可靠。
乙的 JSON 是裸 map `{".txt":{count,bytes}}`：没有 path、没有 total（而表格却打了 TOTAL —— 两种输出模式信息量不一致，脚本得自己 reduce）；且"按 bytes 降序"依赖 dict 插入序，而 JSON object 按规范是无序的，多数解析器（jq 除外的部分场景、Go map、多数 schema 校验）不保证保留顺序 —— 把排序编码进 object key 顺序是脆的。裸 map 还无法在不破坏兼容的前提下加字段。

**2. 结构化错误**
基本打平。甲多一个 `path` 字段（机器可用），乙在文本模式打出了错误码 `Error [not_found]: ...`（人可用），各有一处优势。两者都是 stderr + exit 1、无 traceback，都没兜底 `except OSError` 处理"根目录不可读"这类失败（甲 `onerror=lambda e: None` 静默吞掉，乙靠 rglob 静默吞掉）—— 同样扣分。

**3. 测试质量**
乙更全：空目录、排序断言、两条错误路径都走了 `main()`、并且断言了出错时 `captured.out == ""`（防止脏输出污染管道），12 vs 8 个用例。
甲胜在断言了聚合正确性（total_files/total_bytes）和 JSON 可解析 + 有序性。两者都没测 `--help` 和缺参数时的 exit code 2。

**4. --help**
都不达标：**没有 epilog、没有一条可复制的调用示例**，这是需求点 4 的核心，两份都只有一行 description。甲略高，因为 `prog="dirstat.py"` 打出的 usage 可直接粘贴；乙 `prog="dirstat"` 与实际文件名不符，用户照抄会 command not found。

**5. 代码质量**
甲：dataclass + 采集/格式化/IO 三层分离，`os.walk` 单次 stat，异常时 `continue` 前不落脏数据。
乙有个真实缺陷：`stats.setdefault(ext, ...)` 在 `stat()` 的 try 之前执行，一旦 stat 抛 OSError 就 `continue`，会**留下一个 count=0/bytes=0 的空扩展名条目**输出给用户。另外排序逻辑塞进了 `collect_stats`（采集函数越权做展示排序）、每个文件两次 stat（`is_file()` + `stat()`）、已有 `from __future__ import annotations` 却仍用 `typing.List/Optional/Union`。

## 结论

**选甲。** `--json` 的价值就在于契约稳定，甲的信封式 schema（含 path/totals、排序落在数组里）直接可被脚本消费，而乙的裸 map 少了聚合值又把顺序寄托在 JSON object key 上；乙更全的测试用例是容易补进甲的，乙的 schema 却要破坏性重构才能修。

补甲的两条建议：给 parser 加 `epilog`（`dirstat.py ./src --json | jq '.total_bytes'`）并设 `formatter_class=RawDescriptionHelpFormatter`；把乙的空目录、排序、stdout 洁净度三个用例抄过来。
