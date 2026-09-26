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

    def test_current_roadmap_reprioritizes_only_after_foundation_bounded_pass(self):
        order=roadmap_issue_order((ROOT/"docs/ISSUE_ROADMAP.md").read_text(encoding="utf-8"))
        foundation=self.c["issue_ref"]
        self.assertIn(foundation, order)
        for downstream in (169, 73, 18):
            self.assertIn(downstream, order)

        # Developmental precedence is historical/causal, not a requirement that
        # every later live scheduling document keep #206 textually ahead forever.
        task=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_RECONSTRUCTION_TASK.json")
        returned=task["current_returned_disposition"]
        self.assertEqual(returned["G0_G1"], "PASS_BOUNDED_GROUNDING_AND_TEMPLATE")
        self.assertEqual(returned["G2"], "PASS_BOUNDED_INDEXED_BINDING")
        self.assertEqual(returned["G3"], "PASS_BOUNDED_SYMBOLIC_EVENT_ORDER")
        self.assertTrue(returned["G4"].startswith("PASS_BOUNDED_EXPLICIT_THEATER_STATE"))
        self.assertTrue(returned["G5_ablation"].startswith("PASS_BOUNDED_ISOLATED_SOURCE_REMOVAL"))
        self.assertTrue(returned["G6_internalization"].startswith("WITHHOLD_"))

    def test_internalization_still_requires_source_removal_and_external_evaluation(self):
        order=self.c["experiment_order"]
        self.assertLess(order.index("CAPABILITY_SPECIFIC_DONOR_SOURCE_REMOVAL"), order.index("EXTERNAL_EVALUATION"))
        self.assertEqual(order[-1], "BOUNDED_INTERNALIZATION_RECEIPT_OR_WITHHOLD")
        self.assertIn("EVALUATOR_CUSTODY", self.c["external_roles_preserved"])
        self.assertFalse(self.c["promotion_authority"])
        self.assertFalse(self.c["truth_authority"])

if __name__ == "__main__":
    unittest.main()
