from __future__ import annotations

import unittest

from scripts.lint_github_markdown import split_math_regions


class MarkdownMathScannerTests(unittest.TestCase):
    def test_closing_display_delimiter_does_not_reclassify_prior_math_as_prose(self):
        prose, math, state = split_math_regions(
            r"\end{aligned}$$ where $x\in\mathcal X$ remains bounded.",
            True,
        )
        self.assertFalse(state)
        self.assertIn(r"\end{aligned}", math)
        self.assertIn(r"x\in\mathcal X", math)
        self.assertEqual(prose.strip(), "where  remains bounded.")

    def test_opening_display_delimiter_keeps_following_tex_in_math(self):
        prose, math, state = split_math_regions(
            r"Prefix $$\mathcal F_t := \{T_1,T_2\}",
            False,
        )
        self.assertTrue(state)
        self.assertEqual(prose.strip(), "Prefix")
        self.assertIn(r"\mathcal F_t", math)

    def test_same_line_display_and_inline_math_leave_only_prose(self):
        prose, math, state = split_math_regions(
            r"Before $$\Gamma_t\to\Gamma_{t+1}$$ after $x\neq y$.",
            False,
        )
        self.assertFalse(state)
        self.assertEqual(prose.strip(), "Before  after .")
        self.assertIn(r"\Gamma_t", math)
        self.assertIn(r"x\neq y", math)


if __name__ == "__main__":
    unittest.main()
