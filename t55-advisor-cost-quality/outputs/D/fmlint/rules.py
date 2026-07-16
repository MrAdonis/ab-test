"""Validation rules for the four required frontmatter fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

REQUIRED_FIELDS = ("title", "updated", "type", "tags")
ALLOWED_TYPES = ("concept", "method", "tool")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Issue:
    code: str
    message: str
    field: str | None = None

    def to_dict(self) -> dict:
        d = {"code": self.code, "message": self.message}
        if self.field is not None:
            d["field"] = self.field
        return d


def check_fields(data: dict) -> list[Issue]:
    """Validate an already-parsed frontmatter dict. Never raises."""
    issues: list[Issue] = []

    for name in REQUIRED_FIELDS:
        if name not in data:
            issues.append(Issue("missing_field", f"缺少必填字段: {name}", field=name))

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(Issue("invalid_format", "title 不能为空", field="title"))

    if "updated" in data:
        issues.extend(_check_updated(data["updated"]))

    if "type" in data:
        issues.extend(_check_type(data["type"]))

    if "tags" in data:
        issues.extend(_check_tags(data["tags"]))

    return issues


def _check_updated(value) -> list[Issue]:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return [
            Issue(
                "invalid_format",
                f"updated 必须是 YYYY-MM-DD 格式，实际是: {value!r}",
                field="updated",
            )
        ]
    year, month, day = (int(part) for part in value.split("-"))
    try:
        date(year, month, day)
    except ValueError:
        return [Issue("invalid_format", f"updated 不是合法日期: {value!r}", field="updated")]
    return []


def _check_type(value) -> list[Issue]:
    if value not in ALLOWED_TYPES:
        return [
            Issue(
                "invalid_type_value",
                f"type 取值非法: {value!r}，允许的值: {', '.join(ALLOWED_TYPES)}",
                field="type",
            )
        ]
    return []


def _check_tags(value) -> list[Issue]:
    if not isinstance(value, list) or not value:
        return [Issue("invalid_format", "tags 必须是非空数组", field="tags")]
    return []
