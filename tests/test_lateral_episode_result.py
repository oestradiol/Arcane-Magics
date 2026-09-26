from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"kernel/development/LATERAL_EPISODE_1_RESULT.json"
PROPOSAL=ROOT/"autonomy/evidence/lateral/169/episode-1-proposal.json"


class LateralEpisodeResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=json.loads(RESULT.read_text(encoding="utf-8"))
        cls.proposal=json.loads(PROPOSAL.read_text(encoding="utf-8"))

    def test_bounded_lateral_gain_is_exactly_fenced(self):
        self.assertEqual(
            self.result["status"],
            "PASS_BOUNDED_LATERAL_MISSING_COORDINATE",
        )
        self.assertEqual(self.result["selected_face"],"path_topology")
        self.assertGreater(
            self.result["holdout_accuracy"]["lateral"],
            self.result["holdout_accuracy"]["relation_expanded"],
        )
        self.assertGreater(
            self.result["holdout_accuracy"]["lateral"],
            self.result["holdout_accuracy"]["relation_basic"],
        )
        self.assertFalse(self.result["internalization_claim"])
        self.assertFalse(self.result["promotion_authority"])

    def test_hidden_reveal_followed_prediction_freeze(self):
        self.assertEqual(
            self.result["proposal_blob_sha"],
            "f78209434a6820ca369751ec2eeba5baf98460ac",
        )
        self.assertFalse(self.proposal["holdout_label_accessed"])
        self.assertEqual(len(self.proposal["holdout_predictions"]),7)

    def test_cross_face_residual_is_preserved(self):
        self.assertEqual(
            self.result["cross_face_residual_ids"],
            [153,162,170,172],
        )

if __name__=="__main__":
    unittest.main()
