from __future__ import annotations

"""Bounded returned-outcome learning for autonomous work selection.

Only externally returned GitHub PR dispositions update the learner state. The
state changes future target ranking but never grants merge/promotion authority.
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
    max_abs_weight: float

    def utility(self, features: Mapping[str, bool]) -> float:
        return sum(float(self.weights.get(k, 0.0)) for k, v in features.items() if v)


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_cycle_prs=(),
        weights={name: 0.0 for name in FEATURE_NAMES},
        learning_rate=0.1,
        max_abs_weight=2.0,
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    schema = obj.get("schema")
    if schema == "Venus.AutonomousLearningState.v0.1":
        # Backward-compatible migration from kind-only counters.
        issue_s = int(obj.get("kind_success", {}).get("ISSUE", 0))
        issue_f = int(obj.get("kind_failure", {}).get("ISSUE", 0))
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
            max_abs_weight=2.0,
        )
    return WorkLearningState(
        seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
        weights={name: float(obj.get("weights", {}).get(name, 0.0)) for name in FEATURE_NAMES},
        learning_rate=float(obj.get("learning_rate", 0.1)),
        max_abs_weight=float(obj.get("max_abs_weight", 2.0)),
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.2",
        "seen_cycle_prs": list(state.seen_cycle_prs),
        "weights": dict(state.weights),
        "learning_rate": state.learning_rate,
        "max_abs_weight": state.max_abs_weight,
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


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_cycle_prs)
    weights = {name: float(state.weights.get(name, 0.0)) for name in FEATURE_NAMES}

    for pr in prs:
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

        reward = 1.0 if bool(pr.get("mergedAt")) else -1.0
        for name, active in features.items():
            if active:
                value = weights[name] + state.learning_rate * reward
                weights[name] = max(-state.max_abs_weight, min(state.max_abs_weight, value))
        seen.add(number)

    return WorkLearningState(
        seen_cycle_prs=tuple(sorted(seen)),
        weights=weights,
        learning_rate=state.learning_rate,
        max_abs_weight=state.max_abs_weight,
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
