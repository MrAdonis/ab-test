import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from fmlint.cli import main

VALID_FM = (
    "---\n"
    "title: A valid page\n"
    "updated: 2026-01-01\n"
    "type: concept\n"
    "tags: [a, b]\n"
    "---\n"
    "body\n"
)

INVALID_FM = "---\ntitle: T\nupdated: 2026-01-01\ntype: essay\n---\n"


def run_cli(args):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, stdout.getvalue()


class TestCliJson(unittest.TestCase):
    def test_clean_directory_exit_0(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.md").write_text(VALID_FM, encoding="utf-8")
            exit_code, out = run_cli([d])
            self.assertEqual(exit_code, 0)
            report = json.loads(out)
            self.assertTrue(report["success"])
            self.assertEqual(report["summary"]["total_issues"], 0)
            self.assertEqual(report["summary"]["files_scanned"], 1)

    def test_directory_with_issues_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "bad.md").write_text(INVALID_FM, encoding="utf-8")
            exit_code, out = run_cli([d])
            self.assertEqual(exit_code, 1)
            report = json.loads(out)
            self.assertTrue(report["success"])
            self.assertEqual(report["summary"]["files_with_issues"], 1)
            issue_codes = [i["code"] for i in report["files"][0]["issues"]]
            self.assertIn("missing_field", issue_codes)
            self.assertIn("invalid_type_value", issue_codes)

    def test_nonexistent_directory_exit_2(self):
        exit_code, out = run_cli(["/no/such/directory/xyz"])
        self.assertEqual(exit_code, 2)
        report = json.loads(out)
        self.assertFalse(report["success"])
        self.assertIn("error", report)
        self.assertIn("message", report["error"])

    def test_file_instead_of_directory_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "not_a_dir.md"
            f.write_text(VALID_FM, encoding="utf-8")
            exit_code, out = run_cli([str(f)])
            self.assertEqual(exit_code, 2)
            report = json.loads(out)
            self.assertFalse(report["success"])

    def test_output_is_always_valid_json_even_on_crash_prone_input(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "empty.md").write_text("", encoding="utf-8")
            (Path(d) / "no_fm.md").write_text("just text\n", encoding="utf-8")
            (Path(d) / "broken.md").write_text("---\ntitle: no closing\n", encoding="utf-8")
            exit_code, out = run_cli([d])
            self.assertEqual(exit_code, 1)
            report = json.loads(out)  # must not raise
            self.assertEqual(report["summary"]["files_scanned"], 3)


class TestCliText(unittest.TestCase):
    def test_text_format_does_not_crash_and_mentions_issue(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "bad.md").write_text(INVALID_FM, encoding="utf-8")
            exit_code, out = run_cli([d, "--format", "text"])
            self.assertEqual(exit_code, 1)
            self.assertIn("invalid_type_value", out)


class TestCliPattern(unittest.TestCase):
    def test_custom_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.markdown").write_text(VALID_FM, encoding="utf-8")
            (Path(d) / "b.md").write_text(VALID_FM, encoding="utf-8")
            exit_code, out = run_cli([d, "--pattern", "*.markdown"])
            self.assertEqual(exit_code, 0)
            report = json.loads(out)
            self.assertEqual(report["summary"]["files_scanned"], 1)


if __name__ == "__main__":
    unittest.main()
