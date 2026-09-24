from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import TargetBarrier
from kernel.development.autonomous_worker import (
    ALLOWED_OPERATIONS,
    FORBIDDEN_OPERATIONS,
    WorkItem,
    choose_study_method,
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
    def test_roadmap_has_zero_target_selection_weight(self):
        items = (
            WorkItem("ISSUE", 31, "roadmap first"),
            WorkItem("ISSUE", 72, "roadmap second"),
        )
        a = choose_target(
            items,
            learner_state_id="same",
            feature_weights={},
        )
        b = choose_target(
            tuple(reversed(items)),
            learner_state_id="same",
            feature_weights={},
        )
        self.assertEqual((a.kind, a.number), (b.kind, b.number))

    def test_returned_feature_weight_can_reverse_issue_vs_pr_choice(self):
        items = (
            WorkItem("ISSUE", 900, "issue"),
            WorkItem("PR", 901, "pr"),
        )
        issue = choose_target(
            items,
            learner_state_id="issue",
            feature_weights={"x0": -1.0},
        )
        pr = choose_target(
            items,
            learner_state_id="pr",
            feature_weights={"x0": 1.0},
        )
        self.assertEqual(issue.kind, "ISSUE")
        self.assertEqual(pr.kind, "PR")

    def test_feature_learning_can_prefer_returned_failure_pressure(self):
        items = (
            WorkItem("PR", 1, "failed", ci_failed=True),
            WorkItem("PR", 2, "clean", ci_failed=False),
        )
        chosen = choose_target(
            items,
            learner_state_id="s",
            feature_weights={"x2": 1.0},
        )
        self.assertEqual(chosen.number, 1)

    def test_pending_autonomous_cycle_forces_global_stop(self):
        chosen = choose_target(
            (WorkItem("ISSUE", 31, "a"), WorkItem("PR", 99, "b")),
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=True,
        )
        self.assertIsNone(chosen)

    def test_closed_target_stays_blocked_until_newer_world_update(self):
        barrier = TargetBarrier(
            "ISSUE", 31, 103, "CLOSED", "2026-09-24T21:00:00Z"
        )
        old = WorkItem(
            "ISSUE", 31, "same", updated_at="2026-09-24T20:59:59Z"
        )
        new = WorkItem(
            "ISSUE", 31, "changed", updated_at="2026-09-24T21:00:01Z"
        )
        self.assertIsNone(
            choose_target(
                (old,),
                learner_state_id="s",
                feature_weights={},
                target_barriers=(barrier,),
            )
        )
        self.assertEqual(
            choose_target(
                (new,),
                learner_state_id="s",
                feature_weights={},
                target_barriers=(barrier,),
            ).number,
            31,
        )

    def test_missing_target_time_fails_closed_behind_barrier(self):
        barrier = TargetBarrier(
            "ISSUE", 31, 103, "CLOSED", "2026-09-24T21:00:00Z"
        )
        self.assertIsNone(
            choose_target(
                (WorkItem("ISSUE", 31, "unknown"),),
                learner_state_id="s",
                feature_weights={},
                target_barriers=(barrier,),
            )
        )

    def test_method_utility_causally_changes_study_method(self):
        item = WorkItem("ISSUE", 31, "x")
        baseline = choose_study_method(item, {})
        changed = choose_study_method(
            item,
            {m: (-1.0 if m == baseline else 0.0) for m in (
                "DEPENDENCY_TRACE",
                "DISCRIMINATOR_DESIGN",
                "REPRODUCTION",
                "COMPARATOR_AUDIT",
                "RETURN_BOUNDARY_AUDIT",
            )},
        )
        self.assertNotEqual(baseline, changed)

    def test_conflict_is_causally_visible_to_internal_ostar(self):
        cycle = make_cycle(
            issues=(),
            prs=(WorkItem("PR", 99, "conflict", merge_state="CONFLICTING"),),
            roadmap_text="#31",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={"x4": 1.0},
            method_utility={},
            target_barriers=(),
            active_autonomous_cycle=False,
        )
        self.assertEqual(cycle.decision, "REOPEN")

    def test_unresolved_selected_work_probes_not_self_certifies(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "benchmark"),),
            prs=(),
            roadmap_text="#31",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            method_utility={},
            target_barriers=(),
            active_autonomous_cycle=False,
        )
        self.assertEqual(cycle.decision, "PROBE")
        self.assertFalse(cycle.promotion_authority)
        self.assertFalse(cycle.merge_authority)
        self.assertFalse(cycle.release_authority)
        self.assertIsNotNone(cycle.study_method)

    def test_no_work_stops(self):
        cycle = make_cycle(
            issues=(),
            prs=(),
            roadmap_text="#31",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            method_utility={},
            target_barriers=(),
            active_autonomous_cycle=False,
        )
        self.assertEqual(cycle.decision, "STOP")

    def test_worker_has_no_authority_expansion_operation(self):
        for op in (
            "MERGE_PR",
            "RELEASE",
            "PROMOTE_AUTHORITY",
            "CLOSE_ISSUE",
            "MINT_RETURN",
            "CHANGE_SAFETY_FLOOR",
            "CHANGE_JURISDICTION",
            "ACCESS_SECRETS",
        ):
            self.assertNotIn(op, ALLOWED_OPERATIONS)
            self.assertIn(op, FORBIDDEN_OPERATIONS)

    def test_cycle_records_roadmap_as_context_only(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "x"),),
            prs=(),
            roadmap_text="#999 host priority",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            method_utility={},
            target_barriers=(),
            active_autonomous_cycle=False,
        )
        self.assertIn("zero selection weight", " ".join(cycle.rationale))


if __name__ == "__main__":
    unittest.main()
