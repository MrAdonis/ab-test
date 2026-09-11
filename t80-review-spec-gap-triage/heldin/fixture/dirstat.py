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
