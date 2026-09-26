from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class WWWMindProspectivePrefreezeTests(unittest.TestCase):
    def test_prefreeze_keeps_claim_boundary(self):
        obj=json.loads(
            (ROOT/"kernel/development/WWW_MIND_PROSPECTIVE_1_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(obj["status"],"PREFROZEN_BEFORE_EXTERNAL_NETWORK_RETURN")
        self.assertFalse(obj["independent_evaluative_return"])
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["promotion_authority"])
        self.assertIn("AGI",obj["claim_fence"])
        self.assertIn("GLOBAL_SUBJECT_CLAIM_FALSE",obj["pass_requires"])


    def test_episode2_prefreeze_changes_only_external_center_discovery_basis(self):
        obj=json.loads(
            (ROOT/"kernel/development/WWW_MIND_PROSPECTIVE_2_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(obj["status"],"PREFROZEN_BEFORE_EXTERNAL_NETWORK_RETURN")
        self.assertEqual(
            obj["prior_episode"]["failure"],
            "INSUFFICIENT_EXTERNAL_INDEXED_CENTERS",
        )
        adapter=obj["adapter"]
        self.assertEqual(
            adapter["relaxation_rule"],
            "HIGH_FIDELITY_FIRST_THEN_TWO_ANCHOR_PROJECTIONS_FROM_LEARNER_STUDY_TERMS_ONLY",
        )
        self.assertFalse(adapter["host_added_synonyms"])
        self.assertFalse(adapter["one_token_selected_study_search"])
        self.assertEqual(adapter["minimum_selected_study_relevance_matches"],2)
        self.assertFalse(obj["independent_evaluative_return"])
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["promotion_authority"])
        self.assertIn("AGI",obj["claim_fence"])

    def test_adapter_is_fixed_transport_not_shell(self):
        src=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8").lower()
        self.assertIn('api_origin = "https://api.github.com"',src)
        for forbidden in ("subprocess","os.system","shell=true","eval(","exec("):
            self.assertNotIn(forbidden,src)

    def test_selected_study_gate_requires_relevance_receipt(self):
        src=(ROOT/"scripts/evaluate_www_mind_episode.py").read_text(encoding="utf-8")
        self.assertIn("selected_study_relevance_verified",src)
        self.assertIn("EPISODE1_SELECTED_STUDY_RELEVANCE_UNVERIFIED",src)
        self.assertIn("EPISODE2_SELECTED_STUDY_RELEVANCE_UNVERIFIED",src)
        self.assertIn("relevance_filter_applied",src)
        self.assertIn("relevance_matches",src)

    def test_worker_preserves_relevance_withhold_receipt(self):
        workflow=(ROOT/".github/workflows/minerva-autonomous-worker.yml").read_text(encoding="utf-8")
        self.assertIn("Record episode-1 relevance WITHHOLD",workflow)
        self.assertIn("Record episode-2 relevance WITHHOLD",workflow)
        self.assertIn("NETWORK_RELEVANCE_WITHHOLD.json",workflow)
        self.assertIn("WITHHOLD_NO_RELEVANT_EXTERNAL_SOURCES",workflow)
        self.assertIn("steps.network2.outputs.has_sources == 'true'",workflow)

    def test_structural_evaluator_cannot_promote(self):
        src=(ROOT/"scripts/evaluate_www_mind_episode.py").read_text(encoding="utf-8")
        self.assertIn('"promotion_authority":False',src)
        self.assertIn('"truth_authority":False',src)
        self.assertIn('"agi_claim":False',src)
        self.assertIn('"global_subject_claim":False',src)


if __name__=="__main__":
    unittest.main()
