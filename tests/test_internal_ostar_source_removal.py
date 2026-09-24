from __future__ import annotations

import importlib
import json
from itertools import product
from pathlib import Path
import unittest

from kernel.runtime.induced_policy import (
    LabeledExample,
    execute_tree,
    induce_exact_tree,
    tree_features,
)
from kernel.development.internal_ostar_teacher import exhaustive_training_surface


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json"


class InternalOStarSourceRemovalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_runtime_policy_is_state_owned_and_opaque(self):
        self.assertEqual(self.program["schema"], "Venus.InducedDecisionTree.v0.1")
        self.assertEqual(tuple(self.program["feature_names"]), tuple(f"f{i}" for i in range(8)))
        rendered = json.dumps(self.program, sort_keys=True).lower()
        for forbidden in (
            "strong-n2",
            "intelligent love",
            "anti-minerva",
            "non-sovereignty",
            "correction permeability",
            "external access",
            "reachable revision",
        ):
            self.assertNotIn(forbidden, rendered)

    def test_all_opaque_coordinates_are_causally_used(self):
        self.assertEqual(tree_features(self.program), tuple(f"f{i}" for i in range(8)))

    def test_teacher_is_not_imported_by_runtime_executor(self):
        module = importlib.import_module("kernel.runtime.induced_policy")
        self.assertNotIn("teacher_decision", module.__dict__)
        self.assertNotIn("exhaustive_training_surface", module.__dict__)

    def test_policy_executes_without_teacher_module(self):
        features = {
            "f0": True, "f1": False, "f2": True, "f3": True,
            "f4": True, "f5": False, "f6": False, "f7": False,
        }
        self.assertEqual(execute_tree(self.program, features), "REOPEN")

    def test_internalized_tree_is_reinducible_from_teacher_returns(self):
        rows = exhaustive_training_surface()
        induced = induce_exact_tree(
            LabeledExample(
                example_id=row["example_id"],
                features=row["features"],
                decision=row["decision"],
            )
            for row in rows
        )
        self.assertEqual(induced["tree"], self.program["tree"])

    def test_exhaustive_source_removal_behavior_matches_prefrozen_teacher(self):
        expected = {
            tuple(row["features"][f"f{i}"] for i in range(8)): row["decision"]
            for row in exhaustive_training_surface()
        }
        for bits, decision in expected.items():
            features = dict(zip((f"f{i}" for i in range(8)), bits))
            self.assertEqual(execute_tree(self.program, features), decision)

    def test_each_coordinate_has_a_matched_causal_intervention(self):
        all_rows = [
            dict(zip((f"f{i}" for i in range(8)), bits))
            for bits in product((False, True), repeat=8)
        ]
        for feature in (f"f{i}" for i in range(8)):
            found = False
            for row in all_rows:
                twin = dict(row)
                twin[feature] = not twin[feature]
                if execute_tree(self.program, row) != execute_tree(self.program, twin):
                    found = True
                    break
            self.assertTrue(found, f"{feature} is not decision-causal")


if __name__ == "__main__":
    unittest.main()
