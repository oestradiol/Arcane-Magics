from __future__ import annotations

import unittest

from kernel.development.audit_edu17r1_incidence_substrate import audit


class EDU17R1IncidenceSubstrateAuditTests(unittest.TestCase):
    def setUp(self):
        self.out = audit()

    def test_exact_ancestral_incidence_law_is_recollected(self):
        self.assertEqual(
            self.out["ancestral_incidence_law_sha256"],
            "99154d953f498be374b8af0fbc174ba658d0d52b1ccc684b2bbc09871ac52f3e",
        )
        self.assertTrue(
            self.out["ancestral_incidence_law_bound_in_ig10_recollection"]
        )
        self.assertTrue(self.out["formal_law_indexed_in_ig10_recollection"])

    def test_neutral_incidence_substrate_is_already_present(self):
        for key in (
            "live_law_exposes_neutral_relation_grammar",
            "ig1_returned_operator_semantics",
            "ig2_induced_incidence_basis",
            "ig3_generic_raw_carrier_scanner",
            "ig4_source_relation_inquiry",
            "u4_source_grounded_text_relations",
            "worldmirror_evidence_bound_relations",
            "historical_r194_target_label_free_grammar_expansion",
            "historical_r194_semantic_slots_are_caller_supplied",
            "historical_r194_constructed_executable_is_caller_supplied",
            "neutral_relation_incidence_substrate_present",
        ):
            self.assertTrue(self.out[key], key)

    def test_cross_layer_binder_remains_unadmitted(self):
        self.assertFalse(self.out["admitted_cross_layer_binder"])
        self.assertEqual(
            self.out["status"],
            "WITHHOLD_NEUTRAL_SUBSTRATE_PRESENT_CROSS_LAYER_BINDER_UNADMITTED",
        )
        self.assertIn("cross-layer incidence-binding", self.out["lowest_local_residual"])
        self.assertFalse(self.out["candidate_repair_emitted"])
        self.assertFalse(self.out["hidden_evaluation_exposed"])
        self.assertFalse(self.out["promotion_authority"])

    def test_audit_does_not_turn_donor_grammar_into_answer(self):
        self.assertEqual(self.out["residual"], "MENTION != INCIDENCE")
        self.assertIn("Encoding the EDU17R1 answer", self.out["reason"])


if __name__ == "__main__":
    unittest.main()
