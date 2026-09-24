from __future__ import annotations

import unittest

from kernel.development.autonomous_meta_learning import (
    STRATEGIES,
    choose_strategy,
    empty_meta_state,
    extract_strategy_returns,
    update_from_cycle_carriers,
)


def review(body: str, *, login: str = "oestradiol"):
    return {
        "body": body,
        "author": {"login": login},
        "submittedAt": "2026-09-24T23:10:00Z",
    }


def carrier(*reviews):
    return {
        "number": 999,
        "_carrier_kind": "PR",
        "reviews": list(reviews),
    }


class AutonomousMetaLearningTests(unittest.TestCase):
    def test_default_preserves_existing_return_utility_strategy(self):
        self.assertEqual(
            choose_strategy(empty_meta_state()),
            "RETURN_UTILITY_FIRST",
        )

    def test_authorized_external_return_can_change_learning_strategy(self):
        state = update_from_cycle_carriers(
            empty_meta_state(),
            [carrier(review(
                "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: USEFUL"
            ))],
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(choose_strategy(state), "TARGET_SIGNAL_FIRST")

    def test_self_review_cannot_train_meta_strategy(self):
        state = update_from_cycle_carriers(
            empty_meta_state(),
            [carrier(review(
                "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: USEFUL",
                login="github-actions[bot]",
            ))],
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(state, empty_meta_state())

    def test_unauthorized_external_identity_cannot_train_meta_strategy(self):
        state = update_from_cycle_carriers(
            empty_meta_state(),
            [carrier(review(
                "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: USEFUL",
                login="random-person",
            ))],
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(state, empty_meta_state())

    def test_conflicting_return_on_same_strategy_is_fail_closed(self):
        rows = extract_strategy_returns(
            [carrier(review(
                "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: USEFUL\n"
                "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: UNHELPFUL"
            ))],
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(rows, ())

    def test_same_return_is_applied_once(self):
        c = carrier(review(
            "VENUS_LEARNING_STRATEGY_RETURN: TARGET_SIGNAL_FIRST: USEFUL"
        ))
        once = update_from_cycle_carriers(
            empty_meta_state(), [c], authorized_logins={"oestradiol"}
        )
        twice = update_from_cycle_carriers(
            once, [c], authorized_logins={"oestradiol"}
        )
        self.assertEqual(once, twice)

    def test_strategy_family_is_fixed_and_small(self):
        self.assertEqual(
            STRATEGIES,
            ("RETURN_UTILITY_FIRST", "TARGET_SIGNAL_FIRST"),
        )


if __name__ == "__main__":
    unittest.main()
