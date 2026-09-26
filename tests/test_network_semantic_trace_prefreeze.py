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

    def test_worker_freezes_candidate_before_either_episode2_return(self):
        text=(ROOT/".github/workflows/minerva-autonomous-worker.yml").read_text(encoding="utf-8")
        freeze_at=text.index("Freeze state-owned relation-trace candidate")
        b1_at=text.index("Probe semantic-trace B1 abstraction")
        baseline_at=text.index("Execute memory-derived network query 2")
        candidate_at=text.index("Execute frozen semantic-trace query 2")
        compare_at=text.index("Compare semantic trace against frozen lexical baseline")
        self.assertLess(freeze_at, b1_at)
        self.assertLess(b1_at, candidate_at)
        self.assertLess(freeze_at, baseline_at)
        self.assertLess(baseline_at, compare_at)
        self.assertLess(candidate_at, compare_at)
        self.assertIn("steps.semantic_b1.outputs.passed == 'true'", text)
        self.assertIn("NETWORK_SEMANTIC_TRACE_ABSTRACTION_PROBE.json", text)
        self.assertIn("NETWORK_SEMANTIC_TRACE_RESULT.json", text)

    def test_worker_supplies_current_learning_state_to_trace_freeze_and_b1(self):
        text=(ROOT/".github/workflows/minerva-autonomous-worker.yml").read_text(encoding="utf-8")
        freeze=text.split("Freeze state-owned relation-trace candidate",1)[1].split("Probe semantic-trace B1 abstraction",1)[0]
        b1=text.split("Probe semantic-trace B1 abstraction",1)[1].split("Execute memory-derived network query 2",1)[0]
        self.assertIn("--learning-state /tmp/minerva/LEARNING_STATE.json",freeze)
        self.assertIn("--learning-state /tmp/minerva/LEARNING_STATE.json",b1)

    def test_prefreeze_separates_three_burdens(self):
        p=json.loads((ROOT/"kernel/development/NETWORK_SEMANTIC_TRACE_PREFREEZE.json").read_text(encoding="utf-8"))
        self.assertIn("B1_ABSTRACTION",p["burden_scope"])
        self.assertIn("B2_CAUSAL_USE",p["burden_scope"])
        self.assertIn("B3_INTERNALIZATION",p["burden_scope"])
        self.assertIn("B2_RETURNED_GAIN!=B3_INTERNALIZATION",p["noncollapse"])

    def test_abstraction_probe_is_nuisance_invariant_and_relevant_sensitive(self):
        text=(ROOT/"scripts/evaluate_network_semantic_trace_abstraction.py").read_text(encoding="utf-8")
        self.assertIn("source_order_invariant",text)
        self.assertIn("opaque_source_identity_invariant",text)
        self.assertIn("relevant_anchor_perturbation_changes_trace",text)
        self.assertIn("general_semantics_claim",text)
        self.assertIn("internalization_claim",text)

if __name__=="__main__":
    unittest.main()
