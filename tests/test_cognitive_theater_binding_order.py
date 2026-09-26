from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/evaluate_cognitive_theater_binding_order.py"
SPEC=importlib.util.spec_from_file_location("binding_order_eval",SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load binding/order evaluator")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class CognitiveTheaterBindingOrderTests(unittest.TestCase):
    def test_prefreeze_contains_swapped_binding_and_order_controls(self):
        pre=json.loads((ROOT/"kernel/development/COGNITIVE_THEATER_BINDING_ORDER_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertEqual({x["id"] for x in pre["tasks"]},{"G2_PARTICIPANT_KFS_BINDING","G3_MUSIC_ORDER"})
        self.assertIn("alpha-rename participant/event tokens",pre["controls"])
        self.assertIn("same event inventory across order reversal",pre["controls"])

    def test_scaffold_contains_no_face_language_grammar(self):
        text=(ROOT/"kernel/development/cognitive_theater_binding_order.py").read_text(encoding="utf-8")
        for forbidden in ("ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS","knows","知って","sabe","before","after"):
            self.assertNotIn(forbidden,text)

    def test_return_is_bounded_and_non_authoritative(self):
        out=mod.evaluate()
        print("COGNITIVE_THEATER_BINDING_ORDER_RESULT="+json.dumps(out,ensure_ascii=False,sort_keys=True))
        self.assertEqual(out["total"],16)
        self.assertFalse(out["natural_reference_resolution_claim"])
        self.assertFalse(out["prosody_music_claim"])
        self.assertFalse(out["general_theater_claim"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])

if __name__=="__main__":
    unittest.main()
