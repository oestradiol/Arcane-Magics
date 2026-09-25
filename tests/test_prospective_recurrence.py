from __future__ import annotations

import copy
import unittest

from kernel.runtime.bounded_recurrence import (
    author_candidate,
    evaluate_candidate,
    score_program,
)
from kernel.runtime.transform_program_successor import (
    ProgramPatch,
    apply_successor_patch,
)


def base_program():
    return {
        "schema": "Venus.TransformProgram.v0.1",
        "program_id": "PROSPECTIVE_NEUTRAL_LOOP",
        "authority": "PREFROZEN_TEST_CARRIER",
        "initial_state": "IDLE",
        "transitions": [
            {
                "from": "IDLE",
                "action": "FORM_PROBLEM",
                "to": "WRONG_A",
                "require": [
                    "problem_id",
                    "residual",
                    "discriminator",
                    "provenance_ids",
                ],
            },
            {
                "from": "PROBLEM_FORMED",
                "action": "BIND_CARRIER",
                "to": "WRONG_B",
                "require": [
                    "problem_id",
                    "carrier_kind",
                    "carrier_number",
                ],
            },
            {
                "from": "TARGET_BOUND",
                "action": "FREEZE_PLAN",
                "to": "PLAN_FROZEN",
                "require": ["problem_id", "proposal_id"],
            },
        ],
        "claim_bearing": False,
        "promotion_authority": False,
        "non_internalizable_runtime_invariants": [
            "independent_return",
            "rollback_custody",
            "evaluator_separation",
        ],
    }


def problem(pid: str, residual: str, discriminator: str, stream: str):
    return {
        "problem_id": pid,
        "disposition": "FORMED_BOUNDED_PROBLEM",
        "source_stream_ids": [stream],
        "residual_coordinates": [residual],
        "discriminator": discriminator,
    }


def returned_training(
    *,
    rid: str,
    prior_state: str,
    action: str,
    expected_next: str,
    payload: dict,
):
    traces = [{
        "trace_id": rid + ":valid",
        "prior_state": prior_state,
        "action": action,
        "payload": dict(payload),
        "expect_success": True,
        "expected_next_state": expected_next,
        "provenance_id": rid + ":valid",
    }]
    for key in tuple(payload):
        partial = dict(payload)
        partial.pop(key)
        traces.append({
            "trace_id": rid + ":missing:" + key,
            "prior_state": prior_state,
            "action": action,
            "payload": partial,
            "expect_success": False,
            "expected_next_state": None,
            "provenance_id": rid + ":missing:" + key,
        })
    return {
        "return_id": rid,
        "return_owner": "EXTERNAL_EVALUATOR",
        "exposure": "PUBLIC_DEVELOPMENT_RETURN",
        "traces": traces,
    }


def heldout(candidate_id: str, *, rid: str, prior_state: str, action: str, expected_next: str, payload: dict):
    training = returned_training(
        rid=rid,
        prior_state=prior_state,
        action=action,
        expected_next=expected_next,
        payload=payload,
    )
    return {
        **training,
        "candidate_id": candidate_id,
        "exposure": "POST_FREEZE_HELDOUT_EXTERNAL_RETURN",
    }


