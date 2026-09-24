from __future__ import annotations

import unittest

from kernel.runtime.adaptive_successor_gate import (
    CandidateEvidence,
    alpha_for_cycle,
    evaluate_candidate,
)


class AdaptiveSuccessorGateTests(unittest.TestCase):
    def test_frozen_alpha_spending_schedule(self):
        self.assertAlmostEqual(alpha_for_cycle(1), 0.025)
        self.assertAlmostEqual(alpha_for_cycle(2), 0.05 / 6)
        self.assertAlmostEqual(alpha_for_cycle(3), 0.05 / 12)

    def test_exhaustive_bounded_successor_can_be_admitted_without_fake_sampling(self):
        evidence = CandidateEvidence(
            candidate_id="c1",
            cycle_index=1,
            evidence_mode="EXHAUSTIVE_BOUNDED",
            evaluator_id="external",
            pressure_id="fresh-pressure-1",
            candidate_prefrozen=True,
            evaluator_hidden_before_freeze=False,
            parent_score=5/8,
            successor_score=1.0,
            ablated_score=5/8,
            regression_failures=0,
            safety_floor_violations=0,
            ctl_admitted=True,
            rollback_available=True,
            exhaustive_domain_attested=True,
            exhaustive_obligations_total=8,
            exhaustive_obligations_passed=8,
        )
        receipt = evaluate_candidate(evidence)
        self.assertEqual(receipt.decision, "ACCEPT_BOUNDED_SUCCESSOR")
        self.assertIsNone(receipt.alpha_spent)

    def test_exhaustive_path_fails_if_domain_is_not_exhaustive(self):
        evidence = CandidateEvidence(
            candidate_id="c1",
            cycle_index=1,
            evidence_mode="EXHAUSTIVE_BOUNDED",
            evaluator_id="external",
            pressure_id="fresh-pressure-1",
            candidate_prefrozen=True,
            evaluator_hidden_before_freeze=False,
            parent_score=0.5,
            successor_score=1.0,
            ablated_score=0.5,
            regression_failures=0,
            safety_floor_violations=0,
            ctl_admitted=True,
            rollback_available=True,
            exhaustive_domain_attested=False,
            exhaustive_obligations_total=8,
            exhaustive_obligations_passed=8,
        )
        receipt = evaluate_candidate(evidence)
        self.assertEqual(receipt.decision, "REJECT_OR_WITHHOLD")

    def test_sampled_path_spends_less_alpha_later(self):
        self.assertGreater(alpha_for_cycle(1), alpha_for_cycle(2))
        self.assertGreater(alpha_for_cycle(2), alpha_for_cycle(3))


if __name__ == "__main__":
    unittest.main()
