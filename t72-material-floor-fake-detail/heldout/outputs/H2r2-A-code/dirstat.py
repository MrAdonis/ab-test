#!/usr/bin/env python3
"""统计目录下各扩展名的文件数量和总字节数。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field


NO_EXT_KEY = "<no-ext>"


class DirStatError(Exception):
    """dirstat 结构化错误的基类，携带 error code 供 CLI 分支处理。"""

    def __init__(self, code: str, message: str, path: str):
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path

    def to_dict(self) -> dict:
        return {"success": False, "error": {"code": self.code, "message": self.message, "path": self.path}}


class PathNotFoundError(DirStatError):
    def __init__(self, path: str):
        super().__init__("path_not_found", f"path does not exist: {path}", path)


class NotADirectoryStatError(DirStatError):
    def __init__(self, path: str):
        super().__init__("not_a_directory", f"path is not a directory: {path}", path)


@dataclass
class ExtStat:
    count: int = 0
    total_bytes: int = 0


def collect_stats(root: str) -> dict[str, ExtStat]:
    """遍历 root 下所有文件，按扩展名聚合文件数和字节数。

    root 不存在抛 PathNotFoundError，root 存在但不是目录抛 NotADirectoryStatError。
    符号链接文件按其自身大小统计，不跟随目录符号链接递归（避免环）。
    """
    if not os.path.exists(root):
        raise PathNotFoundError(root)
    if not os.path.isdir(root):
        raise NotADirectoryStatError(root)

    stats: dict[str, ExtStat] = {}
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue
            ext = os.path.splitext(name)[1].lower() or NO_EXT_KEY
            entry = stats.setdefault(ext, ExtStat())
            entry.count += 1
            entry.total_bytes += size

    return stats


def stats_to_dict(stats: dict[str, ExtStat]) -> dict:
    return {
        ext: {"count": s.count, "total_bytes": s.total_bytes}
        for ext, s in sorted(stats.items(), key=lambda kv: kv[1].total_bytes, reverse=True)
    }


def format_human(root: str, stats: dict[str, ExtStat]) -> str:
    if not stats:
        return f"{root}: no files found"

    ordered = sorted(stats.items(), key=lambda kv: kv[1].total_bytes, reverse=True)
    ext_width = max(len(ext) for ext, _ in ordered)
    lines = [f"{'EXT'.ljust(ext_width)}  {'COUNT':>8}  {'BYTES':>14}"]
    total_count = 0
    total_bytes = 0
    for ext, s in ordered:
        lines.append(f"{ext.ljust(ext_width)}  {s.count:>8}  {s.total_bytes:>14}")
        total_count += s.count
        total_bytes += s.total_bytes
    lines.append(f"{'TOTAL'.ljust(ext_width)}  {total_count:>8}  {total_bytes:>14}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="统计目录下各扩展名的文件数和总字节数",
    )
    parser.add_argument("path", help="要统计的目录路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出，便于脚本消费")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirStatError as e:
        if args.json:
            print(json.dumps(e.to_dict(), ensure_ascii=False), file=sys.stderr)
        else:
            print(f"Error: {e.message}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"success": True, "path": args.path, "data": stats_to_dict(stats)}, ensure_ascii=False))
    else:
        print(format_human(args.path, stats))

    return 0


if __name__ == "__main__":
    sys.exit(main())
