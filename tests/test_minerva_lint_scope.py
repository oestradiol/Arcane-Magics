from __future__ import annotations
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class MinervaLintScopeTests(unittest.TestCase):
    def test_minerva_lint_does_not_require_foreign_authority(self):
        text=(ROOT/"scripts/lint_minerva_markdown.py").read_text(encoding="utf-8")
        self.assertIn("foreign live authority copied into split/minerva", text)
        self.assertIn("NxRxI_VOCABULARY_CENTER.md", text)
        self.assertIn("kernel/WORLDMIND.md", text)
        self.assertNotIn("inspect_state_consistency()", text)

    def test_makefile_uses_minerva_lint(self):
        text=(ROOT/"Makefile").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/lint_minerva_markdown.py", text)

if __name__=="__main__":
    unittest.main()
