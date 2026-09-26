from __future__ import annotations

import unittest

from kernel.development.git_world_return import (
    GitCarrierSnapshot,
    GitWorldReturnError,
    form_git_check_problem,
    form_next_head_check_problem,
    freeze_git_world_request,
    observe_git_world_return,
    resolve_continuation_problem,
)


PROBLEM = {
    "problem_id": "git-world-problem",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "source_stream_ids": ["stream:pr"],
    "residual_coordinates": ["continuation_state_unresolved"],
    "discriminator": "OBSERVE_PR_CHECK_TERMINAL_STATE",
    "rivals": [
        {"rival_id": "r0", "statement": "current continuation fails under the repository checks"},
        {"rival_id": "r1", "statement": "the unresolved state is transient and later checks complete successfully"},
    ],
}


def snap(
    *,
    number=166,
    head="a" * 40,
    merge="CLEAN",
    updated="2026-09-25T00:20:00Z",
    run=100,
    status="in_progress",
    conclusion=None,
):
    return GitCarrierSnapshot(
        carrier_kind="PR",
        carrier_number=number,
        head_sha=head,
        merge_state=merge,
        updated_at=updated,
        check_run_id=run,
        check_status=status,
        check_conclusion=conclusion,
    )


class GitWorldReturnTests(unittest.TestCase):
    def request(self):
        return freeze_git_world_request(
            problem=PROBLEM,
            source_stream_id="stream:pr",
            snapshot=snap(),
        )

    def test_postfreeze_completed_success_is_typed_world_return(self):
        req = self.request()
        returned = observe_git_world_return(
            req,
            snap(
                updated="2026-09-25T00:25:00Z",
                status="completed",
                conclusion="success",
            ),
            observed_at="2026-09-25T00:25:01Z",
        )
        self.assertEqual(returned.source_id, "GITHUB_REPOSITORY_STATE")
        self.assertTrue(returned.independent_world_observation)
        self.assertIn("check_status", returned.changed_fields)
        self.assertFalse(returned.promotion_authority)

        resolution = resolve_continuation_problem(PROBLEM, req, returned)
        self.assertEqual(resolution.disposition, "RETURN_REDUCED_RIVALS")
        self.assertEqual(resolution.remaining_rival_ids, ("r1",))
        self.assertTrue(resolution.external_return_consumed)

    def test_same_state_replay_is_not_return(self):
        req = self.request()
        with self.assertRaisesRegex(GitWorldReturnError, "same-state"):
            observe_git_world_return(
                req,
                snap(),
                observed_at="2026-09-25T00:25:01Z",
            )

    def test_wrong_carrier_cannot_satisfy_request(self):
        req = self.request()
        with self.assertRaisesRegex(GitWorldReturnError, "carrier number"):
            observe_git_world_return(
                req,
                snap(number=999, updated="2026-09-25T00:25:00Z", status="completed"),
                observed_at="2026-09-25T00:25:01Z",
            )

    def test_changed_but_nonterminal_world_state_withholds(self):
        req = self.request()
        returned = observe_git_world_return(
            req,
            snap(
                head="b" * 40,
                updated="2026-09-25T00:23:00Z",
                run=101,
                status="in_progress",
            ),
            observed_at="2026-09-25T00:23:01Z",
        )
        resolution = resolve_continuation_problem(PROBLEM, req, returned)
        self.assertEqual(
            resolution.disposition,
            "WITHHOLD_CHANGED_BUT_NONTERMINAL",
        )
        self.assertEqual(resolution.remaining_rival_ids, ("r0", "r1"))

    def test_problem_source_must_be_prefrozen(self):
        with self.assertRaisesRegex(GitWorldReturnError, "prefrozen problem source"):
            freeze_git_world_request(
                problem=PROBLEM,
                source_stream_id="not-a-source",
                snapshot=snap(),
            )

    def test_local_execution_receipt_shape_cannot_be_used_as_snapshot(self):
        req = self.request()
        with self.assertRaises((AttributeError, GitWorldReturnError)):
            observe_git_world_return(
                req,
                {"receipt_id": "local", "effect_digest": "x"},  # type: ignore[arg-type]
                observed_at="2026-09-25T00:25:01Z",
            )


    def test_nonterminal_check_state_forms_problem_without_future_answer(self):
        problem = form_git_check_problem(snap(status="in_progress", conclusion=None))
        self.assertEqual(problem["disposition"], "FORMED_BOUNDED_PROBLEM")
        self.assertEqual(problem["residual_coordinates"], ("check_state_nonterminal",))
        self.assertEqual(problem["discriminator"], "OBSERVE_PR_CHECK_TERMINAL_STATE")
        self.assertEqual(
            tuple(x["rival_id"] for x in problem["rivals"]),
            ("r0", "r1"),
        )
        self.assertTrue(problem["external_return_required"])
        self.assertFalse(problem["promotion_authority"])

    def test_completed_check_state_does_not_invent_new_problem(self):
        problem = form_git_check_problem(
            snap(status="completed", conclusion="success")
        )
        self.assertEqual(problem["disposition"], "STOP_NO_CONSEQUENTIAL_RESIDUAL")
        self.assertEqual(problem["rivals"], ())

    def test_next_head_problem_freezes_without_future_answer(self):
        current = snap(status="completed", conclusion="failure")
        problem = form_next_head_check_problem(current)
        self.assertEqual(problem["discriminator"], "OBSERVE_NEXT_HEAD_CHECK_TERMINAL_STATE")
        self.assertEqual(problem["residual_coordinates"], ("next_head_check_unknown",))
        self.assertTrue(problem["external_return_required"])
        self.assertFalse(problem["promotion_authority"])

    def test_next_head_terminal_return_reduces_rivals(self):
        current = snap(status="completed", conclusion="failure")
        problem = form_next_head_check_problem(current)
        source = problem["source_stream_ids"][0]
        req = freeze_git_world_request(
            problem=problem,
            source_stream_id=source,
            snapshot=current,
        )
        returned = observe_git_world_return(
            req,
            snap(
                head="b" * 40,
                updated="2026-09-25T00:30:00Z",
                run=102,
                status="completed",
                conclusion="success",
            ),
            observed_at="2026-09-25T00:30:01Z",
        )
        resolution = resolve_continuation_problem(problem, req, returned)
        self.assertEqual(resolution.disposition, "RETURN_REDUCED_RIVALS")
        self.assertEqual(resolution.remaining_rival_ids, ("r1",))

    def test_next_head_same_head_withholds_even_if_check_changed(self):
        current = snap(status="completed", conclusion="failure")
        problem = form_next_head_check_problem(current)
        req = freeze_git_world_request(
            problem=problem,
            source_stream_id=problem["source_stream_ids"][0],
            snapshot=current,
        )
        returned = observe_git_world_return(
            req,
            snap(
                head=current.head_sha,
                updated="2026-09-25T00:30:00Z",
                run=103,
                status="completed",
                conclusion="success",
            ),
            observed_at="2026-09-25T00:30:01Z",
        )
        resolution = resolve_continuation_problem(problem, req, returned)
        self.assertEqual(resolution.disposition, "WITHHOLD_NEXT_HEAD_NOT_OBSERVED")

    def test_request_freezes_prior_check_conclusion_exactly(self):
        current = snap(status="completed", conclusion="failure")
        problem = form_next_head_check_problem(current)
        req = freeze_git_world_request(
            problem=problem,
            source_stream_id=problem["source_stream_ids"][0],
            snapshot=current,
        )
        self.assertEqual(req.frozen_check_conclusion, "failure")
        returned = observe_git_world_return(
            req,
            snap(
                head="b" * 40,
                updated="2026-09-25T00:30:00Z",
                run=102,
                status="completed",
                conclusion="failure",
            ),
            observed_at="2026-09-25T00:30:01Z",
        )
        self.assertEqual(returned.before["check_conclusion"], "failure")
        self.assertNotIn("check_conclusion", returned.changed_fields)


if __name__ == "__main__":
    unittest.main()
