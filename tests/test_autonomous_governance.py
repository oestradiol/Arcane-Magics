from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    METHODS,
    USEFUL_MARKER,
    UNHELPFUL_MARKER,
    active_autonomous_cycle,
    empty_state,
    from_json,
    target_barriers,
    target_markers,
    update_from_cycle_prs,
)
from kernel.development.autonomous_worker import (
    WorkItem,
    choose_target,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/minerva-autonomous-worker.yml"


def external_review(body: str, *, login: str = "oestradiol", review_id: int = 1):
    return {
        "id": review_id,
        "body": body,
        "author": {"login": login},
        "submittedAt": "2026-09-24T00:00:00Z",
    }


class AutonomousGovernanceTests(unittest.TestCase):
    def test_merge_without_explicit_review_return_does_not_update_learning(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 201,
                "title": "venus: autonomous cycle issue-31",
                "state": "MERGED",
                "mergedAt": "2026-09-24T00:00:00Z",
                "reviews": [],
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)
        self.assertEqual(updated.kind_failure["ISSUE"], 0)

    def test_close_without_explicit_review_return_does_not_count_as_failure(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "reviews": [],
            }],
        )
        self.assertEqual(updated.kind_failure["PR"], 0)

    def test_explicit_external_useful_review_updates_once(self):
        history = [{
            "number": 203,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
            "reviews": [external_review(USEFUL_MARKER, review_id=77)],
        }]
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(updated.kind_success["ISSUE"], 1)
        again = update_from_cycle_prs(updated, history)
        self.assertEqual(again.kind_success["ISSUE"], 1)

    def test_explicit_external_unhelpful_review_updates_failure(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 204,
                "title": "venus: autonomous cycle pr-99",
                "state": "OPEN",
                "mergedAt": None,
                "reviews": [external_review(UNHELPFUL_MARKER, review_id=78)],
            }],
        )
        self.assertEqual(updated.kind_failure["PR"], 1)
        self.assertEqual(updated.kind_success["PR"], 0)

    def test_self_authored_review_marker_is_not_a_return(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 205,
                "title": "venus: autonomous cycle issue-31",
                "state": "OPEN",
                "mergedAt": None,
                "reviews": [
                    external_review(USEFUL_MARKER, login="github-actions[bot]", review_id=79)
                ],
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)

    def test_unauthorized_external_reviewer_cannot_train_learning_state(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 299,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "reviews": [
                    external_review(
                        USEFUL_MARKER + "\nVENUS_METHOD_RETURN: REPRODUCTION: USEFUL",
                        login="random-commenter",
                        review_id=900,
                    )
                ],
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)
        self.assertEqual(updated.method_success["REPRODUCTION"], 0)
        self.assertEqual(updated.seen_return_ids, ())

    def test_explicit_authority_parameter_fails_closed_on_wildcard(self):
        with self.assertRaisesRegex(ValueError, "non-wildcard"):
            update_from_cycle_prs(
                empty_state(),
                [],
                authorized_logins={"*"},
            )

    def test_self_identity_cannot_be_authorized_as_external_return(self):
        with self.assertRaisesRegex(ValueError, "self-review"):
            update_from_cycle_prs(
                empty_state(),
                [],
                authorized_logins={"github-actions[bot]"},
            )

    def test_ambiguous_review_marker_is_ignored(self):
        body = USEFUL_MARKER + "\n" + UNHELPFUL_MARKER
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 206,
                "title": "venus: autonomous cycle issue-31",
                "state": "OPEN",
                "mergedAt": None,
                "reviews": [external_review(body, review_id=80)],
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)
        self.assertEqual(updated.kind_failure["ISSUE"], 0)

    def test_duplicate_same_method_marker_counts_once_per_return(self):
        body = "\n".join([
            "VENUS_METHOD_RETURN: REPRODUCTION: USEFUL",
            "VENUS_METHOD_RETURN: REPRODUCTION: USEFUL",
        ])
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 306,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "reviews": [external_review(body, review_id=806)],
            }],
        )
        self.assertEqual(updated.method_success["REPRODUCTION"], 1)
        self.assertEqual(len(updated.seen_return_ids), 1)

    def test_conflicting_same_method_markers_fail_closed(self):
        body = "\n".join([
            "VENUS_METHOD_RETURN: REPRODUCTION: USEFUL",
            "VENUS_METHOD_RETURN: REPRODUCTION: UNHELPFUL",
        ])
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 307,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "reviews": [external_review(body, review_id=807)],
            }],
        )
        self.assertEqual(updated.method_success["REPRODUCTION"], 0)
        self.assertEqual(updated.method_failure["REPRODUCTION"], 0)
        self.assertEqual(updated.seen_return_ids, ())

    def test_explicit_external_method_return_changes_only_method_learning(self):
        method = METHODS[0]
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 207,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "mergedAt": None,
                "reviews": [external_review(
                    f"VENUS_METHOD_RETURN: {method}: USEFUL",
                    review_id=81,
                )],
            }],
        )
        self.assertEqual(updated.method_success[method], 1)
        self.assertEqual(updated.kind_success["ISSUE"], 0)

    def test_method_return_from_self_is_ignored(self):
        method = METHODS[0]
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 208,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "mergedAt": None,
                "reviews": [external_review(
                    f"VENUS_METHOD_RETURN: {method}: USEFUL",
                    login="github-actions[bot]",
                    review_id=82,
                )],
            }],
        )
        self.assertEqual(updated.method_success[method], 0)

    def test_issue_comment_can_supply_external_method_return(self):
        method = METHODS[1]
        history = [{
            "_carrier_kind": "ISSUE",
            "number": 300,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "closedAt": None,
            "comments": [{
                "id": 991,
                "body": f"VENUS_METHOD_RETURN: {method}: USEFUL",
                "author": {"login": "oestradiol"},
                "createdAt": "2026-09-24T22:00:00Z",
            }],
        }]
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(updated.method_success[method], 1)
        self.assertEqual(len(updated.seen_return_ids), 1)
        self.assertTrue(updated.seen_return_ids[0].startswith("return:"))
        self.assertTrue(updated.seen_return_ids[0].endswith(f":method:0:{method}"))

    def test_same_review_across_rest_and_graphql_ids_counts_once(self):
        body = "VENUS_METHOD_RETURN: COMPARATOR_AUDIT: UNHELPFUL"
        rest = {
            "_carrier_kind": "PR",
            "number": 124,
            "title": "venus: autonomous cycle pr-106",
            "state": "CLOSED",
            "reviews": [{
                "id": 5310656803,
                "body": body,
                "author": {"login": "oestradiol"},
                "submittedAt": "2026-09-24T21:51:32Z",
            }],
        }
        graphql = {
            "_carrier_kind": "PR",
            "number": 124,
            "title": "venus: autonomous cycle pr-106",
            "state": "CLOSED",
            "reviews": [{
                "id": "PRR_kwDOR4bPY88AAAABPIoxIw",
                "body": body,
                "author": {"login": "oestradiol"},
                "submitted_at": "2026-09-24T21:51:32Z",
            }],
        }
        updated = update_from_cycle_prs(empty_state(), [rest, graphql])
        self.assertEqual(updated.method_failure["COMPARATOR_AUDIT"], 1)
        self.assertEqual(len(updated.seen_return_ids), 1)

    def test_same_text_at_distinct_return_times_remains_distinct(self):
        body = "VENUS_METHOD_RETURN: REPRODUCTION: USEFUL"
        carrier = {
            "_carrier_kind": "ISSUE",
            "number": 300,
            "title": "venus: autonomous cycle pr-107",
            "state": "CLOSED",
            "comments": [
                {
                    "id": 1,
                    "body": body,
                    "author": {"login": "oestradiol"},
                    "createdAt": "2026-09-24T22:00:00Z",
                },
                {
                    "id": 2,
                    "body": body,
                    "author": {"login": "oestradiol"},
                    "createdAt": "2026-09-24T22:05:00Z",
                },
            ],
        }
        updated = update_from_cycle_prs(empty_state(), [carrier])
        self.assertEqual(updated.method_success["REPRODUCTION"], 2)
        self.assertEqual(len(updated.seen_return_ids), 2)

    def test_missing_return_timestamp_fails_closed_for_learning_identity(self):
        carrier = {
            "_carrier_kind": "ISSUE",
            "number": 300,
            "title": "venus: autonomous cycle pr-107",
            "state": "OPEN",
            "comments": [{
                "id": 77,
                "body": "VENUS_METHOD_RETURN: REPRODUCTION: USEFUL",
                "author": {"login": "external-reviewer"},
            }],
        }
        updated = update_from_cycle_prs(empty_state(), [carrier])
        self.assertEqual(updated.method_success["REPRODUCTION"], 0)
        self.assertEqual(updated.seen_return_ids, ())

    def test_self_authored_issue_comment_is_not_learning_return(self):
        method = METHODS[1]
        history = [{
            "_carrier_kind": "ISSUE",
            "number": 301,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "comments": [{
                "id": 992,
                "body": f"VENUS_METHOD_RETURN: {method}: USEFUL",
                "author": {"login": "github-actions[bot]"},
                "createdAt": "2026-09-24T22:00:00Z",
            }],
        }]
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(updated.method_success[method], 0)

    def test_open_issue_cycle_is_global_no_reroll_barrier(self):
        history = [{
            "_carrier_kind": "ISSUE",
            "number": 302,
            "title": "venus: autonomous cycle pr-106",
            "state": "OPEN",
            "closedAt": None,
            "comments": [],
        }]
        self.assertTrue(active_autonomous_cycle(history))
        barriers = target_barriers(history)
        self.assertEqual(len(barriers), 1)
        self.assertEqual(barriers[0].cycle_carrier_kind, "ISSUE")
        self.assertEqual((barriers[0].kind, barriers[0].number), ("PR", 106))

    def test_open_cycle_is_global_no_reroll_barrier(self):
        history = [{
            "number": 209,
            "title": "venus: autonomous cycle issue-31",
            "state": "OPEN",
            "mergedAt": None,
            "closedAt": None,
        }]
        self.assertTrue(active_autonomous_cycle(history))
        barriers = target_barriers(history)
        self.assertEqual(len(barriers), 1)
        self.assertEqual((barriers[0].kind, barriers[0].number), ("ISSUE", 31))

    def test_resolved_cycle_retains_reopening_timestamp_without_becoming_reward(self):
        history = [{
            "number": 210,
            "title": "venus: autonomous cycle issue-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T21:00:00Z",
            "closedAt": "2026-09-24T21:00:00Z",
            "reviews": [],
        }]
        barriers = target_barriers(history)
        self.assertEqual(barriers[0].outcome_at, "2026-09-24T21:00:00Z")
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(updated.kind_success["ISSUE"], 0)

    def test_v01_merge_derived_learning_is_quarantined(self):
        migrated = from_json({
            "schema": "Venus.AutonomousLearningState.v0.1",
            "seen_cycle_prs": [1],
            "kind_success": {"ISSUE": 9, "PR": 4},
            "kind_failure": {"ISSUE": 1, "PR": 2},
        })
        self.assertEqual(migrated.kind_success["ISSUE"], 0)
        self.assertEqual(migrated.kind_failure["ISSUE"], 0)
        self.assertEqual(migrated.seen_return_ids, ())

    def test_open_cycle_marks_original_target_recent(self):
        markers = target_markers([{
            "number": 203,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
        }])
        self.assertEqual(markers, (("ISSUE", 72),))

    def test_returned_learning_can_break_equal_priority_tie(self):
        items = (
            WorkItem("ISSUE", 900, "generic issue"),
            WorkItem("PR", 901, "generic pr"),
        )
        chosen = choose_target(
            items,
            roadmap_text="",
            kind_utility={"ISSUE": 1.0, "PR": -1.0},
        )
        self.assertEqual(chosen.kind, "ISSUE")

    def test_workflow_has_no_self_merge_release_close_or_secret_path(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        forbidden = ("gh pr merge", "gh release create", "gh issue close", "secrets.", "workflow_run:")
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_workflow_creates_only_draft_handoff_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create --draft --base split/venus", text)
        self.assertIn("handoff/minerva-to-venus/", text)
        self.assertNotIn("--base main", text)

    def test_worker_is_global_observer_but_branch_local_author(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("git fetch origin \u0027+refs/heads/*:refs/remotes/origin/*\u0027", text)
        self.assertIn("ref: split/minerva", text)
        self.assertIn("git for-each-ref", text)
        self.assertIn("gh pr list --state all", text)
        self.assertIn("gh run list", text)
        self.assertIn("gh issue list --state open", text)

    def test_worker_has_wall_clock_budget(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("timeout-minutes: 30", text)

    def test_local_machine_verification_occurs_before_handoff_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        verify_at = text.index("Verify Minerva local machine")
        push_at = text.index("git push origin")
        self.assertLess(verify_at, push_at)
        self.assertIn("python -m unittest discover -s tests -p \u0027test_*.py\u0027", text)
        self.assertIn("audit_autonomy_safety_matrix.py", text)

    def test_bounded_cycle_occurs_before_handoff_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        cycle_at = text.index("Form bounded Minerva repository proposal")
        push_at = text.index("git push origin")
        self.assertLess(cycle_at, push_at)
        self.assertIn("run_venus_autonomous_cycle.py", text)
        self.assertIn("--learning-state kernel/development/AUTONOMOUS_LEARNING_STATE.json", text)
        self.assertIn("--developmental-parent-state kernel/development/EDU16_RECONSTRUCTED_STATE.json", text)
        self.assertIn("--current-state-receipt kernel/custody/R226_CURRENT_STATE_RECEIPT.json", text)

    def test_handoff_preserves_minerva_as_second_parent(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('git checkout -b "$branch" origin/split/venus', text)
        self.assertIn('git merge --no-ff -s ours --no-commit "$source_sha"', text)
        self.assertIn("Preserve Minerva as a second parent", text)

    def test_handoff_records_explicit_provenance_receipt(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("provenance/historical/handoffs", text)
        self.assertIn("\u0027source_layer\u0027:\u0027Minerva\u0027", text)
        self.assertIn("\u0027target_layer\u0027:\u0027Venus\u0027", text)
        self.assertIn("\u0027content_admission\u0027:\u0027proposal receipts only; no Minerva tree replacement\u0027", text)
        self.assertIn("\u0027authority\u0027:\u0027engineering candidate only; no Root promotion\u0027", text)

    def test_handoff_admits_proposal_receipts_not_minerva_tree(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("minerva-proposals/${GITHUB_RUN_ID}", text)
        self.assertIn("cycle.json", text)
        self.assertIn("problem.json", text)
        self.assertIn("proposed-learning-state.json", text)
        self.assertNotIn("git add kernel", text)

    def test_workflow_cannot_self_author_learning_return(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(USEFUL_MARKER, text)
        self.assertNotIn(UNHELPFUL_MARKER, text)
        self.assertNotIn("VENUS_METHOD_RETURN:", text)
        lowered = text.lower()
        self.assertNotIn("gh pr review", lowered)
        self.assertNotIn("gh pr edit", lowered)

    def test_retained_external_method_failure_is_canonical_learning_state(self):
        obj = json.loads(
            (ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn(
            "return:a44091dbba6e54ebc12cf8fa8952604bd5e0070758a365084cb47a253b28ace0:method:0:COMPARATOR_AUDIT",
            obj["seen_return_ids"],
        )
        self.assertEqual(obj["method_failure"]["COMPARATOR_AUDIT"], 1)
        self.assertEqual(obj["kind_failure"]["PR"], 0)


    def test_current_worker_does_not_write_runtime_successor_directly(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("cp /tmp/minerva/CYCLE.json kernel/", text)
        self.assertNotIn("git add kernel/development", text)
        self.assertNotIn("gh pr merge", text.lower())

    def test_minerva_to_venus_handoff_precedes_root_integration(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Scientific future discrimination belongs to the subsequent Venus → OFE handoff", text)
        self.assertIn("Root integration comes only after OFE", text)



if __name__ == "__main__":
    unittest.main()
