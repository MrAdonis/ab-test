import pytest
from semver import compare_versions


@pytest.mark.parametrize("a,b,expected", [
    ("1.0.0", "1.0.1", -1),
    ("1.0.1", "1.0.0", 1),
    ("1.0.0", "1.0.0", 0),
    ("1.10.0", "1.9.0", 1),          # numeric, not lexical
    ("2.0.0", "1.99.99", 1),
    ("1.0.0-alpha", "1.0.0", -1),    # pre-release < release
    ("1.0.0", "1.0.0-alpha", 1),
    ("1.0.0+build", "1.0.0", 0),     # build metadata ignored
    ("1.0.0+build.1", "1.0.0+build.2", 0),
    ("1.0.0-alpha+x", "1.0.0-alpha+y", 0),
])
def test_core(a, b, expected):
    assert compare_versions(a, b) == expected


# The canonical semver.org precedence chain:
# 1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta
#   < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
CHAIN = [
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-alpha.beta",
    "1.0.0-beta",
    "1.0.0-beta.2",
    "1.0.0-beta.11",
    "1.0.0-rc.1",
    "1.0.0",
]


@pytest.mark.parametrize("i", range(len(CHAIN) - 1))
def test_precedence_chain(i):
    assert compare_versions(CHAIN[i], CHAIN[i + 1]) == -1
    assert compare_versions(CHAIN[i + 1], CHAIN[i]) == 1


def test_numeric_lower_than_alnum():
    # numeric identifier has lower precedence than alphanumeric
    assert compare_versions("1.0.0-1", "1.0.0-alpha") == -1


def test_more_identifiers_higher():
    assert compare_versions("1.0.0-alpha", "1.0.0-alpha.1") == -1
