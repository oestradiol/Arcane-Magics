from __future__ import annotations

from pathlib import Path
import unittest

from kernel.development.dependency_planning_curriculum import run
from scripts.run_selected_didactic_curriculum import _execution_envelope_status


ROOT = Path(__file__).resolve().parents[1]


class DependencyPlanningCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.result = run(
            ROOT / "kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json",
            ROOT / "kernel/development/DEPENDENCY_PLANNING_DIDACTIC_CASES.json",
        )

    def test_candidate_passes_frozen_b1_and_b2_checks(self):
        self.assertEqual(self.result["status"], "PASS_BOUNDED_DEPENDENCY_PLANNING_B1_B2")
        self.assertTrue(self.result["b1_pass"])
        self.assertTrue(self.result["b2_pass"])
        self.assertTrue(all(self.result["b1_checks"].values()))
        self.assertTrue(all(self.result["b2_checks"].values()))

    def test_candidate_representation_is_learner_state_without_authority(self):
        self.assertEqual(self.candidate["semantics_owner"], "LEARNER_STATE_CANDIDATE")
        self.assertEqual(self.candidate["generic_executor"], "kernel/runtime/task_graph.py")
        self.assertFalse(self.candidate["independent_evaluation"])
        self.assertFalse(self.candidate["internalization_claim"])
        self.assertFalse(self.candidate["promotion_authority"])
        self.assertFalse(self.candidate["truth_authority"])
        self.assertNotIn("K7", str(self.candidate["program"]))
        self.assertNotIn("H1", str(self.candidate["program"]))

    def test_interventions_are_bounded_and_withhold_on_invalid_graphs(self):
        self.assertEqual(
            self.result["bounded_base_result"]["critical_path"],
            ["A", "C", "E"],
        )
        self.assertEqual(self.result["critical_intervention_result"]["span"], 11)
        self.assertEqual(self.result["noncritical_intervention_result"]["span"], 9)
        self.assertEqual(
            self.result["withhold_cases"],
            {
                "cycle": "WITHHOLD_DEPENDENCY_CYCLE",
                "underspecified": "WITHHOLD_UNDERSPECIFIED_GRAPH",
                "missing_duration": "WITHHOLD_MISSING_DURATION",
                "candidate_state_ablation": "WITHHOLD_MISSING_RELATION_CLASSIFIER",
            },
        )

    def test_curriculum_withhold_stops_generic_fallback(self):
        self.assertEqual(
            _execution_envelope_status("WITHHOLD_DEPENDENCY_PLANNING_DISCRIMINATOR_NOT_MET"),
            "WITHHOLD_CURRICULUM_RESULT",
        )
        self.assertEqual(
            _execution_envelope_status("PASS_BOUNDED_DEPENDENCY_PLANNING_B1_B2"),
            "EXECUTED_SELECTED_PREFROZEN_CURRICULUM",
        )
        self.assertEqual(
            _execution_envelope_status("PASS_BOUNDED_LOCAL_ONLY"),
            "WITHHOLD_CURRICULUM_RESULT",
        )
        self.assertEqual(_execution_envelope_status(None), "WITHHOLD_CURRICULUM_RESULT")


if __name__ == "__main__":
    unittest.main()
