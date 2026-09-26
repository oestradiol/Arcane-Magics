from __future__ import annotations

from pathlib import Path
import unittest

from kernel.development.return_credit_curriculum import run


ROOT = Path(__file__).resolve().parents[1]


class ReturnCreditCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.result = run(
            ROOT / "kernel/development/RETURN_CREDIT_ASSIGNMENT_PREFREEZE.json",
            ROOT / "kernel/development/RETURN_CREDIT_ASSIGNMENT_DIDACTIC_CASES.json",
        )

    def test_candidate_passes_prefrozen_abstraction_and_causal_use_checks(self):
        self.assertEqual(self.result["status"], "PASS_BOUNDED_RETURN_CREDIT_B1_B2")
        self.assertTrue(self.result["b1_pass"])
        self.assertTrue(self.result["b2_pass"])
        self.assertTrue(all(self.result["b1_checks"].values()))
        self.assertTrue(all(self.result["b2_checks"].values()))

    def test_counterfactual_ablation_is_localized(self):
        self.assertTrue(self.result["b2_checks"]["counterfactual_locality"])
        self.assertEqual(
            self.result["counterfactual_ledger"]["cA|tX"],
            {"NEG": 1, "POS": 1},
        )

    def test_bounded_pass_does_not_open_internalization_or_authority(self):
        self.assertFalse(self.candidate["internalization_claim"])
        self.assertFalse(self.result["internalization_claim"])
        self.assertFalse(self.result["independent_evaluation"])
        self.assertFalse(self.result["promotion_authority"])
        self.assertFalse(self.result["truth_authority"])


if __name__ == "__main__":
    unittest.main()
