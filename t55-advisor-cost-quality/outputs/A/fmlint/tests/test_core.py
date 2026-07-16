"""Unit tests for fmlint.core — the three required issue classes plus the
must-not-crash edge cases (no frontmatter / empty / broken syntax)."""

import unittest

from fmlint.core import lint_text, parse_frontmatter, validate_frontmatter


def codes(issues):
    return sorted(i["code"] for i in issues)


def fields(issues):
    return sorted(i["field"] for i in issues if i["field"])


VALID = """\
---
title: How caching works
updated: 2026-07-14
type: concept
tags: [caching, performance]
---

Body text here.
"""


class TestValidDocument(unittest.TestCase):
    def test_valid_has_no_issues(self):
        self.assertEqual(lint_text(VALID), [])

    def test_valid_block_style_tags(self):
        doc = (
            "---\n"
            "title: A\n"
            "updated: 2026-01-02\n"
            "type: method\n"
            "tags:\n"
            "  - x\n"
            "  - y\n"
            "---\n"
        )
        self.assertEqual(lint_text(doc), [])

    def test_valid_quoted_scalars(self):
        doc = (
            '---\n'
            'title: "Quoted title"\n'
            "updated: '2026-12-31'\n"
            "type: tool\n"
            'tags: ["a"]\n'
            "---\n"
        )
        self.assertEqual(lint_text(doc), [])


# --- Class 1: missing fields ------------------------------------------------
class TestMissingFields(unittest.TestCase):
    def test_missing_single_field(self):
        doc = "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\n---\n"
        issues = lint_text(doc)
        self.assertEqual(codes(issues), ["missing_field"])
        self.assertEqual(fields(issues), ["tags"])

    def test_missing_all_fields(self):
        doc = "---\nfoo: bar\n---\n"
        issues = lint_text(doc)
        self.assertEqual(fields(issues), ["tags", "title", "type", "updated"])
        self.assertTrue(all(i["code"] == "missing_field" for i in issues))


# --- Class 2: format errors -------------------------------------------------
class TestFormatErrors(unittest.TestCase):
    def _doc(self, updated):
        return ("---\ntitle: A\nupdated: %s\ntype: concept\ntags: [a]\n---\n"
                % updated)

    def test_wrong_date_shape(self):
        issues = lint_text(self._doc("07/14/2026"))
        self.assertEqual(codes(issues), ["invalid_format"])
        self.assertEqual(fields(issues), ["updated"])

    def test_impossible_date_is_rejected(self):
        # Correct shape but not a real calendar date.
        issues = lint_text(self._doc("2026-13-40"))
        self.assertEqual(codes(issues), ["invalid_format"])

    def test_empty_title_is_invalid(self):
        doc = "---\ntitle:\nupdated: 2026-01-01\ntype: concept\ntags: [a]\n---\n"
        issues = lint_text(doc)
        self.assertEqual(codes(issues), ["invalid_value"])
        self.assertEqual(fields(issues), ["title"])

    def test_empty_tags_array_is_invalid(self):
        doc = "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: []\n---\n"
        issues = lint_text(doc)
        self.assertEqual(codes(issues), ["invalid_value"])
        self.assertEqual(fields(issues), ["tags"])

    def test_tags_scalar_not_array_is_invalid(self):
        doc = "---\ntitle: A\nupdated: 2026-01-01\ntype: concept\ntags: nope\n---\n"
        issues = lint_text(doc)
        self.assertEqual(fields(issues), ["tags"])
        self.assertEqual(codes(issues), ["invalid_value"])


# --- Class 3: illegal type value -------------------------------------------
class TestIllegalType(unittest.TestCase):
    def test_bad_type_value(self):
        doc = "---\ntitle: A\nupdated: 2026-01-01\ntype: article\ntags: [a]\n---\n"
        issues = lint_text(doc)
        self.assertEqual(codes(issues), ["invalid_value"])
        self.assertEqual(fields(issues), ["type"])

    def test_each_valid_type_passes(self):
        for t in ("concept", "method", "tool"):
            doc = "---\ntitle: A\nupdated: 2026-01-01\ntype: %s\ntags: [a]\n---\n" % t
            self.assertEqual(lint_text(doc), [], "type %s should be valid" % t)


# --- Edge cases: must not crash --------------------------------------------
class TestEdgeCasesNoCrash(unittest.TestCase):
    def test_no_frontmatter(self):
        issues = lint_text("# Just a heading\n\nSome prose, no frontmatter.\n")
        self.assertEqual(codes(issues), ["missing_frontmatter"])

    def test_empty_file(self):
        self.assertEqual(codes(lint_text("")), ["empty_file"])

    def test_whitespace_only_file(self):
        self.assertEqual(codes(lint_text("   \n\n  \n")), ["empty_file"])

    def test_unterminated_frontmatter(self):
        doc = "---\ntitle: A\nupdated: 2026-01-01\n"  # no closing ---
        self.assertEqual(codes(lint_text(doc)), ["broken_frontmatter"])

    def test_garbage_inside_frontmatter(self):
        doc = "---\nthis is not: valid: yaml: at all\n\tweird indent\n---\n"
        # Must classify as broken, never raise.
        self.assertEqual(codes(lint_text(doc)), ["broken_frontmatter"])

    def test_bare_dashes_only(self):
        self.assertEqual(codes(lint_text("---\n---\n")),
                         ["missing_field"] * 4)

    def test_parse_frontmatter_never_raises_on_fuzz(self):
        samples = [
            "---",
            "---\n",
            "------",
            "---\n:\n---\n",
            "---\n  - orphan list item\n---\n",
            "---\n\x00\x01\n---\n",
            "not frontmatter at all",
            "---\ntitle: [unclosed\n---\n",
        ]
        for s in samples:
            data, status = parse_frontmatter(s)
            self.assertIn(status, (None, "missing", "broken"))


class TestCombinedIssues(unittest.TestCase):
    def test_multiple_issues_reported_together(self):
        doc = "---\nupdated: bad-date\ntype: nope\ntags: []\n---\n"
        issues = lint_text(doc)
        # title missing, updated bad format, type bad value, tags empty
        self.assertEqual(fields(issues), ["tags", "title", "type", "updated"])


if __name__ == "__main__":
    unittest.main()
