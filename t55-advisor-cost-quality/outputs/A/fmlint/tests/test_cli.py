"""End-to-end tests for the `python -m fmlint` entry point: directory
walking, the JSON envelope shape, and exit codes CI relies on."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

from fmlint.core import lint_path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GOOD = "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: [a]\n---\n"
BAD = "---\ntitle: A\nupdated: nope\ntype: concept\ntags: [a]\n---\n"


def write(dirpath, name, content):
    path = os.path.join(dirpath, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def run_cli(*args):
    """Run `python -m fmlint <args>` and return (returncode, stdout)."""
    proc = subprocess.run(
        [sys.executable, "-m", "fmlint", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


class TestLintPathAPI(unittest.TestCase):
    def test_recursive_walk_and_summary(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "ok.md", GOOD)
            write(d, "sub/bad.md", BAD)
            write(d, "notes.txt", "ignored, not markdown")
            env = lint_path(d)

        self.assertTrue(env["success"])
        self.assertIsNone(env["error"])
        summary = env["data"]["summary"]
        self.assertEqual(summary["files_checked"], 2)
        self.assertEqual(summary["files_ok"], 1)
        self.assertEqual(summary["files_with_issues"], 1)
        self.assertEqual(summary["total_issues"], 1)

    def test_missing_path_is_tool_error(self):
        env = lint_path("/no/such/path/really")
        self.assertFalse(env["success"])
        self.assertIsNone(env["data"])
        self.assertEqual(env["error"]["code"], "path_not_found")

    def test_empty_dir_is_success_zero_files(self):
        with tempfile.TemporaryDirectory() as d:
            env = lint_path(d)
        self.assertTrue(env["success"])
        self.assertEqual(env["data"]["summary"]["files_checked"], 0)

    def test_single_file_path(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "one.md", GOOD)
            env = lint_path(p)
        self.assertEqual(env["data"]["summary"]["files_checked"], 1)


class TestCLIExitCodes(unittest.TestCase):
    def test_clean_dir_exit_0_and_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "ok.md", GOOD)
            code, out = run_cli(d)
        self.assertEqual(code, 0)
        env = json.loads(out)
        self.assertTrue(env["success"])
        self.assertEqual(env["data"]["summary"]["total_issues"], 0)

    def test_issues_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "bad.md", BAD)
            code, out = run_cli(d)
        self.assertEqual(code, 1)
        self.assertTrue(json.loads(out)["success"])

    def test_bad_path_exit_2(self):
        code, out = run_cli("/no/such/path/really")
        self.assertEqual(code, 2)
        env = json.loads(out)
        self.assertFalse(env["success"])
        self.assertEqual(env["error"]["code"], "path_not_found")

    def test_text_format_runs(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "bad.md", BAD)
            code, out = run_cli(d, "--format", "text")
        self.assertEqual(code, 1)
        self.assertIn("invalid_format", out)


if __name__ == "__main__":
    unittest.main()
