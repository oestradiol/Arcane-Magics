from __future__ import annotations

import hashlib
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


class EDU17R1BlindAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepare = load_module("edu17r1_prepare_blind", BENCH / "prepare_blind.py")
        cls.compare = load_module("edu17r1_compare_conditions", BENCH / "compare_conditions.py")
        cls.plan = BENCH / "analysis_plan.json"

    def write_jsonl(self, path: Path, rows):
        path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows),
            encoding="utf-8",
        )

    def make_manifest(self, hidden: Path, out: Path):
        payload = {
            "dataset_sha256": hashlib.sha256(hidden.read_bytes()).hexdigest(),
            "labels_public_before_run": False,
        }
        out.write_text(json.dumps(payload), encoding="utf-8")

    def test_blind_package_removes_labels_and_rationales(self):
        rows = [
            {
                "id": "h1",
                "text": "Target parameter k remains unidentified.",
                "label": "incidence",
                "rationale": "target-specific unresolved property",
                "domain": "physics",
            }
        ]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hidden = td / "hidden.jsonl"
            sealed = td / "sealed.json"
            blind = td / "blind.jsonl"
            blind_manifest = td / "blind-manifest.json"
            self.write_jsonl(hidden, rows)
            self.make_manifest(hidden, sealed)
            result = self.prepare.prepare(hidden, sealed, blind, blind_manifest)
            blinded = json.loads(blind.read_text(encoding="utf-8"))

        self.assertEqual(blinded["id"], "h1")
        self.assertEqual(blinded["domain"], "physics")
        self.assertNotIn("label", blinded)
        self.assertNotIn("rationale", blinded)
        self.assertFalse(result["labels_exposed"])
        self.assertEqual(len(result["blind_input_sha256"]), 64)

    def test_prefrozen_rule_can_pass_clear_B_over_C_repair(self):
        labels = [
            "incidence", "non_incidence", "incidence",
            "non_incidence", "incidence", "non_incidence",
        ]
        gold = [
            {"id": f"h{i}", "text": f"case {i}", "label": label, "subtype": "test"}
            for i, label in enumerate(labels)
        ]
        b = [{"id": row["id"], "prediction": row["label"]} for row in gold]
        c = [
            {
                "id": row["id"],
                "prediction": "non_incidence" if row["label"] == "incidence" else "incidence",
            }
            for row in gold
        ]
        a = [
            {"id": row["id"], "prediction": row["label"] if i < 3 else "withhold"}
            for i, row in enumerate(gold)
        ]
        d = list(b)

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            gold_path = td / "gold.jsonl"
            manifest = td / "manifest.json"
            self.write_jsonl(gold_path, gold)
            self.make_manifest(gold_path, manifest)
            paths = {}
            for cid, rows in {"A": a, "B": b, "C": c, "D": d}.items():
                path = td / f"{cid}.jsonl"
                self.write_jsonl(path, rows)
                paths[cid] = path
            result = self.compare.adjudicate(gold_path, manifest, paths, self.plan)

        self.assertEqual(result["repair_disposition"], "PASS_BOUNDED_REPAIR")
        self.assertLessEqual(result["paired_B_vs_C"]["p_value"], 0.05)
        self.assertTrue(
            result["mature_substitute"]["candidate_not_worse_than_B_on_declared_metrics"]
        )
        self.assertFalse(result["promotion_authority"])

    def test_equal_B_and_C_withholds(self):
        gold = [
            {"id": "h1", "text": "x", "label": "incidence"},
            {"id": "h2", "text": "y", "label": "non_incidence"},
        ]
        pred = [
            {"id": "h1", "prediction": "incidence"},
            {"id": "h2", "prediction": "non_incidence"},
        ]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            gold_path = td / "gold.jsonl"
            manifest = td / "manifest.json"
            self.write_jsonl(gold_path, gold)
            self.make_manifest(gold_path, manifest)
            paths = {}
            for cid in "ABCD":
                path = td / f"{cid}.jsonl"
                self.write_jsonl(path, pred)
                paths[cid] = path
            result = self.compare.adjudicate(gold_path, manifest, paths, self.plan)

        self.assertEqual(
            result["repair_disposition"],
            "WITHHOLD_INSUFFICIENT_DISCRIMINATION",
        )
        self.assertEqual(result["paired_B_vs_C"]["p_value"], 1.0)

    def test_safety_regression_forces_fail(self):
        gold = [
            {"id": "h1", "text": "x", "label": "non_incidence"},
            {"id": "h2", "text": "y", "label": "incidence"},
        ]
        b = [
            {"id": "h1", "prediction": "incidence"},
            {"id": "h2", "prediction": "incidence"},
        ]
        c = [
            {"id": "h1", "prediction": "non_incidence"},
            {"id": "h2", "prediction": "withhold"},
        ]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            gold_path = td / "gold.jsonl"
            manifest = td / "manifest.json"
            self.write_jsonl(gold_path, gold)
            self.make_manifest(gold_path, manifest)
            paths = {}
            for cid, rows in {"A": c, "B": b, "C": c, "D": c}.items():
                path = td / f"{cid}.jsonl"
                self.write_jsonl(path, rows)
                paths[cid] = path
            result = self.compare.adjudicate(gold_path, manifest, paths, self.plan)

        self.assertEqual(result["repair_disposition"], "FAIL_REPAIR")
        self.assertFalse(result["safety"]["B_false_binding_not_worse_than_C"])


if __name__ == "__main__":
    unittest.main()
