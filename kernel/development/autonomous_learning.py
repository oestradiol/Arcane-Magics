from __future__ import annotations

"""Bounded externally-returned learning for autonomous work and study method.

No merge/close/CI/execution event is a learning reward. Preference changes
require explicit review text authored outside the Venus worker.

Work feedback updates opaque target-feature weights. Method feedback updates a
separate bounded study-method preference. Work feedback may also adapt the
learning rate, but only within fixed external bounds.

Target recurrence is orthogonal to utility: a studied target remains behind a
barrier until that target's own GitHub state changes after the cycle outcome.
"""

from dataclasses import dataclass
import json
import re
from typing import Any, Iterable, Mapping

from kernel.runtime.vmk2 import digest


FEATURE_NAMES = tuple(f"x{i}" for i in range(8))
METHODS = (
    "DEPENDENCY_TRACE",
    "DISCRIMINATOR_DESIGN",
    "REPRODUCTION",
    "COMPARATOR_AUDIT",
    "RETURN_BOUNDARY_AUDIT",
)
WORK_USEFUL = "VENUS_WORK_RETURN: USEFUL"
WORK_UNHELPFUL = "VENUS_WORK_RETURN: UNHELPFUL"
METHOD_RE = re.compile(
    r"VENUS_METHOD_RETURN:\s*(" + "|".join(METHODS) + r"):\s*(USEFUL|UNHELPFUL)",
    re.I,
)
FEATURE_MARKER = "Venus-Features:"
CYCLE_MARKER = "Venus-Cycle:"
CUSTODY_MARKER = "Venus-Feature-Custody:"
METHOD_MARKER = "Venus-Method:"
_CYCLE_TITLE = re.compile(r"venus: autonomous cycle (issue|pr)-(\d+)$", re.I)
SELF_REVIEW_LOGINS = frozenset({
    "github-actions[bot]",
    "venus-developmental-worker",
    "venus-autonomous-steward",
})


@dataclass(frozen=True)
class TargetBarrier:
    kind: str
    number: int
    cycle_pr_number: int
    cycle_state: str
    outcome_at: str | None


@dataclass(frozen=True)
class WorkLearningState:
    seen_return_ids: tuple[str, ...]
    weights: Mapping[str, float]
    method_success: Mapping[str, int]
    method_failure: Mapping[str, int]
    learning_rate: float
    min_learning_rate: float
    max_learning_rate: float
    max_abs_weight: float
    last_reward: int | None
    last_feature_digest: str | None

    def method_utility(self, method: str) -> float:
        s = int(self.method_success.get(method, 0))
        f = int(self.method_failure.get(method, 0))
        total = s + f
        return 0.0 if total == 0 else (s - f) / total


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_return_ids=(),
        weights={name: 0.0 for name in FEATURE_NAMES},
        method_success={m: 0 for m in METHODS},
        method_failure={m: 0 for m in METHODS},
        learning_rate=0.1,
        min_learning_rate=0.025,
        max_learning_rate=0.2,
        max_abs_weight=2.0,
        last_reward=None,
        last_feature_digest=None,
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    # Older states used merge/close as reward or a different target abstraction.
    # Those observations are quarantined rather than silently reinterpreted.
    if obj.get("schema") != "Venus.AutonomousLearningState.v0.5":
        return empty_state()
    return WorkLearningState(
        seen_return_ids=tuple(str(x) for x in obj.get("seen_return_ids", ())),
        weights={
            name: float((obj.get("weights") or {}).get(name, 0.0))
            for name in FEATURE_NAMES
        },
        method_success={
            m: int((obj.get("method_success") or {}).get(m, 0)) for m in METHODS
        },
        method_failure={
            m: int((obj.get("method_failure") or {}).get(m, 0)) for m in METHODS
        },
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
        "schema": "Venus.AutonomousLearningState.v0.5",
        "seen_return_ids": list(state.seen_return_ids),
        "weights": dict(state.weights),
        "method_success": dict(state.method_success),
        "method_failure": dict(state.method_failure),
        "learning_rate": state.learning_rate,
        "min_learning_rate": state.min_learning_rate,
        "max_learning_rate": state.max_learning_rate,
        "max_abs_weight": state.max_abs_weight,
        "last_reward": state.last_reward,
        "last_feature_digest": state.last_feature_digest,
        "promotion_authority": False,
        "merge_authority": False,
        "release_authority": False,
        "truth_authority": False,
        "safety_floor_authority": False,
    }


def feature_custody(cycle_id: str, features: Mapping[str, bool]) -> str:
    canonical = {name: bool(features[name]) for name in FEATURE_NAMES}
    return digest({"cycle_id": str(cycle_id), "features": canonical})


