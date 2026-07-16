"""Walk a directory of Markdown files and lint each one's frontmatter."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .frontmatter import FrontmatterError, parse_frontmatter
from .rules import Issue, check_fields


@dataclass
class FileResult:
    file: str
    issues: list[Issue]

    def to_dict(self) -> dict:
        return {"file": self.file, "issues": [issue.to_dict() for issue in self.issues]}


@dataclass
class Report:
    root: str
    checked_files: int
    results: list[FileResult] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return sum(len(r.issues) for r in self.results)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "checked_files": self.checked_files,
            "files_with_issues": len(self.results),
            "total_issues": self.total_issues,
            "results": [r.to_dict() for r in self.results],
        }


def find_markdown_files(root: str) -> list[str]:
    matches = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".md"):
                matches.append(os.path.join(dirpath, name))
    return sorted(matches)


def lint_file(path: str) -> list[Issue]:
    """Lint a single file. Never raises — I/O and parse failures become Issues."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        return [Issue("read_error", f"无法读取文件: {exc}")]

    try:
        data = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [Issue(exc.code, exc.message)]

    return check_fields(data)


def lint_directory(root: str) -> Report:
    files = find_markdown_files(root)
    results = []
    for path in files:
        issues = lint_file(path)
        if issues:
            results.append(FileResult(file=os.path.relpath(path, root), issues=issues))
    return Report(root=root, checked_files=len(files), results=results)
