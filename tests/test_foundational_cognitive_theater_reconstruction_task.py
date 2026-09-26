from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class FoundationalCognitiveTheaterReconstructionTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_RECONSTRUCTION_TASK.json").read_text(encoding="utf-8"))

    def test_relation_id_and_teacher_target_are_hidden_at_evaluation(self):
        stages={x["id"]:x for x in self.task["stages"]}
        self.assertFalse(stages["B_HELDOUT_NATIVE_RECONSTRUCTION"]["relation_id_visible"])
        self.assertFalse(stages["C_FACTORIAL_CROSS_FACE_RECONSTRUCTION"]["relation_id_visible"])
        anti=set(self.task["anti_cheat"])
        self.assertIn("relation_id hidden at evaluation",anti)
        self.assertIn("teacher theater target inaccessible at evaluation",anti)

    def test_required_ablations_cover_theater_components(self):
        stages={x["id"]:x for x in self.task["stages"]}
        controls=set(stages["D_ABLATION"]["controls"])
        for required in (
            "surface-only prefrozen comparator",
            "translation-only alignment",
            "no participant/KFS indexing",
            "no temporal order",
            "counts-only structure",
        ):
            self.assertIn(required,controls)

    def test_internalization_requires_source_removal_and_fresh_return(self):
        stages={x["id"]:x for x in self.task["stages"]}
        req=set(stages["E_INTERNALIZATION"]["prerequisites"])
        self.assertIn("capability-specific teacher/parser source inaccessible",req)
        self.assertIn("fresh held-out return",req)
        self.assertFalse(self.task["promotion_authority"])
        self.assertFalse(self.task["truth_authority"])

if __name__=="__main__":
    unittest.main()
