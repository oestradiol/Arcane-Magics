from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    USEFUL_MARKER,
    UNHELPFUL_MARKER,
    empty_state,
    from_json,
    target_markers,
    update_from_cycle_prs,
)
from kernel.development.autonomous_worker import (
    WorkItem,
    choose_target,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


def external_review(body: str, *, login: str = "external-reviewer", review_id: int = 1):
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

    def test_v01_merge_derived_counts_do_not_migrate_as_reward(self):
        old = {
            "schema": "Venus.AutonomousLearningState.v0.1",
            "seen_cycle_prs": [1, 2],
            "kind_success": {"ISSUE": 9, "PR": 4},
            "kind_failure": {"ISSUE": 1, "PR": 2},
        }
        migrated = from_json(old)
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
        forbidden = (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "gh pr review",
            "gh pr edit",
            "gh issue edit",
            "secrets.",
            "workflow_run:",
        )
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_workflow_only_creates_draft_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)

    def test_workflow_cannot_fabricate_its_own_review_return_markers(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(USEFUL_MARKER, text)
        self.assertNotIn(UNHELPFUL_MARKER, text)

    def test_worker_recurrence_wakes_only_from_main_admission(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("branches: [main]", text)
        self.assertNotIn("branches: ['*']", text)

    def test_workflow_runs_safety_tests_before_git_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        tests_at = text.index("Verify bounded autonomy safety surface")
        push_at = text.index("git push origin")
        self.assertLess(tests_at, push_at)

    def test_learning_state_is_committed_but_not_authority(self):
        obj = json.loads(
            (ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(obj["promotion_authority"])
        self.assertFalse(obj["merge_authority"])
        self.assertFalse(obj["truth_authority"])


if __name__ == "__main__":
    unittest.main()
