from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/evaluate_foundational_cognitive_theater_factorial_baseline.py"
SPEC=importlib.util.spec_from_file_location("theater_factorial",SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load theater factorial evaluator")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class FoundationalCognitiveTheaterFactorialTests(unittest.TestCase):
    def test_matched_structure_has_no_cardinality_label_leak(self):
        data=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_MATCHED_STRUCTURE.json").read_text(encoding="utf-8"))
        sigs={
            (
                len(row["roles"]),
                len(row["local_kfs"]),
                len(row["temporal_events"]),
                len(row["invariants"]),
            )
            for row in data["structures"]
        }
        self.assertEqual(sigs,{(3,3,4,3)})

    def test_factorial_folds_cover_every_relation_face_pair_once(self):
        pre=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_FACTORIAL_PREFREEZE.json").read_text(encoding="utf-8"))
        pairs=[tuple(pair) for fold in pre["folds"] for pair in fold]
        expected={(r,f) for r in pre["relations"] for f in pre["faces"]}
        self.assertEqual(set(pairs),expected)
        self.assertEqual(len(pairs),len(set(pairs)))

    def test_checked_result_matches_recomputation(self):
        out=mod.evaluate()
        frozen=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_FACTORIAL_BASELINE_RESULT.json").read_text(encoding="utf-8"))
        for key in ("status","correct","total","accuracy","withholds"):
            self.assertEqual(out[key],frozen[key])

    def test_factorial_baseline_cannot_mint_semantic_claim(self):
        out=mod.evaluate()
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["language_competence_claim"])
        self.assertFalse(out["cultural_cognition_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])

if __name__=="__main__":
    unittest.main()
