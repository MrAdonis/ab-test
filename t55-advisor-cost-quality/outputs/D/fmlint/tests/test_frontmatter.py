import unittest

from fmlint.frontmatter import FrontmatterError, parse_frontmatter


class TestParseFrontmatter(unittest.TestCase):
    def test_scalars_and_inline_list(self):
        text = (
            "---\n"
            "title: 简短标题\n"
            "updated: 2026-07-14\n"
            "type: concept\n"
            "tags: [a, b, c]\n"
            "---\n"
            "body text\n"
        )
        data = parse_frontmatter(text)
        self.assertEqual(
            data,
            {
                "title": "简短标题",
                "updated": "2026-07-14",
                "type": "concept",
                "tags": ["a", "b", "c"],
            },
        )

    def test_block_list(self):
        text = (
            "---\n"
            "title: t\n"
            "tags:\n"
            "  - a\n"
            "  - b\n"
            "---\n"
        )
        data = parse_frontmatter(text)
        self.assertEqual(data["tags"], ["a", "b"])

    def test_quoted_scalar(self):
        text = '---\ntitle: "hello: world"\n---\n'
        data = parse_frontmatter(text)
        self.assertEqual(data["title"], "hello: world")

    def test_empty_inline_list(self):
        text = "---\ntags: []\n---\n"
        data = parse_frontmatter(text)
        self.assertEqual(data["tags"], [])

    def test_declared_but_empty_key_becomes_empty_string(self):
        text = "---\ntitle:\n---\n"
        data = parse_frontmatter(text)
        self.assertEqual(data["title"], "")

    def test_empty_file_raises_empty_file(self):
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter("")
        self.assertEqual(ctx.exception.code, "empty_file")

    def test_whitespace_only_file_raises_empty_file(self):
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter("   \n\n\t\n")
        self.assertEqual(ctx.exception.code, "empty_file")

    def test_no_frontmatter_raises_no_frontmatter(self):
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter("# just a heading\n\nsome body text\n")
        self.assertEqual(ctx.exception.code, "no_frontmatter")

    def test_unterminated_frontmatter_raises_parse_error(self):
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter("---\ntitle: t\nbody without closing delimiter\n")
        self.assertEqual(ctx.exception.code, "parse_error")

    def test_orphan_list_item_raises_parse_error(self):
        text = "---\n- orphan item\n---\n"
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter(text)
        self.assertEqual(ctx.exception.code, "parse_error")

    def test_bad_indentation_raises_parse_error(self):
        text = "---\ntitle: t\n    garbage indented line\n---\n"
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter(text)
        self.assertEqual(ctx.exception.code, "parse_error")

    def test_line_without_colon_raises_parse_error(self):
        text = "---\ntitle: t\nthis line has no colon\n---\n"
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter(text)
        self.assertEqual(ctx.exception.code, "parse_error")

    def test_scalar_then_list_item_conflict_raises_parse_error(self):
        text = "---\ntitle: t\n  - stray item\n---\n"
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter(text)
        self.assertEqual(ctx.exception.code, "parse_error")

    def test_unterminated_inline_list_raises_parse_error(self):
        text = "---\ntitle: Broken\ntags: [a, b\n---\n"
        with self.assertRaises(FrontmatterError) as ctx:
            parse_frontmatter(text)
        self.assertEqual(ctx.exception.code, "parse_error")


if __name__ == "__main__":
    unittest.main()
