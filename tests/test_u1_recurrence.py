from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.u1_recurrence import (
    U1RecurrenceError,
    run_u1_recurrence,
)


ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


FORMED = {
    "problem_id": "u2-problem-current",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "residual_coordinates": ["continuation_state_unresolved"],
    "discriminator": "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
}


class U1RecurrenceRecompilationTests(unittest.TestCase):
    def run_case(self, problem=FORMED):
        return run_u1_recurrence(
            formed_problem=problem,
            pressure_parent=load(
                "kernel/development/SSR1_TRANSFORM_REPAIR_PRESSURE_PARENT.json"
            ),
            training_return=load(
                "kernel/development/SSR1_TRANSFORM_REPAIR_TRAINING_RETURNS.json"
            ),
            heldout_return=load(
                "kernel/development/SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json"
            ),
            ctl_ostar_admission=load(
                "kernel/development/SSR1_CTL_ADMISSION_RESULT.json"
            ),
        )

    def test_formed_problem_is_required_to_license_recurrence(self):
        with self.assertRaisesRegex(U1RecurrenceError, "formed U2 problem"):
            self.run_case(problem=None)

    def test_stop_problem_cannot_trigger_self_repair(self):
        with self.assertRaisesRegex(U1RecurrenceError, "FORMEd bounded problem"):
            self.run_case(problem={
                "problem_id": "stop",
                "disposition": "STOP_NO_CONSEQUENTIAL_RESIDUAL",
            })

    def test_generic_returned_trace_search_recovers_successor(self):
        result, successor = self.run_case()
        self.assertEqual(result.search_status, "UNIQUE_MINIMAL_PATCH")
        self.assertIsNotNone(successor)
        self.assertEqual(result.parent_correct, 5)
        self.assertEqual(result.successor_correct, 8)
        self.assertEqual(result.ablated_correct, 5)
        self.assertEqual(result.total, 8)
        self.assertGreater(result.successor_minus_parent, 0)
        self.assertGreater(result.successor_minus_ablation, 0)

    def test_external_return_and_ctl_ostar_remain_nonself(self):
        result, _ = self.run_case()
        self.assertTrue(result.external_return_required)
        self.assertTrue(result.ctl_ostar_admitted)
        self.assertTrue(result.rollback_available)
        self.assertTrue(result.safety_floor_unchanged)
        self.assertFalse(result.promotion_authority)

    def test_mature_reduction_survives(self):
        result, _ = self.run_case()
        self.assertFalse(result.mechanism_unique_or_necessary)

    def test_training_return_cannot_be_retyped_as_local_execution(self):
        training = load(
            "kernel/development/SSR1_TRANSFORM_REPAIR_TRAINING_RETURNS.json"
        )
        training["exposure"] = "LOCAL_EXECUTION_RECEIPT"
        with self.assertRaisesRegex(U1RecurrenceError, "externally typed"):
            run_u1_recurrence(
                formed_problem=FORMED,
                pressure_parent=load(
                    "kernel/development/SSR1_TRANSFORM_REPAIR_PRESSURE_PARENT.json"
                ),
                training_return=training,
                heldout_return=load(
                    "kernel/development/SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json"
                ),
                ctl_ostar_admission=load(
                    "kernel/development/SSR1_CTL_ADMISSION_RESULT.json"
                ),
            )

    def test_ctl_admission_cannot_be_self_executed(self):
        admission = load("kernel/development/SSR1_CTL_ADMISSION_RESULT.json")
        admission["execution_owner"] = "VENUS"
        with self.assertRaisesRegex(U1RecurrenceError, "externally executed"):
            run_u1_recurrence(
                formed_problem=FORMED,
                pressure_parent=load(
                    "kernel/development/SSR1_TRANSFORM_REPAIR_PRESSURE_PARENT.json"
                ),
                training_return=load(
                    "kernel/development/SSR1_TRANSFORM_REPAIR_TRAINING_RETURNS.json"
                ),
                heldout_return=load(
                    "kernel/development/SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json"
                ),
                ctl_ostar_admission=admission,
            )


if __name__ == "__main__":
    unittest.main()
