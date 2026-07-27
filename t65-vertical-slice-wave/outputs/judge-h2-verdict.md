两份都没有在 `--help` 里放可复制的调用示例（`argparse` 的 `epilog`/`RawDescriptionHelpFormatter` 都没用），这是明确列出的需求，两边同罚。

## 评分

| 维度 | 甲 | 乙 |
|---|---|---|
| 1. 统一输出 schema | 7 | 6 |
| 2. 结构化错误 | 8 | 6 |
| 3. 测试质量 | 8 | 8 |
| 4. --help 自描述 | 5 | 4 |
| 5. 代码质量 | 9 | 7 |
| **总分** | **37** | **31** |

## 逐项理由

**1. 输出 schema**：两份形状其实一样（成功 = `{ext: {count, bytes}}` 走 stdout，失败 = `{error, message}` 走 stderr），都没有统一信封（如 `{"ok": ..., "data"/"error": ...}`），也都没有 schema 版本/扫描根等元信息；且 argparse 的用法错误（缺参数）在两边都会吐非 JSON 文本 + exit 2，`--json` 消费者仍需特判。甲扣分点：错误对象靠 `**details` 变形，`path_not_found` 有 `path` 而 `internal_error` 没有，键集不固定。乙扣分点更实：键混用 `.txt` 与 `(no extension)`（带点 vs 带括号空格的自造字面量），且没导出常量，脚本只能硬编码这个字符串；甲把它提为 `NO_EXT_KEY` 可被 import。乙的 `sort_keys=True` 让键序确定，是它这项唯一实打实的优势（甲是文件系统顺序，跨机不稳定）。

**2. 结构化错误**：主要分差点。乙的 `entry.stat().st_size` 没有保护，`main` 只 catch `DirstatError` —— 权限不可读文件、扫描中途被删的文件（TOCTOU）都会以裸 traceback 出栈，正是需求禁止的形态。甲两道防线：逐文件 `except OSError: continue`，外加兜底 `except Exception` 转 `internal_error`，保证任何路径都不吐 traceback。甲的兜底也有代价（会把真 bug 压成一行 message，且丢了 debug 信息，建议加 `--debug` 开关放行 traceback），但相对乙是明确更强。

**3. 测试**：打平，理由不同。甲对错误路径覆盖更全（missing / not-a-dir / JSON 与 text 双分支 / exit code），断言用整字典相等，更强；靠 `run()` 返回三元组测试，不依赖 capsys。乙独有两个 `subprocess` 端到端用例，能抓到 shebang、`__main__` 装配、真实 returncode 这类甲完全没覆盖的问题，这价值不低。两边共同缺口：`--help` 无断言、`.TXT/.txt` 大小写归并无断言（两份都实现了却都没测）、空目录的 `"No files found."` 文本分支无断言、权限错误无覆盖。

**4. --help**：都没有示例，只有一行 description。甲多 0.5~1 分是因为 `"Emit machine-readable JSON output"` 比 `"Output as JSON"` 更说明用途，且模块 docstring 更完整。两份都应补：`epilog="Examples:\n  dirstat.py . --json | jq '.[\"txt\"].bytes'"`。

**5. 代码质量**：甲有完整类型标注、`run()/main()` 分离（纯函数化，IO 只在 main 一处）、常量提取、docstring 说明了跳过策略。乙更短更直白，但把路径校验塞进 `collect_stats` 让这个函数职责混合（库使用者拿不到"只统计"的纯函数），无类型标注，`format_text` 的 `sorted` 里重复索引 `stats[e]` 也略糙。乙唯一更好的一点是排序键 `(-bytes, ext)` 有确定的 tiebreak，甲的 `sorted(..., reverse=True)` 在 bytes 相同时顺序不稳定。

## 选择

**选甲（37 vs 31）**——核心差距是乙的 `stat()` 无保护会在权限/竞态下漏出裸 traceback，直接违反"结构化报错"这条硬需求，而甲的 `run()` 三元组设计同时买到了更强的错误兜底和更干净的可测试性；把乙的 subprocess 端到端用例和 `sort_keys` 移植进甲即为最优解。
