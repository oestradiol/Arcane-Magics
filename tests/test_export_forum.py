from __future__ import annotations

import unittest

from scripts.export_forum import normalize_forum_markdown


class ForumNormalizationTests(unittest.TestCase):
    def test_removes_unsupported_operatorname_and_labels(self):
        out = normalize_forum_markdown(r"$$\\operatorname{rank}(x)\\label{eq:x}$$")
        self.assertIn(r"\\mathrm{rank}", out)
        self.assertNotIn(r"\\operatorname", out)
        self.assertNotIn(r"\\label", out)

    def test_consumes_pandoc_reference_and_wrappers(self):
        src = (
            '<div class="definition">\n'
            '**Definition.**\n\n'
            '<a href="#eq:x" data-reference-type="eqref" data-reference="eq:x">(3)</a>'
            '</div>'
        )
        out = normalize_forum_markdown(src)
        self.assertNotIn("<div", out)
        self.assertNotIn("data-reference", out)
        self.assertNotIn("**Definition.**", out)
        self.assertIn("(3)", out)

    def test_removes_raw_reference_tokens(self):
        out = normalize_forum_markdown("See [sec:foo] and \\ref{prop:x}.")
        self.assertEqual(out, "See the referenced result and the referenced result.\n")

    def test_plainifies_raw_tex_outside_math_but_preserves_math(self):
        src = (
            r"Outside: \\mathcal{F} \\rightarrow \\text{future family}. "
            r"Escaped: \\\\mathrm{rank}. "
            r"Math: $\\mathcal{F} \\rightarrow Q$."
        )
        out = normalize_forum_markdown(src)
        self.assertNotIn(r"\\mathcal{F}", out.split("Math:", 1)[0])
        self.assertNotIn(r"\\rightarrow", out.split("Math:", 1)[0])
        self.assertNotIn(r"\\text", out.split("Math:", 1)[0])
        self.assertNotIn(r"\\mathrm", out.split("Math:", 1)[0])
        self.assertIn("→", out)
        self.assertIn(r"$\\mathcal{F} \\rightarrow Q$", out)

    def test_plainifies_nested_text_wrapper_command_token(self):
        out = normalize_forum_markdown(
            r"Outside \\text{a \\mathcal{nested} object} remains readable."
        )
        self.assertNotIn(r"\\text", out)
        self.assertNotIn(r"\\mathcal", out)


if __name__ == "__main__":
    unittest.main()
