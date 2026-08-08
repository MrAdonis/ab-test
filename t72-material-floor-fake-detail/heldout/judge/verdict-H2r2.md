## 评分

| 维度 | 甲 | 乙 |
|---|---|---|
| 统一输出 schema | 9 | 7 |
| 结构化错误 | 8 | 9 |
| 测试覆盖质量 | 8.5 | 8 |
| --help 与可发现性 | 9 | 4 |
| 代码质量整体 | 8 | 8.5 |
| **合计** | **42.5** | **36.5** |

## 各维度理由

**统一输出 schema.** 甲两条分支顶层同形（`success` 恒在），成功体是 `extensions: [{extension, files, bytes}]` 的对象数组，外加 `total_files` / `total_bytes`。乙把数据放进 `data: {".py": {...}}`——扩展名当键。这是本次最实质的分歧：数据当键的后果是消费方 jq 要写 `.data.".py"`（带点的键得引号）、无法直接 `map`/`sort_by`，而且乙在 `stats_to_dict` 里辛苦排的序在 JSON 对象里对消费方是不可依赖的语义，等于白排。乙还漏了总计——它的人类输出有 TOTAL 行、JSON 没有，两种模式信息不对等，脚本方得自己求和。需求点名"支持 --json 被脚本调用"，这一维正是需求的重心。

**结构化错误.** 这维乙赢。`DirStatError` 基类 + 两个子类 + `to_dict()`，错误体多带 `path` 字段，且 `collect_stats` 自己做校验、抛类型化异常，模块被 import 时同样有结构化失败语义；甲的 `validate_path` 返回 `(Path, err_dict)` 元组，是 CLI 形状的，复用性差一截。流的选择两边都站得住：乙恒定走 stderr（Unix 正统，但脚本方 `json.loads(stdout)` 会撞空串 decode error），甲 JSON 模式把错误也放 stdout（单流消费更省事，且在 `--help` 里写明了）。甲的问题是错误落哪个流取决于 `--json`，不够自洽；乙的问题是没告诉任何人错误在 stderr。

**测试覆盖质量.** 接近。甲 9 条全走 subprocess，测的是真实契约（退出码、stdout/stderr 分流、文本模式、`--help`），但漏了大小写折叠（代码 `.lower()` 了却没测）。乙 10 条分层更好——capsys 测函数、subprocess 测 CLI，还专门验了 `.py` 与 `.PY` 合并、异常类型和 `code`/`path` 字段。但乙有两个明显空洞：`format_human` 的成功路径**一行没测**（连 `no files found` 那个分支也没有），`--help` 完全没测。甲成功路径的文本输出是测了的。

**--help 与可发现性.** 差距最大的一维，也是甲拉开总分的主因。甲的 epilog 直接把成功/失败两种 JSON 形状、退出码语义、三条可复制示例（含 `| jq '.extensions'`）写进了 `--help`，agent 或人拿到二进制就能自描述地用起来。乙只有一行中文 description，没有 schema、没有示例、没有退出码说明——脚本作者只能去读源码才知道 `data` 是什么形状、错误在哪个流。给别的程序调用的工具，这一项不是加分项而是及格线。

**代码质量整体.** 乙略优。类型注解、`from __future__ import annotations`、dataclass、`ensure_ascii=False`（甲会把非 ASCII 扩展名转义成 `\uXXXX`，仍是合法 JSON 但不可读）、列宽按最长扩展名动态计算（甲写死 20 字符，长扩展名会撑歪表格）。扣分项：`from dataclasses import dataclass, field` 里的 `field` 没用到；以及一处**注释与实现不符**——docstring 说"符号链接文件按其自身大小统计"，但 `os.path.getsize` 内部走 `os.stat` 是跟随符号链接的，拿到的是目标文件大小，要拿链接自身大小得用 `os.lstat`。两份代码运行时行为其实一致，只有乙宣称了错的那个。

## 结论

**甲更好，但差距的性质需要说清楚：明显，且高度集中。**

总分差 6 分，其中 5 分来自 `--help` 一项、2 分来自 schema 形状，其余三维乙实际上还净赢 1 分。也就是说——甲赢在"这东西交出去别人能不能直接用"，乙赢在"这段代码本身写得怎么样"。乙的工程素养（异常体系、类型、可 import 的核心函数、分层测试）看得出来更熟，但它把工具当库写完就收工了，没做完面向调用方的那一半：schema 形状对 jq 不友好、JSON 少了总计、`--help` 空着。需求明写"支持 --json 被脚本调用"，甲正好在这条线上全部踩中。

如果这是招人或定 owner：甲这份可以直接合，乙这份要打回补三样——epilog 加 schema 和示例、`data` 改成对象数组并补 `total_files`/`total_bytes`、补 `format_human` 成功路径的测试（顺手删掉没用的 `field` 导入、修掉 symlink 那句 docstring）。补完之后乙会反超甲，因为它的错误模型和模块化底子更好。反过来甲该吸收乙的三点：类型化异常、错误体带 `path`、`ensure_ascii=False`，再补一条 `.PY`/`.py` 合并的测试。
