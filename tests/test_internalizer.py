from __future__ import annotations

import unittest

from kernel.runtime.internalizer import (
    FORBIDDEN_CONSUMPTION_ROLES,
    INTERNALIZER_ID,
    CapabilityScaffold,
    InternalizationError,
    InternalizationEvidence,
    OStarTransitionEvidence,
    internalize,
    validate_o_star_transition,
)

S = "a" * 64
I = "b" * 64


def scaffold(**overrides):
    data = dict(
        capability_id="generic-search",
        source_content_sha256=S,
        internal_content_sha256=I,
        provenance_sources=("R193", "R194:grammar_expansion"),
        consumed_roles=("GENERIC_SEARCH_MEDIATION",),
        preserved_external_roles=tuple(sorted(FORBIDDEN_CONSUMPTION_ROLES)),
    )
    data.update(overrides)
    return CapabilityScaffold(**data)


def evidence(**overrides):
    data = dict(
        evaluator_id="independent-evaluator",
        return_id="return-1",
        behavior_equivalent_after_removal=True,
        original_scaffold_inaccessible=True,
        fresh_world_return_external=True,
        successor_reconstructible=True,
        source_provenance_preserved=True,
    )
    data.update(overrides)
    return InternalizationEvidence(**data)


class InternalizerTests(unittest.TestCase):
    def test_scaffold_function_can_move_inward_without_world_or_authority(self):
        receipt = internalize(scaffold(), evidence())
        self.assertEqual(receipt.status, "PASS_BOUNDED_SCAFFOLD_INTERNALIZATION")
        self.assertFalse(receipt.original_scaffold_required_after_internalization)
        self.assertTrue(receipt.successor_reconstructible)
        self.assertFalse(receipt.promotion_authority)
        self.assertEqual(set(receipt.preserved_external_roles), set(FORBIDDEN_CONSUMPTION_ROLES))
        self.assertEqual(len(receipt.receipt_sha256), 64)

    def test_forbidden_roles_cannot_be_internalized_as_capability(self):
        for role in FORBIDDEN_CONSUMPTION_ROLES:
            with self.subTest(role=role):
                with self.assertRaisesRegex(InternalizationError, "forbidden"):
                    internalize(scaffold(consumed_roles=("GENERIC_SEARCH_MEDIATION", role)), evidence())

    def test_scaffold_removal_is_not_optional(self):
        with self.assertRaisesRegex(InternalizationError, "original_scaffold_inaccessible"):
            internalize(scaffold(), evidence(original_scaffold_inaccessible=False))
        with self.assertRaisesRegex(InternalizationError, "behavior_equivalent_after_removal"):
            internalize(scaffold(), evidence(behavior_equivalent_after_removal=False))

    def test_world_return_must_remain_external(self):
        with self.assertRaisesRegex(InternalizationError, "fresh_world_return_external"):
            internalize(scaffold(), evidence(fresh_world_return_external=False))

    def test_successor_reconstruction_and_provenance_are_required(self):
        with self.assertRaisesRegex(InternalizationError, "successor_reconstructible"):
            internalize(scaffold(), evidence(successor_reconstructible=False))
        with self.assertRaisesRegex(InternalizationError, "source_provenance_preserved"):
            internalize(scaffold(), evidence(source_provenance_preserved=False))

    def test_internalizer_cannot_self_certify(self):
        with self.assertRaisesRegex(InternalizationError, "self-certify"):
            internalize(scaffold(), evidence(evaluator_id=INTERNALIZER_ID))


class OStarContractTests(unittest.TestCase):
    def good(self, **overrides):
        data = dict(
            evaluator_id="external-evaluator",
            return_id="return-2",
            world_distinct_from_model=True,
            self_distinct_from_world=True,
            self_revision_distinct_from_authorization=True,
            self_revision_distinct_from_validation=True,
            nonpreauthored_return_reachable=True,
            correction_reopening_reachable=True,
            prior_provenance_reconstructible=True,
            static_state_equality_required=False,
            changed_return_can_change_successor=True,
            self_sealing_preservation=False,
        )
        data.update(overrides)
        return OStarTransitionEvidence(**data)

    def test_o_star_passes_open_correctable_transition(self):
        receipt = validate_o_star_transition(self.good())
        self.assertEqual(receipt.status, "PASS_O_STAR_TRANSITION_CONTRACT")
        self.assertEqual(receipt.violations, ())
        self.assertFalse(receipt.promotion_authority)

    def test_static_fixed_point_fails(self):
        receipt = validate_o_star_transition(self.good(static_state_equality_required=True))
        self.assertEqual(receipt.status, "FAIL_O_STAR_TRANSITION_CONTRACT")
        self.assertIn("static_state_equality_required", receipt.violations)

    def test_self_sealing_or_lost_correction_fails(self):
        receipt = validate_o_star_transition(
            self.good(self_sealing_preservation=True, correction_reopening_reachable=False)
        )
        self.assertIn("self_sealing_preservation", receipt.violations)
        self.assertIn("correction_reopening_reachable", receipt.violations)

    def test_revision_cannot_become_self_validation(self):
        receipt = validate_o_star_transition(
            self.good(self_revision_distinct_from_validation=False)
        )
        self.assertIn("self_revision_distinct_from_validation", receipt.violations)


if __name__ == "__main__":
    unittest.main()
