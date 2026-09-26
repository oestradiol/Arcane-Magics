from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("fresh2_eval",ROOT/"scripts/evaluate_cognitive_theater_binding_order_fresh2.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load fresh2 evaluator")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class CognitiveTheaterFresh2Tests(unittest.TestCase):
    def test_prefreeze_is_fresh_and_three_way(self):
        pre=json.loads((ROOT/"kernel/development/COGNITIVE_THEATER_BINDING_ORDER_FRESH2_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertEqual(pre["status"],"PREFROZEN_AFTER_G2_G3_FAILURE_BEFORE_FRESH2_RESULT")
        for task in pre["tasks"]:
            self.assertEqual(len(task["output_schema"]),3)
        self.assertIn("No row from COGNITIVE_THEATER_BINDING_ORDER_PREFREEZE.json is reused",pre["freshness_rule"])

    def test_ordered_scaffold_has_no_face_or_role_semantics(self):
        text=(ROOT/"kernel/development/cognitive_theater_ordered_binding.py").read_text(encoding="utf-8")
        for forbidden in ("ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS","base_knower","meta_knower","ignorant","first","middle","last","知って","sabe"):
            self.assertNotIn(forbidden,text)

    def test_result_is_comparative_not_a_theater_claim(self):
        out=mod.evaluate()
        print("COGNITIVE_THEATER_FRESH2_RESULT="+json.dumps(out,ensure_ascii=False,sort_keys=True))
        self.assertEqual(out["commutative"]["total"],16)
        self.assertEqual(out["ordered"]["total"],16)
        self.assertFalse(out["independent_external_evaluation"])
        self.assertFalse(out["general_theater_claim"])
        self.assertFalse(out["music_prosody_claim"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])

if __name__=="__main__":
    unittest.main()
