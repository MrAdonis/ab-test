#!/usr/bin/env python3
"""Count files and total bytes per extension in a directory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Union


class DirStatError(Exception):
    """Structured error for CLI-facing failures (avoids raw tracebacks)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message}


def collect_stats(root: Union[str, Path]) -> dict:
    """Return {ext: {"count": int, "bytes": int}} sorted by bytes desc."""
    root = Path(root)
    if not root.exists():
        raise DirStatError("not_found", f"Path does not exist: {root}")
    if not root.is_dir():
        raise DirStatError("not_a_directory", f"Path is not a directory: {root}")

    stats: dict = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower() or "<no extension>"
        entry = stats.setdefault(ext, {"count": 0, "bytes": 0})
        try:
            size = path.stat().st_size
        except OSError:
            continue
        entry["count"] += 1
        entry["bytes"] += size

    return dict(sorted(stats.items(), key=lambda kv: kv[1]["bytes"], reverse=True))


def format_table(stats: dict) -> str:
    if not stats:
        return "No files found."
    header = f"{'Extension':<20}{'Count':>10}{'Bytes':>15}"
    sep = "-" * len(header)
    lines = [header, sep]
    total_count = 0
    total_bytes = 0
    for ext, data in stats.items():
        lines.append(f"{ext:<20}{data['count']:>10}{data['bytes']:>15}")
        total_count += data["count"]
        total_bytes += data["bytes"]
    lines.append(sep)
    lines.append(f"{'TOTAL':<20}{total_count:>10}{total_bytes:>15}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat",
        description="Count files and total bytes per extension in a directory.",
    )
    parser.add_argument("directory", help="Path to the directory to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output machine-readable JSON instead of a table",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.directory)
    except DirStatError as exc:
        payload = exc.to_dict()
        if args.as_json:
            print(json.dumps(payload), file=sys.stderr)
        else:
            print(f"Error [{exc.code}]: {exc.message}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(stats, indent=2))
    else:
        print(format_table(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
