---
name: array-stats
description: >
  Compute descriptive statistics (mean, median, std dev, percentiles) on a
  numeric array. Pure local calculation — no API, no key, no subprocess.
  Invoke when the user provides a list/array of numbers and asks for stats,
  summary, or descriptive analysis.
---

# array-stats

Compute mean, median, standard deviation, and percentiles on a numeric array.
All calculation happens in-process with Python's `statistics` module (stdlib).
No network calls, no keys, no external processes.

## When to Use

Invoke this skill when:
- The user provides a list/array of numbers and asks for statistics, summary, or "describe this data"
- The task is purely local numeric analysis with no plotting or ML requirement

## When NOT to Use

- Need a histogram, chart, or visualization → use `/diagram`
- Need regression, clustering, or ML → use pandas/scikit-learn directly
- Array contains non-numeric elements → validate and clean first; this skill does not impute or skip silently
- Need streaming/incremental stats on unbounded data → Welford's algorithm, not this

## Output Contract

The skill always returns a single JSON object with this exact schema. No extra keys, no nesting variation:

```json
{
  "n": 10,
  "mean": 5.5,
  "median": 5.5,
  "std_dev": 3.02,
  "variance": 9.17,
  "min": 1.0,
  "max": 10.0,
  "range": 9.0,
  "percentiles": {
    "p25": 3.25,
    "p50": 5.5,
    "p75": 7.75,
    "p90": 9.1,
    "p95": 9.55,
    "p99": 9.91
  }
}
```

All numeric values are floats rounded to 6 significant figures. `n` is always an integer. `percentiles` always contains all six keys — never omit any, even if `n` is small.

## Workflow

**Step 1 — Validate input**

```python
def validate(arr):
    if not arr:
        return {"error": "empty_array", "message": "Input array is empty"}
    non_numeric = [i for i, v in enumerate(arr) if not isinstance(v, (int, float))]
    if non_numeric:
        return {"error": "non_numeric", "indices": non_numeric,
                "message": f"Non-numeric values at indices {non_numeric}"}
    if len(arr) < 2:
        return {"error": "too_small", "message": "Need at least 2 elements for std_dev"}
    return None
```

Return the error object immediately if validation fails. Do NOT proceed to calculation.

**Step 2 — Calculate**

```python
import statistics, math

def compute_stats(arr):
    arr_f = [float(x) for x in arr]
    arr_s = sorted(arr_f)
    n = len(arr_f)

    def percentile(p):
        idx = (p / 100) * (n - 1)
        lo, hi = int(idx), min(int(idx) + 1, n - 1)
        return arr_s[lo] + (arr_s[hi] - arr_s[lo]) * (idx - lo)

    return {
        "n": n,
        "mean": round(statistics.mean(arr_f), 6),
        "median": round(statistics.median(arr_f), 6),
        "std_dev": round(statistics.stdev(arr_f), 6),
        "variance": round(statistics.variance(arr_f), 6),
        "min": arr_s[0],
        "max": arr_s[-1],
        "range": round(arr_s[-1] - arr_s[0], 6),
        "percentiles": {
            f"p{p}": round(percentile(p), 6)
            for p in [25, 50, 75, 90, 95, 99]
        }
    }
```

**Step 3 — Return**

Return the dict directly. Do not wrap in `{"result": ...}` or `{"data": ...}`. The top-level object IS the result.

## Examples

**Good — basic call, returns exact schema:**

```python
compute_stats([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# → {"n": 10, "mean": 5.5, "median": 5.5, "std_dev": 3.02765, ...}
```

**Good — with options (custom percentiles added inline):**

```python
arr = [14.2, 17.8, 12.1, 19.4, 15.6, 13.3, 18.9, 16.7, 11.8, 20.1]
result = compute_stats(arr)
# result["percentiles"]["p95"] gives the 95th percentile directly
```

**Bad — wrapping the result:**

```python
return {"stats": compute_stats(arr)}   # WRONG — adds an extra wrapper key
return {"result": compute_stats(arr)}  # WRONG — caller must guess the wrapper
```

**Bad — mixing validation and computation:**

```python
# Don't do this — silently drops bad values instead of surfacing the error
arr_clean = [x for x in arr if isinstance(x, (int, float))]
compute_stats(arr_clean)  # WRONG — caller never knows data was dropped
```

**Edge case — n=2 (minimum valid input):**

```python
compute_stats([3.0, 7.0])
# → {"n": 2, "mean": 5.0, "median": 5.0, "std_dev": 2.828427, ...}
# percentiles collapse: p25=p50=p75 will all interpolate within [3.0, 7.0]
# This is correct behavior, not a bug
```

## Gotchas

> Only real failures encountered during execution, not general best practices.

- **`statistics.stdev` requires n ≥ 2** → raises `StatisticsError` on single-element arrays. The validation step gates this explicitly. Do NOT call `stdev` before checking `len(arr) >= 2`.
- **Percentile interpolation with small n collapses quantiles** → with n=2, p25/p50/p75/p90/p95/p99 all interpolate between the same two values. The values are mathematically correct but visually identical. Mention this to the user when `n < 5`.
- **Integer arrays stay integers through `statistics.mean` in Python 3.8+** → `statistics.mean([1,2,3])` returns `2` (int), not `2.0` (float). The `float(x)` cast in Step 2 prevents schema drift — do not skip it.
- **`sorted()` returns a new list; the original `arr` is unchanged** → safe to call repeatedly; no in-place mutation.
