from __future__ import annotations

import unittest

from scripts.run_selected_didactic_curriculum import resolve_selected_curricula


class SelectedCurriculumRouterTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "curricula": [
                {
                    "curriculum_id": "RETURN_CREDIT_ASSIGNMENT_V1",
                    "prefreeze_path": "kernel/development/RETURN_CREDIT_ASSIGNMENT_PREFREEZE.json",
                },
                {
                    "curriculum_id": "DEPENDENCY_PLANNING_V1",
                    "prefreeze_path": "kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json",
                },
            ]
        }

    def test_only_learner_referenced_prefreeze_is_routed(self):
        cycle = {"study": {"referenced_repository_paths": [
            "kernel/development/RETURN_CREDIT_ASSIGNMENT_PREFREEZE.json"
        ]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "READY")
        self.assertEqual(route["rows"][0]["curriculum_id"], "RETURN_CREDIT_ASSIGNMENT_V1")

    def test_selected_dependency_planning_prefreeze_routes_to_its_executor(self):
        cycle = {"study": {"referenced_repository_paths": [
            "kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json"
        ]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "READY")
        self.assertEqual(route["rows"][0]["curriculum_id"], "DEPENDENCY_PLANNING_V1")

    def test_unknown_selected_prefreeze_withholds(self):
        cycle = {"study": {"referenced_repository_paths": [
            "kernel/development/UNSUPPORTED_PREFREEZE.json"
        ]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "WITHHOLD_SELECTED_PREFREEZE_HAS_NO_EXECUTOR")
        self.assertEqual(
            route["unresolved_prefreezes"],
            frozenset({"kernel/development/UNSUPPORTED_PREFREEZE.json"}),
        )

    def test_non_curriculum_references_do_not_block_other_study(self):
        cycle = {"study": {"referenced_repository_paths": [
            "docs/ISSUE_ROADMAP.md"
        ]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "NO_SELECTED_EXECUTABLE_CURRICULUM")


if __name__ == "__main__":
    unittest.main()
