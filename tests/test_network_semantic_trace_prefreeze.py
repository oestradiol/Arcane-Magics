from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class NetworkSemanticTracePrefreezeTests(unittest.TestCase):
    def test_prefreeze_keeps_lexical_baseline_and_candidate_parallel(self):
        p=json.loads((ROOT/"kernel/development/NETWORK_SEMANTIC_TRACE_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertEqual(p["status"],"PREFROZEN_BEFORE_CANDIDATE_EPISODE2_RETURN")
        self.assertIn("same episode-1 returned encounter set",p["matched_conditions"])
        self.assertTrue(p["candidate"]["freeze_before_candidate_return"])
        self.assertFalse(p["independent_evaluation"])
        self.assertFalse(p["promotion_authority"])

    def test_state_is_owned_but_not_a_success_claim(self):
        s=json.loads((ROOT/"kernel/development/NETWORK_SEMANTIC_TRACE_SEARCH_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(s["semantics_owner"],"LEARNER_STATE")
        self.assertFalse(s["future_return_input"])
        self.assertFalse(s["hidden_evaluation_input"])
        self.assertFalse(s["promotion_authority"])
        self.assertGreaterEqual(len(s["candidate_configs"]),3)

    def test_adapter_admits_state_owned_trace_authorship_without_authority(self):
        text=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8")
        self.assertIn("LEARNER_DERIVED_FROM_STATE_OWNED_RELATION_TRACE",text)
        self.assertIn("query execution owner must remain external",text)

if __name__=="__main__":
    unittest.main()
