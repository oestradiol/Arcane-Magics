from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    empty_state,
    target_barriers,
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
        history = [{
            "number": 201,
            "title": "venus: autonomous cycle issue-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T21:00:00Z",
            "closedAt": "2026-09-24T21:00:00Z",
        }]
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
                "closedAt": "2026-09-24T21:00:00Z",
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
                "closedAt": None,
            }],
        )
        self.assertEqual(updated.kind_success["ISSUE"], 0)
        self.assertEqual(updated.kind_failure["ISSUE"], 0)

    def test_open_cycle_is_retained_as_target_barrier(self):
        history = [{
            "number": 203,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
            "closedAt": None,
        }]
        barriers = target_barriers(history)
        self.assertEqual(len(barriers), 1)
        self.assertEqual((barriers[0].kind, barriers[0].number), ("ISSUE", 72))
        self.assertIsNone(barriers[0].outcome_at)
        self.assertEqual(target_markers(history), (("ISSUE", 72),))

    def test_resolved_cycle_retains_outcome_time_for_reopening(self):
        barriers = target_barriers([{
            "number": 204,
            "title": "venus: autonomous cycle issue-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T21:00:00Z",
            "closedAt": "2026-09-24T21:00:00Z",
        }])
        self.assertEqual(len(barriers), 1)
        self.assertEqual(barriers[0].outcome_at, "2026-09-24T21:00:00Z")

    def test_returned_learning_can_override_roadmap_hint(self):
        items = (
            WorkItem("ISSUE", 31, "roadmap issue"),
            WorkItem("PR", 901, "returned-success pr"),
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
            "secrets.",
            "workflow_run:",
        )
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_workflow_only_creates_draft_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)

    def test_workflow_runs_full_test_suite_before_git_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        tests_at = text.index("python -m unittest discover")
        push_at = text.index("git push origin")
        self.assertLess(tests_at, push_at)

    def test_workflow_requires_target_detail_and_study_before_git_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        detail_at = text.index("Return selected target detail from GitHub")
        study_at = text.index("Venus studies selected target against checked-out repository")
        push_at = text.index("git push origin")
        self.assertLess(detail_at, study_at)
        self.assertLess(study_at, push_at)
        self.assertIn("VENUS_AUTONOMOUS_STUDY.json", text)

    def test_workflow_has_no_audit_escape_hatch(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("audit_custody.py || true", text)
        self.assertNotIn("audit_causal_distinctions.py || true", text)

    def test_autonomous_staged_write_scope_is_narrow(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("autonomy/cycles/", text)
        self.assertIn("AUTONOMOUS_LEARNING_STATE.json", text)
        self.assertIn("autonomous write escaped bounded scope", text)

    def test_learning_state_is_committed_but_not_authority(self):
        obj = json.loads(
            (ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(obj["promotion_authority"])


if __name__ == "__main__":
    unittest.main()
