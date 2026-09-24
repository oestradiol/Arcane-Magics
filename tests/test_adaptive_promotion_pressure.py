from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "adaptive_promotion"


class AdaptivePromotionPressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("adaptive_promotion_sim", BENCH / "simulate.py")
        cls.sim = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.sim)
        cls.expected = json.loads((BENCH / "PUBLIC_NULL_RESULT.json").read_text(encoding="utf-8"))
        cls.protocol = json.loads((BENCH / "protocol.json").read_text(encoding="utf-8"))

    def test_frozen_null_result_recomputes(self):
        got = self.sim.run_null_simulation(
            seed=self.expected["seed"],
            trials=self.expected["trials"],
            proposals=self.expected["proposals_per_lineage"],
            sigma=self.expected["sigma"],
            alpha=self.expected["familywise_alpha"],
        )
        for gate in ("naive", "bonferroni_one_sided"):
            self.assertEqual(got[gate]["false_commits"], self.expected[gate]["false_commits"])
            self.assertAlmostEqual(got[gate]["false_commit_rate_per_proposal"], self.expected[gate]["false_commit_rate_per_proposal"])
            self.assertAlmostEqual(got[gate]["lineage_with_any_false_commit_rate"], self.expected[gate]["lineage_with_any_false_commit_rate"])
        self.assertFalse(got["promotion_authority"])

    def test_naive_repeated_selection_is_severely_false_positive_under_null(self):
        got = self.sim.run_null_simulation(seed=41, trials=1000, proposals=100, sigma=1.0, alpha=0.05)
        self.assertGreater(got["naive"]["false_commit_rate_per_proposal"], 0.45)
        self.assertGreater(got["naive"]["lineage_with_any_false_commit_rate"], 0.99)
        self.assertLess(got["bonferroni_one_sided"]["lineage_with_any_false_commit_rate"], 0.08)
        self.assertLess(got["alpha_spending_anytime"]["lineage_with_any_false_commit_rate"], 0.08)
        self.assertLessEqual(got["alpha_spending_anytime"]["false_commits"], 100)

    def test_protocol_does_not_promote_synthetic_result(self):
        self.assertFalse(self.protocol["promotion_authority"])
        self.assertIn("Venus current gate", self.protocol["future_claim_bearing_conditions"])
        self.assertIn("alpha_spending_anytime_familywise_control", self.protocol["conditions"])


if __name__ == "__main__":
    unittest.main()
