from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class InternalizationBoundaryTests(unittest.TestCase):
    def test_boundary_separates_state_substrate_and_external_roles(self):
        b = load("kernel/development/INTERNALIZATION_BOUNDARY.json")
        self.assertIn("LATERALIZATION_POLICY", b["internalizable_state_semantics"])
        self.assertIn("PYTHON_AS_GENERIC_IMPLEMENTATION_SUBSTRATE", b["replaceable_execution_substrate"])
        self.assertIn("FRESH_WORLD_RETURN", b["external_noninternalizable"])
        self.assertFalse(b["claims"]["capability_specific_python_scaffold_may_remain_for_internalized_claim"])
        self.assertFalse(b["claims"]["executable_route_alone_counts_as_internalization"])

    def test_lateral_route_is_not_falsely_claimed_internalized(self):
        p = load("kernel/development/AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json")
        c = p["epistemic_operator_contract"]
        self.assertEqual(c["status"], "ADMITTED_OPERATOR_ROUTE_NOT_INTERNALIZED")
        self.assertFalse(c["internalization_claim"])

    def test_admitted_internalized_states_claim_state_semantics_not_python_scaffold(self):
        for rel in (
            "kernel/development/GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json",
            "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json",
        ):
            with self.subTest(rel=rel):
                obj = load(rel)
                c = obj["internalization_contract"]
                self.assertEqual(c["semantics_owner"], "LEARNER_STATE")
                self.assertFalse(c["capability_specific_python_runtime_dependency"])
                self.assertTrue(c["generic_executor_substrate_allowed"])
                self.assertTrue(c["source_python_reference_is_provenance_only"])

    def test_runtime_executors_do_not_import_capability_teachers_or_donors(self):
        for rel in (
            "kernel/runtime/internalized_search.py",
            "kernel/runtime/induced_policy.py",
        ):
            with self.subTest(rel=rel):
                src = (ROOT / rel).read_text(encoding="utf-8").lower()
                for forbidden in (
                    "recursive_proposal",
                    "grammar_expansion",
                    "internal_ostar_teacher",
                    "canonical/",
                ):
                    self.assertNotIn(forbidden, src)

if __name__ == "__main__":
    unittest.main()
