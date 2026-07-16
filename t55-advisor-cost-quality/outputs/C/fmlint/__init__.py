"""fmlint: lint Markdown frontmatter for required fields, type enum, date format, and tags."""

from .checks import lint_file
from .frontmatter import FrontmatterSyntaxError, parse_frontmatter, split_frontmatter
from .models import FileResult, Issue
from .rules import ALLOWED_TYPES, REQUIRED_FIELDS, validate_frontmatter

__all__ = [
    "lint_file",
    "FrontmatterSyntaxError",
    "parse_frontmatter",
    "split_frontmatter",
    "FileResult",
    "Issue",
    "ALLOWED_TYPES",
    "REQUIRED_FIELDS",
    "validate_frontmatter",
]
