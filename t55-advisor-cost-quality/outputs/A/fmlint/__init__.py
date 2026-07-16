"""fmlint — Markdown frontmatter linter for knowledge bases.

Programmatic use:
    from fmlint.core import lint_path, lint_file, lint_text
    envelope = lint_path("./wiki")

CLI use:
    python -m fmlint ./wiki
"""

from .core import (
    ISSUE_CODES,
    REQUIRED_FIELDS,
    VALID_TYPES,
    lint_file,
    lint_path,
    lint_text,
    validate_frontmatter,
)

__all__ = [
    "ISSUE_CODES",
    "REQUIRED_FIELDS",
    "VALID_TYPES",
    "lint_file",
    "lint_path",
    "lint_text",
    "validate_frontmatter",
]

__version__ = "1.0.0"
