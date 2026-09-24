from __future__ import annotations

import unittest

from kernel.development.autonomous_problem_formation import (
    bind_problem_to_carriers,
    form_problem,
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


if __name__ == "__main__":
    unittest.main()
