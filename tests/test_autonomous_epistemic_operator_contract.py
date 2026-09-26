from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.runtime.transform_program import step, TransformProgramError

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = json.loads(
    (ROOT / "kernel/development/AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json")
    .read_text(encoding="utf-8")
)


class AutonomousEpistemicOperatorContractTests(unittest.TestCase):
    def test_operator_noncollapse_is_explicit(self):
        contract = PROGRAM["epistemic_operator_contract"]
        self.assertEqual(contract["status"], "ADMITTED_OPTIONAL_PATH")
        for invariant in (
            "GENERATE!=DIMENSIONALIZE",
            "DIMENSIONALIZE!=LATERALIZE",
            "LATERALIZE!=CRYSTALLIZE_F",
            "CRYSTALLIZE_F!=INTERNALIZE",
            "INTERNALIZE_COMPETENCE!=INTERNALIZE_CORRECTION_SOVEREIGNTY",
        ):
            self.assertIn(invariant, contract["noncollapse"])

    def test_lateral_path_requires_independent_face_custody(self):
        with self.assertRaisesRegex(TransformProgramError, "independence_claims"):
            step(
                PROGRAM,
                state="COORDINATES_PROPOSED",
                action="LATERALIZE",
                payload={
                    "face_ids": ["f1", "f2"],
                    "projection_discriminator": "d",
                    "provenance_ids": ["p1", "p2"],
                },
                actor_id="test",
            )

    def test_crystallization_preserves_live_separators(self):
        receipt = step(
            PROGRAM,
            state="RESIDUAL_CLASSIFIED",
            action="CRYSTALLIZE_F",
            payload={
                "future_family_id": "F-test",
                "preserved_separator_ids": ["sep-live"],
                "crystal_id": "crystal-1",
            },
            actor_id="test",
        )
        self.assertEqual(receipt.next_state, "CRYSTAL_CANDIDATE")

    def test_internalization_requires_independent_return_evidence(self):
        with self.assertRaisesRegex(TransformProgramError, "return_id"):
            step(
                PROGRAM,
                state="AWAITING_INTERNALIZATION_RETURN",
                action="BIND_INTERNALIZATION_RETURN",
                payload={
                    "evaluator_id": "external-evaluator",
                    "external": True,
                    "source_removed": True,
                    "behavior_equivalent": True,
                    "successor_reconstructible": True,
                },
                actor_id="test",
            )

    def test_short_path_remains_available(self):
        receipt = step(
            PROGRAM,
            state="PROBLEM_FORMED",
            action="BIND_CARRIER",
            payload={
                "problem_id": "p",
                "carrier_kind": "ISSUE",
                "carrier_number": 169,
            },
            actor_id="test",
        )
        self.assertEqual(receipt.next_state, "TARGET_BOUND")


if __name__ == "__main__":
    unittest.main()
