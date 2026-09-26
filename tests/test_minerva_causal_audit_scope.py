from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class MinervaCausalAuditScopeTests(unittest.TestCase):
    def test_foreign_sources_are_explicit_and_not_copied(self):
        scope=json.loads((ROOT/"kernel/development/MINERVA_CAUSAL_AUDIT_SCOPE.json").read_text(encoding="utf-8"))
        foreign=scope["foreign_source_paths"]
        for rel in ("kernel/WORLDMIND.md","kernel/VENUS_INCIDENCE_LAW.tex","docs/META_DYNAMICS.md"):
            self.assertIn(rel,foreign)
            self.assertFalse((ROOT/rel).exists())

    def test_wrapper_keeps_whole_matrix_requirements(self):
        text=(ROOT/"scripts/audit_minerva_causal_distinctions.py").read_text(encoding="utf-8")
        self.assertIn("shared.REQUIRED_FIELDS",text)
        self.assertIn("shared.REQUIRED_CONCEPTS",text)
        self.assertIn("unscoped missing source artifact",text)

if __name__=="__main__":
    unittest.main()
