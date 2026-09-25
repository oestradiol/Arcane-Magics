from __future__ import annotations

import unittest

from kernel.development.autonomous_problem_formation import (
    bind_problem_to_carriers,
    exhaustive_problem_scan,
    form_problem,
    resolve_problem,
    snapshot_to_incidence,
)
from kernel.development.autonomous_worker import WorkItem


class RecompiledU2ProblemFormationTests(unittest.TestCase):
    def test_problem_forms_before_any_target_is_selected(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 401, "ignored title",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
            WorkItem(
                "ISSUE", 402, "also ignored",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertEqual(problem.disposition, "FORMED_BOUNDED_PROBLEM")
        self.assertIn(
            "continuation_state_unresolved",
            problem.residual_coordinates,
        )
        self.assertEqual(len(problem.rivals), 2)
        self.assertEqual(
            problem.discriminator,
            "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
        )
        self.assertFalse(problem.carrier_binding_authority)

    def test_unknown_return_requires_fresh_external_return(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 401, "x",
                merge_state="UNKNOWN",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertTrue(problem.external_return_required)

    def test_dirty_return_can_be_locally_discriminated_without_minting_validation(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 401, "x",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertFalse(problem.external_return_required)
        self.assertFalse(problem.promotion_authority)

    def test_missing_reference_forms_problem_without_semantic_problem_label(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "ISSUE", 500, "arbitrary title",
                body="see #999",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertIn(
            "referenced_incidence_missing",
            problem.residual_coordinates,
        )
        self.assertEqual(problem.discriminator, "RESOLVE_REFERENCED_INCIDENCE")
        self.assertTrue(problem.external_return_required)

    def test_no_defect_field_stops(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 401, "anything",
                merge_state="CLEAN",
                updated_at="2026-09-24T23:00:00Z",
            ),
            WorkItem(
                "ISSUE", 402, "anything else",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertEqual(problem.disposition, "STOP_NO_CONSEQUENTIAL_RESIDUAL")
        self.assertEqual(problem.rivals, ())

    def test_title_changes_do_not_change_problem_partition(self):
        a = form_problem(snapshot_to_incidence((
            WorkItem(
                "PR", 401, "security emergency",
                merge_state="BLOCKED",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        b = form_problem(snapshot_to_incidence((
            WorkItem(
                "PR", 401, "bananas and orchestras",
                merge_state="BLOCKED",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        self.assertEqual(a.residual_coordinates, b.residual_coordinates)
        self.assertEqual(a.discriminator, b.discriminator)
        self.assertEqual(
            tuple(x.statement for x in a.rivals),
            tuple(x.statement for x in b.rivals),
        )

    def test_number_permutation_preserves_consequence_partition(self):
        a = form_problem(snapshot_to_incidence((
            WorkItem(
                "PR", 401, "x",
                merge_state="CONFLICTING",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        b = form_problem(snapshot_to_incidence((
            WorkItem(
                "PR", 987, "x",
                merge_state="CONFLICTING",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        self.assertEqual(a.residual_coordinates, b.residual_coordinates)
        self.assertEqual(a.discriminator, b.discriminator)
        self.assertEqual(a.external_return_required, b.external_return_required)

    def test_problem_receipt_has_no_carrier_or_promotion_authority(self):
        problem = form_problem(snapshot_to_incidence((
            WorkItem(
                "PR", 401, "x",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        self.assertFalse(problem.carrier_binding_authority)
        self.assertFalse(problem.promotion_authority)


    def test_formed_problem_binds_only_its_source_carrier(self):
        items = (
            WorkItem(
                "PR", 401, "first",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
            WorkItem(
                "ISSUE", 402, "second",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )
        problem = form_problem(snapshot_to_incidence(items))
        self.assertEqual(
            bind_problem_to_carriers(problem, items),
            (("PR", 401),),
        )

    def test_stop_problem_binds_no_carrier(self):
        items = (
            WorkItem(
                "PR", 401, "clean",
                merge_state="CLEAN",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )
        problem = form_problem(snapshot_to_incidence(items))
        self.assertEqual(problem.disposition, "STOP_NO_CONSEQUENTIAL_RESIDUAL")
        self.assertEqual(bind_problem_to_carriers(problem, items), ())

    def test_missing_problem_source_fails_closed_instead_of_reranking(self):
        original = (
            WorkItem(
                "PR", 401, "dirty",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )
        problem = form_problem(snapshot_to_incidence(original))
        unrelated = (
            WorkItem(
                "ISSUE", 999, "unrelated",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )
        self.assertEqual(bind_problem_to_carriers(problem, unrelated), ())


    def test_no_return_ablation_preserves_rivals_and_withholds(self):
        problem = form_problem(snapshot_to_incidence((
            WorkItem(
                "ISSUE", 500, "opaque",
                body="see #999",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        resolution = resolve_problem(problem)
        self.assertEqual(resolution.disposition, "WITHHOLD_EXTERNAL_RETURN")
        self.assertEqual(len(resolution.remaining_rival_ids), 2)
        self.assertFalse(resolution.external_return_consumed)

    def test_independent_return_reduces_prefrozen_rivals(self):
        problem = form_problem(snapshot_to_incidence((
            WorkItem(
                "ISSUE", 500, "opaque",
                body="see #999",
                updated_at="2026-09-24T23:00:00Z",
            ),
        )))
        resolution = resolve_problem(problem, returned_rival_id="r0")
        self.assertEqual(resolution.disposition, "RETURN_REDUCED_RIVALS")
        self.assertEqual(resolution.remaining_rival_ids, ("r0",))
        self.assertTrue(resolution.external_return_consumed)
        self.assertFalse(resolution.promotion_authority)

    def test_no_history_grammar_blocks_ordering_dependent_problem(self):
        problem = form_problem(
            snapshot_to_incidence((
                WorkItem(
                    "ISSUE", 500, "opaque",
                    updated_at=None,
                ),
            )),
            history_grammar_available=False,
        )
        self.assertEqual(problem.disposition, "WITHHOLD_NO_HISTORY_GRAMMAR")
        self.assertEqual(problem.rivals, ())

    def test_no_reference_closure_blocks_missing_incidence_problem(self):
        problem = form_problem(
            snapshot_to_incidence((
                WorkItem(
                    "ISSUE", 500, "opaque",
                    body="requires #999",
                    updated_at="2026-09-24T23:00:00Z",
                ),
            )),
            reference_closure_available=False,
        )
        self.assertEqual(problem.disposition, "WITHHOLD_NO_REFERENCE_CLOSURE")
        self.assertEqual(problem.rivals, ())

    def test_mature_exhaustive_comparator_matches_problem_partition(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 401, "opaque",
                merge_state="DIRTY",
                updated_at="2026-09-24T23:00:00Z",
            ),
            WorkItem(
                "ISSUE", 500, "opaque",
                body="requires #999",
                updated_at="2026-09-24T23:00:00Z",
            ),
        ))
        problem = form_problem(rows)
        comparator = exhaustive_problem_scan(rows)
        self.assertIsNotNone(comparator)
        stream_id, residuals = comparator
        self.assertEqual(problem.source_stream_ids, (stream_id,))
        self.assertEqual(problem.residual_coordinates, residuals)


    def test_unstable_pr_forms_continuation_problem(self):
        rows = snapshot_to_incidence((
            WorkItem(
                "PR", 166, "ignored",
                merge_state="UNSTABLE",
                updated_at="2026-09-25T00:20:00Z",
            ),
        ))
        problem = form_problem(rows)
        self.assertEqual(problem.disposition, "FORMED_BOUNDED_PROBLEM")
        self.assertIn("continuation_state_unresolved", problem.residual_coordinates)
        self.assertEqual(
            problem.discriminator,
            "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
        )
        self.assertTrue(problem.external_return_required)


if __name__ == "__main__":
    unittest.main()
