import unittest

from fmlint.rules import validate_frontmatter


def codes(issues):
    return sorted(i.code for i in issues)


class TestValidateFrontmatter(unittest.TestCase):
    def test_fully_valid(self):
        fm = {
            "title": "Hello",
            "updated": "2026-01-01",
            "type": "concept",
            "tags": ["a", "b"],
        }
        self.assertEqual(validate_frontmatter(fm), [])

    def test_missing_all_fields(self):
        issues = validate_frontmatter({})
        self.assertEqual(
            codes(issues),
            ["missing_field", "missing_field", "missing_field", "missing_field"],
        )
        fields = sorted(i.field for i in issues)
        self.assertEqual(fields, ["tags", "title", "type", "updated"])

    def test_missing_one_field(self):
        fm = {"title": "Hello", "updated": "2026-01-01", "type": "concept"}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "missing_field")
        self.assertEqual(issues[0].field, "tags")

    def test_null_value_counts_as_missing(self):
        fm = {"title": None, "updated": "2026-01-01", "type": "concept", "tags": ["a"]}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "missing_field")
        self.assertEqual(issues[0].field, "title")

    def test_empty_title(self):
        fm = {"title": "  ", "updated": "2026-01-01", "type": "concept", "tags": ["a"]}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "empty_field")
        self.assertEqual(issues[0].field, "title")

    def test_invalid_type_value(self):
        fm = {"title": "T", "updated": "2026-01-01", "type": "essay", "tags": ["a"]}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "invalid_type_value")
        self.assertEqual(issues[0].field, "type")

    def test_all_allowed_types_pass(self):
        for t in ("concept", "method", "tool"):
            fm = {"title": "T", "updated": "2026-01-01", "type": t, "tags": ["a"]}
            self.assertEqual(validate_frontmatter(fm), [])

    def test_invalid_date_format(self):
        for bad in ("2026/01/01", "Jan 1 2026", "26-01-01", "2026-1-1", ""):
            fm = {"title": "T", "updated": bad, "type": "concept", "tags": ["a"]}
            issues = validate_frontmatter(fm)
            codes_found = codes(issues)
            self.assertIn("invalid_date_format", codes_found, msg=f"bad date: {bad!r}")

    def test_invalid_calendar_date(self):
        fm = {"title": "T", "updated": "2026-13-40", "type": "concept", "tags": ["a"]}
        issues = validate_frontmatter(fm)
        self.assertEqual(codes(issues), ["invalid_date_format"])

    def test_tags_not_a_list(self):
        fm = {"title": "T", "updated": "2026-01-01", "type": "concept", "tags": "a, b"}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "invalid_tags_type")
        self.assertEqual(issues[0].field, "tags")

    def test_tags_empty_list(self):
        fm = {"title": "T", "updated": "2026-01-01", "type": "concept", "tags": []}
        issues = validate_frontmatter(fm)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "invalid_tags_type")
        self.assertEqual(issues[0].field, "tags")

    def test_multiple_issues_at_once(self):
        fm = {"title": "", "updated": "bad-date", "type": "nope", "tags": []}
        issues = validate_frontmatter(fm)
        self.assertEqual(
            codes(issues),
            sorted(
                [
                    "empty_field",
                    "invalid_date_format",
                    "invalid_type_value",
                    "invalid_tags_type",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
