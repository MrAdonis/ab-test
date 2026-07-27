#!/usr/bin/env python3
"""CLI: report per-extension file count and total bytes for a directory."""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


class DirstatError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def collect_stats(root):
    """Walk `root` recursively and return {ext: {"count": n, "bytes": n}}."""
    root = Path(root)
    if not root.exists():
        raise DirstatError("path_not_found", f"Path does not exist: {root}")
    if not root.is_dir():
        raise DirstatError("not_a_directory", f"Path is not a directory: {root}")

    stats = defaultdict(lambda: {"count": 0, "bytes": 0})
    for entry in root.rglob("*"):
        if entry.is_file():
            ext = entry.suffix.lower() if entry.suffix else "(no extension)"
            stats[ext]["count"] += 1
            stats[ext]["bytes"] += entry.stat().st_size
    return dict(stats)


def format_text(stats):
    if not stats:
        return "No files found."
    width = max(len(ext) for ext in stats)
    lines = []
    for ext in sorted(stats, key=lambda e: (-stats[e]["bytes"], e)):
        data = stats[ext]
        lines.append(f"{ext:<{width}}  count={data['count']:<6} bytes={data['bytes']}")
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Report file count and total bytes per extension in a directory.",
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirstatError as e:
        error = {"error": e.code, "message": e.message}
        if args.json:
            print(json.dumps(error), file=sys.stderr)
        else:
            print(f"Error: {e.message}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(stats, indent=2, sort_keys=True))
    else:
        print(format_text(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
