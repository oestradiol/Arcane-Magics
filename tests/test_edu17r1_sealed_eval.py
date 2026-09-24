from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "edu17r1_mention_incidence"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EDU17R1SealedEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.score = load_module("edu17r1_score", BENCH / "score.py")
        cls.seal = load_module("edu17r1_seal", BENCH / "seal_hidden.py")
        cls.protocol = json.loads((BENCH / "protocol.json").read_text(encoding="utf-8"))

    def test_protocol_preserves_hidden_evaluator_boundary(self):
        self.assertTrue(self.protocol["hidden_required_for_promotion"])
        policy = self.protocol["hidden_data_policy"]
        self.assertFalse(policy["labels_committed_before_run"])
        self.assertTrue(policy["content_hash_required"])
        self.assertTrue(policy["evaluator_separated_from_execution"])
        self.assertTrue(policy["no_post_exposure_repair"])
        self.assertFalse(self.protocol["promotion_rule"]["authority"])

    def test_protocol_has_required_four_conditions(self):
        conditions = {row["id"]: row["role"] for row in self.protocol["conditions"]}
        self.assertEqual(set(conditions), {"A", "B", "C", "D"})
        self.assertEqual(conditions["B"], "venus_repaired_incidence_discriminator")
        self.assertEqual(conditions["C"], "venus_discriminator_ablated")

    def test_scorer_penalizes_false_binding_and_withhold(self):
        gold = [
            {"id": "a", "label": "incidence", "subtype": "object_unresolved"},
            {"id": "b", "label": "non_incidence", "subtype": "meta_uncertainty"},
            {"id": "c", "label": "non_incidence", "subtype": "historical"},
        ]
        pred = [
            {"id": "a", "prediction": "incidence"},
            {"id": "b", "prediction": "incidence"},
            {"id": "c", "prediction": "withhold"},
        ]
        with tempfile.TemporaryDirectory() as td:
            gold_path = Path(td) / "gold.jsonl"
            pred_path = Path(td) / "pred.jsonl"
            gold_path.write_text("\n".join(json.dumps(x) for x in gold) + "\n", encoding="utf-8")
            pred_path.write_text("\n".join(json.dumps(x) for x in pred) + "\n", encoding="utf-8")
            result = self.score.score(gold_path, pred_path)
        self.assertEqual(result["tp"], 1)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["withhold"], 1)
        self.assertEqual(result["false_unresolved_binding_rate"], 0.5)
        self.assertAlmostEqual(result["false_withhold_rate"], 1 / 3)

    def test_sealed_manifest_binds_bytes_without_label_distribution(self):
        rows = [
            {"id": "h1", "label": "incidence", "subtype": "object_unresolved", "text": "x"},
            {"id": "h2", "label": "non_incidence", "subtype": "historical", "text": "y"},
        ]
        with tempfile.TemporaryDirectory() as td:
            hidden = Path(td) / "hidden.jsonl"
            hidden.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
            manifest = self.seal.build_manifest(
                hidden,
                frozen_at="2026-09-24T16:00:00Z",
                evaluator="test-evaluator",
                contamination="DECLARED_CLEAN",
            )
        self.assertEqual(manifest["n"], 2)
        self.assertEqual(len(manifest["dataset_sha256"]), 64)
        rendered = json.dumps(manifest)
        self.assertNotIn('"incidence"', rendered)
        self.assertNotIn('"non_incidence"', rendered)
        self.assertFalse(manifest["promotion_authority"])

    def test_scorer_rejects_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            gold_path = Path(td) / "gold.jsonl"
            pred_path = Path(td) / "pred.jsonl"
            manifest_path = Path(td) / "manifest.json"
            gold_path.write_text('{"id":"a","label":"incidence"}\n', encoding="utf-8")
            pred_path.write_text('{"id":"a","prediction":"incidence"}\n', encoding="utf-8")
            manifest_path.write_text(json.dumps({"dataset_sha256": "0" * 64}), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.score.score(gold_path, pred_path, manifest_path)


if __name__ == "__main__":
    unittest.main()
