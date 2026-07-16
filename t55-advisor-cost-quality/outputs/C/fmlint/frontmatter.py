"""Parsing for Markdown frontmatter blocks.

Deliberately not a general YAML parser: it only understands the flat
subset frontmatter actually uses here — scalar strings and one level of
list values (block `- item` or inline `[a, b]`). Anything it can't
confidently parse raises FrontmatterSyntaxError instead of guessing.
"""

import re
from typing import Optional, Tuple

MARKER = "---"
_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")


class FrontmatterSyntaxError(ValueError):
    """Raised when a frontmatter block can't be parsed."""


def split_frontmatter(raw: str) -> Tuple[Optional[str], bool, bool]:
    """Split raw file text into its frontmatter block.

    Returns (block_text, terminated, has_marker):
      - has_marker=False: file does not start with a '---' line.
      - has_marker=True, terminated=False: opening '---' found but no closing '---'.
      - has_marker=True, terminated=True: block_text is the text between the markers.
    """
    lines = raw.splitlines()
    if not lines or lines[0].strip() != MARKER:
        return None, False, False
    for i in range(1, len(lines)):
        if lines[i].strip() == MARKER:
            return "\n".join(lines[1:i]), True, True
    return None, False, True


def _strip_quotes(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _parse_inline_list(s: str, line_no: int):
    if not s.endswith("]"):
        raise FrontmatterSyntaxError(f"unterminated inline list at line {line_no}: {s!r}")
    inner = s[1:-1].strip()
    if inner == "":
        return []
    return [_strip_quotes(part.strip()) for part in inner.split(",")]


def parse_frontmatter(block: str) -> dict:
    """Parse a frontmatter block into a flat dict.

    Nested mappings (more than one level deep) are stored as an opaque
    dict placeholder since none of the fields this tool validates are
    expected to nest — callers only need to know it isn't a scalar/list.
    """
    lines = block.splitlines()
    data: dict = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent != 0:
            raise FrontmatterSyntaxError(f"unexpected indentation at line {i + 1}: {line!r}")
        match = _KEY_RE.match(line)
        if not match:
            raise FrontmatterSyntaxError(f"cannot parse line {i + 1} as 'key: value': {line!r}")
        key, rest = match.group(1), match.group(2).strip()
        line_no = i + 1
        i += 1
        if rest == "":
            nested = []
            while i < n:
                nxt = lines[i]
                if nxt.strip() == "":
                    i += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent == 0:
                    break
                nested.append(nxt.strip())
                i += 1
            if not nested:
                data[key] = None
            elif all(item == "-" or item.startswith("- ") for item in nested):
                data[key] = [_strip_quotes(item[2:].strip() if item.startswith("- ") else "") for item in nested]
            else:
                data[key] = {"__nested__": True}
        elif rest.startswith("["):
            data[key] = _parse_inline_list(rest, line_no)
        else:
            data[key] = _strip_quotes(rest)
    return data
