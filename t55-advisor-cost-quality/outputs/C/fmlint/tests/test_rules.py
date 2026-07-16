import unittest

from fmlint.rules import validate_frontmatter


def codes(issues):
    return sorted(i.code for i in issues)


VALID = {"title": "A Page", "updated": "2026-01-01", "type": "concept", "tags": ["a"]}


class TestValidateFrontmatter(unittest.TestCase):
    def test_valid_frontmatter_has_no_issues(self):
        self.assertEqual(validate_frontmatter(dict(VALID)), [])

    def test_all_fields_missing(self):
        issues = validate_frontmatter({})
        self.assertEqual(codes(issues), ["missing_field"] * 4)
        fields = sorted(i.field for i in issues)
        self.assertEqual(fields, ["tags", "title", "type", "updated"])

    def test_one_field_missing(self):
        data = dict(VALID)
        del data["tags"]
        issues = validate_frontmatter(data)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "missing_field")
        self.assertEqual(issues[0].field, "tags")

    def test_empty_string_field_counts_as_missing(self):
        data = dict(VALID)
        data["title"] = ""
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["missing_field"])
        self.assertEqual(issues[0].field, "title")

    def test_none_field_counts_as_missing(self):
        data = dict(VALID)
        data["updated"] = None
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["missing_field"])

    def test_invalid_type_value(self):
        data = dict(VALID)
        data["type"] = "guide"
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_type"])
        self.assertEqual(issues[0].field, "type")

    def test_each_allowed_type_is_valid(self):
        for t in ("concept", "method", "tool"):
            data = dict(VALID)
            data["type"] = t
            self.assertEqual(validate_frontmatter(data), [], f"type={t} should be valid")

    def test_invalid_date_format_wrong_shape(self):
        data = dict(VALID)
        data["updated"] = "2026/01/01"
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_date_format"])

    def test_invalid_date_format_not_a_real_calendar_check_but_shape_only(self):
        # shape-only regex check: this tool validates format, not calendar validity
        data = dict(VALID)
        data["updated"] = "2026-13-40"
        self.assertEqual(validate_frontmatter(data), [])

    def test_invalid_date_wrong_length(self):
        data = dict(VALID)
        data["updated"] = "26-01-01"
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_date_format"])

    def test_tags_not_a_list(self):
        data = dict(VALID)
        data["tags"] = "debugging"
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_tags"])

    def test_tags_empty_list(self):
        data = dict(VALID)
        data["tags"] = []
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_tags"])

    def test_title_not_a_string(self):
        data = dict(VALID)
        data["title"] = {"__nested__": True}
        issues = validate_frontmatter(data)
        self.assertEqual([i.code for i in issues], ["invalid_title"])

    def test_multiple_problems_all_reported(self):
        data = {"title": "ok", "type": "guide", "tags": [], "updated": "not-a-date"}
        issues = validate_frontmatter(data)
        self.assertEqual(codes(issues), sorted(["invalid_type", "invalid_tags", "invalid_date_format"]))


if __name__ == "__main__":
    unittest.main()
