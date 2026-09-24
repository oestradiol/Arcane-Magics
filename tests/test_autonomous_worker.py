from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_worker import (
    ALLOWED_OPERATIONS,
    FORBIDDEN_OPERATIONS,
    WorkItem,
    choose_target,
    make_cycle,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads(
    (ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json").read_text(
        encoding="utf-8"
    )
)


class AutonomousWorkerTests(unittest.TestCase):
    def test_roadmap_is_bounded_prior_not_sovereign_curriculum(self):
        items = (
            WorkItem("ISSUE", 31, "roadmap issue"),
            WorkItem("PR", 999, "learned useful pr"),
        )
        chosen = choose_target(
            items,
            roadmap_text="#31",
            kind_utility={"ISSUE": -1.0, "PR": 1.0},
        )
        self.assertEqual(chosen.kind, "PR")

    def test_roadmap_can_break_neutral_tie_as_bootstrap_prior(self):
        items = (
            WorkItem("ISSUE", 72, "later"),
            WorkItem("ISSUE", 31, "first"),
        )
        chosen = choose_target(items, roadmap_text="#31\n#72")
        self.assertEqual(chosen.number, 31)

    def test_conflicted_pr_reopens_before_new_issue(self):
        items = (
            WorkItem("ISSUE", 31, "benchmark"),
            WorkItem("PR", 99, "causal O*", merge_state="CONFLICTING"),
        )
        chosen = choose_target(items, roadmap_text="#31")
        self.assertEqual((chosen.kind, chosen.number), ("PR", 99))

    def test_recent_target_is_not_rerolled_immediately(self):
        items = (
            WorkItem("ISSUE", 31, "benchmark"),
            WorkItem("ISSUE", 72, "Safe Strong RSI"),
        )
        chosen = choose_target(
            items,
            roadmap_text="#31\n#72",
            recent_targets=(("ISSUE", 31),),
        )
        self.assertEqual(chosen.number, 72)

    def test_no_work_stops(self):
        cycle = make_cycle(
            issues=(),
            prs=(),
            roadmap_text="",
            internal_policy=POLICY,
        )
        self.assertEqual(cycle.decision, "STOP")
        self.assertIsNone(cycle.target_number)

    def test_unresolved_selected_work_probes_not_self_certifies(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "benchmark"),),
            prs=(),
            roadmap_text="#31",
            internal_policy=POLICY,
        )
        self.assertEqual(cycle.decision, "PROBE")
        self.assertFalse(cycle.promotion_authority)

    def test_worker_has_no_merge_release_or_promotion_operation(self):
        self.assertNotIn("MERGE_PR", ALLOWED_OPERATIONS)
        self.assertNotIn("RELEASE", ALLOWED_OPERATIONS)
        self.assertNotIn("PROMOTE_AUTHORITY", ALLOWED_OPERATIONS)
        self.assertIn("MERGE_PR", FORBIDDEN_OPERATIONS)
        self.assertIn("PROMOTE_AUTHORITY", FORBIDDEN_OPERATIONS)

    def test_worker_cannot_close_issue_as_success_side_effect(self):
        self.assertNotIn("CLOSE_ISSUE", ALLOWED_OPERATIONS)
        self.assertIn("CLOSE_ISSUE", FORBIDDEN_OPERATIONS)

    def test_internal_policy_is_causally_upstream(self):
        item = WorkItem("PR", 99, "causal O*", merge_state="CONFLICTING")
        cycle = make_cycle(
            issues=(),
            prs=(item,),
            roadmap_text="",
            internal_policy=POLICY,
        )
        self.assertEqual(cycle.decision, "REOPEN")


if __name__ == "__main__":
    unittest.main()
