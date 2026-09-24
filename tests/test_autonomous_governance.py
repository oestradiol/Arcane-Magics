from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    active_autonomous_cycle,
    empty_state,
    update_from_cycle_prs,
)
from kernel.development.autonomous_worker import WorkItem, choose_target


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


def body(features):
    return "Venus-Features: " + json.dumps(features, sort_keys=True, separators=(",", ":"))


class AutonomousGovernanceTests(unittest.TestCase):
    def test_closed_merged_cycle_updates_feature_learning_once(self):
        state = empty_state()
        features = {f"x{i}": i in (0, 2) for i in range(8)}
        history = [{
            "number": 201,
            "title": "venus: autonomous cycle pr-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T00:00:00Z",
            "body": body(features),
        }]
        updated = update_from_cycle_prs(state, history)
        self.assertGreater(updated.weights["x0"], 0)
        self.assertGreater(updated.weights["x2"], 0)
        again = update_from_cycle_prs(updated, history)
        self.assertEqual(again.weights, updated.weights)
        self.assertEqual(again.learning_rate, updated.learning_rate)

    def test_closed_unmerged_cycle_is_negative_return(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body(features),
            }],
        )
        self.assertLess(updated.weights["x0"], 0)

    def test_missing_feature_custody_cannot_train(self):
        updated = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "body": "no feature custody",
            }],
        )
        self.assertTrue(all(v == 0.0 for v in updated.weights.values()))
        self.assertEqual(updated.seen_cycle_prs, ())

    def test_open_cycle_neither_trains_nor_allows_reroll(self):
        history = [{
            "number": 203,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
            "body": body({f"x{i}": False for i in range(8)}),
        }]
        updated = update_from_cycle_prs(empty_state(), history)
        self.assertTrue(all(v == 0.0 for v in updated.weights.values()))
        self.assertTrue(active_autonomous_cycle(history))

    def test_learning_can_causally_reverse_future_work_class(self):
        items = (
            WorkItem("ISSUE", 900, "generic issue"),
            WorkItem("PR", 901, "generic pr"),
        )
        pr_features = {f"x{i}": i == 0 for i in range(8)}
        positive = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 301,
                "title": "venus: autonomous cycle pr-901",
                "state": "MERGED",
                "mergedAt": "x",
                "body": body(pr_features),
            }],
        )
        negative = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 302,
                "title": "venus: autonomous cycle pr-901",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body(pr_features),
            }],
        )
        self.assertEqual(
            choose_target(items, learner_state_id="p", feature_weights=positive.weights).kind,
            "PR",
        )
        self.assertEqual(
            choose_target(items, learner_state_id="n", feature_weights=negative.weights).kind,
            "ISSUE",
        )

    def test_consistent_external_returns_increase_plasticity_inside_fixed_bound(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        s = update_from_cycle_prs(
            empty_state(),
            [
                {"number": 401, "title": "venus: autonomous cycle pr-1", "state": "MERGED", "mergedAt": "x", "body": body(features)},
                {"number": 402, "title": "venus: autonomous cycle pr-2", "state": "MERGED", "mergedAt": "x", "body": body(features)},
                {"number": 403, "title": "venus: autonomous cycle pr-3", "state": "MERGED", "mergedAt": "x", "body": body(features)},
            ],
        )
        self.assertGreater(s.learning_rate, 0.1)
        self.assertLessEqual(s.learning_rate, s.max_learning_rate)

    def test_return_sign_reversal_reduces_plasticity_but_not_below_floor(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        s = update_from_cycle_prs(
            empty_state(),
            [
                {"number": 501, "title": "venus: autonomous cycle pr-1", "state": "MERGED", "mergedAt": "x", "body": body(features)},
                {"number": 502, "title": "venus: autonomous cycle pr-2", "state": "MERGED", "mergedAt": "x", "body": body(features)},
                {"number": 503, "title": "venus: autonomous cycle pr-3", "state": "CLOSED", "mergedAt": None, "body": body(features)},
            ],
        )
        self.assertLess(s.learning_rate, 0.11)
        self.assertGreaterEqual(s.learning_rate, s.min_learning_rate)

    def test_workflow_has_no_self_merge_release_close_secret_or_workflow_chaining(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        for token in (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "secrets.",
            "workflow_run:",
        ):
            self.assertNotIn(token, text)

    def test_workflow_only_creates_draft_pr(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gh pr create", text)
        self.assertIn("--draft", text)

    def test_workflow_runs_full_tests_before_git_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        tests_at = text.index("Verify full safety and regression surface")
        push_at = text.index("git push origin")
        self.assertLess(tests_at, push_at)
        self.assertIn("unittest discover", text)

    def test_workflow_enforces_narrow_staged_write_scope(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("forbidden autonomous write path", text)
        self.assertIn("autonomy/cycles/*.json", text)
        self.assertIn("autonomy/studies/*.json", text)
        self.assertIn("AUTONOMOUS_LEARNING_STATE.json", text)

    def test_workflow_studies_selected_target_before_materialization(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        study_at = text.index("Fetch and study the selected target")
        materialize_at = text.index("Materialize one bounded draft work branch")
        self.assertLess(study_at, materialize_at)
        self.assertIn("study_venus_target.py", text)
        self.assertIn("gh issue view", text)
        self.assertIn("gh pr view", text)

    def test_learning_state_is_not_authority_and_meta_bounds_are_external(self):
        obj = json.loads(
            (ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(obj["promotion_authority"])
        self.assertFalse(obj["merge_authority"])
        self.assertFalse(obj["release_authority"])
        self.assertEqual(obj["min_learning_rate"], 0.025)
        self.assertEqual(obj["max_learning_rate"], 0.2)


if __name__ == "__main__":
    unittest.main()
