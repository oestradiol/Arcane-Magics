from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PREFREEZE=ROOT/"kernel/development/LATERAL_EPISODE_2_PREFREEZE.json"
PROPOSAL=ROOT/"autonomy/evidence/lateral/169/episode-2-proposal.json"
REVEAL=ROOT/"autonomy/evidence/lateral/169/episode-2-hidden-reveal.json"
RESULT=ROOT/"kernel/development/LATERAL_EPISODE_2_RESULT.json"

SPEC=importlib.util.spec_from_file_location(
    "score_lateral_episode2",
    ROOT/"scripts/score_lateral_episode2.py",
)
MOD=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class LateralEpisode2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pre=json.loads(PREFREEZE.read_text(encoding="utf-8"))
        cls.proposal=json.loads(PROPOSAL.read_text(encoding="utf-8"))
        cls.reveal=json.loads(REVEAL.read_text(encoding="utf-8"))
        cls.result=json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_exact_evaluator_output(self):
        computed=MOD.evaluate(
            self.pre,
            self.proposal,
            self.reveal,
            proposal_blob_sha=MOD.git_blob_sha(PROPOSAL),
        )
        self.assertEqual(computed,self.result)

    def test_reveal_is_bound_after_frozen_proposal(self):
        self.assertEqual(
            self.reveal["revealed_after_proposal_sha"],
            MOD.git_blob_sha(PROPOSAL),
        )
        self.assertFalse(self.proposal["holdout_labels_accessed"])
        self.assertFalse(self.reveal["learner_authored_labels"])

    def test_literal_threshold_pass_does_not_become_generalization(self):
        self.assertTrue(self.result["prefrozen_threshold_pass"])
        self.assertEqual(self.result["holdout_accuracy"],0.5)
        self.assertEqual(self.result["prior_transfer_accuracy"],0.125)
        self.assertEqual(self.result["absolute_improvement_over_prior_transfer"],0.375)
        self.assertFalse(self.result["generalization_claim"])
        self.assertFalse(self.result["general_lateralizer_claim"])

    def test_selected_revision_drops_lateral_face_and_matches_constant_control(self):
        self.assertEqual(self.result["selected_policy"]["faces"],["relation_expanded"])
        self.assertEqual(self.result["selected_lateral_faces"],[])
        self.assertEqual(
            self.result["lateral_face_status"],
            "NOT_RETAINED_BY_SELECTED_REVISION",
        )
        self.assertTrue(self.result["constant_prediction_holdout"])
        self.assertEqual(self.result["delta_over_best_constant"],0.0)
        self.assertEqual(
            self.result["post_reveal_discriminator_status"],
            "WITHHOLD_NO_GAIN_OVER_CONSTANT_CONTROL",
        )


if __name__=="__main__":
    unittest.main()
