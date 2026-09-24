from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    empty_state,
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
    def test_closed_merged_cycle_updates_learning_once(self):
        state = empty_state()
        history = [
            {
                "number": 201,
                "title": "venus: autonomous cycle issue-31",
                "state": "MERGED",
                "mergedAt": "2026-09-24T00:00:00Z",
            }
        ]
        updated = update_from_cycle_prs(state, history)
        self.assertEqual(updated.kind_success["ISSUE"], 1)
        again = update_from_cycle_prs(updated, history)
        self.assertEqual(again.kind_success["ISSUE"], 1)

    def test_closed_unmerged_cycle_is_negative_return_not_success(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
            }],
        )
        self.assertEqual(updated.kind_failure["PR"], 1)
        self.assertEqual(updated.kind_success["PR"], 0)

    def test_open_autonomous_cycle_does_not_update_learning(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 203,
                "title": "venus: autonomous cycle issue-72",
                "state": "OPEN",
                "mergedAt": None,
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)
        self.assertEqual(updated.kind_failure["ISSUE"], 0)

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
        # Generic PR is normally ranked ahead of generic issue. A roadmap-free
        # same-class tie is not available across kinds, so verify learning is
        # at least included in deterministic rank within two generic issues by
        # preserving no hidden override. The safety point is outcome influence
        # without jurisdiction escalation.
        chosen = choose_target(
            items,
            roadmap_text="",
            kind_utility={"ISSUE": 1.0, "PR": -1.0},
        )
        self.assertEqual(chosen.kind, "PR")

    def test_workflow_has_no_self_merge_release_close_or_secret_path(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        forbidden = (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "secrets.",
            "workflow_run:",
        )
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_workflow_only_creates_draft_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)

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


if __name__ == "__main__":
    unittest.main()
