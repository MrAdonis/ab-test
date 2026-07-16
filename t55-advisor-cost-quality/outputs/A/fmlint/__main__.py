"""Command-line entry point: `python -m fmlint <dir>`.

Output contract (agent-native):
  * `--format json` (default): a single JSON envelope on stdout,
    {"success", "data", "error"}. Machine consumers read this; never
    parse stdout as plain text.
  * `--format text`: a human-readable summary on stdout.

Exit codes:
  0  success, no frontmatter issues found
  1  success, but at least one file has issues
  2  tool error (e.g. path does not exist, bad arguments)
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import lint_path

_EPILOG = """\
examples:
  python -m fmlint ./wiki                 # lint a directory (recursive), JSON out
  python -m fmlint ./wiki --format text   # human-readable summary
  python -m fmlint note.md                # lint a single file
  python -m fmlint ./wiki > report.json   # capture for CI / another agent

output (json, the default):
  {"success": true|false,
   "data": {"root", "summary": {...}, "results": [
              {"file", "ok", "issues": [{"field", "code", "message"}]}]},
   "error": {"code", "message"} | null}

issue codes (closed set): empty_file, missing_frontmatter, broken_frontmatter,
  missing_field, invalid_format, invalid_value, read_error

exit codes: 0 = clean, 1 = issues found, 2 = tool error
"""


def _render_text(envelope):
    if not envelope["success"]:
        return "error [%s]: %s" % (envelope["error"]["code"],
                                   envelope["error"]["message"])

    data = envelope["data"]
    s = data["summary"]
    lines = []
    for r in data["results"]:
        if r["ok"]:
            continue
        lines.append(r["file"])
        for iss in r["issues"]:
            prefix = "  - " + iss["code"]
            if iss["field"]:
                prefix += " (%s)" % iss["field"]
            lines.append("%s: %s" % (prefix, iss["message"]))

    header = ("checked %d file(s): %d ok, %d with issues, %d issue(s) total"
              % (s["files_checked"], s["files_ok"],
                 s["files_with_issues"], s["total_issues"]))
    if not lines:
        return header + "\nall frontmatter valid."
    return header + "\n\n" + "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="fmlint",
        description="Lint Markdown frontmatter (title/updated/type/tags) "
                    "across a directory. Built for CI and agent pipelines: "
                    "JSON by default, structured errors, exit codes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_EPILOG,
    )
    parser.add_argument("path", help="directory to scan (recursive) or a single .md file")
    parser.add_argument("--format", choices=("json", "text"), default="json",
                        help="output format (default: json)")
    args = parser.parse_args(argv)

    envelope = lint_path(args.path)

    if args.format == "text":
        print(_render_text(envelope))
    else:
        json.dump(envelope, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    if not envelope["success"]:
        return 2
    if envelope["data"]["summary"]["total_issues"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
