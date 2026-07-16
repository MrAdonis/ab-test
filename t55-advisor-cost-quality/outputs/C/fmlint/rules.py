"""Validation rules for a parsed frontmatter dict."""

import re
from typing import List

from .models import Issue

REQUIRED_FIELDS = ("title", "updated", "type", "tags")
ALLOWED_TYPES = ("concept", "method", "tool")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_present(data: dict, field_name: str) -> bool:
    return field_name in data and data[field_name] not in (None, "")


def validate_frontmatter(data: dict) -> List[Issue]:
    issues: List[Issue] = []

    for field_name in REQUIRED_FIELDS:
        if not _is_present(data, field_name):
            issues.append(
                Issue(code="missing_field", field=field_name, message=f"missing required field: {field_name}")
            )

    if _is_present(data, "title") and not isinstance(data["title"], str):
        issues.append(
            Issue(
                code="invalid_title",
                field="title",
                message=f"title must be a string, got {type(data['title']).__name__}",
            )
        )

    if _is_present(data, "updated"):
        updated = data["updated"]
        if not isinstance(updated, str) or not DATE_PATTERN.match(updated):
            issues.append(
                Issue(
                    code="invalid_date_format",
                    field="updated",
                    message=f"updated must match YYYY-MM-DD, got: {updated!r}",
                )
            )

    if _is_present(data, "type") and data["type"] not in ALLOWED_TYPES:
        issues.append(
            Issue(
                code="invalid_type",
                field="type",
                message=f"type must be one of {ALLOWED_TYPES}, got: {data['type']!r}",
            )
        )

    if _is_present(data, "tags"):
        tags = data["tags"]
        if not isinstance(tags, list) or len(tags) == 0:
            issues.append(
                Issue(
                    code="invalid_tags",
                    field="tags",
                    message=f"tags must be a non-empty array, got: {tags!r}",
                )
            )

    return issues
