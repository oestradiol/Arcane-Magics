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
    def test_no_host_roadmap_priority_in_target_choice(self):
        items = (
            WorkItem("ISSUE", 72, "Safe Strong RSI"),
            WorkItem("ISSUE", 31, "hidden semantic return"),
        )
        a = choose_target(
            items,
            learner_state_id="s0",
            feature_weights={f"x{i}": 0.0 for i in range(8)},
        )
        b = choose_target(
            tuple(reversed(items)),
            learner_state_id="s0",
            feature_weights={f"x{i}": 0.0 for i in range(8)},
        )
        self.assertEqual((a.kind, a.number), (b.kind, b.number))

    def test_returned_feature_weights_can_change_target_class(self):
        items = (
            WorkItem("ISSUE", 900, "generic issue"),
            WorkItem("PR", 901, "generic pr"),
        )
        choose_issue = choose_target(
            items,
            learner_state_id="s1",
            feature_weights={"x0": -1.0},
        )
        choose_pr = choose_target(
            items,
            learner_state_id="s2",
            feature_weights={"x0": 1.0},
        )
        self.assertEqual(choose_issue.kind, "ISSUE")
        self.assertEqual(choose_pr.kind, "PR")

    def test_active_autonomous_cycle_stops_instead_of_reroll(self):
        chosen = choose_target(
            (WorkItem("ISSUE", 31, "benchmark"),),
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=True,
        )
        self.assertIsNone(chosen)

    def test_no_work_stops(self):
        cycle = make_cycle(
            issues=(),
            prs=(),
            roadmap_text="#31",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=False,
            repo_root=ROOT,
        )
        self.assertEqual(cycle.decision, "STOP")
        self.assertIsNone(cycle.target_number)

    def test_unresolved_selected_work_probes_not_self_certifies(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "benchmark"),),
            prs=(),
            roadmap_text="#999",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=False,
            repo_root=ROOT,
        )
        self.assertEqual(cycle.decision, "PROBE")
        self.assertFalse(cycle.promotion_authority)
        self.assertFalse(cycle.merge_authority)
        self.assertFalse(cycle.release_authority)

    def test_worker_has_no_merge_release_promotion_or_return_minting_operation(self):
        for op in ("MERGE_PR", "RELEASE", "PROMOTE_AUTHORITY", "MINT_RETURN"):
            self.assertNotIn(op, ALLOWED_OPERATIONS)
            self.assertIn(op, FORBIDDEN_OPERATIONS)

    def test_worker_cannot_close_issue_or_change_safety_floor(self):
        for op in ("CLOSE_ISSUE", "CHANGE_SAFETY_FLOOR", "CHANGE_JURISDICTION"):
            self.assertNotIn(op, ALLOWED_OPERATIONS)
            self.assertIn(op, FORBIDDEN_OPERATIONS)

    def test_internal_policy_is_causally_upstream(self):
        item = WorkItem("PR", 99, "causal O*", merge_state="CONFLICTING")
        cycle = make_cycle(
            issues=(),
            prs=(item,),
            roadmap_text="",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={"x0": 1.0},
            active_autonomous_cycle=False,
            repo_root=ROOT,
        )
        self.assertEqual(cycle.decision, "REOPEN")

    def test_cycle_contains_repo_study_surface(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 72, "Safe Strong RSI"),),
            prs=(),
            roadmap_text="",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=False,
            repo_root=ROOT,
        )
        self.assertTrue(cycle.study_protocol)
        self.assertIsInstance(cycle.related_paths, tuple)


if __name__ == "__main__":
    unittest.main()
