from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("fresh4_eval",ROOT/"scripts/evaluate_cognitive_theater_joint_scene_fresh4.py")
if SPEC is None or SPEC.loader is None: raise RuntimeError("fresh4")
m=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m)

class CognitiveTheaterFresh4Tests(unittest.TestCase):
    def test_prefreeze_is_new(self):
        pre=json.loads((ROOT/"kernel/development/COGNITIVE_THEATER_JOINT_SCENE_FRESH4_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertEqual(pre["status"],"PREFROZEN_AFTER_FRESH3_BEFORE_FRESH4_RESULT")
        self.assertIn("No Fresh3 heldout surface is reused",pre["freshness_rule"])

    def test_joint_scaffold_has_no_face_or_role_semantics(self):
        text=(ROOT/"kernel/development/cognitive_theater_joint_scene.py").read_text(encoding="utf-8")
        for forbidden in ("ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS","base_knower","meta_knower","ignorant","source","receiver_knower","excluded","知って","sabe","tells"):
            self.assertNotIn(forbidden,text)

    def test_all_comparators_return_without_claim_promotion(self):
        out=m.evaluate()
        print("COGNITIVE_THEATER_FRESH4_RESULT="+json.dumps(out,ensure_ascii=False,sort_keys=True))
        for k in ("count_only","unary_ordered","pairwise_relational","joint_scene"): self.assertEqual(out[k]["total"],16)
        self.assertFalse(out["independent_external_evaluation"]); self.assertFalse(out["general_theater_claim"]); self.assertFalse(out["internalization_claim"]); self.assertFalse(out["promotion_authority"]); self.assertFalse(out["truth_authority"])

if __name__=="__main__": unittest.main()
