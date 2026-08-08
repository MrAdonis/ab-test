#!/usr/bin/env python3
"""Count files and total bytes per file extension in a directory (recursive)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


class DirStatError(Exception):
    """Raised for any expected failure (bad path etc). Never a raw traceback."""

    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type
        self.message = message

    def to_dict(self) -> dict:
        return {"type": self.error_type, "message": self.message}


def collect_stats(root) -> dict:
    """Walk `root` recursively and aggregate file count / total bytes per extension.

    Returns:
        {"root": str, "extensions": {ext: {"count": int, "bytes": int}},
         "total_files": int, "total_bytes": int}
    Extensions are lower-cased; files with no extension are grouped under "<no ext>".
    Raises DirStatError (never a bare exception) if `root` is missing or not a directory.
    """
    root_path = Path(root)

    if not root_path.exists():
        raise DirStatError("path_not_found", f"path does not exist: {root_path}")
    if not root_path.is_dir():
        raise DirStatError("not_a_directory", f"path is not a directory: {root_path}")

    extensions: dict[str, dict[str, int]] = {}
    total_files = 0
    total_bytes = 0

    for dirpath, _dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                size = file_path.stat().st_size
            except OSError:
                continue  # broken symlink / race condition — skip, don't crash the whole scan

            ext = file_path.suffix.lower() or "<no ext>"
            entry = extensions.setdefault(ext, {"count": 0, "bytes": 0})
            entry["count"] += 1
            entry["bytes"] += size
            total_files += 1
            total_bytes += size

    return {
        "root": str(root_path),
        "extensions": extensions,
        "total_files": total_files,
        "total_bytes": total_bytes,
    }


def format_human(stats: dict) -> str:
    lines = [f"Directory: {stats['root']}"]
    rows = sorted(stats["extensions"].items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    if not rows:
        lines.append("(no files found)")
    else:
        ext_width = max(len("extension"), *(len(ext) for ext, _ in rows))
        lines.append(f"{'extension':<{ext_width}}  {'count':>8}  {'bytes':>14}")
        for ext, data in rows:
            lines.append(f"{ext:<{ext_width}}  {data['count']:>8}  {data['bytes']:>14}")
    lines.append(f"\nTotal: {stats['total_files']} files, {stats['total_bytes']} bytes")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Count files and total bytes per file extension in a directory (recursive).",
        epilog=(
            "Examples:\n"
            "  dirstat.py /path/to/dir\n"
            "  dirstat.py /path/to/dir --json\n"
            "  dirstat.py /path/to/dir --json | jq '.data.extensions'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="directory to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "emit machine-readable JSON on stdout: {success, data} or "
            "{success, error:{type,message}} — never parse stdout as plain text "
            "when this flag is set"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirStatError as exc:
        if args.json:
            print(json.dumps({"success": False, "error": exc.to_dict()}))
        else:
            print(f"error: {exc.message}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"success": True, "data": stats}))
    else:
        print(format_human(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
