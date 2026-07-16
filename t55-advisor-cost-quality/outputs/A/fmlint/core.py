"""Core frontmatter linting logic for fmlint.

Zero-dependency: parses the small YAML subset used by knowledge-base
frontmatter itself, so a malformed file becomes a structured *finding*
instead of an uncaught exception. No external packages required.

Public API (stable, safe for CI / other agents to import):
    lint_text(text)            -> list[dict]   issues for one document
    lint_file(path, name=None) -> dict         {"file", "ok", "issues"}
    lint_path(root)            -> dict          envelope: {"success", "data", "error"}

Every issue is a dict: {"field", "code", "message"}.
Issue codes are a closed set (see ISSUE_CODES) so downstream tooling can
switch on `code` without parsing `message`.
"""

from __future__ import annotations

import datetime
import os
import re

REQUIRED_FIELDS = ("title", "updated", "type", "tags")
VALID_TYPES = ("concept", "method", "tool")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Closed set of issue codes. Downstream consumers switch on these.
ISSUE_CODES = (
    "empty_file",          # file has no content
    "missing_frontmatter", # file has content but no leading `---` block
    "broken_frontmatter",  # `---` block present but not parseable
    "missing_field",       # a required field is absent
    "invalid_format",      # field present but wrong format (e.g. updated)
    "invalid_value",       # field present but value not allowed (e.g. type, tags)
    "read_error",          # file could not be read from disk
)


class FMParseError(Exception):
    """Raised internally when a frontmatter block cannot be parsed.

    Always caught inside this module and turned into a `broken_frontmatter`
    issue; it never propagates to callers.
    """


def _issue(field, code, message):
    return {"field": field, "code": code, "message": message}


def _unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _split_inline_list(inner):
    """Split the body of a `[a, b, c]` flow list. Empty -> []."""
    inner = inner.strip()
    if inner == "":
        return []
    return [_unquote(part) for part in inner.split(",")]


def parse_frontmatter(text):
    """Extract and parse a leading `---` frontmatter block.

    Returns (data, status):
        (dict, None)      parsed successfully
        (None, "missing") no leading frontmatter block
        (None, "broken")  block present but malformed / unterminated

    Never raises.
    """
    # Normalise newlines and strip a UTF-8 BOM if present.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("﻿"):
        text = text[1:]

    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "missing"

    # Find the closing delimiter.
    close = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() in ("---", "..."):
            close = idx
            break
    if close is None:
        return None, "broken"  # unterminated block

    block = lines[1:close]
    try:
        return _parse_block(block), None
    except FMParseError:
        return None, "broken"
    except Exception:
        # Absolute safety net: any unforeseen parse error is "broken",
        # never a crash.
        return None, "broken"


def _parse_block(lines):
    """Parse the interior of a frontmatter block into a dict.

    Supports the subset knowledge-base frontmatter actually uses:
    scalars, inline lists `[a, b]`, and block lists (`-` items). Anything
    outside that subset raises FMParseError -> reported as broken.
    """
    data = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()
        i += 1

        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue

        # A top-level key must not be indented.
        if line[0] in (" ", "\t"):
            raise FMParseError("unexpected indentation: %r" % line)

        if ":" not in line:
            raise FMParseError("expected 'key: value': %r" % line)

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key == "":
            raise FMParseError("empty key: %r" % line)

        if value == "":
            # Either a block list follows, or it is an empty scalar.
            items = []
            while i < n:
                nxt = lines[i].rstrip()
                s = nxt.strip()
                if s == "" or s.startswith("#"):
                    i += 1
                    continue
                if s.startswith("-"):
                    items.append(_unquote(s[1:].strip()))
                    i += 1
                    continue
                break  # next top-level key
            data[key] = items if items else ""
        elif value.startswith("[") and value.endswith("]"):
            data[key] = _split_inline_list(value[1:-1])
        else:
            data[key] = _unquote(value)

    return data


def validate_frontmatter(data):
    """Validate a parsed frontmatter dict. Returns a list of issue dicts."""
    issues = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            issues.append(_issue(field, "missing_field",
                                 "missing required field '%s'" % field))

    if "title" in data:
        v = data["title"]
        if not isinstance(v, str) or v.strip() == "":
            issues.append(_issue("title", "invalid_value",
                                 "title must be a non-empty string"))

    if "updated" in data:
        v = data["updated"]
        if not (isinstance(v, str) and _DATE_RE.match(v.strip()) and _is_real_date(v.strip())):
            issues.append(_issue("updated", "invalid_format",
                                 "updated must be a valid YYYY-MM-DD date, got %r" % v))

    if "type" in data:
        v = data["type"]
        if not isinstance(v, str) or v.strip() not in VALID_TYPES:
            issues.append(_issue("type", "invalid_value",
                                 "type must be one of %s, got %r"
                                 % ("/".join(VALID_TYPES), v)))

    if "tags" in data:
        v = data["tags"]
        if (not isinstance(v, list) or len(v) == 0
                or any(not isinstance(x, str) or x.strip() == "" for x in v)):
            issues.append(_issue("tags", "invalid_value",
                                 "tags must be a non-empty array of non-empty strings"))

    return issues


def _is_real_date(s):
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def lint_text(text):
    """Lint one document's raw text. Returns a list of issue dicts."""
    if text.strip() == "":
        return [_issue(None, "empty_file", "file is empty")]

    data, status = parse_frontmatter(text)
    if status == "missing":
        return [_issue(None, "missing_frontmatter",
                       "no frontmatter block found")]
    if status == "broken":
        return [_issue(None, "broken_frontmatter",
                       "frontmatter block is present but could not be parsed")]

    return validate_frontmatter(data)


def lint_file(path, name=None):
    """Lint a single file on disk. Never raises.

    Returns {"file": <name>, "ok": bool, "issues": [...]}.
    """
    display = name if name is not None else path
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "file": display,
            "ok": False,
            "issues": [_issue(None, "read_error", "could not read file: %s" % exc)],
        }

    issues = lint_text(text)
    return {"file": display, "ok": len(issues) == 0, "issues": issues}


def _iter_markdown_files(root):
    """Yield (abs_path, display_path) for every .md file under root, sorted."""
    if os.path.isfile(root):
        yield root, os.path.basename(root)
        return

    collected = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn.lower().endswith((".md", ".markdown")):
                abs_path = os.path.join(dirpath, fn)
                collected.append((abs_path, os.path.relpath(abs_path, root)))
    collected.sort(key=lambda pair: pair[1])
    for pair in collected:
        yield pair


def lint_path(root):
    """Lint every markdown file under `root` (file or directory).

    Returns the standard envelope:
        {"success": bool, "data": {...} | None, "error": {...} | None}

    - success=False only for tool-level errors (bad path). Lint findings
      are NOT errors; they live in data.results with success=True.
    """
    if not os.path.exists(root):
        return {
            "success": False,
            "data": None,
            "error": {"code": "path_not_found",
                      "message": "path does not exist: %s" % root},
        }

    results = []
    for abs_path, display in _iter_markdown_files(root):
        results.append(lint_file(abs_path, name=display))

    files_with_issues = sum(1 for r in results if not r["ok"])
    total_issues = sum(len(r["issues"]) for r in results)

    return {
        "success": True,
        "data": {
            "root": root,
            "summary": {
                "files_checked": len(results),
                "files_with_issues": files_with_issues,
                "files_ok": len(results) - files_with_issues,
                "total_issues": total_issues,
            },
            "results": results,
        },
        "error": None,
    }
