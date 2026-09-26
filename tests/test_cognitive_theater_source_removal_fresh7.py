from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fresh7_eval",
    ROOT / "scripts/evaluate_cognitive_theater_source_removal_fresh7.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("fresh7 evaluator")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class CognitiveTheaterSourceRemovalFresh7Tests(unittest.TestCase):
    def test_state_declares_semantics_owner_and_no_capability_runtime_dependency(self):
        state = json.loads(
            (ROOT / "kernel/development/COGNITIVE_THEATER_STATE_OWNERSHIP_CANDIDATE.json").read_text(
                encoding="utf-8"
            )
        )
        contract = state["internalization_contract"]
        self.assertEqual(contract["semantics_owner"], "LEARNER_STATE")
        self.assertFalse(contract["capability_specific_python_runtime_dependency"])
        self.assertTrue(contract["generic_executor_substrate_allowed"])
        self.assertTrue(contract["source_python_reference_is_provenance_only"])
        self.assertFalse(contract["internalization_claim"])

    def test_generic_executor_has_no_capability_semantics_or_development_import(self):
        src = (
            ROOT / "kernel/runtime/structured_template_machine.py"
        ).read_text(encoding="utf-8").casefold()
        for forbidden in (
            "english",
            "japanese",
            "brazilian_portuguese",
            "mathematics",
            "theater",
            "#206",
            "cognitive_theater_state_composer",
            "foundational_cognitive_theater",
            "kernel.development",
        ):
            self.assertNotIn(forbidden, src)

    def test_isolated_state_owned_execution_survives_source_removal(self):
        out = m.evaluate()
        print("COGNITIVE_THEATER_FRESH7_RESULT=" + json.dumps(out, ensure_ascii=False, sort_keys=True))

        self.assertEqual(out["total"], 24)
        self.assertEqual(out["task_binding_correct"], 24)
        self.assertEqual(out["state_correct"], 24)
        self.assertEqual(out["gauge_pairs_identical_state"], out["gauge_pairs_total"])
        self.assertFalse(out["capability_specific_source_in_isolated_execution"])
        self.assertEqual(out["forbidden_bundle_hits"], [])
        self.assertEqual(out["runtime_forbidden_marker_hits"], [])
        self.assertTrue(out["source_removal_pass"])

        # The technical source-removal pass must not self-mint the final
        # Internalizer/evaluation claim.
        self.assertFalse(out["fresh_world_return_external"])
        self.assertFalse(out["independent_external_evaluation"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])


if __name__ == "__main__":
    unittest.main()
