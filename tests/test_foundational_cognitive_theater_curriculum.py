from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_worker import roadmap_issue_order

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class FoundationalCognitiveTheaterCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_CURRICULUM.json")

    def test_four_foundational_faces_are_present_and_hypotheses(self):
        faces={x["id"]:x for x in self.c["faces"]}
        self.assertEqual(
            set(faces),
            {"ENGLISH","JAPANESE","BRAZILIAN_PORTUGUESE","MATHEMATICS"},
        )
        for face in faces.values():
            self.assertEqual(face["status"], "HYPOTHESIS_UNDER_TEST")

    def test_canonical_didactic_lineage_exists_locally(self):
        for rel in self.c["canonical_donor_lineage"]:
            self.assertTrue((ROOT/rel).is_file(), rel)

    def test_theater_is_not_translation(self):
        inv=set(self.c["noncollapse"])
        for required in (
            "TRANSLATION!=UNDERSTANDING",
            "ENGLISH_SURFACE!=SEMANTIC_OBJECT",
            "CULTURAL_HYPOTHESIS!=CULTURAL_ESSENCE",
            "FORMAL_SYMBOL_MATCH!=PROOF",
            "REGISTER!=AUTHORITY",
        ):
            self.assertIn(required, inv)
        self.assertIn("participants", self.c["theater_episode_schema"]["required_fields"])
        self.assertIn("local_knowledge_fields", self.c["theater_episode_schema"]["required_fields"])
        self.assertIn("temporal_sequence", self.c["theater_episode_schema"]["required_fields"])
        self.assertIn("face_specific_residuals", self.c["theater_episode_schema"]["required_fields"])

    def test_temporal_religion_kfs_science_are_axes_not_literal_identity(self):
        self.assertTrue(self.c["temporal_axes"]["orthogonal_not_identity"])
        self.assertIn("provenance", self.c["temporal_axes"]["past_religion"])
        self.assertIn("Knowledge Field State", self.c["temporal_axes"]["now_kfs"])
        self.assertIn("reopening", self.c["temporal_axes"]["future_science"])

    def test_current_roadmap_routes_foundation_before_deeper_semantic_targets(self):
        order=roadmap_issue_order((ROOT/"docs/ISSUE_ROADMAP.md").read_text(encoding="utf-8"))
        foundation=self.c["issue_ref"]
        self.assertIn(foundation, order)
        for downstream in (169, 73, 18):
            self.assertIn(downstream, order)
            self.assertLess(order.index(foundation), order.index(downstream))

    def test_internalization_still_requires_source_removal_and_external_evaluation(self):
        order=self.c["experiment_order"]
        self.assertLess(order.index("CAPABILITY_SPECIFIC_DONOR_SOURCE_REMOVAL"), order.index("EXTERNAL_EVALUATION"))
        self.assertEqual(order[-1], "BOUNDED_INTERNALIZATION_RECEIPT_OR_WITHHOLD")
        self.assertIn("EVALUATOR_CUSTODY", self.c["external_roles_preserved"])
        self.assertFalse(self.c["promotion_authority"])
        self.assertFalse(self.c["truth_authority"])

if __name__ == "__main__":
    unittest.main()
