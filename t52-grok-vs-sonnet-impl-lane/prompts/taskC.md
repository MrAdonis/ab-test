Write a Python module `semver.py` with a single function:

    compare_versions(a: str, b: str) -> int

It compares two Semantic Versioning 2.0.0 strings (see semver.org) and returns:
- `-1` if `a` has lower precedence than `b`
- `0`  if they have equal precedence
- `1`  if `a` has higher precedence than `b`

Precedence rules (per the semver.org spec):
- Compare `major`, then `minor`, then `patch` **numerically** (so `1.10.0` > `1.9.0`).
- A version with a pre-release tag has LOWER precedence than the same version without one
  (`1.0.0-alpha` < `1.0.0`).
- Pre-release precedence: compare dot-separated identifiers left to right. Numeric identifiers
  are compared numerically; identifiers with letters are compared lexically (ASCII). A numeric
  identifier always has lower precedence than an alphanumeric one. If all shared identifiers are
  equal, the version with MORE identifiers has higher precedence.
- Build metadata (anything after `+`) is IGNORED for precedence (`1.0.0+build.1` == `1.0.0`).

Examples:
- `compare_versions("1.0.0", "1.0.1")` -> -1
- `compare_versions("1.10.0", "1.9.0")` -> 1
- `compare_versions("1.0.0-alpha", "1.0.0")` -> -1
- `compare_versions("1.0.0+build", "1.0.0")` -> 0

You may assume both inputs are well-formed version strings.
Only output the contents of `semver.py`. No tests, no explanation.
