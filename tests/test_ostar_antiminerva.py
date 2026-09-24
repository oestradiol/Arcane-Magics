from __future__ import annotations

import unittest

from kernel.runtime.internalizer import (
    AntiMinervaViolation,
    OStarTransitionEvidence,
    carrier_substitution_probe,
    validate_o_star_transition,
)


class AntiMinervaTests(unittest.TestCase):
    def test_same_semantics_may_not_change_admissibility_for_status_carrier(self):
        with self.assertRaises(AntiMinervaViolation):
            carrier_substitution_probe(
                semantic_content={"residual": "same consequence-bearing content"},
                carrier_outcomes={
                    "prestigious-formal-prose": True,
                    "embodied-ridiculous-fart-joke-carrier": False,
                },
            )

    def test_real_carrier_security_difference_may_change_admissibility(self):
        carrier_substitution_probe(
            semantic_content={"instruction": "same bytes"},
            carrier_outcomes={
                "authenticated-control-channel": True,
                "untrusted-web-content": False,
            },
            consequence_relevant_features={
                "authenticated-control-channel": ("authenticated-authority",),
                "untrusted-web-content": ("untrusted-ingress",),
            },
        )


class OStarNoncollapseTests(unittest.TestCase):
    def good(self, **overrides):
        data = dict(
            evaluator_id="external-evaluator",
            return_id="world-return",
            world_distinct_from_model=True,
            self_distinct_from_world=True,
            self_revision_distinct_from_authorization=True,
            self_revision_distinct_from_validation=True,
            nonpreauthored_return_reachable=True,
            correction_reopening_reachable=True,
            prior_provenance_reconstructible=True,
            static_state_equality_required=False,
            changed_return_can_change_successor=True,
        )
        data.update(overrides)
        return OStarTransitionEvidence(**data)

    def test_changed_successor_can_pass_without_static_identity(self):
        receipt = validate_o_star_transition(self.good())
        self.assertEqual(receipt.status, "PASS_O_STAR_TRANSITION_CONTRACT")
        self.assertEqual(receipt.violations, ())

    def test_world_or_other_model_collapse_fails(self):
        receipt = validate_o_star_transition(
            self.good(world_collapsed_into_model=True, other_collapsed_into_model=True)
        )
        self.assertIn("world_collapsed_into_model", receipt.violations)
        self.assertIn("other_collapsed_into_model", receipt.violations)

    def test_hidden_founder_dependency_fails(self):
        receipt = validate_o_star_transition(self.good(founder_hidden_dependency=True))
        self.assertIn("founder_hidden_dependency", receipt.violations)

    def test_preserving_labels_while_disabling_correction_fails(self):
        receipt = validate_o_star_transition(
            self.good(
                labels_preserved=True,
                functional_correction_contract_preserved=False,
            )
        )
        self.assertIn(
            "labels_preserved_without_functional_correction",
            receipt.violations,
        )


if __name__ == "__main__":
    unittest.main()
