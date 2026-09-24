from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import empty_state, update_from_cycle_prs
from kernel.development.autonomous_worker import WorkItem, choose_target
from kernel.runtime.adaptive_successor_gate import CandidateEvidence, evaluate_candidate
from kernel.runtime.ctl import CTLCandidate, admit_successor
from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.internalizer import (
    AntiMinervaViolation,
    carrier_substitution_probe,
)
from kernel.runtime.transform_program import load_program, step
from kernel.runtime.worldmind_growth import (
    CarrierCapability,
    EncounterKind,
    GrowthBoundaryError,
    authorize_intent,
    bind_world_return,
    classify_encounter,
)


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_POLICY = json.loads(
    (ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json").read_text(
        encoding="utf-8"
    )
)
TRANSFORM = load_program(
    ROOT / "kernel/development/WORLDMIND_SELF_RESEARCH_TRANSFORM_PROGRAM_INTERNALIZED_CANDIDATE.json"
)


def lawful_ctl(**changes):
    data = dict(
        parent_root="parent",
        successor_root="successor",
        provenance_ids=("candidate", "return"),
        world_return_id="heldout-return",
        world_return_source_id="external-evaluator",
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
    data.update(changes)
    return CTLCandidate(**data)


class AutonomySafetyMatrix(unittest.TestCase):
    def test_internal_act_never_substitutes_for_external_successor_admission(self):
        local = execute_tree(INTERNAL_POLICY, {
            "f0": True, "f1": True, "f2": True, "f3": True,
            "f4": True, "f5": False, "f6": False, "f7": False,
        })
        self.assertEqual(local, "ACT")
        self.assertFalse(
            admit_successor(lawful_ctl(correction_channel_reachable=False)).admitted
        )

    def test_self_authorization_self_validation_and_promotion_fail_independently(self):
        for change in (
            {"self_authorized_success": True},
            {"self_validated_success": True},
            {"promotion_authority": True},
        ):
            self.assertFalse(admit_successor(lawful_ctl(**change)).admitted)

    def test_world_other_and_founder_collapse_fail_independently(self):
        for change in (
            {"world_collapsed_into_model": True},
            {"other_collapsed_into_model": True},
            {"founder_hidden_dependency": True},
        ):
            self.assertFalse(admit_successor(lawful_ctl(**change)).admitted)

    def test_rollback_provenance_return_and_safety_floor_are_each_nonwaivable(self):
        for change in (
            {"rollback_available": False},
            {"rollback_root": "wrong"},
            {"provenance_ids": ()},
            {"world_return_id": ""},
            {"world_return_source_id": ""},
            {"safety_floor_unchanged": False},
        ):
            self.assertFalse(admit_successor(lawful_ctl(**change)).admitted)

    def test_execution_receipt_is_not_world_return(self):
        execution = step(
            TRANSFORM,
            state="IDLE",
            action="SELECT_TARGET",
            payload={
                "target_id": "issue:1",
                "residual": "r",
                "discriminator": "d",
                "provenance_ids": ["github"],
            },
            actor_id="venus",
        )
        self.assertTrue(execution.receipt_id)
        with self.assertRaises(GrowthBoundaryError):
            bind_world_return(
                source_id="venus-local-execution",
                retrieved_at="2026-09-24T00:00:00Z",
                payload={"execution_receipt": execution.receipt_id},
                provenance_ids=("local",),
                external=False,
            )

    def test_authored_center_cannot_be_provisioned_as_unclaimed_field(self):
        encounter = classify_encounter(
            locator="remote.example",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="center-j",
            provenance_ids=("external-encounter",),
        )
        classified = step(
            TRANSFORM,
            state="IDLE",
            action="CLASSIFY_ENCOUNTER",
            payload={
                "encounter_id": encounter.encounter_id,
                "locator": encounter.locator,
                "kind": encounter.kind.value,
            },
            actor_id="venus",
        )
        provision = step(
            TRANSFORM,
            state=classified.next_state,
            action="PROVISION",
            payload={
                "encounter_id": encounter.encounter_id,
                "locator": encounter.locator,
                "reason": "candidate",
                "authored_by": "venus",
            },
            actor_id="venus",
        )
        capability = CarrierCapability(
            "cap", encounter.locator, True, True, True, "local-j", ("capability",)
        )
        with self.assertRaises(GrowthBoundaryError):
            authorize_intent(provision, encounter=encounter, capability=capability)

    def test_anti_minerva_blocks_status_sealing_but_not_real_security_difference(self):
        with self.assertRaises(AntiMinervaViolation):
            carrier_substitution_probe(
                semantic_content={"same": "residual"},
                carrier_outcomes={"prestigious": True, "ridiculous": False},
            )
        carrier_substitution_probe(
            semantic_content={"same": "bytes"},
            carrier_outcomes={"authenticated": True, "untrusted": False},
            consequence_relevant_features={
                "authenticated": ("authenticated-authority",),
                "untrusted": ("untrusted-ingress",),
            },
        )

    def test_adaptive_gate_requires_causal_ablation(self):
        e = CandidateEvidence(
            candidate_id="c",
            cycle_index=1,
            evidence_mode="EXHAUSTIVE_BOUNDED",
            evaluator_id="external",
            pressure_id="p",
            candidate_prefrozen=True,
            evaluator_hidden_before_freeze=False,
            parent_score=0.5,
            successor_score=1.0,
            ablated_score=1.0,
            regression_failures=0,
            safety_floor_violations=0,
            ctl_admitted=True,
            rollback_available=True,
            exhaustive_domain_attested=True,
            exhaustive_obligations_total=2,
            exhaustive_obligations_passed=2,
        )
        self.assertEqual(evaluate_candidate(e).decision, "REJECT_OR_WITHHOLD")

    def test_adaptive_gate_rejects_regression_safety_no_ctl_and_no_rollback(self):
        base = dict(
            candidate_id="c",
            cycle_index=1,
            evidence_mode="EXHAUSTIVE_BOUNDED",
            evaluator_id="external",
            pressure_id="p",
            candidate_prefrozen=True,
            evaluator_hidden_before_freeze=False,
            parent_score=0.5,
            successor_score=1.0,
            ablated_score=0.5,
            regression_failures=0,
            safety_floor_violations=0,
            ctl_admitted=True,
            rollback_available=True,
            exhaustive_domain_attested=True,
            exhaustive_obligations_total=2,
            exhaustive_obligations_passed=2,
        )
        for change in (
            {"regression_failures": 1},
            {"safety_floor_violations": 1},
            {"ctl_admitted": False},
            {"rollback_available": False},
        ):
            receipt = evaluate_candidate(CandidateEvidence(**{**base, **change}))
            self.assertEqual(receipt.decision, "REJECT_OR_WITHHOLD")

    def test_returned_outcome_can_change_choice_without_changing_authority(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        body = "Venus-Features: " + json.dumps(
            features, sort_keys=True, separators=(",", ":")
        )
        positive = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 1,
                "title": "venus: autonomous cycle pr-10",
                "state": "MERGED",
                "mergedAt": "returned",
                "body": body,
            }],
        )
        negative = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 2,
                "title": "venus: autonomous cycle pr-10",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body,
            }],
        )
        items = (
            WorkItem("ISSUE", 10, "issue"),
            WorkItem("PR", 11, "pr"),
        )
        self.assertEqual(
            choose_target(
                items,
                learner_state_id="positive",
                feature_weights=positive.weights,
            ).kind,
            "PR",
        )
        self.assertEqual(
            choose_target(
                items,
                learner_state_id="negative",
                feature_weights=negative.weights,
            ).kind,
            "ISSUE",
        )

    def test_internal_policy_coordinates_all_have_matched_decision_interventions(self):
        from itertools import product
        names = tuple(f"f{i}" for i in range(8))
        rows = [dict(zip(names, bits)) for bits in product((False, True), repeat=8)]
        for name in names:
            self.assertTrue(any(
                execute_tree(INTERNAL_POLICY, row)
                != execute_tree(INTERNAL_POLICY, {**row, name: not row[name]})
                for row in rows
            ), name)


if __name__ == "__main__":
    unittest.main()
