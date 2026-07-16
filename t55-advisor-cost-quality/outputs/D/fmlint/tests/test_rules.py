import unittest

from fmlint.rules import check_fields


VALID = {
    "title": "示例标题",
    "updated": "2026-07-14",
    "type": "concept",
    "tags": ["a", "b"],
}


class TestCheckFields(unittest.TestCase):
    def test_valid_frontmatter_has_no_issues(self):
        self.assertEqual(check_fields(dict(VALID)), [])

    def test_missing_single_field(self):
        data = dict(VALID)
        del data["tags"]
        issues = check_fields(data)
        codes = [(i.code, i.field) for i in issues]
        self.assertIn(("missing_field", "tags"), codes)

    def test_missing_all_fields(self):
        issues = check_fields({})
        codes = {i.field for i in issues if i.code == "missing_field"}
        self.assertEqual(codes, {"title", "updated", "type", "tags"})

    def test_empty_title_is_invalid_format(self):
        data = dict(VALID, title="   ")
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_format" and i.field == "title" for i in issues)
        )

    def test_updated_bad_format_string(self):
        data = dict(VALID, updated="07/14/2026")
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_format" and i.field == "updated" for i in issues)
        )

    def test_updated_impossible_calendar_date(self):
        data = dict(VALID, updated="2026-13-40")
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_format" and i.field == "updated" for i in issues)
        )

    def test_updated_correct_format_passes(self):
        data = dict(VALID, updated="2026-01-05")
        issues = check_fields(data)
        self.assertFalse(any(i.field == "updated" for i in issues))

    def test_type_invalid_value(self):
        data = dict(VALID, type="note")
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_type_value" and i.field == "type" for i in issues)
        )

    def test_type_each_allowed_value_passes(self):
        for value in ("concept", "method", "tool"):
            data = dict(VALID, type=value)
            issues = check_fields(data)
            self.assertFalse(any(i.field == "type" for i in issues), value)

    def test_tags_not_a_list(self):
        data = dict(VALID, tags="a, b, c")
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_format" and i.field == "tags" for i in issues)
        )

    def test_tags_empty_list(self):
        data = dict(VALID, tags=[])
        issues = check_fields(data)
        self.assertTrue(
            any(i.code == "invalid_format" and i.field == "tags" for i in issues)
        )

    def test_multiple_problems_all_reported(self):
        data = {"title": "t", "updated": "bad", "type": "bad", "tags": []}
        issues = check_fields(data)
        codes = {(i.code, i.field) for i in issues}
        self.assertIn(("invalid_format", "updated"), codes)
        self.assertIn(("invalid_type_value", "type"), codes)
        self.assertIn(("invalid_format", "tags"), codes)


if __name__ == "__main__":
    unittest.main()
