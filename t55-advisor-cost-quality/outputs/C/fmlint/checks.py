"""Per-file lint entry point: read -> split -> parse -> validate, never raising."""

from pathlib import Path

from .frontmatter import FrontmatterSyntaxError, parse_frontmatter, split_frontmatter
from .models import FileResult, Issue
from .rules import validate_frontmatter


def lint_file(path: Path) -> FileResult:
    path_str = str(path)

    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return FileResult(path=path_str, issues=[Issue(code="encoding_error", message=f"not valid utf-8: {exc}")])
    except OSError as exc:
        return FileResult(path=path_str, issues=[Issue(code="read_error", message=str(exc))])

    if not raw.strip():
        return FileResult(path=path_str, issues=[Issue(code="empty_file", message="file is empty")])

    block, terminated, has_marker = split_frontmatter(raw)

    if not has_marker:
        return FileResult(
            path=path_str,
            issues=[Issue(code="missing_frontmatter", message="file does not start with a '---' frontmatter block")],
        )

    if not terminated:
        return FileResult(
            path=path_str,
            issues=[Issue(code="unterminated_frontmatter", message="frontmatter block has no closing '---'")],
        )

    try:
        data = parse_frontmatter(block)
    except FrontmatterSyntaxError as exc:
        return FileResult(path=path_str, issues=[Issue(code="invalid_frontmatter_syntax", message=str(exc))])

    return FileResult(path=path_str, issues=validate_frontmatter(data))
