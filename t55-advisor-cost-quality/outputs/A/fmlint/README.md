# fmlint

Lint Markdown frontmatter across a knowledge base. Every `.md` file is
expected to carry four frontmatter fields:

| field     | rule                                             |
|-----------|--------------------------------------------------|
| `title`   | non-empty string                                 |
| `updated` | `YYYY-MM-DD`, a real calendar date               |
| `type`    | one of `concept` / `method` / `tool`             |
| `tags`    | non-empty array of non-empty strings             |

Zero dependencies — pure Python standard library (3.8+).

## Usage

```bash
python -m fmlint ./wiki                 # lint a directory (recursive)
python -m fmlint note.md                # lint a single file
python -m fmlint ./wiki --format text   # human-readable summary
python -m fmlint ./wiki > report.json   # capture for CI / another agent
```

Default output is JSON on stdout; `--format text` prints a readable summary.

## For CI and agent scripts

Consume the JSON envelope, not the text. Shape:

```json
{
  "success": true,
  "data": {
    "root": "./wiki",
    "summary": {"files_checked": 132, "files_ok": 130,
                "files_with_issues": 2, "total_issues": 3},
    "results": [
      {"file": "concepts/caching.md", "ok": false,
       "issues": [{"field": "type", "code": "invalid_value",
                   "message": "type must be one of concept/method/tool, got 'article'"}]}
    ]
  },
  "error": null
}
```

- `success` is `false` **only** for tool-level failures (e.g. the path does
  not exist); then `data` is `null` and `error` is `{"code", "message"}`.
  Frontmatter findings are *not* errors — they live in `data.results` with
  `success: true`.
- Switch on `issue.code`, never parse `issue.message`. Closed set:
  `empty_file`, `missing_frontmatter`, `broken_frontmatter`, `missing_field`,
  `invalid_format`, `invalid_value`, `read_error`.

### Exit codes

| code | meaning                          |
|------|----------------------------------|
| 0    | clean — no issues                |
| 1    | success, but issues were found   |
| 2    | tool error (bad path / bad args) |

CI can gate on the exit code alone; richer detail is in the JSON.

## Programmatic API

```python
from fmlint.core import lint_path, lint_file, lint_text

envelope = lint_path("./wiki")          # same dict the CLI emits
result   = lint_file("note.md")         # {"file", "ok", "issues"}
issues   = lint_text(raw_markdown)      # list of {"field", "code", "message"}
```

## Tests

```bash
python -m unittest discover -s fmlint   # run from this project's parent dir
```

No pip install required.
