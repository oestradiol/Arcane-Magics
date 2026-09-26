from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class FoundationalCognitiveTheaterReconstructionTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task=json.loads((ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_RECONSTRUCTION_TASK.json").read_text(encoding="utf-8"))
        cls.stages={x["id"]:x for x in cls.task["stages"]}

    def test_relation_id_and_teacher_target_are_hidden_after_grounding(self):
        for stage in ("G1_GROUNDED_TEMPLATE_RECONSTRUCTION","G2_THEATER_BINDING","G3_MUSIC_ORDER","G4_CROSS_FACE_COMPOSITION"):
            self.assertFalse(self.stages[stage]["relation_id_visible"])
        anti=set(self.task["anti_cheat"])
        self.assertIn("relation_id hidden at evaluation",anti)
        self.assertIn("teacher theater target inaccessible at evaluation",anti)

    def test_identifiability_repair_separates_grounding_from_theater(self):
        repair=self.task["identifiability_repair"]
        self.assertIn("lexical grounding",repair["problem"])
        self.assertIn("COGNITIVE_THEATER_FACTOR_MODEL.json",repair["factor_model_ref"])
        anti=set(self.task["anti_cheat"])
        self.assertIn("target relation sentences excluded from independent grounding curriculum",anti)
        self.assertIn("same atom inventory with different participant binding must remain distinguishable",anti)
        self.assertIn("same event inventory with different temporal order must remain distinguishable",anti)

    def test_required_ablations_cover_language_theater_and_music(self):
        controls=set(self.stages["G5_ABLATION"]["controls"])
        for required in (
            "surface-only prefrozen comparator",
            "translation-only alignment",
            "grounding-only without participant/KFS binding",
            "no participant/KFS indexing",
            "bag-of-events / no temporal order",
            "counts-only structure",
        ):
            self.assertIn(required,controls)

    def test_internalization_requires_source_removal_fresh_return_and_interventions(self):
        req=set(self.stages["G6_INTERNALIZATION"]["prerequisites"])
        self.assertIn("capability-specific teacher/parser/trainer source inaccessible",req)
        self.assertIn("fresh held-out return",req)
        self.assertIn("participant/KFS intervention pass",req)
        self.assertIn("temporal-order intervention pass",req)
        self.assertFalse(self.task["promotion_authority"])
        self.assertFalse(self.task["truth_authority"])

if __name__=="__main__":
    unittest.main()
