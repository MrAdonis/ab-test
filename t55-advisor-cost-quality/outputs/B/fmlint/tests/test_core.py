import tempfile
import unittest
from pathlib import Path

from fmlint.core import lint_directory, lint_file, lint_text


def codes(issues):
    return sorted(i.code for i in issues)


VALID_FM = (
    "---\n"
    "title: A valid page\n"
    "updated: 2026-01-01\n"
    "type: concept\n"
    "tags: [a, b]\n"
    "---\n"
    "body\n"
)


class TestLintText(unittest.TestCase):
    def test_valid_frontmatter_has_no_issues(self):
        self.assertEqual(lint_text(VALID_FM), [])

    def test_empty_file_does_not_crash(self):
        issues = lint_text("")
        self.assertEqual(codes(issues), ["empty_file"])

    def test_whitespace_only_file_does_not_crash(self):
        issues = lint_text("   \n\t\n")
        self.assertEqual(codes(issues), ["empty_file"])

    def test_no_frontmatter_does_not_crash(self):
        issues = lint_text("# just a heading\n\nsome text\n")
        self.assertEqual(codes(issues), ["no_frontmatter"])

    def test_unterminated_frontmatter_does_not_crash(self):
        text = "---\ntitle: broken\nno closing delimiter\n"
        issues = lint_text(text)
        self.assertEqual(codes(issues), ["unterminated_frontmatter"])

    def test_broken_yaml_syntax_does_not_crash(self):
        text = '---\ntitle: "unterminated quote\nupdated: 2026-01-01\n---\nbody\n'
        issues = lint_text(text)
        self.assertEqual(codes(issues), ["malformed_frontmatter"])

    def test_missing_field(self):
        text = "---\ntitle: T\nupdated: 2026-01-01\ntype: concept\n---\n"
        issues = lint_text(text)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "missing_field")
        self.assertEqual(issues[0].field, "tags")

    def test_invalid_type_value(self):
        text = (
            "---\ntitle: T\nupdated: 2026-01-01\ntype: essay\ntags: [a]\n---\n"
        )
        issues = lint_text(text)
        self.assertEqual(codes(issues), ["invalid_type_value"])

    def test_invalid_date_format(self):
        text = (
            "---\ntitle: T\nupdated: 01/01/2026\ntype: concept\ntags: [a]\n---\n"
        )
        issues = lint_text(text)
        self.assertEqual(codes(issues), ["invalid_date_format"])

    def test_tags_not_array(self):
        text = '---\ntitle: T\nupdated: 2026-01-01\ntype: concept\ntags: "a, b"\n---\n'
        issues = lint_text(text)
        self.assertEqual(codes(issues), ["invalid_tags_type"])


class TestLintFile(unittest.TestCase):
    def test_lint_file_reads_and_reports(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_text(VALID_FM, encoding="utf-8")
            result = lint_file(p)
            self.assertTrue(result.ok)
            self.assertEqual(result.issues, [])

    def test_lint_file_on_bad_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.md"
            p.write_text("", encoding="utf-8")
            result = lint_file(p)
            self.assertFalse(result.ok)
            self.assertEqual(codes(result.issues), ["empty_file"])


class TestLintDirectory(unittest.TestCase):
    def test_scans_only_matching_pattern_recursively(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "good.md").write_text(VALID_FM, encoding="utf-8")
            (root / "bad.md").write_text("no frontmatter here\n", encoding="utf-8")
            (root / "ignore.txt").write_text("not markdown\n", encoding="utf-8")
            nested = root / "sub"
            nested.mkdir()
            (nested / "nested.md").write_text(VALID_FM, encoding="utf-8")

            results = lint_directory(root)
            names = sorted(Path(r.path).name for r in results)
            self.assertEqual(names, ["bad.md", "good.md", "nested.md"])

            ok_map = {Path(r.path).name: r.ok for r in results}
            self.assertTrue(ok_map["good.md"])
            self.assertTrue(ok_map["nested.md"])
            self.assertFalse(ok_map["bad.md"])

    def test_empty_directory_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(lint_directory(Path(d)), [])


if __name__ == "__main__":
    unittest.main()