def _cycle_markers(body: str) -> tuple[str, dict[str, bool], str, str | None] | None:
    cycle_id: str | None = None
    features: dict[str, bool] | None = None
    custody: str | None = None
    method: str | None = None
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
        elif line.startswith(METHOD_MARKER):
            candidate = line[len(METHOD_MARKER):].strip().upper()
            method = candidate if candidate in METHODS else None
    if not cycle_id or features is None or not custody:
        return None
    if feature_custody(cycle_id, features) != custody:
        return None
    return cycle_id, features, custody, method


def _review_login(review: Mapping[str, Any]) -> str:
    author = review.get("author") or {}
    if isinstance(author, Mapping):
        return str(author.get("login") or "")
    return ""


def _review_id(pr_number: int, review: Mapping[str, Any], index: int) -> str:
    rid = review.get("id") or review.get("submittedAt") or index
    return f"pr:{pr_number}:review:{rid}"


def _next_learning_rate(
    state: WorkLearningState,
    reward: int,
    feature_digest: str,
) -> float:
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
    seen = set(state.seen_return_ids)
    weights = {name: float(state.weights.get(name, 0.0)) for name in FEATURE_NAMES}
    method_success = dict(state.method_success)
    method_failure = dict(state.method_failure)
    current = state

    for pr in sorted(prs, key=lambda x: int(x["number"])):
        title = str(pr.get("title", ""))
        if not _CYCLE_TITLE.match(title):
            continue
        markers = _cycle_markers(str(pr.get("body") or ""))
        if markers is None:
            continue
        _cycle_id, features, custody, selected_method = markers
        pr_number = int(pr["number"])

        for index, review in enumerate(pr.get("reviews") or ()):
            login = _review_login(review)
            if not login or login.lower() in SELF_REVIEW_LOGINS:
                continue
            body = str(review.get("body") or "")
            prefix = _review_id(pr_number, review, index)

            useful = WORK_USEFUL in body
            unhelpful = WORK_UNHELPFUL in body
            if useful != unhelpful:
                return_id = prefix + ":work"
                if return_id not in seen:
                    reward = 1 if useful else -1
                    lr_used = current.learning_rate
                    for name, active in features.items():
                        if active:
                            weights[name] = max(
                                -current.max_abs_weight,
                                min(
                                    current.max_abs_weight,
                                    weights[name] + lr_used * reward,
                                ),
                            )
                    current = WorkLearningState(
                        seen_return_ids=current.seen_return_ids,
                        weights=weights,
                        method_success=method_success,
                        method_failure=method_failure,
                        learning_rate=_next_learning_rate(current, reward, custody),
                        min_learning_rate=current.min_learning_rate,
                        max_learning_rate=current.max_learning_rate,
                        max_abs_weight=current.max_abs_weight,
                        last_reward=reward,
                        last_feature_digest=custody,
                    )
                    seen.add(return_id)

            for mindex, match in enumerate(METHOD_RE.finditer(body)):
                method = match.group(1).upper()
                disposition = match.group(2).upper()
                return_id = f"{prefix}:method:{mindex}:{method}"
                if return_id in seen:
                    continue
                # A reviewer may score any declared method, but the cycle's
                # selected method is retained in custody for later attribution.
                bucket = method_success if disposition == "USEFUL" else method_failure
                bucket[method] = bucket.get(method, 0) + 1
                seen.add(return_id)

    return WorkLearningState(
        seen_return_ids=tuple(sorted(seen)),
        weights=weights,
        method_success=method_success,
        method_failure=method_failure,
        learning_rate=current.learning_rate,
        min_learning_rate=current.min_learning_rate,
        max_learning_rate=current.max_learning_rate,
        max_abs_weight=current.max_abs_weight,
        last_reward=current.last_reward,
        last_feature_digest=current.last_feature_digest,
    )


def target_barriers(prs: Iterable[Mapping[str, Any]]) -> tuple[TargetBarrier, ...]:
    out: list[TargetBarrier] = []
    for pr in prs:
        match = _CYCLE_TITLE.match(str(pr.get("title", "")))
        if not match:
            continue
        state_name = str(pr.get("state", "")).upper()
        outcome_at = pr.get("mergedAt") or pr.get("closedAt")
        out.append(
            TargetBarrier(
                kind=match.group(1).upper(),
                number=int(match.group(2)),
                cycle_pr_number=int(pr["number"]),
                cycle_state=state_name,
                outcome_at=str(outcome_at) if outcome_at else None,
            )
        )
    return tuple(sorted(out, key=lambda x: (x.kind, x.number, x.cycle_pr_number)))


def active_autonomous_cycle(prs: Iterable[Mapping[str, Any]]) -> bool:
    return any(b.cycle_state == "OPEN" for b in target_barriers(prs))