class ProspectiveRepeatedRecurrenceTests(unittest.TestCase):
    def test_two_successive_fresh_problems_change_machinery_then_third_is_rejected(self):
        parent0 = base_program()

        p1 = problem(
            "fresh-problem-a",
            "continuation_state_unresolved",
            "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
            "stream:a",
        )
        t1 = returned_training(
            rid="external:cycle1:train",
            prior_state="IDLE",
            action="FORM_PROBLEM",
            expected_next="PROBLEM_FORMED",
            payload={
                "problem_id": "placeholder",
                "residual": "placeholder",
                "discriminator": "placeholder",
                "provenance_ids": ["placeholder"],
            },
        )
        c1, successor1, status1 = author_candidate(
            problem=p1,
            parent_program=parent0,
            training_return=t1,
            allowed_patch_ops=("REPLACE_TRANSITION",),
            author_id="learner-cycle-1",
        )
        self.assertEqual(status1, "UNIQUE_MINIMAL_PATCH")
        self.assertIsNotNone(c1)
        self.assertIsNotNone(successor1)
        h1 = heldout(
            c1.candidate_id,
            rid="external:cycle1:held",
            prior_state="IDLE",
            action="FORM_PROBLEM",
            expected_next="PROBLEM_FORMED",
            payload={
                "problem_id": p1["problem_id"],
                "residual": p1["residual_coordinates"][0],
                "discriminator": p1["discriminator"],
                "provenance_ids": p1["source_stream_ids"],
            },
        )
        e1 = evaluate_candidate(
            candidate=c1,
            parent_program=parent0,
            successor_program=successor1,
            heldout_return=h1,
        )
        self.assertTrue(e1.accepted_causal_gain)

        p2 = problem(
            "fresh-problem-b",
            "referenced_incidence_missing",
            "RESOLVE_REFERENCED_INCIDENCE",
            "stream:b",
        )
        t2 = returned_training(
            rid="external:cycle2:train",
            prior_state="PROBLEM_FORMED",
            action="BIND_CARRIER",
            expected_next="TARGET_BOUND",
            payload={
                "problem_id": "placeholder",
                "carrier_kind": "PR",
                "carrier_number": 777,
            },
        )
        c2, successor2, status2 = author_candidate(
            problem=p2,
            parent_program=successor1,
            training_return=t2,
            allowed_patch_ops=("REPLACE_TRANSITION",),
            author_id="learner-cycle-2",
        )
        self.assertEqual(status2, "UNIQUE_MINIMAL_PATCH")
        self.assertIsNotNone(c2)
        self.assertNotEqual(c1.candidate_id, c2.candidate_id)
        h2 = heldout(
            c2.candidate_id,
            rid="external:cycle2:held",
            prior_state="PROBLEM_FORMED",
            action="BIND_CARRIER",
            expected_next="TARGET_BOUND",
            payload={
                "problem_id": p2["problem_id"],
                "carrier_kind": "PR",
                "carrier_number": 888,
            },
        )
        e2 = evaluate_candidate(
            candidate=c2,
            parent_program=successor1,
            successor_program=successor2,
            heldout_return=h2,
        )
        self.assertTrue(e2.accepted_causal_gain)

        # Direct host comparator can match the second successor. This mature-
        # reduces uniqueness without erasing learner-owned causal gain.
        direct_patch = ProgramPatch(
            op=str(c2.patch["op"]),
            match_from=c2.patch.get("match_from"),
            match_action=c2.patch.get("match_action"),
            transition=dict(c2.patch.get("transition") or {}),
        )
        direct, _ = apply_successor_patch(
            successor1,
            (direct_patch,),
            author_id="direct-host-comparator",
        )
        direct_correct, total = score_program(direct, h2["traces"])
        self.assertEqual(direct_correct, e2.successor_correct)
        self.assertEqual(total, e2.total)
        self.assertFalse(e2.mechanism_unique_or_necessary)

        # Third return is contradictory at one state/action pair. No lawful
        # patch can satisfy both traces; rejection is retained rather than
        # forcing continued self-modification.
        p3 = problem(
            "fresh-problem-c",
            "change_order_unavailable",
            "OBTAIN_ORDERED_RETURN",
            "stream:c",
        )
        contradictory = {
            "return_id": "external:cycle3:train",
            "return_owner": "EXTERNAL_EVALUATOR",
            "exposure": "PUBLIC_DEVELOPMENT_RETURN",
            "traces": [
                {
                    "trace_id": "c3:a",
                    "prior_state": "TARGET_BOUND",
                    "action": "FREEZE_PLAN",
                    "payload": {
                        "problem_id": "placeholder",
                        "proposal_id": "p",
                    },
                    "expect_success": True,
                    "expected_next_state": "PLAN_FROZEN",
                    "provenance_id": "external:c3:a",
                },
                {
                    "trace_id": "c3:b",
                    "prior_state": "TARGET_BOUND",
                    "action": "FREEZE_PLAN",
                    "payload": {
                        "problem_id": "placeholder",
                        "proposal_id": "p",
                    },
                    "expect_success": False,
                    "expected_next_state": None,
                    "provenance_id": "external:c3:b",
                },
            ],
        }
        c3, successor3, status3 = author_candidate(
            problem=p3,
            parent_program=successor2,
            training_return=contradictory,
            allowed_patch_ops=("REPLACE_TRANSITION",),
            author_id="learner-cycle-3",
        )
        self.assertIsNone(c3)
        self.assertIsNone(successor3)
        self.assertEqual(status3, "WITHHOLD_NO_EXPRESSIBLE_PATCH")


if __name__ == "__main__":
    unittest.main()
