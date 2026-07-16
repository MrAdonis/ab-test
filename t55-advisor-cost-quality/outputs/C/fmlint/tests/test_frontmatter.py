import unittest

from fmlint.frontmatter import FrontmatterSyntaxError, parse_frontmatter, split_frontmatter


class TestSplitFrontmatter(unittest.TestCase):
    def test_no_marker(self):
        block, terminated, has_marker = split_frontmatter("# just a heading\n\nbody text\n")
        self.assertIsNone(block)
        self.assertFalse(terminated)
        self.assertFalse(has_marker)

    def test_unterminated(self):
        raw = "---\ntitle: foo\nupdated: 2026-01-01\n"
        block, terminated, has_marker = split_frontmatter(raw)
        self.assertIsNone(block)
        self.assertFalse(terminated)
        self.assertTrue(has_marker)

    def test_normal_block(self):
        raw = "---\ntitle: foo\nupdated: 2026-01-01\n---\nbody\n"
        block, terminated, has_marker = split_frontmatter(raw)
        self.assertEqual(block, "title: foo\nupdated: 2026-01-01")
        self.assertTrue(terminated)
        self.assertTrue(has_marker)

    def test_empty_block(self):
        raw = "---\n---\nbody\n"
        block, terminated, has_marker = split_frontmatter(raw)
        self.assertEqual(block, "")
        self.assertTrue(terminated)
        self.assertTrue(has_marker)

    def test_no_trailing_body(self):
        raw = "---\ntitle: foo\n---"
        block, terminated, has_marker = split_frontmatter(raw)
        self.assertEqual(block, "title: foo")
        self.assertTrue(terminated)


class TestParseFrontmatter(unittest.TestCase):
    def test_flat_scalars(self):
        data = parse_frontmatter("title: My Page\nupdated: 2026-01-01\ntype: concept")
        self.assertEqual(data, {"title": "My Page", "updated": "2026-01-01", "type": "concept"})

    def test_quoted_scalar(self):
        data = parse_frontmatter('title: "Quoted: Title"')
        self.assertEqual(data["title"], "Quoted: Title")

    def test_inline_list(self):
        data = parse_frontmatter("tags: [debugging, python]")
        self.assertEqual(data["tags"], ["debugging", "python"])

    def test_inline_list_quoted_items(self):
        data = parse_frontmatter('tags: ["a b", c]')
        self.assertEqual(data["tags"], ["a b", "c"])

    def test_inline_empty_list(self):
        data = parse_frontmatter("tags: []")
        self.assertEqual(data["tags"], [])

    def test_block_list(self):
        data = parse_frontmatter("tags:\n  - debugging\n  - python\n")
        self.assertEqual(data["tags"], ["debugging", "python"])

    def test_empty_value_is_none(self):
        data = parse_frontmatter("status:\ntitle: foo")
        self.assertIsNone(data["status"])
        self.assertEqual(data["title"], "foo")

    def test_empty_block_is_empty_dict(self):
        self.assertEqual(parse_frontmatter(""), {})
        self.assertEqual(parse_frontmatter("\n\n"), {})

    def test_nested_mapping_is_opaque_not_a_list_or_string(self):
        data = parse_frontmatter("metadata:\n  type: user\n  confidence: high\n")
        self.assertIsInstance(data["metadata"], dict)

    def test_unparseable_line_raises(self):
        with self.assertRaises(FrontmatterSyntaxError):
            parse_frontmatter("this is not a key value line at all")

    def test_unterminated_inline_list_raises(self):
        with self.assertRaises(FrontmatterSyntaxError):
            parse_frontmatter("tags: [a, b")

    def test_unexpected_indentation_raises(self):
        with self.assertRaises(FrontmatterSyntaxError):
            parse_frontmatter("  title: indented from the start")


if __name__ == "__main__":
    unittest.main()
