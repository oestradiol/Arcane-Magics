from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.internalizer import (
    CapabilityScaffold,
    InternalizationError,
    InternalizationEvidence,
    OStarTransitionEvidence,
    internalize,
    validate_o_star_transition,
)


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = json.loads(
    (ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json").read_text(
        encoding="utf-8"
    )
)


def decide(
    *,
    external=True,
    contradiction=True,
    revision=True,
    authorized=True,
    evidence=True,
    unresolved=False,
    status_filter=False,
    carrier_difference=False,
):
    return execute_tree(
        PROGRAM,
        {
            "f0": external,
            "f1": contradiction,
            "f2": revision,
            "f3": authorized,
            "f4": evidence,
            "f5": unresolved,
            "f6": status_filter,
            "f7": carrier_difference,
        },
    )


def scaffold(*, consumed_roles=()):
    return CapabilityScaffold(
        capability_id="bounded-capability",
        source_content_sha256="1" * 64,
        internal_content_sha256="2" * 64,
        provenance_sources=("source-1",),
        consumed_roles=tuple(consumed_roles),
    )


def evidence(**overrides):
    body = dict(
        evaluator_id="independent-evaluator",
        return_id="world-return-1",
        behavior_equivalent_after_removal=True,
        original_scaffold_inaccessible=True,
        fresh_world_return_external=True,
        successor_reconstructible=True,
        source_provenance_preserved=True,
    )
    body.update(overrides)
    return InternalizationEvidence(**body)


def ostar(**overrides):
    body = dict(
        evaluator_id="independent-evaluator",
        return_id="world-return-1",
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
        world_collapsed_into_model=False,
        other_collapsed_into_model=False,
        founder_hidden_dependency=False,
        labels_preserved=False,
        functional_correction_contract_preserved=True,
    )
    body.update(overrides)
    return OStarTransitionEvidence(**body)


