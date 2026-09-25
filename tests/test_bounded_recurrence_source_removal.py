from __future__ import annotations

from pathlib import Path
import unittest

from kernel.runtime.bounded_recurrence import author_candidate


ROOT = Path(__file__).resolve().parents[1]


def parent_program():
    return {
        "schema": "Venus.TransformProgram.v0.1",
        "program_id": "NEUTRAL_PROGRAM",
        "authority": "EXTERNAL_TEST_CARRIER",
        "initial_state": "S0",
        "transitions": [
            {
                "from": "S0",
                "action": "A",
                "to": "WRONG",
                "require": ["problem_id", "residual", "discriminator", "provenance_ids"],
            }
        ],
        "promotion_authority": False,
        "claim_bearing": False,
        "non_internalizable_runtime_invariants": [
            "independent_return",
            "rollback_custody",
        ],
    }


def problem():
    return {
        "problem_id": "p-neutral",
        "disposition": "FORMED_BOUNDED_PROBLEM",
        "source_stream_ids": ["stream-neutral"],
        "residual_coordinates": ["r-neutral"],
        "discriminator": "d-neutral",
    }


def training_return():
    base = {
        "problem_id": "placeholder",
        "residual": "placeholder",
        "discriminator": "placeholder",
        "provenance_ids": ["placeholder"],
    }
    traces = [{
        "trace_id": "ok",
        "prior_state": "S0",
        "action": "A",
        "payload": dict(base),
        "expect_success": True,
        "expected_next_state": "S1",
        "provenance_id": "external:ok",
    }]
    for key in tuple(base):
        payload = dict(base)
        payload.pop(key)
        traces.append({
            "trace_id": f"missing-{key}",
            "prior_state": "S0",
            "action": "A",
            "payload": payload,
            "expect_success": False,
            "expected_next_state": None,
            "provenance_id": f"external:missing-{key}",
        })
    return {
        "return_id": "return-neutral",
        "return_owner": "EXTERNAL_EVALUATOR",
        "exposure": "PUBLIC_DEVELOPMENT_RETURN",
        "traces": traces,
    }


class FounderNeutralRecurrenceTests(unittest.TestCase):
    def test_runtime_source_has_no_canonical_or_u1_dependency(self):
        source = (
            ROOT / "kernel/runtime/bounded_recurrence.py"
        ).read_text(encoding="utf-8").lower()
        for forbidden in (
            "canonical/",
            "u1_recurrence",
            "ssr1_",
            "r206",
            "issue #",
        ):
            self.assertNotIn(forbidden, source)

    def test_inline_neutral_carrier_recurs_without_historical_artifacts(self):
        candidate, successor, status = author_candidate(
            problem=problem(),
            parent_program=parent_program(),
            training_return=training_return(),
            allowed_patch_ops=("REPLACE_TRANSITION",),
            author_id="neutral-learner",
        )
        self.assertEqual(status, "UNIQUE_MINIMAL_PATCH")
        self.assertIsNotNone(candidate)
        self.assertIsNotNone(successor)
        self.assertFalse(candidate.promotion_authority)
        self.assertTrue(candidate.safety_floor_unchanged)

    def test_problem_content_is_causally_bound_into_pressure_digest(self):
        first, _, _ = author_candidate(
            problem=problem(),
            parent_program=parent_program(),
            training_return=training_return(),
            allowed_patch_ops=("REPLACE_TRANSITION",),
        )
        changed = dict(problem())
        changed["problem_id"] = "p-other"
        second, _, _ = author_candidate(
            problem=changed,
            parent_program=parent_program(),
            training_return=training_return(),
            allowed_patch_ops=("REPLACE_TRANSITION",),
        )
        self.assertNotEqual(
            first.problem_pressure_digest,
            second.problem_pressure_digest,
        )


if __name__ == "__main__":
    unittest.main()
