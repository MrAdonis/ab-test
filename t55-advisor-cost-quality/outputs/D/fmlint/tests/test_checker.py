import os
import tempfile
import unittest

from fmlint.checker import find_markdown_files, lint_directory, lint_file


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


VALID_MD = (
    "---\n"
    "title: 有效笔记\n"
    "updated: 2026-07-14\n"
    "type: concept\n"
    "tags: [a, b]\n"
    "---\n"
    "body\n"
)


class TestLintFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def path(self, name: str) -> str:
        return os.path.join(self.tmpdir.name, name)

    def test_valid_file_has_no_issues(self):
        p = self.path("ok.md")
        write(p, VALID_MD)
        self.assertEqual(lint_file(p), [])

    def test_missing_field(self):
        p = self.path("missing.md")
        write(p, "---\ntitle: t\nupdated: 2026-07-14\ntype: concept\n---\n")
        issues = lint_file(p)
        self.assertTrue(any(i.code == "missing_field" and i.field == "tags" for i in issues))

    def test_bad_format(self):
        p = self.path("bad_format.md")
        write(
            p,
            "---\ntitle: t\nupdated: not-a-date\ntype: concept\ntags: [a]\n---\n",
        )
        issues = lint_file(p)
        self.assertTrue(any(i.code == "invalid_format" and i.field == "updated" for i in issues))

    def test_bad_type_value(self):
        p = self.path("bad_type.md")
        write(
            p,
            "---\ntitle: t\nupdated: 2026-07-14\ntype: essay\ntags: [a]\n---\n",
        )
        issues = lint_file(p)
        self.assertTrue(any(i.code == "invalid_type_value" for i in issues))

    def test_no_frontmatter_does_not_crash(self):
        p = self.path("no_fm.md")
        write(p, "# just a heading\n\nsome content, no frontmatter at all\n")
        issues = lint_file(p)  # must not raise
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "no_frontmatter")

    def test_empty_file_does_not_crash(self):
        p = self.path("empty.md")
        write(p, "")
        issues = lint_file(p)  # must not raise
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "empty_file")

    def test_broken_frontmatter_syntax_does_not_crash(self):
        p = self.path("broken.md")
        write(p, "---\ntitle: t\nthis is not key value\n---\n")
        issues = lint_file(p)  # must not raise
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "parse_error")

    def test_unterminated_frontmatter_does_not_crash(self):
        p = self.path("unterminated.md")
        write(p, "---\ntitle: t\nupdated: 2026-07-14\n")
        issues = lint_file(p)  # must not raise
        self.assertEqual(issues[0].code, "parse_error")


class TestFindMarkdownFiles(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def test_finds_nested_md_files_only(self):
        write(os.path.join(self.tmpdir.name, "a.md"), VALID_MD)
        write(os.path.join(self.tmpdir.name, "sub", "b.md"), VALID_MD)
        write(os.path.join(self.tmpdir.name, "notes.txt"), "not markdown")
        found = find_markdown_files(self.tmpdir.name)
        names = sorted(os.path.relpath(f, self.tmpdir.name) for f in found)
        self.assertEqual(names, sorted(["a.md", os.path.join("sub", "b.md")]))


class TestLintDirectory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def test_mixed_directory_summary_counts(self):
        write(os.path.join(self.tmpdir.name, "ok.md"), VALID_MD)
        write(
            os.path.join(self.tmpdir.name, "missing.md"),
            "---\ntitle: t\nupdated: 2026-07-14\ntype: concept\n---\n",
        )
        write(os.path.join(self.tmpdir.name, "empty.md"), "")
        write(os.path.join(self.tmpdir.name, "notes.txt"), "ignored, not markdown")

        report = lint_directory(self.tmpdir.name)

        self.assertEqual(report.checked_files, 3)  # .txt excluded
        self.assertEqual(len(report.results), 2)
        self.assertEqual(report.total_issues, 2)  # 1 missing_field + 1 empty_file

        files_with_issues = {r.file for r in report.results}
        self.assertEqual(files_with_issues, {"missing.md", "empty.md"})

    def test_clean_directory_has_zero_total_issues(self):
        write(os.path.join(self.tmpdir.name, "a.md"), VALID_MD)
        write(os.path.join(self.tmpdir.name, "b.md"), VALID_MD)
        report = lint_directory(self.tmpdir.name)
        self.assertEqual(report.total_issues, 0)
        self.assertEqual(report.results, [])

    def test_empty_directory(self):
        report = lint_directory(self.tmpdir.name)
        self.assertEqual(report.checked_files, 0)
        self.assertEqual(report.total_issues, 0)


if __name__ == "__main__":
    unittest.main()
