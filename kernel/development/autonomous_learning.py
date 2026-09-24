from __future__ import annotations

"""Bounded returned-outcome learning for autonomous work selection.

Only externally returned GitHub PR dispositions update this state. The state may
alter future target selection and, within fixed external bounds, its own learning
rate. It never grants merge/promotion/release authority.

The exact opaque feature vector used for a cycle is embedded in the draft PR
body and returned with its external merge/close disposition.
"""

from dataclasses import dataclass
import json
import re
from typing import Any, Iterable, Mapping

FEATURE_NAMES = tuple(f"x{i}" for i in range(8))
FEATURE_MARKER = "Venus-Features:"


@dataclass(frozen=True)
class WorkLearningState:
    seen_cycle_prs: tuple[int, ...]
    weights: Mapping[str, float]
    learning_rate: float
    min_learning_rate: float
    max_learning_rate: float
    max_abs_weight: float
    last_reward: int | None

    def utility(self, features: Mapping[str, bool]) -> float:
        return sum(float(self.weights.get(k, 0.0)) for k, v in features.items() if v)


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_cycle_prs=(),
        weights={name: 0.0 for name in FEATURE_NAMES},
        learning_rate=0.1,
        min_learning_rate=0.025,
        max_learning_rate=0.2,
        max_abs_weight=2.0,
        last_reward=None,
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    schema = obj.get("schema")
    if schema == "Venus.AutonomousLearningState.v0.1":
        pr_s = int(obj.get("kind_success", {}).get("PR", 0))
        pr_f = int(obj.get("kind_failure", {}).get("PR", 0))
        weights = {name: 0.0 for name in FEATURE_NAMES}
        pr_total = pr_s + pr_f
        if pr_total:
            weights["x0"] = (pr_s - pr_f) / pr_total
        return WorkLearningState(
            seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
            weights=weights,
            learning_rate=0.1,
            min_learning_rate=0.025,
            max_learning_rate=0.2,
            max_abs_weight=2.0,
            last_reward=None,
        )

    return WorkLearningState(
        seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
        weights={name: float(obj.get("weights", {}).get(name, 0.0)) for name in FEATURE_NAMES},
        learning_rate=float(obj.get("learning_rate", 0.1)),
        min_learning_rate=float(obj.get("min_learning_rate", 0.025)),
        max_learning_rate=float(obj.get("max_learning_rate", 0.2)),
        max_abs_weight=float(obj.get("max_abs_weight", 2.0)),
        last_reward=(
            None if obj.get("last_reward") is None else int(obj.get("last_reward"))
        ),
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.3",
        "seen_cycle_prs": list(state.seen_cycle_prs),
        "weights": dict(state.weights),
        "learning_rate": state.learning_rate,
        "min_learning_rate": state.min_learning_rate,
        "max_learning_rate": state.max_learning_rate,
        "max_abs_weight": state.max_abs_weight,
        "last_reward": state.last_reward,
        "promotion_authority": False,
        "merge_authority": False,
        "release_authority": False,
    }


def _features_from_body(body: str) -> dict[str, bool] | None:
    for line in body.splitlines():
        if line.startswith(FEATURE_MARKER):
            raw = line[len(FEATURE_MARKER):].strip()
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                return None
            if set(obj) != set(FEATURE_NAMES):
                return None
            return {name: bool(obj[name]) for name in FEATURE_NAMES}
    return None


def _next_learning_rate(state: WorkLearningState, reward: int) -> float:
    """Adapt plasticity only inside externally fixed bounds.

    Repeatedly consistent return slightly increases plasticity; a sign reversal
    halves it. The external min/max bounds are never learner-modified here.
    """
    lr = state.learning_rate
    if state.last_reward is None:
        return lr
    if reward == state.last_reward:
        return min(state.max_learning_rate, lr * 1.1)
    return max(state.min_learning_rate, lr * 0.5)


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_cycle_prs)
    weights = {name: float(state.weights.get(name, 0.0)) for name in FEATURE_NAMES}
    current = state

    for pr in sorted(prs, key=lambda x: int(x["number"])):
        number = int(pr["number"])
        if number in seen:
            continue
        title = str(pr.get("title", ""))
        if not re.match(r"venus: autonomous cycle (issue|pr)-\d+$", title, re.I):
            continue
        state_name = str(pr.get("state", "")).upper()
        if state_name == "OPEN":
            continue

        features = _features_from_body(str(pr.get("body", "")))
        if features is None:
            # Missing custody vector means the return cannot train selection.
            continue

        reward = 1 if bool(pr.get("mergedAt")) else -1
        lr_used = current.learning_rate
        for name, active in features.items():
            if active:
                value = weights[name] + lr_used * reward
                weights[name] = max(
                    -current.max_abs_weight,
                    min(current.max_abs_weight, value),
                )

        next_lr = _next_learning_rate(current, reward)
        current = WorkLearningState(
            seen_cycle_prs=current.seen_cycle_prs,
            weights=weights,
            learning_rate=next_lr,
            min_learning_rate=current.min_learning_rate,
            max_learning_rate=current.max_learning_rate,
            max_abs_weight=current.max_abs_weight,
            last_reward=reward,
        )
        seen.add(number)

    return WorkLearningState(
        seen_cycle_prs=tuple(sorted(seen)),
        weights=weights,
        learning_rate=current.learning_rate,
        min_learning_rate=current.min_learning_rate,
        max_learning_rate=current.max_learning_rate,
        max_abs_weight=current.max_abs_weight,
        last_reward=current.last_reward,
    )


def active_autonomous_cycle(prs: Iterable[Mapping[str, Any]]) -> bool:
    for pr in prs:
        title = str(pr.get("title", ""))
        if (
            re.match(r"venus: autonomous cycle (issue|pr)-\d+$", title, re.I)
            and str(pr.get("state", "")).upper() == "OPEN"
        ):
            return True
    return False
