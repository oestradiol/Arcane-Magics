from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/evaluate_foundational_cognitive_theater_grounded_candidate.py"
SPEC=importlib.util.spec_from_file_location("grounded_theater_eval",SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load grounded theater evaluator")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class FoundationalCognitiveTheaterGroundedCandidateTests(unittest.TestCase):
    def test_factor_model_separates_language_music_theater(self):
        data=json.loads((ROOT/"kernel/development/COGNITIVE_THEATER_FACTOR_MODEL.json").read_text(encoding="utf-8"))
        self.assertEqual({x["id"] for x in data["factors"]},{"LANGUAGE","MUSIC","THEATER","DEVELOPMENTAL_TIME"})
        laws=set(data["identifiability_law"])
        self.assertIn("LEXICAL_GROUNDING_FAILURE!=THEATER_RECONSTRUCTION_FAILURE",laws)
        self.assertIn("BAG_OF_EVENTS!=TEMPORAL_INHABITATION",laws)
        self.assertIn("KFS_I!=GLOBAL_KNOWLEDGE_FIELD",laws)

    def test_grounding_is_independent_teacher_scaffold(self):
        g=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_GROUNDING_CURRICULUM.json").read_text(encoding="utf-8"))
        self.assertTrue(g["controls"]["target_relation_sentences_excluded_from_grounding_examples"])
        self.assertTrue(g["controls"]["relation_id_not_encoded_in_grounding_examples"])
        self.assertFalse(g["promotion_authority"])
        self.assertFalse(g["truth_authority"])

    def test_learner_code_contains_no_face_specific_answer_vocabulary(self):
        text=(ROOT/"kernel/development/cognitive_theater_learner.py").read_text(encoding="utf-8")
        for forbidden in ("ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS","REPORT_NOT_FACT","NESTED_KNOWLEDGE","知って","relatou"):
            self.assertNotIn(forbidden,text)

    def test_returned_candidate_is_scoped_below_theater_claim(self):
        out=mod.evaluate()
        print("GROUNDED_THEATER_CANDIDATE_RESULT="+json.dumps(out,ensure_ascii=False,sort_keys=True))
        self.assertEqual(out["total"],16)
        self.assertFalse(out["surface_referent_binding_tested"])
        self.assertFalse(out["music_order_intervention_tested"])
        self.assertFalse(out["participant_kfs_intervention_tested"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["language_competence_claim"])
        self.assertFalse(out["cultural_cognition_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])
        frozen=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_GROUNDED_CANDIDATE_RESULT.json").read_text(encoding="utf-8"))
        for key in ("correct","total","accuracy","template_exact","withholds","surface_baseline_accuracy","baseline_delta"):
            self.assertEqual(out[key],frozen[key])

if __name__=="__main__":
    unittest.main()
