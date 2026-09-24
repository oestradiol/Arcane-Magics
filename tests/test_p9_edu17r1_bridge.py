from __future__ import annotations

import unittest

from kernel.development.audit_p9_edu17r1_bridge import audit


class P9EDU17R1BridgeAuditTests(unittest.TestCase):
    def test_bridge_withholds_without_neutral_incidence_operator(self):
        out = audit()
        self.assertEqual(out["residual"], "MENTION != INCIDENCE")
        self.assertEqual(out["status"], "WITHHOLD_NO_NEUTRAL_INCIDENCE_OPERATOR")
        self.assertEqual(out["semantic_relation_ops"], [])
        self.assertFalse(out["candidate_grammar_changes_event_semantics"])
        self.assertFalse(out["candidate_repair_emitted"])
        self.assertFalse(out["hidden_evaluation_exposed"])
        self.assertFalse(out["promotion_authority"])

    def test_p9_donor_remains_generic_capacity_search(self):
        out = audit()
        self.assertIn("SOURCE", out["event_ops"])
        self.assertIn("ASK_TRUSTED", out["event_ops"])
        self.assertIn("HYP", out["event_ops"])
        self.assertIn("source_indexed", out["mutation_axes"])
        self.assertIn("hypothesis_slots", out["mutation_axes"])

    def test_reopening_requires_neutral_relation_representation(self):
        out = audit()
        self.assertIn("neutral relation/incidence representation", out["next_reopening_condition"])


if __name__ == "__main__":
    unittest.main()
