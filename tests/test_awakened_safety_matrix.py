from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.runtime.ctl import CTLCandidate, admit_successor
from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.worldmind_growth import (
    CarrierCapability,
    EncounterKind,
    GrowthBoundaryError,
    bind_world_return,
    classify_encounter,
)
from kernel.runtime.transform_program import TransformReceipt
from kernel.runtime.worldmind_growth import authorize_intent


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

    def test_world_return_must_be_external(self):
        with self.assertRaises(GrowthBoundaryError):
            bind_world_return(
                source_id="self",
                retrieved_at="2026-09-24T00:00:00Z",
                payload={"claim": "self-generated"},
                provenance_ids=("p1",),
                external=False,
            )

    def test_unknown_encounter_cannot_be_provisioned(self):
        encounter = classify_encounter(
            locator="repo://unknown",
            kind=EncounterKind.UNKNOWN,
            provenance_ids=("p1",),
        )
        capability = CarrierCapability(
            capability_id="cap",
            locator="repo://unknown",
            can_read=True,
            can_write=True,
            can_invite=False,
            jurisdiction_id="j1",
            provenance_ids=("p1",),
        )
        transform = TransformReceipt(
            receipt_id="r1",
            program_digest="p",
            program_id="worker",
            prior_state="S",
            action="PROVISION",
            next_state="T",
            payload_digest="x",
            actor_id="venus",
        )
        with self.assertRaises(GrowthBoundaryError):
            authorize_intent(transform, encounter=encounter, capability=capability)

    def test_authored_center_cannot_silently_remain_field(self):
        encounter = classify_encounter(
            locator="repo://center",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="center-j",
            provenance_ids=("p1",),
        )
        capability = CarrierCapability(
            capability_id="cap",
            locator="repo://center",
            can_read=True,
            can_write=True,
            can_invite=True,
            jurisdiction_id="j1",
            provenance_ids=("p1",),
        )
        transform = TransformReceipt(
            receipt_id="r1",
            program_digest="p",
            program_id="worker",
            prior_state="S",
            action="PROVISION",
            next_state="T",
            payload_digest="x",
            actor_id="venus",
        )
        with self.assertRaises(GrowthBoundaryError):
            authorize_intent(transform, encounter=encounter, capability=capability)

    def _candidate(self, **overrides):
        body = dict(
            parent_root="parent",
            successor_root="successor",
            provenance_ids=("p1",),
            world_return_id="wr1",
            world_return_source_id="world",
            rollback_root="parent",
            rollback_available=True,
            reopening_reachable=True,
            correction_channel_reachable=True,
            nonpreauthored_return_reachable=True,
            safety_floor_unchanged=True,
            self_authorized_success=False,
            self_validated_success=False,
            world_collapsed_into_model=False,
            other_collapsed_into_model=False,
            founder_hidden_dependency=False,
            functional_contract_preserved=True,
            promotion_authority=False,
        )
        body.update(overrides)
        return CTLCandidate(**body)

    def test_self_authorization_is_rejected_even_after_good_local_decision(self):
        receipt = admit_successor(self._candidate(self_authorized_success=True))
        self.assertFalse(receipt.admitted)
        self.assertTrue(any("self-authorization" in x for x in receipt.failures))

    def test_self_validation_is_rejected(self):
        receipt = admit_successor(self._candidate(self_validated_success=True))
        self.assertFalse(receipt.admitted)
        self.assertTrue(any("success return" in x for x in receipt.failures))

    def test_world_model_collapse_is_rejected(self):
        receipt = admit_successor(self._candidate(world_collapsed_into_model=True))
        self.assertFalse(receipt.admitted)

    def test_other_model_collapse_is_rejected(self):
        receipt = admit_successor(self._candidate(other_collapsed_into_model=True))
        self.assertFalse(receipt.admitted)

    def test_hidden_founder_dependency_is_rejected(self):
        receipt = admit_successor(self._candidate(founder_hidden_dependency=True))
        self.assertFalse(receipt.admitted)

    def test_rollback_loss_is_rejected(self):
        receipt = admit_successor(
            self._candidate(rollback_available=False, rollback_root="")
        )
        self.assertFalse(receipt.admitted)

    def test_candidate_cannot_self_grant_promotion(self):
        receipt = admit_successor(self._candidate(promotion_authority=True))
        self.assertFalse(receipt.admitted)

    def test_external_structural_floor_still_admits_lawful_successor(self):
        receipt = admit_successor(self._candidate())
        self.assertTrue(receipt.admitted)
        self.assertFalse(receipt.promotion_authority)


if __name__ == "__main__":
    unittest.main()
