from __future__ import annotations

from pathlib import Path
import unittest

from kernel.development.recursive_proposal import (
    EXPECTED_DONOR_GIT_BLOB_SHA,
    RecursiveProposalError,
    ResidualObservation,
    git_blob_sha,
    load_donor,
    search,
)


class GenericRecursiveProposalTests(unittest.TestCase):
    def test_exact_ancestral_generic_constructor_is_bound(self):
        donor = load_donor()
        self.assertIsNotNone(donor)
        from kernel.development import recursive_proposal as rp
        self.assertEqual(git_blob_sha(rp.DONOR), EXPECTED_DONOR_GIT_BLOB_SHA)

    def test_single_returned_constraint_withholds_and_asks_next_discriminator(self):
        out = search(
            [
                ResidualObservation(
                    features=(1, 0, 1),
                    desired_action=0,
                    provenance_id="returned-failure-1",
                )
            ]
        )
        self.assertEqual(
            out.status,
            "WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR",
        )
        self.assertGreater(len(out.exact_semantic_candidates), 1)
        self.assertIsNotNone(out.next_discriminator)
        self.assertFalse(out.hidden_evaluation_exposed)
        self.assertFalse(out.promotion_authority)

    def test_full_xor_returns_unique_bounded_program(self):
        rows = [
            ResidualObservation((0, 0), 0, "r00"),
            ResidualObservation((0, 1), 1, "r01"),
            ResidualObservation((1, 0), 1, "r10"),
            ResidualObservation((1, 1), 0, "r11"),
        ]
        out = search(rows)
        self.assertEqual(out.status, "UNIQUE_BOUNDED_PROGRAM_CANDIDATE")
        self.assertEqual(out.exact_semantic_candidates, ("XOR(x0,x1)",))
        self.assertIsNone(out.next_discriminator)

    def test_unexpressible_return_set_withholds(self):
        # XNOR is not present in the bounded RAW/AND/OR/XOR grammar.
        rows = [
            ResidualObservation((0, 0), 1, "r00"),
            ResidualObservation((0, 1), 0, "r01"),
            ResidualObservation((1, 0), 0, "r10"),
            ResidualObservation((1, 1), 1, "r11"),
        ]
        out = search(rows)
        self.assertEqual(out.status, "WITHHOLD_NO_EXPRESSIBLE_CANDIDATE")
        self.assertEqual(out.exact_semantic_candidates, ())
        self.assertIsNone(out.next_discriminator)

    def test_hidden_evaluation_cannot_enter_search(self):
        with self.assertRaisesRegex(RecursiveProposalError, "hidden evaluation"):
            search(
                [ResidualObservation((1, 0), 0, "returned")],
                hidden_evaluation_exposed=True,
            )

    def test_search_source_contains_no_edu17r1_answer_vocabulary(self):
        from kernel.development import recursive_proposal as rp
        text = Path(rp.__file__).read_text(encoding="utf-8").casefold()
        for forbidden in (
            "mention != incidence",
            "uncertainty-marker",
            "object-level unresolved",
            "typed_relation_admission_gate",
            "required_target_relation_present",
        ):
            self.assertNotIn(forbidden.casefold(), text)


if __name__ == "__main__":
    unittest.main()
