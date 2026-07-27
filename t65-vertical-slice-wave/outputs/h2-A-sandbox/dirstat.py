#!/usr/bin/env python3
"""CLI to report per-extension file counts and total sizes under a directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NO_EXT_KEY = "<noext>"


class DirstatError(Exception):
    """Raised for expected, user-facing failures (bad path, etc.)."""

    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message, **self.details}


def collect_stats(root: Path) -> dict[str, dict[str, int]]:
    """Walk `root` and return {extension: {"count": n, "bytes": n}}.

    Extension is lowercased without the leading dot; files with no
    extension are grouped under NO_EXT_KEY. Files that raise OSError
    when stat'd (permission errors, broken symlinks, ...) are skipped.
    """
    stats: dict[str, dict[str, int]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower().lstrip(".") or NO_EXT_KEY
        try:
            size = path.stat().st_size
        except OSError:
            continue
        entry = stats.setdefault(ext, {"count": 0, "bytes": 0})
        entry["count"] += 1
        entry["bytes"] += size
    return stats


def resolve_root(directory: str) -> Path:
    root = Path(directory)
    if not root.exists():
        raise DirstatError(
            "path_not_found",
            f"Directory not found: {directory}",
            path=str(directory),
        )
    if not root.is_dir():
        raise DirstatError(
            "not_a_directory",
            f"Not a directory: {directory}",
            path=str(directory),
        )
    return root


def format_text(stats: dict[str, dict[str, int]]) -> str:
    if not stats:
        return "No files found."
    rows = sorted(stats.items(), key=lambda kv: kv[1]["bytes"], reverse=True)
    ext_width = max(len(ext) for ext, _ in rows)
    lines = [f"{'EXT':<{ext_width}}  {'COUNT':>8}  {'BYTES':>12}"]
    for ext, info in rows:
        lines.append(f"{ext:<{ext_width}}  {info['count']:>8}  {info['bytes']:>12}")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirstat.py",
        description="Report file count and total size per extension for a directory.",
    )
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )
    return parser


def run(argv: list[str] | None = None) -> tuple[int, str, str]:
    """Execute the CLI logic and return (exit_code, stdout, stderr).

    Kept separate from main() so callers (and tests) can invoke dirstat
    programmatically without touching sys.stdout/sys.stderr/sys.exit.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.directory)
        stats = collect_stats(root)
    except DirstatError as exc:
        payload = exc.to_dict()
        if args.json:
            return 1, "", json.dumps(payload) + "\n"
        return 1, "", f"Error: {payload['message']}\n"
    except Exception as exc:  # unexpected failure: still report structured, no traceback
        payload = {"error": "internal_error", "message": str(exc)}
        if args.json:
            return 1, "", json.dumps(payload) + "\n"
        return 1, "", f"Error: {exc}\n"

    if args.json:
        return 0, json.dumps(stats) + "\n", ""
    return 0, format_text(stats) + "\n", ""


def main(argv: list[str] | None = None) -> int:
    code, out, err = run(argv)
    if out:
        sys.stdout.write(out)
    if err:
        sys.stderr.write(err)
    return code


if __name__ == "__main__":
    sys.exit(main())
