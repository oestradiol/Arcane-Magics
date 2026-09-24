from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    INVALID_LABEL,
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
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


class AutonomousGovernanceTests(unittest.TestCase):
    def test_merge_without_explicit_review_return_does_not_train(self):
        state = empty_state()
        history = [{
            "number": 201,
            "title": "venus: autonomous cycle issue-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T00:00:00Z",
            "labels": [],
        }]
        updated = update_from_cycle_prs(state, history)
        self.assertEqual(updated.kind_useful["ISSUE"], 0)
        self.assertEqual(updated.kind_unhelpful["ISSUE"], 0)
        self.assertEqual(updated.seen_review_prs, ())

    def test_close_without_explicit_review_return_does_not_train(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "labels": [],
            }],
        )
        self.assertEqual(updated.kind_useful["PR"], 0)
        self.assertEqual(updated.kind_unhelpful["PR"], 0)

    def test_explicit_positive_review_return_updates_once(self):
        history = [{
            "number": 203,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
            "labels": [{"name": POSITIVE_LABEL}],
        }]
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(updated.kind_useful["ISSUE"], 1)
        again = update_from_cycle_prs(updated, history)
        self.assertEqual(again.kind_useful["ISSUE"], 1)

    def test_explicit_negative_review_return_updates_unhelpful(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 204,
                "title": "venus: autonomous cycle pr-100",
                "state": "OPEN",
                "mergedAt": None,
                "labels": [{"name": NEGATIVE_LABEL}],
            }],
        )
        self.assertEqual(updated.kind_unhelpful["PR"], 1)
        self.assertEqual(updated.kind_useful["PR"], 0)

    def test_invalid_review_return_consumes_episode_without_reward(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 205,
                "title": "venus: autonomous cycle issue-31",
                "state": "OPEN",
                "labels": [{"name": INVALID_LABEL}],
            }],
        )
        self.assertIn(205, updated.seen_review_prs)
        self.assertEqual(updated.kind_useful["ISSUE"], 0)
        self.assertEqual(updated.kind_unhelpful["ISSUE"], 0)

    def test_conflicting_review_labels_do_not_train(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 206,
                "title": "venus: autonomous cycle issue-31",
                "state": "OPEN",
                "labels": [{"name": POSITIVE_LABEL}, {"name": NEGATIVE_LABEL}],
            }],
        )
        self.assertEqual(updated.seen_review_prs, ())
        self.assertEqual(updated.kind_useful["ISSUE"], 0)

    def test_v01_merge_counts_do_not_migrate_as_reward(self):
        old = {
            "schema": "Venus.AutonomousLearningState.v0.1",
            "seen_cycle_prs": [1, 2],
            "kind_success": {"ISSUE": 7, "PR": 3},
            "kind_failure": {"ISSUE": 2, "PR": 1},
        }
        migrated = from_json(old)
        self.assertEqual(migrated.kind_useful["ISSUE"], 0)
        self.assertEqual(migrated.kind_unhelpful["ISSUE"], 0)
        self.assertEqual(migrated.seen_review_prs, ())

    def test_open_cycle_marks_original_target_recent(self):
        markers = target_markers([{
            "number": 207,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
        }])
        self.assertEqual(markers, (("ISSUE", 72),))

    def test_returned_utility_can_override_roadmap_prior(self):
        items = (
            WorkItem("ISSUE", 31, "roadmap issue"),
            WorkItem("PR", 901, "returned-useful pr"),
        )
        chosen = choose_target(
            items,
            roadmap_text="#31",
            kind_utility={"ISSUE": -1.0, "PR": 1.0},
        )
        self.assertEqual(chosen.kind, "PR")

    def test_workflow_has_no_self_merge_release_close_or_secret_path(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        forbidden = (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "gh pr edit",
            "gh issue edit",
            "--add-label",
            "venus-return-useful",
            "venus-return-unhelpful",
            "venus-return-invalid",
            "secrets.",
            "workflow_run:",
        )
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_workflow_only_creates_draft_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)

    def test_workflow_fetches_external_review_labels(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("mergedAt,closedAt,labels", text)

    def test_workflow_runs_safety_tests_before_git_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        tests_at = text.index("Verify bounded autonomy safety surface")
        push_at = text.index("git push origin")
        self.assertLess(tests_at, push_at)

    def test_learning_state_is_not_truth_or_authority(self):
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
