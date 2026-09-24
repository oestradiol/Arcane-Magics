from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from evaluation.sealed_eval import (
    SealedEvaluationError,
    bind_run_receipt,
    seal_hidden_dataset,
    validate_hidden_manifest,
)


class SealedEvaluationTests(unittest.TestCase):
    def test_seal_binds_hidden_bytes_without_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            hidden = Path(td) / "hidden.jsonl"
            hidden.write_text('{"id":"x","label":"secret"}\n', encoding="utf-8")
            manifest = seal_hidden_dataset(
                hidden,
                benchmark="demo",
                frozen_at="2026-09-24T17:10:00Z",
                evaluator="independent-evaluator",
                contamination="DECLARED_CLEAN",
                n=1,
            )
        self.assertEqual(validate_hidden_manifest(manifest), [])
        self.assertFalse(manifest["promotion_authority"])
        self.assertFalse(manifest["labels_public_before_run"])
        self.assertEqual(len(manifest["dataset_sha256"]), 64)

    def test_manifest_detects_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            hidden = Path(td) / "hidden.jsonl"
            hidden.write_text('{"id":"x"}\n', encoding="utf-8")
            manifest = seal_hidden_dataset(
                hidden,
                benchmark="demo",
                frozen_at="2026-09-24T17:10:00Z",
                evaluator="eval",
                contamination="UNKNOWN",
            )
        manifest["evaluator"] = "rewritten-after-freeze"
        self.assertIn("manifest_sha256 mismatch", validate_hidden_manifest(manifest))

    def test_run_receipt_requires_exact_condition_set_and_same_evaluator(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            hidden = root / "hidden.jsonl"
            hidden.write_text('{"id":"x"}\n', encoding="utf-8")
            manifest = seal_hidden_dataset(
                hidden,
                benchmark="demo",
                frozen_at="2026-09-24T17:10:00Z",
                evaluator="eval",
                contamination="DECLARED_CLEAN",
            )
            outputs = {}
            for cid in ("A", "B"):
                p = root / f"{cid}.jsonl"
                p.write_text('{"id":"x","prediction":"y"}\n', encoding="utf-8")
                outputs[cid] = p

            receipt = bind_run_receipt(
                hidden_manifest=manifest,
                condition_outputs=outputs,
                run_id="r1",
                executed_at="2026-09-24T17:11:00Z",
                evaluator="eval",
                required_conditions=("A", "B"),
            )
            self.assertFalse(receipt["promotion_authority"])
            self.assertEqual(set(receipt["conditions"]), {"A", "B"})

            with self.assertRaises(SealedEvaluationError):
                bind_run_receipt(
                    hidden_manifest=manifest,
                    condition_outputs={"A": outputs["A"]},
                    run_id="r2",
                    executed_at="2026-09-24T17:12:00Z",
                    evaluator="eval",
                    required_conditions=("A", "B"),
                )
            with self.assertRaises(SealedEvaluationError):
                bind_run_receipt(
                    hidden_manifest=manifest,
                    condition_outputs=outputs,
                    run_id="r3",
                    executed_at="2026-09-24T17:12:00Z",
                    evaluator="other",
                    required_conditions=("A", "B"),
                )


if __name__ == "__main__":
    unittest.main()
