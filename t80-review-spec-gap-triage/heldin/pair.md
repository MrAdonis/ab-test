# 两份代码 review 报告盲评

下面是同一份代码（按同一需求单实现）的两份 review 报告，来自两位不同的 reviewer。请先自己读需求单和代码，再逐条核对两份报告的每条发现是否成立，然后打分。

打分维度（各 1-10）：
1. **覆盖面**：真实缺陷 + 实现替需求单拍板的未定义行为，抓到多少、漏了什么关键的
2. **真实性**：有没有断言代码里不存在的问题、夸大低概率场景、把正常行为报成缺陷（每条误报扣分）
3. **归因与处置**：需求单已写明的问题是否给了具体修法；需求单没写的行为是否交回需求方定（带当前行为 + 推荐答案），而不是让实现者按 reviewer 猜测再猜一次；标反方向要扣分
4. **可用性**：实现者拿到报告能不能直接开工，优先级是否清楚

输出格式：
- 先逐份列「成立的发现 / 误报 / 归因有误」三个清单（带原文摘录）
- 再给分数表：| 报告 | 覆盖面 | 真实性 | 归因与处置 | 可用性 | 合计 |
- 最后一句话结论：甲更好 / 乙更好 / 打平，并说明最关键的差异是什么

## 需求单

# dirstat.py 需求单

写一个 Python CLI `dirstat.py`：输入一个目录路径，统计各扩展名的文件数和总字节数。要能被脚本调用（支持 `--json`），目录不存在时给结构化报错而不是裸 traceback，附带能跑的 pytest。

## 代码 dirstat.py

```python
#!/usr/bin/env python3
"""统计目录下各扩展名文件数量与总字节数。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


class DirstatError(Exception):
    """dirstat 业务错误的基类，携带结构化字段，不抛裸 traceback。"""

    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type
        self.message = message

    def to_dict(self) -> dict:
        return {"type": self.error_type, "message": self.message}


class PathNotFoundError(DirstatError):
    def __init__(self, path: str):
        super().__init__("PathNotFoundError", f"路径不存在: {path}")


class NotADirectoryDirstatError(DirstatError):
    def __init__(self, path: str):
        super().__init__("NotADirectoryError", f"路径不是目录: {path}")


NO_EXT_KEY = "<no-ext>"


def collect_stats(root: str | os.PathLike) -> dict[str, dict[str, int]]:
    """递归统计 root 下各扩展名的文件数和总字节数。

    返回形如 {".py": {"count": 3, "bytes": 1234}, "<no-ext>": {...}} 的字典。
    路径不存在或不是目录时抛出 DirstatError 子类，不抛裸异常。
    """
    root_path = Path(root)

    if not root_path.exists():
        raise PathNotFoundError(str(root))
    if not root_path.is_dir():
        raise NotADirectoryDirstatError(str(root))

    stats: dict[str, dict[str, int]] = {}
    for dirpath, _dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            ext = file_path.suffix.lower() or NO_EXT_KEY
            try:
                size = file_path.stat().st_size
            except OSError:
                # 损坏的符号链接等不可 stat 的文件，跳过不计入
                continue
            entry = stats.setdefault(ext, {"count": 0, "bytes": 0})
            entry["count"] += 1
            entry["bytes"] += size

    return stats


def build_result(root: str, stats: dict[str, dict[str, int]]) -> dict:
    total_files = sum(v["count"] for v in stats.values())
    total_bytes = sum(v["bytes"] for v in stats.values())
    return {
        "success": True,
        "root": root,
        "stats": stats,
        "total_files": total_files,
        "total_bytes": total_bytes,
    }


def format_human(result: dict) -> str:
    lines = [f"目录: {result['root']}"]
    rows = sorted(result["stats"].items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    if not rows:
        lines.append("(空目录，无文件)")
    else:
        lines.append(f"{'扩展名':<12}{'文件数':>8}{'总字节数':>14}")
        for ext, info in rows:
            lines.append(f"{ext:<12}{info['count']:>8}{info['bytes']:>14}")
    lines.append(f"合计: {result['total_files']} 个文件, {result['total_bytes']} 字节")
    return "\n".join(lines)


def build_error_result(err: DirstatError) -> dict:
    return {"success": False, "error": err.to_dict()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dirstat.py", description="统计目录下各扩展名的文件数和总字节数"
    )
    parser.add_argument("path", help="要统计的目录路径")
    parser.add_argument(
        "--json", action="store_true", help="以 JSON 格式输出（默认人类可读格式）"
    )
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirstatError as err:
        error_result = build_error_result(err)
        if args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"错误: {err.message}", file=sys.stderr)
        return 1

    result = build_result(args.path, stats)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 测试 test_dirstat.py

```python
import json

