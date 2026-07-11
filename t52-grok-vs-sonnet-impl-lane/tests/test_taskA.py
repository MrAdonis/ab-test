import pytest
from duration import parse_duration


@pytest.mark.parametrize("s,expected", [
    ("90s", 90),
    ("1h30m", 5400),
    ("2d", 172800),
    ("1h30m45s", 5445),
    ("45m", 2700),
    ("0s", 0),
    ("1d2h3m4s", 93784),
    ("10h", 36000),
    ("  1h30m  ", 5400),      # surrounding whitespace tolerated
    ("100s", 100),           # multi-digit
    ("1d", 86400),
])
def test_valid(s, expected):
    assert parse_duration(s) == expected


@pytest.mark.parametrize("s", [
    "",            # empty
    "   ",         # blank
    "90",          # bare number, no unit
    "abc",         # garbage
    "1x",          # unknown unit
    "1h30",        # trailing number without unit
    "-5s",         # negative
    "1.5h",        # decimal
    "h",           # unit without number
    "1h m",        # internal space
    "1H",          # wrong-case unit (spec uses lowercase)
])
def test_invalid_raises(s):
    with pytest.raises(ValueError):
        parse_duration(s)
