Write a Python module `duration.py` with a single function:

    parse_duration(s: str) -> int

It parses a human-readable duration string into a total number of **seconds** (an int).

Supported units: `d` (day = 86400s), `h` (hour = 3600s), `m` (minute = 60s), `s` (second = 1s).

A valid string is one or more `<integer><unit>` components concatenated, e.g.:
- `"90s"` -> 90
- `"1h30m"` -> 5400
- `"2d"` -> 172800
- `"1h30m45s"` -> 5445

Rules:
- Numbers are non-negative integers (no decimals, no signs).
- Leading/trailing whitespace should be tolerated.
- Any input that does not fully match this format must raise `ValueError`
  (e.g. empty string, a bare number with no unit, an unknown unit, a decimal, a negative number, trailing garbage).

Only output the contents of `duration.py`. No tests, no explanation.
