Works correctly end to end. All 9 pytest cases pass, `--json`/text/error paths behave as designed.

`/tmp/ho2-H2-B-mSpYBW/dirstat.py` — CLI that recursively walks a directory, aggregates file count and total bytes per extension (lowercase, `""` bucket for extensionless files), and outputs either a text table or JSON.

`/tmp/ho2-H2-B-mSpYBW/test_dirstat.py` — 9 subprocess-based pytest cases covering JSON schema, sort order, text output, empty dirs, recursion, missing path, path-is-a-file, and `--help`.

Design notes:
- `--json` always emits a single JSON object to stdout on both success and failure (`{"success": true/false, ...}`), so a caller can `json.loads(stdout)` unconditionally and branch on `success`/exit code — no traceback ever hits stdout/stderr.
- Errors are structured: `{"success": false, "error": {"code": "not_found"|"not_a_directory", "message": "..."}}`, exit code 1.
- Unreadable files/subdirs during the walk are silently skipped rather than crashing (permission errors, broken symlinks).
- `--help` includes a documented JSON schema and copy-pasteable examples.

Run tests: `cd /tmp/ho2-H2-B-mSpYBW && .venv/bin/pytest test_dirstat.py -v` (a venv with pytest was created at `/tmp/ho2-H2-B-mSpYBW/.venv` since the system Python had none).