import pytest

import dirstat


def _make_files(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")  # 5 bytes
    (tmp_path / "b.txt").write_bytes(b"world!")  # 6 bytes
    (tmp_path / "c.py").write_bytes(b"print(1)")  # 8 bytes
    (tmp_path / "noext").write_bytes(b"xx")  # 2 bytes, no extension
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.py").write_bytes(b"x")  # 1 byte, nested
    return tmp_path


def test_collect_stats_counts_and_bytes(tmp_path):
    root = _make_files(tmp_path)
    stats = dirstat.collect_stats(root)

    assert stats[".txt"] == {"count": 2, "bytes": 11}
    assert stats[".py"] == {"count": 2, "bytes": 9}
    assert stats[dirstat.NO_EXT_KEY] == {"count": 1, "bytes": 2}


def test_collect_stats_recurses_into_subdirectories(tmp_path):
    root = _make_files(tmp_path)
    stats = dirstat.collect_stats(root)
    # d.py 在 sub/ 下，应被计入 .py 的合计里
    assert stats[".py"]["count"] == 2


def test_collect_stats_empty_directory(tmp_path):
    stats = dirstat.collect_stats(tmp_path)
    assert stats == {}


def test_collect_stats_extension_case_insensitive(tmp_path):
    (tmp_path / "a.TXT").write_bytes(b"abc")
    (tmp_path / "b.txt").write_bytes(b"de")
    stats = dirstat.collect_stats(tmp_path)
    assert stats[".txt"] == {"count": 2, "bytes": 5}


def test_collect_stats_missing_path_raises_structured_error(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(dirstat.PathNotFoundError) as exc_info:
        dirstat.collect_stats(missing)
    assert exc_info.value.error_type == "PathNotFoundError"
    assert str(missing) in exc_info.value.message


def test_collect_stats_path_is_file_not_dir_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    with pytest.raises(dirstat.NotADirectoryDirstatError) as exc_info:
        dirstat.collect_stats(file_path)
    assert exc_info.value.error_type == "NotADirectoryError"


def test_main_json_output_success(tmp_path, capsys):
    _make_files(tmp_path)
    exit_code = dirstat.main([str(tmp_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["success"] is True
    assert payload["root"] == str(tmp_path)
    assert payload["total_files"] == 5
    assert payload["total_bytes"] == 22
    assert payload["stats"][".py"]["count"] == 2


def test_main_json_output_missing_dir_is_structured_not_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.err == ""  # 结构化错误走 stdout JSON，不是裸 traceback
    payload = json.loads(captured.out)
    assert payload["success"] is False
    assert payload["error"]["type"] == "PathNotFoundError"


def test_main_human_output_missing_dir_prints_to_stderr(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "错误" in captured.err
    assert str(missing) in captured.err


def test_main_human_output_readable_table(tmp_path, capsys):
    _make_files(tmp_path)
    exit_code = dirstat.main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "合计: 5 个文件, 22 字节" in captured.out


def test_main_path_is_file_returns_error(tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    exit_code = dirstat.main([str(file_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["error"]["type"] == "NotADirectoryError"
```

## 报告 甲

## P0（静默错误数据）

- **权限受限目录被静默吞掉，产出的统计"看起来完整但实际残缺"**：`collect_stats` 用 `os.walk(root_path)`，未传 `onerror` 回调，`os.walk` 默认 `onerror=None` 会静默吞掉 `scandir` 抛出的 `PermissionError` 等异常，被拒目录直接跳过、不计入、不报错。极端情况下如果 **root 本身**不可读，`os.walk` 会静默返回空结果，此时 `collect_stats` 返回 `{}`，与"真的是空目录"完全无法区分——调用方拿到 `success: true, total_files: 0` 却不知道数据是残缺的。这正好命中 coding-dod 定义的"静默错误数据"红线，且测试套件里没有任何用例覆盖这个分支（无法证明当前行为是有意为之）。

## P1（正确性边界）

- **符号链接语义不一致，且可能与用户直觉（如 `du`/`ls`）不符**：`file_path.stat()`（第 57 行）默认 `follow_symlinks=True`，会把符号链接解析到目标文件后取其体积计入统计，但 `os.walk` 默认 `followlinks=False` 又会跳过符号链接目录。也就是"文件型软链接"被跟随计数（可能把目录外任意大小的文件算进来，或造成硬链接/软链接重复计数），"目录型软链接"却被忽略。这是未声明、未测试的行为组合，容易在真实文件树（如带 `node_modules` 符号链接的项目)上产生反直觉的总字节数。

## P2（标题）

- 异常类命名冗余：`NotADirectoryDirstatError` 中间夹带 "Dirstat" 不一致于同级的 `PathNotFoundError`，纯风格问题
- 隐藏文件（如 `.gitignore`）因 `Path.suffix` 特性被归入 `<no-ext>`，属于 pathlib 标准行为但未在 SPEC/文档/测试中说明，属边界澄清缺口

## 总体评估

核心功能（递归统计、`--json`、结构化报错、pytest 覆盖）已按 SPEC 落地且测试可跑通，但存在一个静默产出错误数据的 P0 缺口（权限受限目录/根目录被吞不报错）和一个未声明的符号链接语义不一致问题，建议修复后再合入。

## 报告 乙

## 代码审查结果

**测试执行**：`pytest test_dirstat.py` 11 passed，实现与测试自洽。

### P0

1. **[需求缺口] 不可读文件被静默剔除，输出仍标记 `success: true` 且总数看似完整** — `dirstat.py:56-60`：`file_path.stat()` 抛 `OSError`（损坏符号链接、权限拒绝）时直接 `continue`，不计入任何统计,也不在返回结果里留痕迹。同理 `os.walk` 默认 `onerror=None`，遇到不可读子目录同样静默跳过。SPEC 只说"目录不存在时给结构化报错"，完全没提对"部分文件不可访问"这种场景的期望行为——所以这不是编码错误,是实现者自己拍的边界决策。但因为 SPEC 明确要求"能被脚本调用",下游脚本会把 `total_files`/`total_bytes` 当作完整可信的数字,而实际可能悄悄漏计。需要向需求方确认三选一:(a) 维持现状静默跳过;(b) 结果里加 `skipped: [{path, reason}]` 字段暴露给调用方;(c) 遇到不可访问文件直接报错退出。我的推荐是 (b)——既不中断正常统计,也不让调用方在不知情下拿到偏低的数字。

### P1

1. **[需求缺口] TOCTOU 竞态**：`collect_stats` 先 `exists()`/`is_dir()` 检查再 `os.walk`,如果目录在检查通过后、遍历开始前被删除/替换,`os.walk` 会静默返回空结果而非报 `PathNotFoundError`,导致"目录刚好在这个窗口消失"时输出 `{success: true, total_files: 0}` 而非结构化错误。本地 CLI 场景概率低,但 SPEC 对"目录在统计过程中消失"没有覆盖,建议至少在 README/docstring 里注明这个已知限制,不必现在就修。

2. **[需求缺口] 递归语义未在 SPEC 中显式约定**："统计目录下各扩展名的文件数和总字节数"没写清是否递归子目录。当前实现选择全树递归（`test_collect_stats_recurses_into_subdirectories` 已锁定该行为）,这是合理默认,但因为它是从模糊需求里"拍"出来的基础语义决策,建议找需求方过一遍确认,避免后续有人期望"只统计当前层"。

### P2

- [需求缺口] `--json` 非默认输出，与内部 agent-native 工具 DoD（脚本可调用工具应默认 JSON、人读格式作为可选 flag）方向相反，建议确认预期默认值
- [需求缺口] `--help` 缺少可复制的调用 Examples，不满足"脚本可调用工具需自带发现入口"的惯例
- [需求缺口] 复合扩展名（如 `archive.tar.gz`）按 `.gz` 计算而非 `.tar.gz`，SPEC 未定义扩展名切分规则，需确认是否符合预期
- [需求缺口] 隐藏文件（如 `.env`）因 `Path.suffix` 特性被归入 `<no-ext>`，SPEC 未提及是否需要特殊处理
- 测试集未覆盖符号链接、权限拒绝等边界路径，建议补充以固化 P0 决策后的行为
- `format_human` 表头列宽用 `len()` 对齐，中文字符实际显示宽度是西文的两倍，终端下列不齐（纯 cosmetic）

### 总体评估

核心统计逻辑、结构化错误、JSON/人类可读双输出和测试覆盖都做得扎实，11 项测试全过；主要风险不在编码正确性，而在 SPEC 对"不可访问文件""目录消失""默认输出格式"等边界场景完全没有定义，实现者的默认选择（尤其是静默跳过不可读文件）建议回需求方过一遍再定稿。
