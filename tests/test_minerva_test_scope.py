from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MinervaTestScopeTests(unittest.TestCase):
    def test_exclusions_are_explicit_cross_register_jurisdiction(self):
        scope=json.loads((ROOT/"kernel/development/MINERVA_TEST_SCOPE.json").read_text(encoding="utf-8"))
        rows=scope["excluded"]
        self.assertEqual(
            {r["path"] for r in rows},
            {"tests/test_historical_regressions.py","tests/test_edu17r1_incidence_substrate.py"},
        )
        for row in rows:
            self.assertTrue((ROOT/row["path"]).is_file())
            self.assertTrue(row["authority"])
            self.assertTrue(row["reason"])

    def test_runner_auto_discovers_test_files(self):
        text=(ROOT/"scripts/run_minerva_tests.py").read_text(encoding="utf-8")
        self.assertIn('glob("test_*.py")',text)
        self.assertNotIn("test_vm_internalization_phase_plan.py",text)

if __name__=="__main__":
    unittest.main()
