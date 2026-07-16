"""Parse the leading frontmatter block of a Markdown file.

This is deliberately not a full YAML parser: it only understands the
subset frontmatter actually uses in this vault — scalar `key: value`
lines, quoted strings, inline lists (`key: [a, b]`), and block lists
(`key:` followed by indented `- item` lines). Anything outside that
subset is reported as a parse error rather than raising, so callers
never see an exception escape a malformed file.
"""

from __future__ import annotations

_DELIM = "---"


class FrontmatterError(Exception):
    """A file's frontmatter could not be read into a field dict."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def parse_frontmatter(text: str) -> dict:
    """Parse the frontmatter block at the top of ``text``.

    Raises FrontmatterError (never a bare exception) for: an empty
    file, a file with no frontmatter delimiters, an unterminated
    frontmatter block, or a block whose contents don't fit the
    supported subset.
    """
    if not text.strip():
        raise FrontmatterError("empty_file", "文件为空")

    lines = text.splitlines()
    if lines[0].strip() != _DELIM:
        raise FrontmatterError("no_frontmatter", "文件缺少 frontmatter（未以 --- 开头）")

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == _DELIM:
            end = i
            break
    if end is None:
        raise FrontmatterError("parse_error", "frontmatter 未闭合（缺少结尾的 ---）")

    return _parse_block(lines[1:end])


def _parse_block(lines: list[str]) -> dict:
    result: dict = {}
    current_key: str | None = None

    for lineno, raw in enumerate(lines, start=2):  # +2: header --- is line 1
        line = raw.rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        if stripped.startswith("- "):
            if current_key is None:
                raise FrontmatterError(
                    "parse_error", f"第 {lineno} 行是孤立的列表项（前面没有对应的 key）"
                )
            item = _parse_scalar(stripped[2:].strip())
            existing = result.get(current_key)
            if existing is None:
                result[current_key] = [item]
            elif isinstance(existing, list):
                existing.append(item)
            else:
                raise FrontmatterError(
                    "parse_error", f"第 {lineno} 行: `{current_key}` 同时有标量值和列表项"
                )
            continue

        if line[:1].isspace():
            raise FrontmatterError("parse_error", f"第 {lineno} 行缩进无法识别: {line!r}")

        if ":" not in line:
            raise FrontmatterError(
                "parse_error", f"第 {lineno} 行不是合法的 key: value 格式: {line!r}"
            )

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            raise FrontmatterError("parse_error", f"第 {lineno} 行缺少 key")

        current_key = key
        if value == "":
            result[key] = None  # may become a block list, or stay empty
        elif value.startswith("["):
            if not value.endswith("]"):
                raise FrontmatterError(
                    "parse_error", f"第 {lineno} 行的内联列表未闭合: {line!r}"
                )
            inner = value[1:-1].strip()
            result[key] = [] if not inner else [_parse_scalar(p.strip()) for p in inner.split(",")]
        else:
            result[key] = _parse_scalar(value)

    for key, value in result.items():
        if value is None:
            result[key] = ""

    return result


def _parse_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value
