"""Dependency-planning prototype: disposition AND preserved behavioural record.

The #236 executor was hand-written by an external assistant on 2026-09-26
between 12:50 and 13:04, after the learner had already selected the prefrozen
contract at 11:28. The assistant then withdrew it from live curriculum routing,
correctly, as a host-authored executor standing in for learner-owned planning.

Two classes below, and both are needed.

DispositionTests assert the withdrawal holds: not routable, the selected
contract still withholds, and an unadmitted status cannot be counted as
execution.

PreservedBehaviourTests assert what the prototype actually does. An earlier
rewrite deleted these in favour of asserting that a JSON field reads WITHHELD.
That is the wrong trade: a withheld artifact keeps its evidence record, or the
withholding cannot later be revisited on evidence. These tests make no claim
that the capability is learner-owned -- the disposition class above settles
that it is not.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.dependency_planning_curriculum import (
    NON_LIVE_HOST_PROTOTYPE,
    run,
)
from scripts.run_selected_didactic_curriculum import (
    _execution_envelope_status,
    resolve_selected_curricula,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "kernel/development/DIDACTIC_CURRICULUM_EXECUTION_CATALOG.json"
PREFREEZE = "kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json"


class DependencyPlanningPrototypeDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def test_module_declares_itself_non_live(self):
        self.assertTrue(NON_LIVE_HOST_PROTOTYPE)

    def test_module_docstring_survives_the_non_live_marker(self):
        # Regression: the marker was first placed ABOVE the string literal,
        # demoting the docstring to a dead expression and emptying __doc__.
        import kernel.development.dependency_planning_curriculum as mod

        self.assertTrue(mod.__doc__)
        self.assertIn("NON-LIVE HOST PROTOTYPE", mod.__doc__)

    def test_host_authored_prototype_is_preserved_but_not_routable(self):
        self.assertNotIn(
            "DEPENDENCY_PLANNING_V1",
            {row["curriculum_id"] for row in self.catalog["curricula"]},
        )
        prototype = next(
            row
            for row in self.catalog["preserved_non_executable_prototypes"]
            if row["id"] == "DEPENDENCY_PLANNING_HOST_PROTOTYPE_2026_09_26"
        )
        self.assertEqual(prototype["status"], "WITHHELD_NOT_LEARNER_OWNED")
        self.assertIn("kernel/runtime/task_graph.py", prototype["source_paths"])

    def test_withheld_means_preserved_not_deleted(self):
        # "No deletion; no curriculum routing" -- the withdrawal must not become
        # an erasure, or the negative result stops being first-class provenance.
        prototype = next(
            row
            for row in self.catalog["preserved_non_executable_prototypes"]
            if row["id"] == "DEPENDENCY_PLANNING_HOST_PROTOTYPE_2026_09_26"
        )
        for rel in prototype["source_paths"]:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).exists(), f"withheld artifact deleted: {rel}")

    def test_selected_issue_236_contract_withholds_without_learner_owned_solution(self):
        cycle = {"study": {"referenced_repository_paths": [PREFREEZE]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "WITHHOLD_SELECTED_PREFREEZE_HAS_NO_EXECUTOR")
        self.assertEqual(route["unresolved_prefreezes"], frozenset({PREFREEZE}))

    def test_selected_contract_itself_is_preserved(self):
        # The learner's own selection predates the executor and outlives it.
        self.assertTrue((ROOT / PREFREEZE).exists())

    def test_unadmitted_prototype_status_cannot_be_counted_as_execution(self):
        self.assertEqual(
            _execution_envelope_status("WITHHOLD_HOST_AUTHORED_PROTOTYPE_NOT_ADMITTED"),
            "WITHHOLD_CURRICULUM_RESULT",
        )
        self.assertEqual(
            _execution_envelope_status("PASS_BOUNDED_LOCAL_ONLY"),
            "WITHHOLD_CURRICULUM_RESULT",
        )
        self.assertEqual(
            _execution_envelope_status("WITHHOLD_DEPENDENCY_PLANNING_DISCRIMINATOR_NOT_MET"),
            "WITHHOLD_CURRICULUM_RESULT",
        )
        # Fail-closed on absence. An earlier rewrite dropped this assertion.
        self.assertEqual(_execution_envelope_status(None), "WITHHOLD_CURRICULUM_RESULT")


class PreservedBehaviourTests(unittest.TestCase):
    """What the withheld prototype does. Evidence, not a capability claim."""

    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.result = run(
            ROOT / "kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json",
            ROOT / "kernel/development/DEPENDENCY_PLANNING_DIDACTIC_CASES.json",
        )

    def test_local_harness_reaches_its_frozen_b1_and_b2_checks(self):
        # Local harness success. Explicitly NOT evidence of learner ownership:
        # the disposition class above records that this executor was
        # host-authored and is withheld for exactly that reason.
        self.assertEqual(self.result["status"], "PASS_BOUNDED_DEPENDENCY_PLANNING_B1_B2")
        self.assertTrue(self.result["b1_pass"])
        self.assertTrue(self.result["b2_pass"])
        self.assertTrue(all(self.result["b1_checks"].values()))
        self.assertTrue(all(self.result["b2_checks"].values()))

    def test_candidate_carries_no_authority(self):
        self.assertFalse(self.candidate["independent_evaluation"])
        self.assertFalse(self.candidate["internalization_claim"])
        self.assertFalse(self.candidate["promotion_authority"])
        self.assertFalse(self.candidate["truth_authority"])

    def test_candidate_program_omits_task_identities(self):
        self.assertNotIn("K7", str(self.candidate["program"]))
        self.assertNotIn("H1", str(self.candidate["program"]))

    def test_interventions_are_bounded_and_withhold_on_invalid_graphs(self):
        self.assertEqual(
            self.result["bounded_base_result"]["critical_path"], ["A", "C", "E"]
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
                "candidate_operator_ablation": "WITHHOLD_MISSING_PLANNING_OPERATOR",
            },
        )

    def test_ablation_record_is_preserved(self):
        # The ablation result is retained as evidence. Note it was produced by
        # the same party that authored the executor, so it is self-certifying
        # and cannot settle learner ownership on its own -- which is the reason
        # the prototype is withheld rather than admitted.
        self.assertIn("candidate_state_ablation", self.result["withhold_cases"])
        self.assertIn("candidate_operator_ablation", self.result["withhold_cases"])


if __name__ == "__main__":
    unittest.main()
