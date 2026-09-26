from __future__ import annotations

import json
from pathlib import Path
import unittest

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

    def test_host_authored_prototype_is_preserved_but_not_routable(self):
        self.assertNotIn(
            "DEPENDENCY_PLANNING_V1",
            {row["curriculum_id"] for row in self.catalog["curricula"]},
        )
        prototype = next(
            row for row in self.catalog["preserved_non_executable_prototypes"]
            if row["id"] == "DEPENDENCY_PLANNING_HOST_PROTOTYPE_2026_09_26"
        )
        self.assertEqual(prototype["status"], "WITHHELD_NOT_LEARNER_OWNED")
        self.assertIn("kernel/runtime/task_graph.py", prototype["source_paths"])

    def test_selected_issue_236_contract_withholds_without_learner_owned_solution(self):
        cycle = {"study": {"referenced_repository_paths": [PREFREEZE]}}
        route = resolve_selected_curricula(cycle, self.catalog)
        self.assertEqual(route["status"], "WITHHOLD_SELECTED_PREFREEZE_HAS_NO_EXECUTOR")
        self.assertEqual(route["unresolved_prefreezes"], frozenset({PREFREEZE}))

    def test_unadmitted_prototype_status_cannot_be_counted_as_execution(self):
        self.assertEqual(
            _execution_envelope_status("WITHHOLD_HOST_AUTHORED_PROTOTYPE_NOT_ADMITTED"),
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


if __name__ == "__main__":
    unittest.main()
