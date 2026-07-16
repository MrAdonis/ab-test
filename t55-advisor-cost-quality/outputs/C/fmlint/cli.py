"""Command-line entry point.

Output is JSON by default so CI and other agent scripts can parse it
directly; --human is the opt-in for a person reading a terminal.
"""

import argparse
import json
from pathlib import Path
from typing import List, Optional

from .checks import lint_file
from .models import FileResult

EXAMPLES = """
Examples:
  python -m fmlint ~/Documents/brain/01-Wiki
  python -m fmlint ~/Documents/brain/01-Wiki --human
  python -m fmlint . | jq '.summary'
  python -m fmlint . | jq '.results[] | select(.ok == false)'

Output schema (JSON, default):
  {
    "success": bool,          // false only on a tool-level error (e.g. bad directory)
    "error": str | null,      // set only when success is false
    "summary": {"files_scanned": int, "files_with_issues": int, "total_issues": int} | null,
    "results": [
      {"path": str, "ok": bool, "issues": [{"code": str, "field": str | null, "message": str}]}
    ]
  }

Issue codes:
  empty_file, missing_frontmatter, unterminated_frontmatter,
  invalid_frontmatter_syntax, missing_field, invalid_title,
  invalid_date_format, invalid_type, invalid_tags,
  encoding_error, read_error

Exit codes:
  0 = ran fine, no lint issues found
  1 = ran fine, lint issues found in one or more files
  2 = tool-level error (bad directory, bad arguments)
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fmlint",
        description="Lint Markdown frontmatter for required fields (title/updated/type/tags), "
        "a type enum, a YYYY-MM-DD date, and a non-empty tags array.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="Directory to scan recursively for *.md files")
    parser.add_argument("--human", action="store_true", help="Print a human-readable report instead of JSON")
    return parser


def _build_output(results: List[FileResult]) -> dict:
    files_with_issues = sum(1 for r in results if not r.ok)
    total_issues = sum(len(r.issues) for r in results)
    return {
        "success": True,
        "error": None,
        "summary": {
            "files_scanned": len(results),
            "files_with_issues": files_with_issues,
            "total_issues": total_issues,
        },
        "results": [r.to_dict() for r in results],
    }


def _print_human(output: dict) -> None:
    summary = output["summary"]
    for r in output["results"]:
        if r["ok"]:
            continue
        print(r["path"])
        for issue in r["issues"]:
            field_part = f" [{issue['field']}]" if issue["field"] else ""
            print(f"  - {issue['code']}{field_part}: {issue['message']}")
    print(
        f"\n{summary['files_scanned']} files scanned, "
        f"{summary['files_with_issues']} with issues, "
        f"{summary['total_issues']} total issues."
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    directory = Path(args.directory)

    if not directory.is_dir():
        output = {
            "success": False,
            "error": f"not a directory: {directory}",
            "summary": None,
            "results": [],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 2

    md_files = sorted(directory.rglob("*.md"))
    results = [lint_file(p) for p in md_files]
    output = _build_output(results)

    if args.human:
        _print_human(output)
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0 if output["summary"]["files_with_issues"] == 0 else 1
