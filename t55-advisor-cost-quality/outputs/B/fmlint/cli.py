"""fmlint 命令行入口。

设计给 CI 和其他 agent/脚本直接调用消费：
  - 默认输出 JSON 到 stdout（人读格式用 --format text 显式切换）
  - 失败一律返回结构化 {"success": false, "error": {...}}，不裸抛栈
  - exit code: 0 = 无问题 / 1 = 发现 lint 问题 / 2 = 工具本身执行出错
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .core import lint_directory
from .models import FileResult

_EPILOG = """\
Examples:
  python -m fmlint ./wiki
  python -m fmlint ./wiki --format text
  python -m fmlint ./wiki --pattern "*.markdown"

Output (--format json, 默认，供 CI / 其他脚本消费):
  {
    "success": true,
    "root": "./wiki",
    "summary": {"files_scanned": 10, "files_ok": 8, "files_with_issues": 2, "total_issues": 3},
    "files": [
      {"path": "wiki/a.md", "ok": true, "issues": []},
      {"path": "wiki/b.md", "ok": false, "issues": [
        {"code": "missing_field", "field": "tags", "message": "缺少字段 'tags'"}
      ]}
    ]
  }

Exit codes:
  0  未发现任何 frontmatter 问题
  1  发现 lint 问题（files_with_issues > 0）
  2  工具执行出错（目录不存在等），stdout 输出 {"success": false, "error": {...}}

Run tests:
  python -m unittest discover -s fmlint/tests -p "test_*.py" -v
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fmlint",
        description="检查目录下所有 Markdown 文件的 frontmatter 是否合规"
        "（必需字段 title/updated/type/tags，type 取值受限，updated 需 YYYY-MM-DD，tags 需非空数组）。",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="要检查的目录路径")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="输出格式，默认 json（供程序消费）；text 为人读格式",
    )
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="文件匹配模式（glob，相对于目录递归匹配），默认 *.md",
    )
    return parser


def build_report(root: Path, results: List[FileResult]) -> dict:
    files_ok = sum(1 for r in results if r.ok)
    total_issues = sum(len(r.issues) for r in results)
    return {
        "success": True,
        "root": str(root),
        "summary": {
            "files_scanned": len(results),
            "files_ok": files_ok,
            "files_with_issues": len(results) - files_ok,
            "total_issues": total_issues,
        },
        "files": [r.to_dict() for r in results],
    }


def render_text(report: dict) -> str:
    s = report["summary"]
    lines = [
        f"扫描 {s['files_scanned']} 个文件，{s['files_ok']} 个正常，"
        f"{s['files_with_issues']} 个有问题，共 {s['total_issues']} 处问题"
    ]
    for f in report["files"]:
        if not f["issues"]:
            continue
        lines.append(f"\n{f['path']}")
        for issue in f["issues"]:
            field_part = f" [{issue['field']}]" if issue.get("field") else ""
            lines.append(f"  - {issue['code']}{field_part}: {issue['message']}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.directory)

    if not root.exists() or not root.is_dir():
        error_report = {
            "success": False,
            "error": {"message": f"目录不存在或不是目录：{args.directory}"},
        }
        print(json.dumps(error_report, ensure_ascii=False, indent=2))
        return 2

    results = lint_directory(root, args.pattern)
    report = build_report(root, results)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))

    return 0 if report["summary"]["total_issues"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
