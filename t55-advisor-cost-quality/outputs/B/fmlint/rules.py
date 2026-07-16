"""frontmatter 字段合规规则。"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List

from .models import Issue

REQUIRED_FIELDS = ("title", "updated", "type", "tags")
ALLOWED_TYPES = ("concept", "method", "tool")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_frontmatter(fm: dict) -> List[Issue]:
    issues: List[Issue] = []

    for field_name in REQUIRED_FIELDS:
        if field_name not in fm or fm[field_name] is None:
            issues.append(Issue("missing_field", field_name, f"缺少字段 '{field_name}'"))

    if fm.get("title") is not None:
        v = fm["title"]
        if not isinstance(v, str) or v.strip() == "":
            issues.append(Issue("empty_field", "title", "title 字段为空"))

    if fm.get("updated") is not None:
        v = fm["updated"]
        if not isinstance(v, str) or not _DATE_RE.match(v.strip()):
            issues.append(
                Issue(
                    "invalid_date_format",
                    "updated",
                    f"updated 字段必须是 YYYY-MM-DD 格式，实际为 {v!r}",
                )
            )
        else:
            try:
                datetime.strptime(v.strip(), "%Y-%m-%d")
            except ValueError:
                issues.append(
                    Issue(
                        "invalid_date_format",
                        "updated",
                        f"updated 字段不是合法日期：{v!r}",
                    )
                )

    if fm.get("type") is not None:
        v = fm["type"]
        if not isinstance(v, str) or v.strip() not in ALLOWED_TYPES:
            issues.append(
                Issue(
                    "invalid_type_value",
                    "type",
                    f"type 取值非法，应为 {list(ALLOWED_TYPES)} 之一，实际为 {v!r}",
                )
            )

    if fm.get("tags") is not None:
        v = fm["tags"]
        if not isinstance(v, list):
            issues.append(
                Issue(
                    "invalid_tags_type",
                    "tags",
                    f"tags 字段必须是数组，实际类型为 {type(v).__name__}",
                )
            )
        elif len(v) == 0:
            issues.append(Issue("invalid_tags_type", "tags", "tags 数组不能为空"))

    return issues
