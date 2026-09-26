from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class VMInternalizationPhasePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load("kernel/development/VM_INTERNALIZATION_PHASE_PLAN.json")

    def test_every_runtime_python_file_has_exactly_one_disposition(self):
        actual = {
            p.as_posix().replace(ROOT.as_posix() + "/", "")
            for p in (ROOT / "kernel/runtime").glob("*.py")
        }
        rows = self.plan["runtime_dispositions"]
        planned = [r["path"] for r in rows]
        self.assertEqual(len(planned), len(set(planned)))
        self.assertEqual(actual, set(planned))

    def test_constitutional_external_relations_are_not_internalization_targets(self):
        forbidden = set(self.plan["noninternalizable_relations"])
        for required in (
            "WORLD_OTHER", "FRESH_WORLD_RETURN", "EVALUATOR_CUSTODY",
            "AUTHORIZATION", "JURISDICTION", "ROLLBACK_PARENT_CUSTODY",
            "ANTI_MINERVA_CORRECTION_PERMEABILITY",
        ):
            self.assertIn(required, forbidden)
        self.assertFalse(self.plan["promotion_authority"])
        self.assertFalse(self.plan["truth_authority"])

    def test_code_deletion_is_not_internalization_and_reduction_can_win(self):
        laws = set(self.plan["laws"])
        self.assertIn("CODE_DELETION!=INTERNALIZATION", laws)
        self.assertIn("STATE_OWNERSHIP!=GENERALIZATION", laws)
        self.assertIn("MATURE_REDUCTION_BEATS_INTERNALIZING_UNNECESSARY_COMPLEXITY", laws)
        by_path = {r["path"]: r for r in self.plan["runtime_dispositions"]}
        self.assertEqual(
            by_path["kernel/runtime/transform_program_multi_repair.py"]["disposition"],
            "MATURE_REDUCED_GENERIC_SUBSTITUTE",
        )

    def test_lateral_internalization_pass_does_not_launder_failed_generalization(self):
        result = load("kernel/development/LATERAL_INTERNALIZATION_TRANSFER_1_RESULT.json")
        self.assertEqual(
            result["ownership_status"],
            "PASS_BOUNDED_INTERNALIZATION_EPISODE1_PROJECTION_POLICY",
        )
        self.assertEqual(result["generalization_status"], "FAIL_FRESH_TRANSFER_GENERALIZATION")
        self.assertFalse(result["general_lateralizer_claim"])
        self.assertEqual(result["fresh_transfer_correct"], 1)
        self.assertEqual(result["fresh_transfer_total"], 8)

    def test_canonical_r193_is_explicit_source_constraint(self):
        self.assertIn(
            "provenance/canonical-extracts/R193_SCAFFOLD_INTERNALIZATION_REFERENCE.md",
            self.plan["source_constraints"],
        )

    def test_foundational_cognitive_theater_precedes_p2(self):
        prereq=self.plan["foundational_semantic_prerequisite"]
        self.assertEqual(
            prereq["ref"],
            "kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_CURRICULUM.json",
        )
        self.assertFalse(prereq.get("promotion_authority", False))
        phase="\n".join(self.plan["phase_order"])
        self.assertLess(phase.index("P1.5"), phase.index("P2 "))
        for row in self.plan["developmental_targets"]:
            if row["priority"] <= 7:
                self.assertTrue(row["requires_foundational_cognitive_theater"])

if __name__ == "__main__":
    unittest.main()
