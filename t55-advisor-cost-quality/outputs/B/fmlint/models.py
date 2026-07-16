"""结构化结果类型，供 CLI 输出和其他脚本/agent 消费。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Issue:
    code: str
    field: Optional[str]
    message: str

    def to_dict(self) -> dict:
        return {"code": self.code, "field": self.field, "message": self.message}


@dataclass
class FileResult:
    path: str
    ok: bool
    issues: List[Issue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "ok": self.ok,
            "issues": [i.to_dict() for i in self.issues],
        }
