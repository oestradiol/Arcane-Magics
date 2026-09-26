from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class MinervaConstructAuditScopeTests(unittest.TestCase):
    def test_foreign_construct_evidence_is_explicit(self):
        scope=json.loads((ROOT/"kernel/development/MINERVA_CONSTRUCT_AUDIT_SCOPE.json").read_text(encoding="utf-8"))
        foreign=scope["foreign_evidence_paths"]
        for rel in ("monographs/01_OFE/main.tex","kernel/WORLDMIND.md","monographs/02_ECLIPSIS/main.tex","kernel/VENUS_INCIDENCE_LAW.tex"):
            self.assertIn(rel,foreign)
            self.assertFalse((ROOT/rel).exists())

    def test_wrapper_preserves_reduction_rules(self):
        text=(ROOT/"scripts/audit_minerva_construct_dispositions.py").read_text(encoding="utf-8")
        self.assertIn("shared.ALLOWED",text)
        self.assertIn("genealogy must remain preserved",text)
        self.assertIn("subsumed/retired status requires mature_substitute",text)
        self.assertIn("unscoped missing evidence path",text)

if __name__=="__main__":
    unittest.main()
