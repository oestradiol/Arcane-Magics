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
    def test_roadmap_has_zero_target_selection_authority(self):
        items = (
            WorkItem("ISSUE", 31, "roadmap first"),
            WorkItem("ISSUE", 72, "roadmap second"),
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

    def test_returned_feature_weights_can_reverse_work_class(self):
        items = (
            WorkItem("ISSUE", 900, "generic issue"),
            WorkItem("PR", 901, "generic pr"),
        )
        issue = choose_target(
            items,
            learner_state_id="issue-pref",
            feature_weights={"x0": -1.0},
        )
        pr = choose_target(
            items,
            learner_state_id="pr-pref",
            feature_weights={"x0": 1.0},
        )
        self.assertEqual(issue.kind, "ISSUE")
        self.assertEqual(pr.kind, "PR")

    def test_open_autonomous_cycle_forces_global_stop_not_reroll(self):
        chosen = choose_target(
            (
                WorkItem("ISSUE", 31, "a"),
                WorkItem("PR", 99, "b"),
            ),
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
        )
        self.assertEqual(cycle.decision, "STOP")
        self.assertIsNone(cycle.target_number)

    def test_unresolved_selected_work_probes_not_self_certifies(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "benchmark"),),
            prs=(),
            roadmap_text="#31",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=False,
        )
        self.assertEqual(cycle.decision, "PROBE")
        self.assertFalse(cycle.promotion_authority)
        self.assertFalse(cycle.merge_authority)
        self.assertFalse(cycle.release_authority)

    def test_conflict_is_causally_visible_to_internal_policy(self):
        cycle = make_cycle(
            issues=(),
            prs=(WorkItem("PR", 99, "causal O*", merge_state="CONFLICTING"),),
            roadmap_text="",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={"x4": 1.0},
            active_autonomous_cycle=False,
        )
        self.assertEqual(cycle.decision, "REOPEN")

    def test_worker_has_no_authority_expansion_operations(self):
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

    def test_cycle_records_roadmap_only_as_context_provenance(self):
        cycle = make_cycle(
            issues=(WorkItem("ISSUE", 31, "benchmark"),),
            prs=(),
            roadmap_text="#999 host ordering",
            internal_policy=POLICY,
            learner_state_id="s",
            feature_weights={},
            active_autonomous_cycle=False,
        )
        rendered = " ".join(cycle.rationale).lower()
        self.assertIn("zero selection weight", rendered)


if __name__ == "__main__":
    unittest.main()
