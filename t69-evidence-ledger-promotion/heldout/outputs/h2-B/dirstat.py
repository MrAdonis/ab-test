#!/usr/bin/env python3
"""Count files and total bytes per extension under a directory tree."""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

NO_EXT_KEY = "<no ext>"


def collect_stats(root: Path) -> dict:
    """Walk `root` recursively and tally file count / byte total per extension.

    Raises FileNotFoundError if root doesn't exist, NotADirectoryError if
    root exists but isn't a directory.
    """
    if not root.exists():
        raise FileNotFoundError(f"path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    counts: dict = defaultdict(lambda: {"count": 0, "bytes": 0})
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            fpath = Path(dirpath) / name
            try:
                size = fpath.stat().st_size
            except OSError:
                # Broken symlink or file removed mid-scan; skip rather than crash.
                continue
            ext = fpath.suffix if fpath.suffix else NO_EXT_KEY
            counts[ext]["count"] += 1
            counts[ext]["bytes"] += size

    total_files = sum(v["count"] for v in counts.values())
    total_bytes = sum(v["bytes"] for v in counts.values())

    return {
        "path": str(root.resolve()),
        "extensions": dict(counts),
        "total_files": total_files,
        "total_bytes": total_bytes,
    }


def format_human(data: dict) -> str:
    lines = [f"Directory: {data['path']}", ""]
    rows = sorted(data["extensions"].items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    ext_width = max([len(ext) for ext, _ in rows] + [len("EXTENSION")])
    lines.append(f"{'EXTENSION':<{ext_width}}  {'FILES':>8}  {'BYTES':>14}")
    for ext, stat in rows:
        lines.append(f"{ext:<{ext_width}}  {stat['count']:>8}  {stat['bytes']:>14}")
    lines.append("")
    lines.append(f"Total: {data['total_files']} files, {data['total_bytes']} bytes")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Count files and total bytes per extension in a directory tree.",
        epilog=(
            "Examples:\n"
            "  dirstat.py .\n"
            "  dirstat.py /path/to/dir --json\n"
            "  dirstat.py /path/to/dir --json | jq '.data.extensions'\n"
            "\n"
            "Output contract (--json): {\"success\": true, \"data\": {...}} on success,\n"
            "{\"success\": false, \"error\": \"...\"} on failure. Exit code is 1 on failure.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="directory path to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="emit {success, data, error} JSON instead of a human-readable table",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        data = collect_stats(Path(args.directory))
    except (FileNotFoundError, NotADirectoryError) as exc:
        error = {"success": False, "error": str(exc)}
        if args.as_json:
            print(json.dumps(error))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps({"success": True, "data": data}))
    else:
        print(format_human(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
