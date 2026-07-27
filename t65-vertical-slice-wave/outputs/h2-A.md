Done. Two files created in the working directory:

- **`dirstat.py`** — CLI that recursively scans a directory and reports per-extension file count + total bytes.
  - `collect_stats(root)` — core logic, importable for scripting.
  - `--json` flag emits `{"ext": {"count": N, "bytes": N}, ...}` to stdout; without it, prints a sorted plain-text table.
  - Bad input (missing path, path is a file, or any unexpected exception) is caught and reported as structured output — JSON on stderr with `--json`, a plain `Error: ...` line otherwise — never a raw traceback, always exit code `1`.
  - `run(argv)` returns `(exit_code, stdout, stderr)` without touching real stdio, so it's easy to call/test programmatically; `main(argv)` is the thin stdio-writing wrapper for `if __name__ == "__main__"`.

- **`test_dirstat.py`** — 9 pytest cases covering nested files, no-extension grouping, empty dirs, `--json`/text output, missing-directory and file-instead-of-directory error paths (asserting no traceback), and `main()`'s exit code.

Verified: `python3 -m pytest test_dirstat.py` → 9 passed; manually ran the CLI in text/JSON/error modes to confirm output shapes. (Used a throwaway local venv to install pytest for the test run, since none was on PATH — removed it afterward, so no dependency artifacts were left behind.)
