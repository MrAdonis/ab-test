#!/usr/bin/env python3
"""Count files and total bytes per file extension in a directory tree."""

import argparse
import json
import os
import sys
from pathlib import Path


def collect_stats(root):
    """Recursively aggregate (files, bytes) per extension under root.

    Returns a dict mapping extension (lowercase, "" for none) to
    {"files": int, "bytes": int}. Unreadable files/dirs are skipped.
    """
    stats = {}
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            try:
                size = os.stat(full_path).st_size
            except OSError:
                continue
            ext = os.path.splitext(name)[1].lower()
            entry = stats.setdefault(ext, {"files": 0, "bytes": 0})
            entry["files"] += 1
            entry["bytes"] += size
    return stats


def build_report(path):
    """Build the success report dict for an already-validated directory path."""
    stats = collect_stats(path)
    extensions = [
        {"extension": ext, "files": v["files"], "bytes": v["bytes"]}
        for ext, v in stats.items()
    ]
    extensions.sort(key=lambda e: e["bytes"], reverse=True)
    return {
        "success": True,
        "path": str(path),
        "total_files": sum(e["files"] for e in extensions),
        "total_bytes": sum(e["bytes"] for e in extensions),
        "extensions": extensions,
    }


def error_report(code, message):
    return {"success": False, "error": {"code": code, "message": message}}


def validate_path(raw_path):
    """Check existence/type. Returns (Path, None) or (None, error_report)."""
    p = Path(raw_path)
    if not p.exists():
        return None, error_report("not_found", f"Directory not found: {raw_path}")
    if not p.is_dir():
        return None, error_report("not_a_directory", f"Not a directory: {raw_path}")
    return p, None


def format_text(report):
    lines = [f"Directory: {report['path']}", ""]
    lines.append(f"{'Extension':<20}{'Files':>10}{'Bytes':>15}")
    for e in report["extensions"]:
        label = e["extension"] or "(no extension)"
        lines.append(f"{label:<20}{e['files']:>10}{e['bytes']:>15}")
    lines.append(f"{'TOTAL':<20}{report['total_files']:>10}{report['total_bytes']:>15}")
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Count files and total bytes per file extension in a directory tree.",
        epilog=(
            "Output (--json):\n"
            '  success: {"success": true, "path": "...", "total_files": N,\n'
            '            "total_bytes": N, "extensions": '
            '[{"extension": ".py", "files": N, "bytes": N}, ...]}\n'
            '  error:   {"success": false, "error": {"code": "...", "message": "..."}}\n'
            "  Errors are printed to stdout as JSON too (never a traceback);\n"
            "  exit code is 0 on success, 1 on error.\n\n"
            "Examples:\n"
            "  dirstat.py ./src\n"
            "  dirstat.py ./src --json\n"
            "  dirstat.py ./src --json | jq '.extensions'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="directory to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        help="output machine-readable JSON instead of a text table",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    validated_path, err = validate_path(args.path)
    if err is not None:
        if args.json:
            print(json.dumps(err))
        else:
            print(f"Error: {err['error']['message']}", file=sys.stderr)
        return 1

    report = build_report(validated_path)
    if args.json:
        print(json.dumps(report))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
