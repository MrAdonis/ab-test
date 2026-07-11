import re

_UNIT_SECONDS = {
    "d": 86400,
    "h": 3600,
    "m": 60,
    "s": 1,
}

_COMPONENT_RE = re.compile(r"(\d+)([dhms])")
_FULL_RE = re.compile(r"(?:\d+[dhms])+")


def parse_duration(s: str) -> int:
    if not isinstance(s, str):
        raise ValueError(f"Invalid duration: {s!r}")

    stripped = s.strip()

    if not stripped:
        raise ValueError(f"Invalid duration: {s!r}")

    if not _FULL_RE.fullmatch(stripped):
        raise ValueError(f"Invalid duration: {s!r}")

    total = 0
    for value, unit in _COMPONENT_RE.findall(stripped):
        total += int(value) * _UNIT_SECONDS[unit]

    return total
