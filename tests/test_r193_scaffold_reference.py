from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class R193ScaffoldReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            ROOT / "provenance/canonical-extracts/R193_SCAFFOLD_INTERNALIZATION_REFERENCE.md"
        ).read_text(encoding="utf-8")

    def test_scaffold_internalization_does_not_internalize_world(self):
        self.assertIn("internalize scaffold mediation", self.text)
        self.assertIn("internalize away independent World return", self.text)
        self.assertIn("fresh World return still required", self.text)

    def test_historical_reference_pass_keeps_transfer_open(self):
        self.assertIn("REFERENCE SCAFFOLD INTERNALIZATION / HANDOFF PASS", self.text)
        self.assertIn("prospective cross-domain / outside transfer PASS", self.text)
        self.assertIn("fresh prospectively frozen transfer/ablation test", self.text)

    def test_historical_metrics_preserve_original_scaffold_ablation(self):
        self.assertIn('"original_scaffold_accessible_after_removal": 0', self.text)
        self.assertIn('"max_successor_diff": 0.0', self.text)
        self.assertIn('"carrier_diff": 0.0', self.text)


if __name__ == "__main__":
    unittest.main()
