from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "evaluation" / "plan_paired_power.py"


def load_module():
    spec = importlib.util.spec_from_file_location("paired_power", PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PairedPowerPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_power_increases_with_stronger_conditional_win_probability(self):
        weak = self.mod.power_for_discordant_pairs(40, win_probability=0.60, alpha=0.025)
        strong = self.mod.power_for_discordant_pairs(40, win_probability=0.80, alpha=0.025)
        self.assertGreater(strong, weak)

    def test_planner_requires_prospective_assumptions(self):
        with self.assertRaises(ValueError):
            self.mod.plan(
                win_probability=0.50,
                discordance_rate=0.2,
                familywise_alpha=0.05,
                target_power=0.8,
            )
        with self.assertRaises(ValueError):
            self.mod.plan(
                win_probability=0.7,
                discordance_rate=0.0,
                familywise_alpha=0.05,
                target_power=0.8,
            )

    def test_plan_returns_nonpromotional_case_requirement(self):
        out = self.mod.plan(
            win_probability=0.75,
            discordance_rate=0.25,
            familywise_alpha=0.05,
            target_power=0.8,
        )
        self.assertGreater(out["minimum_expected_discordant_pairs"], 0)
        self.assertGreaterEqual(
            out["minimum_total_cases_at_expected_discordance"],
            out["minimum_expected_discordant_pairs"],
        )
        self.assertFalse(out["promotion_authority"])
        self.assertAlmostEqual(
            out["assumptions"]["per_claim_conservative_alpha"], 0.025
        )


if __name__ == "__main__":
    unittest.main()
