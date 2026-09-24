from __future__ import annotations

from pathlib import Path
import unittest

from kernel.development.generic_residual_search import (
    GenericSearchError,
    ResidualObservation,
    search,
)
from scripts.audit_generic_search_internalization import audit


class GenericResidualSearchTests(unittest.TestCase):
    def test_one_observation_withholds_and_asks_for_discriminator(self):
        out = search([ResidualObservation((1, 0, 1), 0, "returned-1")])
        self.assertEqual(
            out.status,
            "WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR",
        )
        self.assertGreater(len(out.exact_semantic_candidates), 1)
        self.assertIsNotNone(out.next_discriminator)
        self.assertFalse(out.hidden_evaluation_exposed)
        self.assertFalse(out.promotion_authority)

    def test_full_xor_table_identifies_one_program(self):
        rows = [
            ResidualObservation((0, 0), 0, "r00"),
            ResidualObservation((0, 1), 1, "r01"),
            ResidualObservation((1, 0), 1, "r10"),
            ResidualObservation((1, 1), 0, "r11"),
        ]
        out = search(rows)
        self.assertEqual(out.status, "UNIQUE_BOUNDED_PROGRAM_CANDIDATE")
        self.assertEqual(out.exact_semantic_candidates, ("XOR(x0,x1)",))

    def test_xnor_is_outside_bounded_one_step_grammar(self):
        rows = [
            ResidualObservation((0, 0), 1, "r00"),
            ResidualObservation((0, 1), 0, "r01"),
            ResidualObservation((1, 0), 0, "r10"),
            ResidualObservation((1, 1), 1, "r11"),
        ]
        out = search(rows)
        self.assertEqual(out.status, "WITHHOLD_NO_EXPRESSIBLE_CANDIDATE")

    def test_hidden_evaluation_is_rejected(self):
        with self.assertRaisesRegex(GenericSearchError, "hidden evaluation"):
            search(
                [ResidualObservation((0, 1), 1, "r")],
                hidden_evaluation_exposed=True,
            )

    def test_source_contains_no_edu17r1_answer_vocabulary_or_runtime_donor_import(self):
        from kernel.development import generic_residual_search as module

        text = Path(module.__file__).read_text(encoding="utf-8").casefold()
        for forbidden in (
            "mention != incidence",
            "uncertainty-marker",
            "object-level unresolved",
            "typed_relation_admission_gate",
            "required_target_relation_present",
            "historical-runtime",
            "grammar_expansion.py",
        ):
            self.assertNotIn(forbidden.casefold(), text)

    def test_r193_internalization_audit_passes_without_authoring_repair(self):
        out = audit()
        self.assertTrue(all(out["semantic_equivalence_by_width"].values()))
        self.assertTrue(out["isolated_without_historical_scaffold"])
        self.assertFalse(out["source_runtime_dependency"])
        self.assertEqual(
            out["receipt"]["status"],
            "PASS_BOUNDED_SCAFFOLD_INTERNALIZATION",
        )
        self.assertFalse(out["repair_candidate_authored"])
        self.assertFalse(out["hidden_evaluation_exposed"])
        self.assertFalse(out["promotion_authority"])


if __name__ == "__main__":
    unittest.main()
