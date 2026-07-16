"""Frontmatter 提取 + 一个不依赖第三方库的最小 YAML 子集解析器。

只覆盖个人知识库 frontmatter 实际会用到的写法：
  - 顶层 `key: value`
  - 标量值（可加单/双引号）
  - 行内数组 `key: [a, b, "c"]`
  - 块状数组：
        tags:
          - a
          - b
不支持嵌套映射、多行字符串（`|`/`>`）、锚点等完整 YAML 特性——
遇到无法识别的写法一律当作语法错误抛出 FrontmatterParseError，
不静默猜测，也不让调用方崩溃（由 core.py 统一捕获转成 lint 问题）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

_DELIM = "---"
_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


class FrontmatterParseError(Exception):
    """frontmatter 分隔符正常，但 YAML 子集内容解析失败。"""


@dataclass
class SplitResult:
    """split_frontmatter 的返回值。

    error 非 None 时，fm_lines/body 无意义，调用方应直接据 error 生成问题。
    error 取值：'empty_file' | 'no_frontmatter' | 'unterminated_frontmatter'
    """

    fm_lines: Optional[List[str]]
    body: Optional[str]
    error: Optional[str]


def split_frontmatter(text: str) -> SplitResult:
    if text.strip() == "":
        return SplitResult(None, None, "empty_file")

    lines = text.splitlines()
    if lines[0].strip() != _DELIM:
        return SplitResult(None, text, "no_frontmatter")

    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == _DELIM:
            closing_idx = i
            break

    if closing_idx is None:
        return SplitResult(None, None, "unterminated_frontmatter")

    fm_lines = lines[1:closing_idx]
    body = "\n".join(lines[closing_idx + 1 :])
    return SplitResult(fm_lines, body, None)


def parse_scalar(raw: str, lineno: int) -> object:
    v = raw.strip()
    if v == "":
        return None

    if v[0] == '"' or v[0] == "'":
        quote = v[0]
        if len(v) < 2 or v[-1] != quote:
            raise FrontmatterParseError(f"第 {lineno} 行：未闭合的引号 {raw!r}")
        return v[1:-1]

    if (v[0] == '"') != (v[-1] == '"') or (v[0] == "'") != (v[-1] == "'"):
        raise FrontmatterParseError(f"第 {lineno} 行：引号不匹配 {raw!r}")

    if v == "null" or v == "~":
        return None
    if v == "true":
        return True
    if v == "false":
        return False
    return v


def _split_inline_list(inner: str, lineno: int) -> List[str]:
    items: List[str] = []
    current = ""
    in_quote: Optional[str] = None
    for ch in inner:
        if in_quote:
            current += ch
            if ch == in_quote:
                in_quote = None
        elif ch in ("'", '"'):
            in_quote = ch
            current += ch
        elif ch == ",":
            items.append(current)
            current = ""
        else:
            current += ch
    if in_quote:
        raise FrontmatterParseError(f"第 {lineno} 行：行内数组中有未闭合的引号")
    items.append(current)
    return items


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_yaml_subset(fm_lines: List[str]) -> dict:
    result: dict = {}
    i = 0
    n = len(fm_lines)
    while i < n:
        line = fm_lines[i]
        lineno = i + 1
        if line.strip() == "" or line.strip().startswith("#"):
            i += 1
            continue

        if _indent_of(line) != 0:
            raise FrontmatterParseError(f"第 {lineno} 行：意外的缩进（顶层字段不应缩进）")

        m = _KEY_RE.match(line.strip())
        if not m:
            raise FrontmatterParseError(f"第 {lineno} 行：无法识别的字段语法 {line!r}")

        key, value = m.group(1), m.group(2).strip()

        if value == "":
            items: List[object] = []
            j = i + 1
            while j < n:
                nxt = fm_lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if _indent_of(nxt) == 0:
                    break
                nstripped = nxt.strip()
                if not nstripped.startswith("- "):
                    raise FrontmatterParseError(
                        f"第 {j + 1} 行：期望列表项（以 '- ' 开头），实际为 {nxt!r}"
                    )
                items.append(parse_scalar(nstripped[2:], j + 1))
                j += 1
            result[key] = items if items else None
            i = j
            continue

        if value.startswith("["):
            if not value.endswith("]"):
                raise FrontmatterParseError(f"第 {lineno} 行：未闭合的行内数组 {value!r}")
            inner = value[1:-1].strip()
            if inner == "":
                result[key] = []
            else:
                raw_items = _split_inline_list(inner, lineno)
                result[key] = [parse_scalar(x, lineno) for x in raw_items]
        else:
            result[key] = parse_scalar(value, lineno)

        i += 1

    return result
