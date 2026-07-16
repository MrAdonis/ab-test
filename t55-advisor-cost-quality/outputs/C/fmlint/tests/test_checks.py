import tempfile
import unittest
from pathlib import Path

from fmlint.checks import lint_file


def write(dirpath: Path, name: str, content: str) -> Path:
    p = dirpath / name
    p.write_text(content, encoding="utf-8")
    return p


class TestLintFile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_file_is_ok(self):
        p = write(
            self.dir,
            "valid.md",
            "---\ntitle: Valid Page\nupdated: 2026-01-01\ntype: concept\ntags: [a, b]\n---\nbody\n",
        )
        result = lint_file(p)
        self.assertTrue(result.ok)
        self.assertEqual(result.issues, [])

    def test_missing_field_detected(self):
        p = write(self.dir, "missing.md", "---\ntitle: Foo\nupdated: 2026-01-01\ntype: concept\n---\nbody\n")
        result = lint_file(p)
        self.assertFalse(result.ok)
        self.assertEqual([i.code for i in result.issues], ["missing_field"])
        self.assertEqual(result.issues[0].field, "tags")

    def test_invalid_type_detected(self):
        p = write(
            self.dir,
            "badtype.md",
            "---\ntitle: Foo\nupdated: 2026-01-01\ntype: guide\ntags: [a]\n---\n",
        )
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["invalid_type"])

    def test_invalid_date_format_detected(self):
        p = write(
            self.dir,
            "baddate.md",
            "---\ntitle: Foo\nupdated: Jan 1 2026\ntype: concept\ntags: [a]\n---\n",
        )
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["invalid_date_format"])

    # --- must-not-crash cases ---

    def test_no_frontmatter_does_not_crash(self):
        p = write(self.dir, "nofm.md", "# Just a heading\n\nSome body text.\n")
        result = lint_file(p)
        self.assertFalse(result.ok)
        self.assertEqual([i.code for i in result.issues], ["missing_frontmatter"])

    def test_empty_file_does_not_crash(self):
        p = write(self.dir, "empty.md", "")
        result = lint_file(p)
        self.assertFalse(result.ok)
        self.assertEqual([i.code for i in result.issues], ["empty_file"])

    def test_whitespace_only_file_does_not_crash(self):
        p = write(self.dir, "whitespace.md", "   \n\n\t\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["empty_file"])

    def test_unterminated_frontmatter_does_not_crash(self):
        p = write(self.dir, "unterminated.md", "---\ntitle: Foo\nupdated: 2026-01-01\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["unterminated_frontmatter"])

    def test_garbage_frontmatter_syntax_does_not_crash(self):
        p = write(self.dir, "garbage.md", "---\nthis is not valid at all !!!\n---\nbody\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["invalid_frontmatter_syntax"])

    def test_unterminated_inline_list_does_not_crash(self):
        p = write(self.dir, "badlist.md", "---\ntitle: Foo\ntags: [a, b\n---\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["invalid_frontmatter_syntax"])

    def test_empty_frontmatter_block_reports_all_missing(self):
        p = write(self.dir, "emptyfm.md", "---\n---\nbody\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["missing_field"] * 4)

    def test_non_utf8_file_does_not_crash(self):
        p = self.dir / "binary.md"
        p.write_bytes(b"---\ntitle: \xff\xfe bad bytes\n---\n")
        result = lint_file(p)
        self.assertEqual([i.code for i in result.issues], ["encoding_error"])

    def test_nonexistent_file_does_not_crash(self):
        result = lint_file(self.dir / "does-not-exist.md")
        self.assertEqual([i.code for i in result.issues], ["read_error"])


if __name__ == "__main__":
    unittest.main()
