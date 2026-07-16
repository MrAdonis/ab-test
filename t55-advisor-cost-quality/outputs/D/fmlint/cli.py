"""Command-line entry point: `python -m fmlint <dir>`."""

from __future__ import annotations

import argparse
import json
import os
import sys

from .checker import lint_directory

EPILOG = """\
Examples:
  python -m fmlint ./wiki                  # JSON report on stdout (default)
  python -m fmlint ./wiki --human          # human-readable report
  python -m fmlint ./wiki | jq '.data.total_issues'

Output schema (always one JSON object on stdout, even on error):
  success case:
    {"success": true, "data": {"root", "checked_files", "files_with_issues",
     "total_issues", "results": [{"file", "issues": [{"code", "field", "message"}]}]},
     "error": null}
  tool-level failure (bad path, etc.):
    {"success": false, "data": null, "error": {"code", "message"}}

Issue codes: missing_field, invalid_format, invalid_type_value,
             no_frontmatter, empty_file, parse_error, read_error

Exit codes:
  0  no frontmatter issues found
  1  frontmatter issues found (wire this into CI as a gate)
  2  tool-level error (bad directory, etc.) — see `error` in the JSON output
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fmlint",
        description=(
            "检查目录下所有 Markdown 文件的 frontmatter 是否合规"
            "（必填字段 title/updated/type/tags，type 取值 concept|method|tool，"
            "updated 为 YYYY-MM-DD，tags 为非空数组）。"
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="要扫描的目录（递归查找所有 .md 文件）")
    parser.add_argument(
        "--human", action="store_true", help="输出人类可读格式（默认输出 JSON）"
    )
    return parser


def _format_human(data: dict) -> str:
    lines = [
        f"scanned {data['checked_files']} files, "
        f"{data['files_with_issues']} with issues, "
        f"{data['total_issues']} issues total"
    ]
    for entry in data["results"]:
        lines.append(f"\n{entry['file']}")
        for issue in entry["issues"]:
            tag = f" [{issue['field']}]" if "field" in issue else ""
            lines.append(f"  - {issue['code']}{tag}: {issue['message']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.isdir(args.directory):
        payload = {
            "success": False,
            "data": None,
            "error": {"code": "dir_not_found", "message": f"目录不存在: {args.directory}"},
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    report = lint_directory(args.directory)
    data = report.to_dict()

    if args.human:
        print(_format_human(data))
    else:
        payload = {"success": True, "data": data, "error": None}
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 1 if data["total_issues"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
