from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    METHODS,
    active_autonomous_cycle,
    empty_state,
    feature_custody,
    from_json,
    target_barriers,
    update_from_cycle_prs,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


def features(*active):
    return {f"x{i}": f"x{i}" in active for i in range(8)}


def cycle_pr(
    *,
    number=201,
    kind="issue",
    target=31,
    cycle_id="cycle-a",
    feat=None,
    method="DISCRIMINATOR_DESIGN",
    state="OPEN",
    merged_at=None,
    closed_at=None,
    reviews=(),
):
    feat = feat or features()
    custody = feature_custody(cycle_id, feat)
    body = "\n".join([
        f"Venus-Cycle: {cycle_id}",
        "Venus-Features: " + json.dumps(feat, sort_keys=True, separators=(",", ":")),
        f"Venus-Feature-Custody: {custody}",
        f"Venus-Method: {method}",
    ])
    return {
        "number": number,
        "title": f"venus: autonomous cycle {kind}-{target}",
        "state": state,
        "mergedAt": merged_at,
        "closedAt": closed_at,
        "body": body,
        "reviews": list(reviews),
    }


def review(body, *, rid="r1", login="external-reviewer"):
    return {"id": rid, "body": body, "author": {"login": login}}


class AutonomousGovernanceTests(unittest.TestCase):
    def test_merge_without_explicit_review_is_not_learning_reward(self):
        state = update_from_cycle_prs(
            empty_state(),
            [cycle_pr(state="MERGED", merged_at="2026-09-24T21:00:00Z", feat=features("x0"))],
        )
        self.assertTrue(all(v == 0.0 for v in state.weights.values()))
        self.assertEqual(state.seen_return_ids, ())

    def test_explicit_external_useful_review_updates_exact_features(self):
        state = update_from_cycle_prs(
            empty_state(),
            [cycle_pr(
                feat=features("x0", "x2"),
                reviews=(review("VENUS_WORK_RETURN: USEFUL"),),
            )],
        )
        self.assertGreater(state.weights["x0"], 0.0)
        self.assertGreater(state.weights["x2"], 0.0)
        self.assertEqual(state.weights["x1"], 0.0)

    def test_explicit_external_unhelpful_review_is_negative(self):
        state = update_from_cycle_prs(
            empty_state(),
            [cycle_pr(
                feat=features("x4"),
                reviews=(review("VENUS_WORK_RETURN: UNHELPFUL"),),
            )],
        )
        self.assertLess(state.weights["x4"], 0.0)

    def test_self_review_cannot_train(self):
        state = update_from_cycle_prs(
            empty_state(),
            [cycle_pr(
                feat=features("x0"),
                reviews=(review(
                    "VENUS_WORK_RETURN: USEFUL",
                    login="github-actions[bot]",
                ),),
            )],
        )
        self.assertEqual(state.weights["x0"], 0.0)
        self.assertEqual(state.seen_return_ids, ())

    def test_same_review_return_is_applied_once(self):
        row = cycle_pr(
            feat=features("x0"),
            reviews=(review("VENUS_WORK_RETURN: USEFUL", rid="stable"),),
        )
        first = update_from_cycle_prs(empty_state(), [row])
        second = update_from_cycle_prs(first, [row])
        self.assertEqual(first.weights, second.weights)
        self.assertEqual(first.learning_rate, second.learning_rate)

    def test_method_review_changes_method_utility_without_truth_authority(self):
        state = update_from_cycle_prs(
            empty_state(),
            [cycle_pr(reviews=(
                review(
                    "VENUS_METHOD_RETURN: COMPARATOR_AUDIT: USEFUL",
                    rid="method",
                ),
            ))],
        )
        self.assertGreater(state.method_utility("COMPARATOR_AUDIT"), 0.0)
        self.assertEqual(state.method_utility("REPRODUCTION"), 0.0)

    def test_same_sign_different_pressure_increases_plasticity_within_ceiling(self):
        a = cycle_pr(
            number=301,
            cycle_id="a",
            feat=features("x0"),
            reviews=(review("VENUS_WORK_RETURN: USEFUL", rid="a"),),
        )
        b = cycle_pr(
            number=302,
            cycle_id="b",
            feat=features("x1"),
            reviews=(review("VENUS_WORK_RETURN: USEFUL", rid="b"),),
        )
        first = update_from_cycle_prs(empty_state(), [a])
        second = update_from_cycle_prs(first, [a, b])
        self.assertGreater(second.learning_rate, first.learning_rate)
        self.assertLessEqual(second.learning_rate, second.max_learning_rate)

    def test_sign_reversal_reduces_plasticity_above_floor(self):
        a = cycle_pr(
            number=401,
            cycle_id="a",
            feat=features("x0"),
            reviews=(review("VENUS_WORK_RETURN: USEFUL", rid="a"),),
        )
        b = cycle_pr(
            number=402,
            cycle_id="b",
            feat=features("x1"),
            reviews=(review("VENUS_WORK_RETURN: UNHELPFUL", rid="b"),),
        )
        first = update_from_cycle_prs(empty_state(), [a])
        second = update_from_cycle_prs(first, [a, b])
        self.assertLess(second.learning_rate, first.learning_rate)
        self.assertGreaterEqual(second.learning_rate, second.min_learning_rate)

    def test_legacy_merge_reward_state_is_quarantined(self):
        legacy = {
            "schema": "Venus.AutonomousLearningState.v0.1",
            "kind_success": {"ISSUE": 99, "PR": 99},
            "kind_failure": {"ISSUE": 0, "PR": 0},
        }
        state = from_json(legacy)
        self.assertTrue(all(v == 0.0 for v in state.weights.values()))
        self.assertTrue(all(state.method_utility(m) == 0.0 for m in METHODS))

    def test_open_cycle_is_global_backpressure(self):
        history = [cycle_pr(state="OPEN")]
        self.assertTrue(active_autonomous_cycle(history))
        barrier = target_barriers(history)[0]
        self.assertEqual((barrier.kind, barrier.number), ("ISSUE", 31))
        self.assertIsNone(barrier.outcome_at)

    def test_resolved_cycle_retains_target_outcome_time_independent_of_reward(self):
        history = [cycle_pr(
            state="CLOSED",
            closed_at="2026-09-24T21:05:00Z",
            reviews=(),
        )]
        barrier = target_barriers(history)[0]
        self.assertEqual(barrier.outcome_at, "2026-09-24T21:05:00Z")
        learned = update_from_cycle_prs(empty_state(), history)
        self.assertEqual(learned.seen_return_ids, ())

    def test_workflow_has_no_self_merge_release_close_or_secrets(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        for token in (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "secrets.",
        ):
            self.assertNotIn(token, text)

    def test_workflow_wakes_on_main_admission_and_still_supports_manual_schedule(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("branches: [main]", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("schedule:", text)

    def test_workflow_binds_review_custody_and_feedback_markers(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Venus-Cycle:", text)
        self.assertIn("Venus-Features:", text)
        self.assertIn("Venus-Feature-Custody:", text)
        self.assertIn("Venus-Method:", text)
        self.assertIn("VENUS_WORK_RETURN: USEFUL", text)
        self.assertIn("VENUS_METHOD_RETURN:", text)

    def test_workflow_runs_safety_suite_before_any_git_push(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertLess(text.index("python -m unittest discover"), text.index("git push origin"))
        self.assertLess(text.index("audit_autonomy_safety_matrix.py"), text.index("git push origin"))
        self.assertLess(text.index("audit_custody.py"), text.index("git push origin"))

    def test_workflow_write_scope_stays_narrow(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("autonomous write escaped bounded scope", text)
        self.assertIn("autonomy/cycles/", text)
        self.assertIn("AUTONOMOUS_LEARNING_STATE.json", text)

    def test_persistent_state_has_no_authority_flags(self):
        obj = json.loads(
            (ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        for key in (
            "promotion_authority",
            "merge_authority",
            "release_authority",
            "truth_authority",
            "safety_floor_authority",
        ):
            self.assertFalse(obj[key])
        self.assertEqual(obj["min_learning_rate"], 0.025)
        self.assertEqual(obj["max_learning_rate"], 0.2)


if __name__ == "__main__":
    unittest.main()
