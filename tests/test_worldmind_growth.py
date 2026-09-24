from __future__ import annotations

import copy
import unittest
from pathlib import Path

from kernel.development.ownership_audit import (
    CausalReturn,
    FunctionOwnership,
    select_internalization_target,
)

from kernel.runtime.transform_program import (
    TransformProgramError,
    allowed_actions,
    load_program,
    step,
)
from kernel.runtime.transform_program_repair_search import (
    BehavioralTrace,
    search_missing_transition,
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


class OwnershipAuditTests(unittest.TestCase):
    def test_multiple_host_scaffolds_withhold_without_returned_discriminator(self):
        funcs = (
            FunctionOwnership("a", "HOST_SCAFFOLD", True, False, "p:a"),
            FunctionOwnership("b", "HOST_SCAFFOLD", True, False, "p:b"),
            FunctionOwnership("world", "EXTERNAL_WORLD_INTERFACE", False, True, "p:w"),
        )
        out = select_internalization_target(funcs)
        self.assertEqual(out.status, "WITHHOLD_MULTIPLE_INTERNALIZATION_TARGETS")
        self.assertIsNone(out.selected_target_id)

    def test_returned_causal_evidence_selects_internalization_target(self):
        funcs = (
            FunctionOwnership("a", "HOST_SCAFFOLD", True, False, "p:a"),
            FunctionOwnership("b", "HOST_SCAFFOLD", True, False, "p:b"),
        )
        returns = (
            CausalReturn("a", True, 1.0, "r:a"),
            CausalReturn("b", False, 0.0, "r:b"),
        )
        out = select_internalization_target(funcs, causal_returns=returns)
        self.assertEqual(out.status, "SELECTED_BY_RETURNED_CAUSAL_EVIDENCE")
        self.assertEqual(out.selected_target_id, "a")
        self.assertFalse(out.promotion_authority)


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


class TransformRepairSearchTests(unittest.TestCase):
    def setUp(self):
        self.program = load_program(PROGRAM)
        self.ablated = copy.deepcopy(self.program)
        self.ablated["transitions"] = [
            row for row in self.ablated["transitions"]
            if not (row["from"] == "IDLE" and row["action"] == "SELECT_TARGET")
        ]

    def test_returned_behavior_reconstructs_missing_transition_without_policy_rule(self):
        good = {
            "target_id": "opaque-target",
            "residual": "opaque-residual",
            "discriminator": "opaque-discriminator",
            "provenance_ids": ["world-return"],
        }
        traces = [
            BehavioralTrace(
                "ok", "IDLE", "SELECT_TARGET", good, True, "TARGET_SELECTED", "eval:ok"
            ),
        ]
        for field in tuple(good):
            bad = dict(good)
            bad.pop(field)
            traces.append(
                BehavioralTrace(
                    "missing-" + field,
                    "IDLE",
                    "SELECT_TARGET",
                    bad,
                    False,
                    None,
                    "eval:missing:" + field,
                )
            )

        out = search_missing_transition(self.ablated, traces)
        self.assertEqual(out.status, "UNIQUE_MINIMAL_PATCH")
        transition = out.selected_patch["transition"]
        self.assertEqual(transition["from"], "IDLE")
        self.assertEqual(transition["action"], "SELECT_TARGET")
        self.assertEqual(transition["to"], "TARGET_SELECTED")
        self.assertEqual(set(transition["require"]), set(good))
        self.assertFalse(out.promotion_authority)

    def test_ambiguous_return_yields_withhold(self):
        traces = (
            BehavioralTrace(
                "ok",
                "IDLE",
                "SELECT_TARGET",
                {"x": 1},
                True,
                None,
                "eval:underspecified",
            ),
        )
        out = search_missing_transition(self.ablated, traces)
        self.assertEqual(out.status, "WITHHOLD_AMBIGUOUS_MINIMAL_PATCHES")


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
