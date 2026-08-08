#!/usr/bin/env python3
"""Report per-extension file count and total byte size for a directory."""
import argparse
import json
import sys
from pathlib import Path

NO_EXT_KEY = "<no ext>"


class DirStatError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code


def collect_stats(root):
    """Return {ext: {"count": int, "bytes": int}} for all files under root."""
    root_path = Path(root)
    if not root_path.exists():
        raise DirStatError(f"path does not exist: {root}", "path_not_found")
    if not root_path.is_dir():
        raise DirStatError(f"not a directory: {root}", "not_a_directory")

    stats = {}
    for path in root_path.rglob("*"):
        try:
            if not path.is_file():
                continue
            size = path.stat().st_size
        except OSError:
            continue
        ext = path.suffix.lower() if path.suffix else NO_EXT_KEY
        entry = stats.setdefault(ext, {"count": 0, "bytes": 0})
        entry["count"] += 1
        entry["bytes"] += size
    return stats


def format_table(stats):
    if not stats:
        return "(no files found)"
    rows = sorted(stats.items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    ext_width = max(len(ext) for ext, _ in rows)
    ext_width = max(ext_width, len("extension"))
    lines = [f"{'extension':<{ext_width}}  {'count':>8}  {'bytes':>12}"]
    for ext, entry in rows:
        lines.append(f"{ext:<{ext_width}}  {entry['count']:>8}  {entry['bytes']:>12}")
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="dirstat",
        description="Per-extension file count and total byte size for a directory",
    )
    parser.add_argument("path", help="directory to scan")
    parser.add_argument("--json", action="store_true", help="output JSON instead of a table")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirStatError as e:
        error = {"success": False, "error": {"code": e.code, "message": e.message}}
        if args.json:
            print(json.dumps(error))
        else:
            print(f"error: {e.message}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"success": True, "data": stats}))
    else:
        print(format_table(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
