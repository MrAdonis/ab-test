import unittest

from fmlint.parser import FrontmatterParseError, parse_yaml_subset, split_frontmatter


class TestSplitFrontmatter(unittest.TestCase):
    def test_normal_frontmatter(self):
        text = "---\ntitle: Hello\nupdated: 2026-01-01\n---\nbody text\n"
        result = split_frontmatter(text)
        self.assertIsNone(result.error)
        self.assertEqual(result.fm_lines, ["title: Hello", "updated: 2026-01-01"])
        self.assertEqual(result.body, "body text")

    def test_empty_file(self):
        result = split_frontmatter("")
        self.assertEqual(result.error, "empty_file")

    def test_whitespace_only_file(self):
        result = split_frontmatter("   \n  \n")
        self.assertEqual(result.error, "empty_file")

    def test_no_frontmatter(self):
        result = split_frontmatter("# Just a heading\n\nsome content\n")
        self.assertEqual(result.error, "no_frontmatter")

    def test_unterminated_frontmatter(self):
        text = "---\ntitle: Hello\nno closing delimiter here\n"
        result = split_frontmatter(text)
        self.assertEqual(result.error, "unterminated_frontmatter")


class TestParseYamlSubset(unittest.TestCase):
    def test_simple_scalars(self):
        fm = parse_yaml_subset(["title: Hello World", "type: concept"])
        self.assertEqual(fm, {"title": "Hello World", "type": "concept"})

    def test_quoted_scalar(self):
        fm = parse_yaml_subset(['title: "Hello: World"'])
        self.assertEqual(fm["title"], "Hello: World")

    def test_inline_list(self):
        fm = parse_yaml_subset(['tags: [a, b, "c d"]'])
        self.assertEqual(fm["tags"], ["a", "b", "c d"])

    def test_inline_empty_list(self):
        fm = parse_yaml_subset(["tags: []"])
        self.assertEqual(fm["tags"], [])

    def test_block_list(self):
        fm = parse_yaml_subset(["tags:", "  - a", "  - b"])
        self.assertEqual(fm["tags"], ["a", "b"])

    def test_block_list_then_next_key(self):
        fm = parse_yaml_subset(["tags:", "  - a", "  - b", "type: concept"])
        self.assertEqual(fm, {"tags": ["a", "b"], "type": "concept"})

    def test_empty_value_no_block_becomes_none(self):
        fm = parse_yaml_subset(["title:"])
        self.assertIsNone(fm["title"])

    def test_unterminated_quote_raises(self):
        with self.assertRaises(FrontmatterParseError):
            parse_yaml_subset(['title: "unterminated'])

    def test_unterminated_inline_list_raises(self):
        with self.assertRaises(FrontmatterParseError):
            parse_yaml_subset(["tags: [a, b"])

    def test_invalid_line_syntax_raises(self):
        with self.assertRaises(FrontmatterParseError):
            parse_yaml_subset(["this is not key value"])

    def test_unexpected_indentation_raises(self):
        with self.assertRaises(FrontmatterParseError):
            parse_yaml_subset(["  title: Hello"])

    def test_bad_block_list_item_raises(self):
        with self.assertRaises(FrontmatterParseError):
            parse_yaml_subset(["tags:", "  not a list item"])


if __name__ == "__main__":
    unittest.main()
