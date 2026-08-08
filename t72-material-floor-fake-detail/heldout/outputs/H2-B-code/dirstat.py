#!/usr/bin/env python3
"""Count files and total bytes per file extension under a directory.

Examples:
    dirstat.py /path/to/dir
    dirstat.py /path/to/dir --json
    dirstat.py /path/to/dir --json | jq '.data["no_ext"]'
"""
import argparse
import json
import sys
from pathlib import Path


def collect_stats(root: Path) -> dict:
    stats = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower() if path.suffix else "no_ext"
        entry = stats.setdefault(ext, {"files": 0, "bytes": 0})
        entry["files"] += 1
        entry["bytes"] += path.stat().st_size
    return stats


def run(dir_path: str) -> dict:
    root = Path(dir_path)
    if not root.exists():
        return {"success": False, "error": f"path does not exist: {dir_path}"}
    if not root.is_dir():
        return {"success": False, "error": f"path is not a directory: {dir_path}"}
    return {"success": True, "data": collect_stats(root)}


def format_text(stats: dict) -> str:
    if not stats:
        return "(no files found)"
    rows = sorted(stats.items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    width = max(len(ext) for ext, _ in rows)
    lines = [f"{'EXT':<{width}}  {'FILES':>8}  {'BYTES':>14}"]
    for ext, info in rows:
        lines.append(f"{ext:<{width}}  {info['files']:>8}  {info['bytes']:>14}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Count files and total bytes per file extension under a directory.",
        epilog="Examples:\n"
        "  dirstat.py .\n"
        "  dirstat.py /var/log --json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of a text table")
    args = parser.parse_args(argv)

    result = run(args.directory)

    if args.json:
        print(json.dumps(result))
    elif result["success"]:
        print(format_text(result["data"]))
    else:
        print(f"error: {result['error']}", file=sys.stderr)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
