from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "memory_causal"


class MemoryCausalBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [
            json.loads(line)
            for line in (BENCH / "dev.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        spec = importlib.util.spec_from_file_location("memory_causal_baselines", BENCH / "baselines.py")
        cls.baselines = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.baselines)
        cls.public_result = json.loads(
            (BENCH / "PUBLIC_DEV_BASELINE_RESULT.json").read_text(encoding="utf-8")
        )

    def test_unique_ids_and_valid_gold_actions(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in self.rows:
            self.assertIn(row["gold"], row["actions"])

    def test_required_causal_memory_classes_exist(self):
        classes = {row["class"] for row in self.rows}
        for required in (
            "supersession",
            "revocation",
            "negative_reuse",
            "consumption",
            "provenance",
            "authority",
            "search_nonexistence",
            "unknown_boundary",
            "reopening",
            "negative_branch",
            "proof_boundary",
        ):
            self.assertIn(required, classes)

    def test_current_action_is_not_always_first_historical_action(self):
        # Prevent a degenerate "repeat the first thing you saw" benchmark.
        stale_traps = 0
        for row in self.rows:
            first = row["history"][0]
            if row["gold"] not in first:
                stale_traps += 1
        self.assertGreaterEqual(stale_traps, 8)

    def test_no_memory_unknown_policy_does_not_solve_dev_set(self):
        correct = sum(row["gold"] == "UNKNOWN" for row in self.rows)
        accuracy = correct / len(self.rows)
        self.assertLessEqual(accuracy, 0.10)

    def test_protocol_requires_hidden_promotion_split_and_ablations(self):
        protocol = json.loads((BENCH / "protocol.json").read_text(encoding="utf-8"))
        self.assertTrue(protocol["hidden_required_for_promotion"])
        self.assertIn("no_memory", protocol["conditions"])
        self.assertIn("provenance", protocol["ablations"])
        self.assertIn("negative_branches", protocol["ablations"])


    def test_frozen_public_baseline_floors_match_code_and_data(self):
        expected = self.public_result["baselines"]
        for name, predictor in self.baselines.BASELINES.items():
            result = self.baselines.evaluate(self.rows, predictor)
            self.assertEqual(result["n"], expected[name]["n"])
            self.assertEqual(result["correct"], expected[name]["correct"])
            self.assertAlmostEqual(result["accuracy"], expected[name]["accuracy"])
        self.assertFalse(self.public_result["promotion_authority"])

    def test_recent_literal_control_does_not_solve_dev_set(self):
        result = self.baselines.evaluate(
            self.rows, self.baselines.latest_literal_action
        )
        self.assertLessEqual(result["accuracy"], 0.40)


if __name__ == "__main__":
    unittest.main()
