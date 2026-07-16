"""Data shapes shared by the checker and the CLI."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Issue:
    code: str
    message: str
    field: Optional[str] = None

    def to_dict(self) -> dict:
        return {"code": self.code, "field": self.field, "message": self.message}


@dataclass
class FileResult:
    path: str
    issues: List[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict:
        return {"path": self.path, "ok": self.ok, "issues": [i.to_dict() for i in self.issues]}
