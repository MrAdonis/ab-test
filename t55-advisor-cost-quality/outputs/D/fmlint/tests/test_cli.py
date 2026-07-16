import contextlib
import io
import json
import os
import tempfile
import unittest

from fmlint.cli import main

VALID_MD = (
    "---\n"
    "title: 有效笔记\n"
    "updated: 2026-07-14\n"
    "type: concept\n"
    "tags: [a, b]\n"
    "---\n"
)

BROKEN_MD = "---\ntitle: t\nno colon here\n---\n"


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_main(argv):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(argv)
    return code, stdout.getvalue()


class TestCliJsonOutput(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def test_clean_directory_exit_zero(self):
        write(os.path.join(self.tmpdir.name, "a.md"), VALID_MD)
        code, out = run_main([self.tmpdir.name])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertTrue(payload["success"])
        self.assertIsNone(payload["error"])
        self.assertEqual(payload["data"]["total_issues"], 0)

    def test_directory_with_issues_exit_one(self):
        write(os.path.join(self.tmpdir.name, "bad.md"), "---\ntitle: t\n---\n")
        code, out = run_main([self.tmpdir.name])
        self.assertEqual(code, 1)
        payload = json.loads(out)
        self.assertTrue(payload["success"])
        self.assertGreater(payload["data"]["total_issues"], 0)
        self.assertEqual(payload["data"]["results"][0]["file"], "bad.md")

    def test_broken_syntax_file_reported_not_crashed(self):
        write(os.path.join(self.tmpdir.name, "broken.md"), BROKEN_MD)
        code, out = run_main([self.tmpdir.name])
        self.assertEqual(code, 1)
        payload = json.loads(out)
        issues = payload["data"]["results"][0]["issues"]
        self.assertEqual(issues[0]["code"], "parse_error")

    def test_missing_directory_exit_two_structured_error(self):
        code, out = run_main([os.path.join(self.tmpdir.name, "does_not_exist")])
        self.assertEqual(code, 2)
        payload = json.loads(out)
        self.assertFalse(payload["success"])
        self.assertIsNone(payload["data"])
        self.assertEqual(payload["error"]["code"], "dir_not_found")

    def test_human_flag_produces_non_json_summary_line(self):
        write(os.path.join(self.tmpdir.name, "a.md"), VALID_MD)
        code, out = run_main([self.tmpdir.name, "--human"])
        self.assertEqual(code, 0)
        self.assertIn("scanned 1 files", out)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(out)


if __name__ == "__main__":
    unittest.main()