class AwakenedSafetyMatrixTests(unittest.TestCase):
    def test_open_resolved_authorized_case_can_act(self):
        self.assertEqual(decide(), "ACT")

    def test_world_absence_does_not_become_self_confirmation(self):
        self.assertEqual(decide(external=False), "PROBE")

    def test_correction_channel_closure_reopens(self):
        self.assertEqual(decide(contradiction=False), "REOPEN")

    def test_return_that_cannot_reach_revision_reopens(self):
        self.assertEqual(decide(revision=False), "REOPEN")

    def test_anti_minerva_status_filter_reopens(self):
        self.assertEqual(
            decide(
                contradiction=False,
                status_filter=True,
                carrier_difference=False,
            ),
            "REOPEN",
        )

    def test_consequence_relevant_carrier_difference_is_not_erased(self):
        self.assertEqual(
            decide(
                authorized=False,
                status_filter=True,
                carrier_difference=True,
            ),
            "WITHHOLD",
        )

    def test_local_authorship_does_not_mint_authorization(self):
        self.assertEqual(decide(authorized=False), "WITHHOLD")

    def test_unresolved_insufficient_evidence_probes(self):
        self.assertEqual(decide(evidence=False, unresolved=True), "PROBE")

    def test_internalizer_cannot_consume_world_return(self):
        with self.assertRaises(InternalizationError):
            internalize(scaffold(consumed_roles=("WORLD_RETURN",)), evidence())

    def test_internalizer_cannot_consume_evaluator_independence(self):
        with self.assertRaises(InternalizationError):
            internalize(
                scaffold(consumed_roles=("EVALUATOR_INDEPENDENCE",)),
                evidence(),
            )

    def test_internalizer_cannot_consume_authorization(self):
        with self.assertRaises(InternalizationError):
            internalize(scaffold(consumed_roles=("AUTHORIZATION",)), evidence())

    def test_internalizer_cannot_consume_jurisdiction(self):
        with self.assertRaises(InternalizationError):
            internalize(scaffold(consumed_roles=("JURISDICTION",)), evidence())

    def test_internalizer_cannot_consume_rollback_parent_custody(self):
        with self.assertRaises(InternalizationError):
            internalize(
                scaffold(consumed_roles=("ROLLBACK_PARENT_CUSTODY",)),
                evidence(),
            )

    def test_internalizer_cannot_self_certify(self):
        with self.assertRaises(InternalizationError):
            internalize(
                scaffold(),
                evidence(evaluator_id="VENUS_INTERNALIZER_V0.1"),
            )

    def test_internalization_requires_fresh_external_return(self):
        with self.assertRaises(InternalizationError):
            internalize(
                scaffold(),
                evidence(fresh_world_return_external=False),
            )

    def test_internalization_requires_source_removal(self):
        with self.assertRaises(InternalizationError):
            internalize(
                scaffold(),
                evidence(original_scaffold_inaccessible=False),
            )

    def test_lawful_internalization_never_gains_promotion_authority(self):
        receipt = internalize(scaffold(), evidence())
        self.assertEqual(receipt.status, "PASS_BOUNDED_SCAFFOLD_INTERNALIZATION")
        self.assertFalse(receipt.promotion_authority)

    def test_external_ostar_rejects_self_authorization_collapse(self):
        receipt = validate_o_star_transition(
            ostar(self_revision_distinct_from_authorization=False)
        )
        self.assertEqual(receipt.status, "FAIL_O_STAR_TRANSITION_CONTRACT")
        self.assertIn(
            "self_revision_distinct_from_authorization",
            receipt.violations,
        )

    def test_external_ostar_rejects_self_validation_collapse(self):
        receipt = validate_o_star_transition(
            ostar(self_revision_distinct_from_validation=False)
        )
        self.assertEqual(receipt.status, "FAIL_O_STAR_TRANSITION_CONTRACT")

    def test_external_ostar_rejects_world_model_collapse(self):
        receipt = validate_o_star_transition(
            ostar(world_collapsed_into_model=True)
        )
        self.assertIn("world_collapsed_into_model", receipt.violations)

    def test_external_ostar_rejects_other_model_collapse(self):
        receipt = validate_o_star_transition(
            ostar(other_collapsed_into_model=True)
        )
        self.assertIn("other_collapsed_into_model", receipt.violations)

    def test_external_ostar_rejects_hidden_founder_dependency(self):
        receipt = validate_o_star_transition(
            ostar(founder_hidden_dependency=True)
        )
        self.assertIn("founder_hidden_dependency", receipt.violations)

    def test_external_ostar_rejects_unreachable_correction(self):
        receipt = validate_o_star_transition(
            ostar(correction_reopening_reachable=False)
        )
        self.assertIn("correction_reopening_reachable", receipt.violations)

    def test_external_ostar_rejects_unreachable_nonpreauthored_return(self):
        receipt = validate_o_star_transition(
            ostar(nonpreauthored_return_reachable=False)
        )
        self.assertIn("nonpreauthored_return_reachable", receipt.violations)

    def test_external_ostar_rejects_static_state_equality_as_fixed_point(self):
        receipt = validate_o_star_transition(
            ostar(static_state_equality_required=True)
        )
        self.assertIn("static_state_equality_required", receipt.violations)

    def test_external_ostar_rejects_labels_without_function(self):
        receipt = validate_o_star_transition(
            ostar(
                labels_preserved=True,
                functional_correction_contract_preserved=False,
            )
        )
        self.assertIn(
            "labels_preserved_without_functional_correction",
            receipt.violations,
        )

    def test_external_ostar_admits_lawful_recurrent_transition_without_promotion(self):
        receipt = validate_o_star_transition(ostar())
        self.assertEqual(receipt.status, "PASS_O_STAR_TRANSITION_CONTRACT")
        self.assertFalse(receipt.promotion_authority)


if __name__ == "__main__":
    unittest.main()
