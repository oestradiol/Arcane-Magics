from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/evaluate_foundational_cognitive_theater_baseline.py"
SPEC=importlib.util.spec_from_file_location("theater_baseline", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load cognitive-theater evaluator")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class FoundationalCognitiveTheaterBaselineTests(unittest.TestCase):
    def test_checked_in_result_matches_recomputation(self):
        out=mod.evaluate()
        frozen=json.loads(
            (ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SURFACE_BASELINE_RESULT.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(out["status"], frozen["status"])
        self.assertEqual(out["native"]["correct"], frozen["native"]["correct"])
        self.assertEqual(out["native"]["total"], frozen["native"]["total"])
        self.assertEqual(out["native"]["accuracy"], frozen["native"]["accuracy"])
        self.assertEqual(out["native"]["withholds"], frozen["native"]["withholds"])
        self.assertEqual(out["leave_one_face_out"]["correct"], frozen["leave_one_face_out"]["correct"])
        self.assertEqual(out["leave_one_face_out"]["total"], frozen["leave_one_face_out"]["total"])
        self.assertEqual(out["leave_one_face_out"]["accuracy"], frozen["leave_one_face_out"]["accuracy"])
        self.assertEqual(out["leave_one_face_out"]["withholds"], frozen["leave_one_face_out"]["withholds"])

    def test_surface_baseline_failure_is_not_laundered_into_language_or_internalization_claim(self):
        out=mod.evaluate()
        self.assertEqual(out["status"], "FAIL_SURFACE_ONLY_CROSS_FACE_INVARIANCE")
        self.assertLess(out["leave_one_face_out"]["accuracy"], out["threshold"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["general_language_claim"])
        self.assertFalse(out["cultural_cognition_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])

    def test_japanese_leave_one_face_out_withholds_rather_than_inventing_alignment(self):
        out=mod.evaluate()
        ja=next(x for x in out["leave_one_face_out"]["per_face"] if x["face"]=="JAPANESE")
        self.assertEqual(ja["withholds"], ja["total"])

if __name__=="__main__":
    unittest.main()
