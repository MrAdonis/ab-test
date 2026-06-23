---
name: array-stats
description: Compute descriptive statistics (mean, median, std dev, percentiles) for a numeric array. Returns a structured result object. Pure local computation — no API, no network, no external process.
---

## When to Use

Invoke when given a numeric array and asked for any combination of: mean, average, median, standard deviation, variance, percentile, quantile, min, max, range, or "summary statistics."

Do **not** use for:
- Arrays with more than ~10 million elements — use numpy/pandas directly instead (memory overhead of pure Python loops becomes prohibitive above this scale)
- Streaming or chunked data where you don't have the full array in memory at once — build an incremental stats accumulator instead
- Statistical inference (hypothesis tests, p-values, confidence intervals) — those require scipy or statsmodels, not this skill

## Output Contract

Always return a dict with this exact shape. Read every field by name — do not parse as plain text:

```python
{
  "n":          int,      # count of valid (non-NaN) elements
  "mean":       float,    # arithmetic mean
  "median":     float,    # 50th percentile
  "std":        float,    # sample standard deviation (ddof=1); None if n < 2
  "variance":   float,    # sample variance (ddof=1); None if n < 2
  "min":        float,
  "max":        float,
  "range":      float,    # max - min
  "percentiles": {        # only present when requested
    "p25": float,
    "p75": float,
    "p90": float,
    "p95": float,
    "p99": float
  },
  "skipped":    int,      # count of elements dropped (NaN, None, non-numeric)
  "warnings":   list[str] # non-empty if anything notable happened
}
```

## Implementation

### Step 1 — Validate input (write dead, not "check as needed")

Trigger a hard error if any of these is true:
- Input is not a list or tuple
- Input is empty after filtering non-numeric values (`n == 0`)

For non-empty input with some bad values, filter them out, increment `skipped`, append a warning string — do **not** error.

**Good** — explicit gate before any math:
```python
if not isinstance(arr, (list, tuple)):
    raise TypeError(f"Expected list or tuple, got {type(arr).__name__}")

valid = [x for x in arr if isinstance(x, (int, float)) and x == x]  # x==x filters NaN
skipped = len(arr) - len(valid)
if not valid:
    raise ValueError("No valid numeric elements after filtering")
```

**Bad** — letting Python blow up mid-calculation with a confusing error:
```python
mean = sum(arr) / len(arr)  # crashes on NaN, None, strings with no context
```

### Step 2 — Core calculations

Use only Python builtins and `math` (always available). Do not import numpy, scipy, or statistics unless already confirmed present in the environment.

```python
import math

n = len(valid)
mean = sum(valid) / n
sorted_vals = sorted(valid)

# Median
mid = n // 2
median = sorted_vals[mid] if n % 2 else (sorted_vals[mid-1] + sorted_vals[mid]) / 2

# Sample std dev (ddof=1)
if n >= 2:
    variance = sum((x - mean) ** 2 for x in valid) / (n - 1)
    std = math.sqrt(variance)
else:
    variance = None
    std = None
```

### Step 3 — Percentiles (only when requested)

Use linear interpolation (matches numpy's default `method='linear'`):

```python
def percentile(sorted_vals, p):
    n = len(sorted_vals)
    if n == 1:
        return float(sorted_vals[0])
    idx = (p / 100) * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])
```

Compute `p25, p75, p90, p95, p99` only when the caller asks for percentiles or quantiles. Omit `percentiles` key entirely if not requested — do not return null values for unrequested fields.

### Step 4 — Assemble and return

```python
result = {
    "n": n,
    "mean": mean,
    "median": median,
    "std": std,
    "variance": variance,
    "min": float(sorted_vals[0]),
    "max": float(sorted_vals[-1]),
    "range": float(sorted_vals[-1] - sorted_vals[0]),
    "skipped": skipped,
    "warnings": warnings,  # list, may be empty
}
if percentiles_requested:
    result["percentiles"] = { ... }
return result
```

## Examples

### Basic — mean and std of a small array

```python
compute_stats([2, 4, 6, 8, 10])
# → {"n": 5, "mean": 6.0, "median": 6.0, "std": 3.162..., "min": 2.0, "max": 10.0, "range": 8.0, "skipped": 0, "warnings": []}
```

### With bad values mixed in

```python
compute_stats([1, None, "x", 3, float("nan"), 5])
# → {"n": 3, "mean": 3.0, ..., "skipped": 3, "warnings": ["3 non-numeric or NaN values were skipped"]}
```

### With percentiles requested

```python
compute_stats([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], percentiles=True)
# → {..., "percentiles": {"p25": 32.5, "p75": 77.5, "p90": 91.0, "p95": 95.5, "p99": 99.1}}
```

### Edge case — single element

```python
compute_stats([42])
# → {"n": 1, "mean": 42.0, "median": 42.0, "std": None, "variance": None, "min": 42.0, "max": 42.0, "range": 0.0, "skipped": 0, "warnings": []}
```

## Gotchas

> Only real execution failures documented here.

- **`std` and `variance` are `None` when `n < 2`** — sample std dev requires at least 2 points (divides by `n-1`). Do not substitute 0 or omit the key; return `None` and let the caller decide. Callers that check `result["std"] is not None` before using it are correct.

- **`float("nan")` passes `isinstance(x, float)` — use `x == x` to filter it** — `math.isnan()` also works, but the `x == x` idiom catches it without an import. Forgetting this causes `mean` to silently return `nan` and propagate through all downstream calculations.

- **`sorted()` on a list of integers returns ints, not floats** — `sorted_vals[0]` may be an `int`. Cast to `float` explicitly when populating `min`/`max`/`range` to keep the return type consistent.

- **Percentile interpolation differs by method** — this skill uses linear interpolation (numpy default). If a caller compares output to R's `quantile()` or Excel's `PERCENTILE.EXC`, results will differ at the tails. If exact match to a specific tool is required, document which method is needed before computing.

- **Empty list after filtering is a hard error, not a warning** — returning `{"n": 0, "mean": None, ...}` looks like a valid result and will silently corrupt downstream aggregations. Raise `ValueError` so the caller knows the input was unusable.
