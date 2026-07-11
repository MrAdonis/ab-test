import re

_UNIT_SECONDS = {
    "d": 86400,
    "h": 3600,
    "m": 60,
    "s": 1,
}

_COMPONENT_RE = re.compile(r"(\d+)([dhms])")


def parse_duration(s: str) -> int:
    text = s.strip()
    if not text:
        raise ValueError("invalid duration")

    total = 0
    pos = 0

    for match in _COMPONENT_RE.finditer(text):
        if match.start() != pos:
            raise ValueError("invalid duration")
        number, unit = match.groups()
        total += int(number) * _UNIT_SECONDS[unit]
        pos = match.end()

    if pos != len(text) or pos == 0:
        raise ValueError("invalid duration")

    return total
