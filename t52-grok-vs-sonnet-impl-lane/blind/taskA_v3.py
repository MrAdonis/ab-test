import re

_UNIT_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1}
_PATTERN = re.compile(r"^(?:\d+[dhms])+$")


def parse_duration(s: str) -> int:
    s = s.strip()
    if not _PATTERN.fullmatch(s):
        raise ValueError(f"invalid duration: {s!r}")

    total = 0
    for num, unit in re.findall(r"(\d+)([dhms])", s):
        total += int(num) * _UNIT_SECONDS[unit]
    return total
