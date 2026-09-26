from __future__ import annotations
import importlib.util, json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("fresh3_eval",ROOT/"scripts/evaluate_cognitive_theater_relational_graph_fresh3.py")
if SPEC is None or SPEC.loader is None: raise RuntimeError("fresh3")
m=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m)

class CognitiveTheaterFresh3Tests(unittest.TestCase):
    def test_prefreeze_has_no_fresh2_heldout_reuse(self):
        pre=json.loads((ROOT/"kernel/development/COGNITIVE_THEATER_RELATIONAL_GRAPH_FRESH3_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertEqual(pre["status"],"PREFROZEN_AFTER_FRESH2_BEFORE_FRESH3_RESULT")
        self.assertIn("No Fresh2 heldout row is reused",pre["freshness_rule"])

    def test_pairwise_scaffold_has_no_face_or_role_semantics(self):
        text=(ROOT/"kernel/development/cognitive_theater_relational_graph.py").read_text(encoding="utf-8")
        for forbidden in ("ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS","base_knower","meta_knower","ignorant","receiver_knower","excluded","知って","sabe","tells"):
            self.assertNotIn(forbidden,text)

    def test_three_comparators_return_without_claim_promotion(self):
        out=m.evaluate()
        print("COGNITIVE_THEATER_FRESH3_RESULT="+json.dumps(out,ensure_ascii=False,sort_keys=True))
        for key in ("count_only","unary_ordered","pairwise_relational"):
            self.assertEqual(out[key]["total"],16)
        self.assertFalse(out["independent_external_evaluation"])
        self.assertFalse(out["general_theater_claim"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])

if __name__=="__main__":
    unittest.main()
