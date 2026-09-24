from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from kernel.runtime.calibrated_retrieval import LabeledExample, leave_one_out, predict
from scripts.run_edu17r1_semantic_ingress_search import run
from scripts.audit_edu17r1_semantic_ingress import audit

ROOT=Path(__file__).resolve().parents[1]
METHOD=ROOT/"kernel/development/EDU17R1_SEMANTIC_INGRESS_SELECTED_METHOD.json"


class EDU17R1SemanticIngressTests(unittest.TestCase):
    def test_public_method_search_reproduces_frozen_winner(self):
        out=run()
        self.assertEqual(out["winner"]["method"]["id"],"WORD_JACCARD_K3")
        self.assertEqual(out["winner"]["accuracy"],0.875)
        self.assertAlmostEqual(out["winner"]["macro_f1"],0.8333333333333333)
        self.assertFalse(out["hidden_evaluation_exposed"])

    def test_runtime_withholds_without_similarity(self):
        method=json.loads(METHOD.read_text(encoding="utf-8"))["method"]
        calibration=(
            LabeledExample("a","alpha beta","x","ret:a"),
            LabeledExample("b","gamma delta","y","ret:b"),
        )
        out=predict(method,calibration,"zzzz qqqq")
        self.assertIsNone(out.label)
        self.assertEqual(out.status,"WITHHOLD_NO_SIMILAR_RETURN")

    def test_freeze_audit_binds_candidate_and_receipt(self):
        out=audit()
        self.assertEqual(out["status"],"PASS_FROZEN_LEARNER_SIDE_PUBLIC_DEV_CANDIDATE")
        self.assertTrue(all(out["gates"].values()))
        self.assertFalse(out["hidden_evaluation_exposed"])
        self.assertFalse(out["promotion_authority"])


if __name__=="__main__":
    unittest.main()
