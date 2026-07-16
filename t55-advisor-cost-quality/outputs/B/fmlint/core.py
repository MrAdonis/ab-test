"""单文件 / 目录级别的 lint 逻辑。任何输入都不应让这里抛出异常。"""

from __future__ import annotations

from pathlib import Path
from typing import List

from .models import FileResult, Issue
from .parser import FrontmatterParseError, parse_yaml_subset, split_frontmatter
from .rules import validate_frontmatter

_ERROR_MESSAGES = {
    "empty_file": "文件为空",
    "no_frontmatter": "文件缺少 frontmatter（未以 '---' 开头）",
    "unterminated_frontmatter": "frontmatter 缺少闭合的 '---'",
}


def lint_text(text: str) -> List[Issue]:
    split = split_frontmatter(text)
    if split.error is not None:
        return [Issue(split.error, None, _ERROR_MESSAGES[split.error])]

    try:
        fm = parse_yaml_subset(split.fm_lines)
    except FrontmatterParseError as e:
        return [Issue("malformed_frontmatter", None, str(e))]

    if not isinstance(fm, dict):
        return [Issue("malformed_frontmatter", None, "frontmatter 顶层必须是键值映射")]

    return validate_frontmatter(fm)


def lint_file(path: Path) -> FileResult:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001 - 任何读取失败都必须转成结构化问题，不能崩
        return FileResult(str(path), False, [Issue("read_error", None, f"无法读取文件：{e}")])

    issues = lint_text(text)
    return FileResult(str(path), len(issues) == 0, issues)


def lint_directory(root: Path, pattern: str = "*.md") -> List[FileResult]:
    files = sorted(root.rglob(pattern))
    return [lint_file(f) for f in files]
