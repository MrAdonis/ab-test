#!/usr/bin/env python3
"""Count files and total bytes per extension under a directory."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


class DirStatError(Exception):
    """Raised for expected, user-facing failures (bad path, permissions, ...)."""

    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path

    def to_dict(self) -> dict:
        d = {"error": self.code, "message": self.message}
        if self.path is not None:
            d["path"] = self.path
        return d


@dataclass
class ExtStats:
    count: int = 0
    bytes: int = 0


def collect_stats(directory: str | Path) -> dict[str, ExtStats]:
    """Walk `directory` recursively and tally file count/size per extension.

    Extension is the lowercased suffix including the dot (e.g. ".py").
    Files with no extension are grouped under "" (empty string).

    Raises DirStatError if the path does not exist or is not a directory.
    """
    root = Path(directory)

    if not root.exists():
        raise DirStatError("path_not_found", f"path does not exist: {root}", str(root))
    if not root.is_dir():
        raise DirStatError("not_a_directory", f"path is not a directory: {root}", str(root))

    stats: dict[str, ExtStats] = {}
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
        for name in filenames:
            fpath = Path(dirpath) / name
            try:
                size = fpath.stat().st_size
            except OSError:
                continue
            ext = fpath.suffix.lower()
            entry = stats.setdefault(ext, ExtStats())
            entry.count += 1
            entry.bytes += size

    return stats


def _stats_to_rows(stats: dict[str, ExtStats]) -> list[dict]:
    rows = [
        {"extension": ext or "(none)", "count": s.count, "bytes": s.bytes}
        for ext, s in stats.items()
    ]
    rows.sort(key=lambda r: r["bytes"], reverse=True)
    return rows


def format_json(stats: dict[str, ExtStats], directory: str) -> str:
    rows = _stats_to_rows(stats)
    total_count = sum(r["count"] for r in rows)
    total_bytes = sum(r["bytes"] for r in rows)
    return json.dumps(
        {
            "path": directory,
            "extensions": rows,
            "total_files": total_count,
            "total_bytes": total_bytes,
        },
        indent=2,
    )


def format_table(stats: dict[str, ExtStats], directory: str) -> str:
    rows = _stats_to_rows(stats)
    if not rows:
        return f"{directory}: no files found"

    lines = [f"{'EXT':<12}{'COUNT':>10}{'BYTES':>16}"]
    for r in rows:
        lines.append(f"{r['extension']:<12}{r['count']:>10}{r['bytes']:>16}")
    total_count = sum(r["count"] for r in rows)
    total_bytes = sum(r["bytes"] for r in rows)
    lines.append("-" * 38)
    lines.append(f"{'TOTAL':<12}{total_count:>10}{total_bytes:>16}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Count files and total bytes per extension in a directory (recursive).",
    )
    parser.add_argument("path", help="directory to scan")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        stats = collect_stats(args.path)
    except DirStatError as e:
        if args.json:
            print(json.dumps(e.to_dict(), indent=2), file=sys.stderr)
        else:
            print(f"Error: {e.message}", file=sys.stderr)
        return 1

    if args.json:
        print(format_json(stats, args.path))
    else:
        print(format_table(stats, args.path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
