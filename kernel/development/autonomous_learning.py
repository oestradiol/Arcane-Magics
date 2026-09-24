from __future__ import annotations

"""Bounded returned-outcome learning for autonomous work selection.

Only externally returned GitHub PR dispositions update this state. The state may
alter future target selection and, within fixed external bounds, its own learning
rate. It never grants merge/promotion/release authority.

Causal custody:
- every trainable cycle PR must expose the cycle id, exact opaque feature vector,
  and a content digest binding those two;
- merged cycle PR = positive external admission;
- closed-unmerged is NOT automatically negative evidence;
- negative learning requires the explicit external label
  `venus-return-negative`;
- WITHHOLD/supersession/ordinary close without that label produces no update.
"""

from dataclasses import dataclass
import json
import re
from typing import Any, Iterable, Mapping

from kernel.runtime.vmk2 import digest

FEATURE_NAMES = tuple(f"x{i}" for i in range(8))
FEATURE_MARKER = "Venus-Features:"
CYCLE_MARKER = "Venus-Cycle:"
CUSTODY_MARKER = "Venus-Feature-Custody:"
NEGATIVE_LABEL = "venus-return-negative"


@dataclass(frozen=True)
class WorkLearningState:
    seen_cycle_prs: tuple[int, ...]
    weights: Mapping[str, float]
    learning_rate: float
    min_learning_rate: float
    max_learning_rate: float
    max_abs_weight: float
    last_reward: int | None
    last_feature_digest: str | None


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_cycle_prs=(),
        weights={name: 0.0 for name in FEATURE_NAMES},
        learning_rate=0.1,
        min_learning_rate=0.025,
        max_learning_rate=0.2,
        max_abs_weight=2.0,
        last_reward=None,
        last_feature_digest=None,
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    if obj.get("schema") == "Venus.AutonomousLearningState.v0.1":
        pr_s = int(obj.get("kind_success", {}).get("PR", 0))
        pr_f = int(obj.get("kind_failure", {}).get("PR", 0))
        weights = {name: 0.0 for name in FEATURE_NAMES}
        total = pr_s + pr_f
        if total:
            weights["x0"] = (pr_s - pr_f) / total
        return WorkLearningState(
            seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
            weights=weights,
            learning_rate=0.1,
            min_learning_rate=0.025,
            max_learning_rate=0.2,
            max_abs_weight=2.0,
            last_reward=None,
            last_feature_digest=None,
        )
    return WorkLearningState(
        seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
        weights={name: float(obj.get("weights", {}).get(name, 0.0)) for name in FEATURE_NAMES},
        learning_rate=float(obj.get("learning_rate", 0.1)),
        min_learning_rate=float(obj.get("min_learning_rate", 0.025)),
        max_learning_rate=float(obj.get("max_learning_rate", 0.2)),
        max_abs_weight=float(obj.get("max_abs_weight", 2.0)),
        last_reward=None if obj.get("last_reward") is None else int(obj["last_reward"]),
        last_feature_digest=(
            None if obj.get("last_feature_digest") is None
            else str(obj["last_feature_digest"])
        ),
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.4",
        "seen_cycle_prs": list(state.seen_cycle_prs),
        "weights": dict(state.weights),
        "learning_rate": state.learning_rate,
        "min_learning_rate": state.min_learning_rate,
        "max_learning_rate": state.max_learning_rate,
        "max_abs_weight": state.max_abs_weight,
        "last_reward": state.last_reward,
        "last_feature_digest": state.last_feature_digest,
        "promotion_authority": False,
        "merge_authority": False,
        "release_authority": False,
    }


def feature_custody(cycle_id: str, features: Mapping[str, bool]) -> str:
    canonical = {name: bool(features[name]) for name in FEATURE_NAMES}
    return digest({"cycle_id": str(cycle_id), "features": canonical})


def _markers_from_body(body: str) -> tuple[str, dict[str, bool], str] | None:
    cycle_id: str | None = None
    features: dict[str, bool] | None = None
    custody: str | None = None
    for line in body.splitlines():
        if line.startswith(CYCLE_MARKER):
            cycle_id = line[len(CYCLE_MARKER):].strip()
        elif line.startswith(FEATURE_MARKER):
            try:
                obj = json.loads(line[len(FEATURE_MARKER):].strip())
            except json.JSONDecodeError:
                return None
            if set(obj) != set(FEATURE_NAMES):
                return None
            features = {name: bool(obj[name]) for name in FEATURE_NAMES}
        elif line.startswith(CUSTODY_MARKER):
            custody = line[len(CUSTODY_MARKER):].strip()
    if not cycle_id or features is None or not custody:
        return None
    if feature_custody(cycle_id, features) != custody:
        return None
    return cycle_id, features, custody


def _labels(pr: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for label in pr.get("labels") or ():
        if isinstance(label, Mapping):
            name = label.get("name")
        else:
            name = label
        if name:
            out.add(str(name).lower())
    return out


def _returned_reward(pr: Mapping[str, Any]) -> int | None:
    if bool(pr.get("mergedAt")):
        return 1
    if NEGATIVE_LABEL in _labels(pr):
        return -1
    return None


def _next_learning_rate(
    state: WorkLearningState,
    reward: int,
    feature_digest: str,
) -> float:
    """Adapt plasticity without rewarding repeated copies of the same pressure.

    - first returned update: preserve current plasticity;
    - sign reversal: reduce plasticity;
    - same-sign return on a *different* feature pattern: modestly increase;
    - repeated same feature pattern: do not ratchet plasticity upward.
    """
    if state.last_reward is None:
        return state.learning_rate
    if reward != state.last_reward:
        return max(state.min_learning_rate, state.learning_rate * 0.5)
    if feature_digest != state.last_feature_digest:
        return min(state.max_learning_rate, state.learning_rate * 1.1)
    return state.learning_rate


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
        if str(pr.get("state", "")).upper() == "OPEN":
            continue

        markers = _markers_from_body(str(pr.get("body", "")))
        if markers is None:
            continue
        _cycle_id, features, custody = markers

        reward = _returned_reward(pr)
        if reward is None:
            # Administrative close/supersession/WITHHOLD is not learning evidence.
            continue

        lr_used = current.learning_rate
        for name, active in features.items():
            if active:
                weights[name] = max(
                    -current.max_abs_weight,
                    min(current.max_abs_weight, weights[name] + lr_used * reward),
                )

        current = WorkLearningState(
            seen_cycle_prs=current.seen_cycle_prs,
            weights=weights,
            learning_rate=_next_learning_rate(current, reward, custody),
            min_learning_rate=current.min_learning_rate,
            max_learning_rate=current.max_learning_rate,
            max_abs_weight=current.max_abs_weight,
            last_reward=reward,
            last_feature_digest=custody,
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
        last_feature_digest=current.last_feature_digest,
    )


def active_autonomous_cycle(prs: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        re.match(r"venus: autonomous cycle (issue|pr)-\d+$", str(pr.get("title", "")), re.I)
        and str(pr.get("state", "")).upper() == "OPEN"
        for pr in prs
    )
