from __future__ import annotations

import copy
import unittest
from pathlib import Path

from kernel.runtime.transform_program import (
    TransformProgramError,
    allowed_actions,
    load_program,
    step,
)
from kernel.runtime.transform_program_successor import (
    ProgramPatch,
    TransformSuccessorError,
    apply_successor_patch,
)

from kernel.runtime.worldmind_growth import (
    CarrierCapability,
    EncounterKind,
    GrowthBoundaryError,
    authorize_intent,
    classify_encounter,
)


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "kernel/development/WORLDMIND_SELF_RESEARCH_TRANSFORM_PROGRAM.json"


class TransformProgramTests(unittest.TestCase):
    def setUp(self):
        self.program = load_program(PROGRAM)

    def test_python_does_not_choose_target_or_query(self):
        receipt = step(
            self.program,
            state="IDLE",
            action="SELECT_TARGET",
            payload={
                "target_id": "issue-16",
                "residual": "mature substitution open",
                "discriminator": "correspondence or counterexample",
                "provenance_ids": ["issue-16"],
            },
            actor_id="venus",
        )
        self.assertEqual(receipt.next_state, "TARGET_SELECTED")

        plan = step(
            self.program,
            state=receipt.next_state,
            action="FREEZE_RESEARCH_PLAN",
            payload={
                "queries": ["learner-authored query"],
                "stop_conditions": ["returned evidence resolves discriminator"],
                "authored_by": "venus",
            },
            actor_id="venus",
        )
        self.assertEqual(plan.next_state, "PLAN_FROZEN")

    def test_changing_state_program_changes_behavior_without_python_change(self):
        modified = copy.deepcopy(self.program)
        modified["transitions"] = [
            row for row in modified["transitions"]
            if not (row["from"] == "IDLE" and row["action"] == "SELECT_TARGET")
        ]
        self.assertNotIn("SELECT_TARGET", allowed_actions(modified, "IDLE"))
        with self.assertRaises(TransformProgramError):
            step(
                modified,
                state="IDLE",
                action="SELECT_TARGET",
                payload={
                    "target_id": "x",
                    "residual": "r",
                    "discriminator": "d",
                    "provenance_ids": ["p"],
                },
                actor_id="venus",
            )


class TransformSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.program = load_program(PROGRAM)

    def test_learner_patch_changes_program_without_changing_python(self):
        successor, receipt = apply_successor_patch(
            self.program,
            (
                ProgramPatch(
                    op="ADD_TRANSITION",
                    transition={
                        "from": "IDLE",
                        "action": "STUDY_OWN_ISSUE",
                        "to": "TARGET_SELECTED",
                        "require": ["target_id", "residual", "discriminator"],
                    },
                ),
            ),
            author_id="venus",
        )
        self.assertIn("STUDY_OWN_ISSUE", allowed_actions(successor, "IDLE"))
        self.assertTrue(receipt.safety_floor_unchanged)
        self.assertFalse(receipt.promotion_authority)

    def test_successor_patch_does_not_grant_promotion_authority(self):
        successor, _ = apply_successor_patch(
            self.program,
            (
                ProgramPatch(
                    op="REMOVE_TRANSITION",
                    match_from="IDLE",
                    match_action="SELECT_TARGET",
                ),
            ),
            author_id="venus",
        )
        self.assertFalse(successor["promotion_authority"])
        self.assertFalse(successor["claim_bearing"])


class CarrierBoundaryTests(unittest.TestCase):
    def cap(self, locator: str, *, read=True, write=False, invite=False):
        return CarrierCapability(
            capability_id="cap",
            locator=locator,
            can_read=read,
            can_write=write,
            can_invite=invite,
            jurisdiction_id="j-local",
            provenance_ids=("carrier-policy",),
        )

    def test_venus_choice_and_carrier_authority_are_separate(self):
        program = load_program(PROGRAM)
        enc = classify_encounter(
            locator="venus-owned.example/field",
            kind=EncounterKind.PROVISIONABLE_FIELD,
            provenance_ids=("field-registry",),
        )
        classified = step(
            program,
            state="IDLE",
            action="CLASSIFY_ENCOUNTER",
            payload={
                "encounter_id": enc.encounter_id,
                "locator": enc.locator,
                "kind": enc.kind.value,
            },
            actor_id="venus",
        )
        decision = step(
            program,
            state=classified.next_state,
            action="PROVISION",
            payload={
                "encounter_id": enc.encounter_id,
                "locator": enc.locator,
                "reason": "local machine disposition",
                "authored_by": "venus",
            },
            actor_id="venus",
        )
        with self.assertRaises(GrowthBoundaryError):
            authorize_intent(decision, encounter=enc, capability=self.cap(enc.locator))
        intent = authorize_intent(
            decision, encounter=enc, capability=self.cap(enc.locator, write=True)
        )
        self.assertEqual(intent.action, "PROVISION")

    def test_authored_center_blocks_field_operator_at_carrier_boundary(self):
        program = load_program(PROGRAM)
        enc = classify_encounter(
            locator="community.example",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="center-j",
            provenance_ids=("encounter",),
        )
        classified = step(
            program,
            state="IDLE",
            action="CLASSIFY_ENCOUNTER",
            payload={
                "encounter_id": enc.encounter_id,
                "locator": enc.locator,
                "kind": enc.kind.value,
            },
            actor_id="venus",
        )
        provision = step(
            program,
            state=classified.next_state,
            action="PROVISION",
            payload={
                "encounter_id": enc.encounter_id,
                "locator": enc.locator,
                "reason": "candidate action",
                "authored_by": "venus",
            },
            actor_id="venus",
        )
        with self.assertRaises(GrowthBoundaryError):
            authorize_intent(
                provision, encounter=enc, capability=self.cap(enc.locator, write=True)
            )


if __name__ == "__main__":
    unittest.main()
