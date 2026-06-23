---
name: csv-to-markdown
description: Convert a CSV file to a Markdown table. Handles delimiter detection, header inference, and edge cases (quoted fields, empty cells, Unicode). Trigger when the user provides a CSV file path or pastes CSV content and asks for a Markdown table.
---

# csv-to-markdown

## When to Use

Trigger when:
- User provides a `.csv` file path and asks for a Markdown table
- User pastes raw CSV text and wants it as a Markdown table

## Not for This Skill

- CSV with complex nested structures or multi-line cells that need custom reshaping → handle manually with pandas and describe the desired shape first
- Generating a CSV from data (reverse direction) → write the CSV directly, no skill needed
- Markdown tables that need visual styling, column width tuning, or alignment decisions beyond left/right/center → out of scope; this skill outputs standard GFM tables only

## Workflow

### Step 1 — Read the input

If given a file path, read the file. If given pasted text, use it directly. Do not ask the user for clarification unless the input is completely absent.

### Step 2 — Detect delimiter

Check in order: comma → tab → semicolon → pipe. Use the character that produces the most consistent column count across rows. If ambiguous, default to comma and note the assumption in output.

### Step 3 — Parse rows

- Strip leading/trailing whitespace from each cell
- Handle quoted fields: `"value with, comma"` → `value with, comma`
- Empty cells become empty table cells (not `N/A` or `-` unless the user asked)
- If row column counts are inconsistent, pad shorter rows with empty cells to match the header width

### Step 4 — Build the Markdown table

```
| col1 | col2 | col3 |
| ---- | ---- | ---- |
| val  | val  | val  |
```

- Use the first row as headers unless the user explicitly says "no header" or the first row contains only numeric values
- Separator row uses `----` (four dashes), not a fixed number matching column width — GFM does not require it
- Default alignment: left (no colons). Apply `:---:` or `---:` only if the user specifies

### Step 5 — Output

Return the Markdown table as a fenced code block (` ```markdown `) so it renders cleanly in chat, followed by the raw table text so the user can copy it directly.

If the CSV was read from a file, note the row count: `Converted N rows (excluding header).`

## Gotchas

> Only real failures encountered during execution, not general best practices.

- **Quoted fields containing newlines** → multi-line cell content breaks the Markdown table format. Collapse newlines inside quoted fields to a space before inserting into the table. Do not silently drop them.
- **BOM prefix on Windows CSV files** (`﻿` at start of file) → strips the BOM before parsing; otherwise the first header cell gets a leading `ï»¿` artifact.
- **Pipe `|` characters inside cell values** → escape as `\|` in the Markdown table; unescaped pipes break GFM table parsing.
