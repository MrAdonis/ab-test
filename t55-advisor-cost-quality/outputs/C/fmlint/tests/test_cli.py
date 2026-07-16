import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fmlint.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exit_code = main(argv)
    return exit_code, buf.getvalue()


class TestCliJsonOutput(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name, content):
        (self.dir / name).write_text(content, encoding="utf-8")

    def test_directory_not_found_exits_2(self):
        exit_code, out = run_main([str(self.dir / "nope")])
        payload = json.loads(out)
        self.assertEqual(exit_code, 2)
        self.assertFalse(payload["success"])
        self.assertIsNotNone(payload["error"])
        self.assertEqual(payload["results"], [])

    def test_all_valid_exits_0(self):
        self._write(
            "a.md",
            "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: [x]\n---\n",
        )
        exit_code, out = run_main([str(self.dir)])
        payload = json.loads(out)
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["summary"]["files_scanned"], 1)
        self.assertEqual(payload["summary"]["files_with_issues"], 0)

    def test_issues_found_exits_1_and_reports_counts(self):
        self._write(
            "good.md",
            "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: [x]\n---\n",
        )
        self._write("bad.md", "---\ntitle: B\ntype: not-a-type\ntags: []\n---\n")
        exit_code, out = run_main([str(self.dir)])
        payload = json.loads(out)
        self.assertEqual(exit_code, 1)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["summary"]["files_scanned"], 2)
        self.assertEqual(payload["summary"]["files_with_issues"], 1)
        bad_result = next(r for r in payload["results"] if r["path"].endswith("bad.md"))
        self.assertFalse(bad_result["ok"])
        codes = {i["code"] for i in bad_result["issues"]}
        self.assertIn("missing_field", codes)
        self.assertIn("invalid_type", codes)
        self.assertIn("invalid_tags", codes)

    def test_recurses_into_subdirectories(self):
        sub = self.dir / "nested"
        sub.mkdir()
        (sub / "deep.md").write_text("no frontmatter here\n", encoding="utf-8")
        exit_code, out = run_main([str(self.dir)])
        payload = json.loads(out)
        self.assertEqual(payload["summary"]["files_scanned"], 1)
        self.assertEqual(exit_code, 1)

    def test_human_mode_does_not_crash_and_skips_json(self):
        self._write("bad.md", "not frontmatter\n")
        exit_code, out = run_main([str(self.dir), "--human"])
        with self.assertRaises(json.JSONDecodeError):
            json.loads(out)
        self.assertIn("bad.md", out)
        self.assertEqual(exit_code, 1)


class TestCliSubprocess(unittest.TestCase):
    """One true end-to-end check of `python -m fmlint <dir>`."""

    def test_module_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            dirpath = Path(d)
            (dirpath / "ok.md").write_text(
                "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: [x]\n---\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, "-m", "fmlint", str(dirpath)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["success"])
            self.assertEqual(payload["summary"]["files_with_issues"], 0)


if __name__ == "__main__":
    unittest.main()
