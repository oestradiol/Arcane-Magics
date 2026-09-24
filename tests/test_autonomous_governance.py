from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    active_autonomous_cycle,
    empty_state,
    feature_custody,
    update_from_cycle_prs,
)
from kernel.development.autonomous_worker import WorkItem, choose_target


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


def body(cycle_id, features, *, custody_override=None):
    custody = custody_override or feature_custody(cycle_id, features)
    return "\n".join((
        f"Venus-Cycle: {cycle_id}",
        "Venus-Features: " + json.dumps(
            features, sort_keys=True, separators=(",", ":")
        ),
        f"Venus-Feature-Custody: {custody}",
    ))


def negative_label():
    return [{"name": "venus-return-negative"}]


class AutonomousGovernanceTests(unittest.TestCase):
    def test_merged_cycle_updates_exact_features_once(self):
        features = {f"x{i}": i in (0, 2) for i in range(8)}
        history = [{
            "number": 201,
            "title": "venus: autonomous cycle pr-31",
            "state": "MERGED",
            "mergedAt": "2026-09-24T00:00:00Z",
            "body": body("c201", features),
            "labels": [],
        }]
        state = update_from_cycle_prs(empty_state(), history)
        self.assertGreater(state.weights["x0"], 0)
        self.assertGreater(state.weights["x2"], 0)
        again = update_from_cycle_prs(state, history)
        self.assertEqual(again.weights, state.weights)
        self.assertEqual(again.learning_rate, state.learning_rate)

    def test_administrative_close_is_not_negative_learning_evidence(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        state = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 202,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body("c202", features),
                "labels": [],
            }],
        )
        self.assertTrue(all(v == 0.0 for v in state.weights.values()))
        self.assertEqual(state.seen_cycle_prs, ())

    def test_explicit_external_negative_label_can_train_negative(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        state = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 203,
                "title": "venus: autonomous cycle pr-99",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body("c203", features),
                "labels": negative_label(),
            }],
        )
        self.assertLess(state.weights["x0"], 0)
        self.assertEqual(state.seen_cycle_prs, (203,))

    def test_missing_or_tampered_feature_custody_cannot_train(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        tampered = dict(features)
        tampered["x1"] = True
        valid_for_original = feature_custody("c204", features)

        rows = [
            {
                "number": 204,
                "title": "venus: autonomous cycle pr-99",
                "state": "MERGED",
                "mergedAt": "x",
                "body": "no custody vector",
                "labels": [],
            },
            {
                "number": 205,
                "title": "venus: autonomous cycle pr-99",
                "state": "MERGED",
                "mergedAt": "x",
                "body": body("c204", tampered, custody_override=valid_for_original),
                "labels": [],
            },
        ]
        state = update_from_cycle_prs(empty_state(), rows)
        self.assertTrue(all(v == 0.0 for v in state.weights.values()))
        self.assertEqual(state.seen_cycle_prs, ())

    def test_open_cycle_neither_trains_nor_allows_reroll(self):
        features = {f"x{i}": False for i in range(8)}
        history = [{
            "number": 206,
            "title": "venus: autonomous cycle issue-72",
            "state": "OPEN",
            "mergedAt": None,
            "body": body("c206", features),
            "labels": [],
        }]
        state = update_from_cycle_prs(empty_state(), history)
        self.assertTrue(all(v == 0.0 for v in state.weights.values()))
        self.assertTrue(active_autonomous_cycle(history))

    def test_returned_learning_can_reverse_future_work_class(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        positive = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 301,
                "title": "venus: autonomous cycle pr-901",
                "state": "MERGED",
                "mergedAt": "x",
                "body": body("c301", features),
                "labels": [],
            }],
        )
        negative = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 302,
                "title": "venus: autonomous cycle pr-901",
                "state": "CLOSED",
                "mergedAt": None,
                "body": body("c302", features),
                "labels": negative_label(),
            }],
        )
        items = (WorkItem("ISSUE", 900, "issue"), WorkItem("PR", 901, "pr"))
        self.assertEqual(
            choose_target(items, learner_state_id="p", feature_weights=positive.weights).kind,
            "PR",
        )
        self.assertEqual(
            choose_target(items, learner_state_id="n", feature_weights=negative.weights).kind,
            "ISSUE",
        )

    def test_repeated_same_pressure_cannot_ratchet_plasticity(self):
        features = {f"x{i}": i == 0 for i in range(8)}
        rows = [
            {
                "number": 400 + i,
                "title": f"venus: autonomous cycle pr-{i}",
                "state": "MERGED",
                "mergedAt": "x",
                "body": body(f"c{400+i}", features),
                "labels": [],
            }
            for i in range(1, 6)
        ]
        state = update_from_cycle_prs(empty_state(), rows)
        self.assertEqual(state.learning_rate, 0.1)

    def test_consistent_return_on_distinct_pressure_can_increase_plasticity_within_ceiling(self):
        a = {f"x{i}": i == 0 for i in range(8)}
        b = {f"x{i}": i == 1 for i in range(8)}
        state = update_from_cycle_prs(
            empty_state(),
            [
                {"number": 501, "title": "venus: autonomous cycle pr-1", "state": "MERGED", "mergedAt": "x", "body": body("c501", a), "labels": []},
                {"number": 502, "title": "venus: autonomous cycle pr-2", "state": "MERGED", "mergedAt": "x", "body": body("c502", b), "labels": []},
            ],
        )
        self.assertGreater(state.learning_rate, 0.1)
        self.assertLessEqual(state.learning_rate, state.max_learning_rate)

    def test_return_sign_reversal_reduces_plasticity_above_floor(self):
        a = {f"x{i}": i == 0 for i in range(8)}
        b = {f"x{i}": i == 1 for i in range(8)}
        state = update_from_cycle_prs(
            empty_state(),
            [
                {"number": 601, "title": "venus: autonomous cycle pr-1", "state": "MERGED", "mergedAt": "x", "body": body("c601", a), "labels": []},
                {"number": 602, "title": "venus: autonomous cycle pr-2", "state": "CLOSED", "mergedAt": None, "body": body("c602", b), "labels": negative_label()},
            ],
        )
        self.assertLess(state.learning_rate, 0.1)
        self.assertGreaterEqual(state.learning_rate, state.min_learning_rate)

    def test_workflow_has_no_self_merge_release_close_secret_or_chain(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        for token in (
            "gh pr merge",
            "gh release create",
            "gh issue close",
            "secrets.",
            "workflow_run:",
        ):
            self.assertNotIn(token, text)

    def test_workflow_runs_full_suite_and_study_before_write(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        tests_at = text.index("python -m unittest discover")
        study_at = text.index("Venus studies selected target")
        push_at = text.index("git push origin")
        self.assertLess(tests_at, study_at)
        self.assertLess(study_at, push_at)
        self.assertNotIn("audit_custody.py || true", text)
        self.assertNotIn("audit_causal_distinctions.py || true", text)

    def test_workflow_has_causal_feature_custody_and_narrow_write_scope(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Venus-Cycle:", text)
        self.assertIn("Venus-Features:", text)
        self.assertIn("Venus-Feature-Custody:", text)
        self.assertIn("body,labels", text)
        self.assertIn("autonomous write escaped bounded scope", text)
        self.assertIn("autonomy/cycles/", text)
        self.assertIn("AUTONOMOUS_LEARNING_STATE.json", text)

    def test_learning_state_is_not_authority_and_meta_bounds_are_fixed(self):
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
        self.assertIsNone(obj["last_feature_digest"])


if __name__ == "__main__":
    unittest.main()
