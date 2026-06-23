---
name: csv-to-markdown
description: Convert a CSV file to a Markdown table. Triggered when the user says "convert CSV to Markdown", "CSV to table", "turn this CSV into a table", or provides a .csv file and asks for a Markdown table.
---

# csv-to-markdown

## When to Use

Triggered when: user provides a CSV file path or CSV content and wants a Markdown table output.

Not for: large-scale data processing pipelines, CSV analysis, filtering/sorting/aggregating data, or Excel/HTML output — those need a different tool.

## Workflow

**Input**: CSV file path or raw CSV text pasted inline.

**Step 1 — Read input**

If a file path is given, read the file. If raw text is pasted, use it directly. Do not attempt to infer column types or transform values — preserve them exactly as-is.

**Step 2 — Parse**

- First row = header row (column names)
- Delimiter = comma by default; if parsing produces a single column for every row, retry with tab (`\t`) as delimiter
- Strip leading/trailing whitespace from each cell value
- Preserve empty cells as empty (do not fill with `—` or other placeholders unless user requests it)

**Step 3 — Render Markdown table**

```
| col1 | col2 | col3 |
| ---- | ---- | ---- |
| val  | val  | val  |
```

Rules:
- Separator row uses `----` (four dashes), not spaces or fancy alignment
- Pipe characters (`|`) inside a cell must be escaped as `\|`
- Newlines inside a cell are not valid Markdown table syntax — collapse them to a space
- Do not pad columns to equal width (wastes tokens, no visual benefit in raw Markdown)

**Step 4 — Output**

Return the Markdown table in a fenced code block with language tag `markdown` so the user can copy it cleanly. Then offer to output it raw (no fence) if they need it for direct pasting.

## Examples

### Basic

Input CSV:
```
Name,Age,City
Alice,30,New York
Bob,25,London
```

Output:
````markdown
| Name | Age | City |
| ---- | ---- | ---- |
| Alice | 30 | New York |
| Bob | 25 | London |
````

### With problematic characters (Good vs Bad)

**Good** — pipe in cell is escaped:
```
| Plan | Price | Notes |
| ---- | ---- | ---- |
| Basic \| Pro | $10 | — |
```

**Bad** — unescaped pipe breaks table rendering:
```
| Basic | Pro | $10 | — |   ← parser sees extra column
```

### Edge cases

- **Empty cells**: `Alice,,New York` → `| Alice |  | New York |` (empty cell, not a dash)
- **Quoted fields with commas**: `"Smith, John",42,Paris` → cell value is `Smith, John`, the comma inside is not a delimiter
- **No header row**: if user says "there's no header", label columns `Column 1`, `Column 2`, … and note this in the response
- **Single-column result**: likely wrong delimiter — retry with `\t`, then ask user to confirm

## Not in scope (self-exclusion)

Do not use this skill for:
- Files > 500 rows: output will likely exceed what's useful in chat — suggest the user run a script instead (`python3 -c "import csv, sys; ..."`)
- Data transformation (sorting, filtering, aggregation) — parse only, no mutations
- Excel or HTML table output — different format, different tool
- CSV validation or schema checking

## Gotchas

> Only real failures go here. Empty until first execution failure is diagnosed and traced to root cause.

- *(none yet)*
