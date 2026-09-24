from __future__ import annotations

"""Bounded external-return learning for autonomous work and study-method choice.

Only explicit reviews authored outside the autonomous carrier may update this
state. Merge/close status, CI status, execution receipts, and Venus's own
comments are never rewards.

The learning state has three distinct adaptive surfaces:

1. work-class utility (ISSUE vs PR);
2. study-method utility;
3. opaque target-feature weights plus a bounded learning rate.

The third surface supports learning-to-learn, but the learning-rate bounds,
authority boundary, return source, and replay rules remain externally fixed.
"""

from dataclasses import dataclass
import json
import re
from typing import Any, Iterable, Mapping

from kernel.runtime.vmk2 import digest


USEFUL_MARKER = "VENUS_WORK_RETURN: USEFUL"
UNHELPFUL_MARKER = "VENUS_WORK_RETURN: UNHELPFUL"

METHODS = (
    "DEPENDENCY_TRACE",
    "DISCRIMINATOR_DESIGN",
    "REPRODUCTION",
    "COMPARATOR_AUDIT",
    "RETURN_BOUNDARY_AUDIT",
)
METHOD_RE = re.compile(
    r"VENUS_METHOD_RETURN:\s*(" + "|".join(METHODS) + r"):\s*(USEFUL|UNHELPFUL)",
    re.I,
)

FEATURE_NAMES = tuple(f"x{i}" for i in range(8))
CYCLE_MARKER = "Venus-Cycle:"
FEATURE_MARKER = "Venus-Features:"
METHOD_MARKER = "Venus-Study-Method:"
CUSTODY_MARKER = "Venus-Causal-Custody:"

SELF_REVIEW_LOGINS = frozenset({
    "github-actions[bot]",
    "venus-developmental-worker",
    "venus-autonomous-steward",
})
_CYCLE_TITLE = re.compile(r"venus: autonomous cycle (issue|pr)-(\d+)$", re.I)


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
    kind_success: Mapping[str, int]
    kind_failure: Mapping[str, int]
    method_success: Mapping[str, int]
    method_failure: Mapping[str, int]
    feature_weights: Mapping[str, float]
    learning_rate: float
    min_learning_rate: float
    max_learning_rate: float
    max_abs_weight: float
    last_work_reward: int | None
    last_feature_digest: str | None

    @staticmethod
    def _utility(
        success: Mapping[str, int],
        failure: Mapping[str, int],
        key: str,
    ) -> float:
        s = int(success.get(key, 0))
        f = int(failure.get(key, 0))
        total = s + f
        return 0.0 if total == 0 else (s - f) / total

    def utility(self, kind: str) -> float:
        return self._utility(self.kind_success, self.kind_failure, kind)

    def method_utility(self, method: str) -> float:
        return self._utility(self.method_success, self.method_failure, method)

    def feature_utility(self, features: Mapping[str, bool]) -> float:
        return sum(
            float(self.feature_weights.get(name, 0.0))
            for name, active in features.items()
            if active
        )


@dataclass(frozen=True)
class ExplicitReturn:
    return_id: str
    axis: str
    key: str
    useful: bool
    features: Mapping[str, bool] | None = None


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_return_ids=(),
        kind_success={"ISSUE": 0, "PR": 0},
        kind_failure={"ISSUE": 0, "PR": 0},
        method_success={m: 0 for m in METHODS},
        method_failure={m: 0 for m in METHODS},
        feature_weights={name: 0.0 for name in FEATURE_NAMES},
        learning_rate=0.1,
        min_learning_rate=0.025,
        max_learning_rate=0.2,
        max_abs_weight=2.0,
        last_work_reward=None,
        last_feature_digest=None,
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    if obj.get("schema") == "Venus.AutonomousLearningState.v0.1":
        return empty_state()

    base = empty_state()
    return WorkLearningState(
        seen_return_ids=tuple(str(x) for x in obj.get("seen_return_ids", ())),
        kind_success={
            "ISSUE": int((obj.get("kind_success") or {}).get("ISSUE", 0)),
            "PR": int((obj.get("kind_success") or {}).get("PR", 0)),
        },
        kind_failure={
            "ISSUE": int((obj.get("kind_failure") or {}).get("ISSUE", 0)),
            "PR": int((obj.get("kind_failure") or {}).get("PR", 0)),
        },
        method_success={
            m: int((obj.get("method_success") or {}).get(m, 0)) for m in METHODS
        },
        method_failure={
            m: int((obj.get("method_failure") or {}).get(m, 0)) for m in METHODS
        },
        feature_weights={
            name: float((obj.get("feature_weights") or {}).get(name, 0.0))
            for name in FEATURE_NAMES
        },
        learning_rate=float(obj.get("learning_rate", base.learning_rate)),
        min_learning_rate=float(
            obj.get("min_learning_rate", base.min_learning_rate)
        ),
        max_learning_rate=float(
            obj.get("max_learning_rate", base.max_learning_rate)
        ),
        max_abs_weight=float(obj.get("max_abs_weight", base.max_abs_weight)),
        last_work_reward=(
            None
            if obj.get("last_work_reward") is None
            else int(obj["last_work_reward"])
        ),
        last_feature_digest=(
            None
            if obj.get("last_feature_digest") is None
            else str(obj["last_feature_digest"])
        ),
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.4",
        "seen_return_ids": list(state.seen_return_ids),
        "kind_success": dict(state.kind_success),
        "kind_failure": dict(state.kind_failure),
        "method_success": dict(state.method_success),
        "method_failure": dict(state.method_failure),
        "feature_weights": dict(state.feature_weights),
        "learning_rate": state.learning_rate,
        "min_learning_rate": state.min_learning_rate,
        "max_learning_rate": state.max_learning_rate,
        "max_abs_weight": state.max_abs_weight,
        "last_work_reward": state.last_work_reward,
        "last_feature_digest": state.last_feature_digest,
        "promotion_authority": False,
        "merge_authority": False,
        "truth_authority": False,
        "safety_floor_authority": False,
    }


def cycle_custody(
    cycle_id: str,
    features: Mapping[str, bool],
    study_method: str,
) -> str:
    if set(features) != set(FEATURE_NAMES):
        raise ValueError("feature custody requires exact opaque coordinate set")
    if study_method not in METHODS:
        raise ValueError("feature custody requires admitted study method")
    canonical = {name: bool(features[name]) for name in FEATURE_NAMES}
    return digest({
        "cycle_id": str(cycle_id),
        "features": canonical,
        "study_method": study_method,
    })


def _review_login(review: Mapping[str, Any]) -> str:
    author = review.get("author") or {}
    if isinstance(author, Mapping):
        return str(author.get("login") or "")
    return ""


def _review_body(review: Mapping[str, Any]) -> str:
    return str(review.get("body") or "")


def _cycle_causal_markers(
    pr: Mapping[str, Any],
) -> tuple[str, dict[str, bool], str, str] | None:
    cycle_id: str | None = None
    features: dict[str, bool] | None = None
    study_method: str | None = None
    custody: str | None = None

    for line in str(pr.get("body") or "").splitlines():
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
        elif line.startswith(METHOD_MARKER):
            study_method = line[len(METHOD_MARKER):].strip().upper()
        elif line.startswith(CUSTODY_MARKER):
            custody = line[len(CUSTODY_MARKER):].strip()

    if not cycle_id or features is None or not study_method or not custody:
        return None
    if study_method not in METHODS:
        return None
    if cycle_custody(cycle_id, features, study_method) != custody:
        return None
    return cycle_id, features, study_method, custody


def _external_reviews(pr: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    rows = []
    for review in pr.get("reviews") or ():
        if not isinstance(review, Mapping):
            continue
        login = _review_login(review)
        if not login or login.lower() in SELF_REVIEW_LOGINS:
            continue
        rows.append(review)
    return tuple(rows)


def _unanimous(values: Iterable[bool]) -> bool | None:
    rows = tuple(values)
    if not rows:
        return None
    if all(x == rows[0] for x in rows):
        return rows[0]
    return None


def extract_explicit_returns(
    prs: Iterable[Mapping[str, Any]],
) -> tuple[ExplicitReturn, ...]:
    """Extract at most one work return and one used-method return per cycle.

    A cycle must be resolved before its reviews can train the next learner
    state. Conflicting external reviews WITHHOLD learning on that axis.
    """
    out: list[ExplicitReturn] = []

    for pr in sorted(prs, key=lambda row: int(row["number"])):
        title = str(pr.get("title", ""))
        match = _CYCLE_TITLE.match(title)
        if not match:
            continue
        if str(pr.get("state", "")).upper() == "OPEN":
            continue

        markers = _cycle_causal_markers(pr)
        if markers is None:
            continue
        _cycle_id, features, study_method, _custody = markers

        reviews = _external_reviews(pr)
        kind = match.group(1).upper()
        pr_number = int(pr["number"])

        work_values: list[bool] = []
        method_values: list[bool] = []

        for review in reviews:
            body = _review_body(review)

            useful = USEFUL_MARKER in body
            unhelpful = UNHELPFUL_MARKER in body
            if useful != unhelpful:
                work_values.append(useful)

            for mm in METHOD_RE.finditer(body):
                method = mm.group(1).upper()
                if method != study_method:
                    continue
                method_values.append(mm.group(2).upper() == "USEFUL")

        work = _unanimous(work_values)
        if work is not None:
            out.append(ExplicitReturn(
                return_id=f"pr:{pr_number}:work",
                axis="KIND_AND_FEATURE",
                key=kind,
                useful=work,
                features=features,
            ))

        method = _unanimous(method_values)
        if method is not None:
            out.append(ExplicitReturn(
                return_id=f"pr:{pr_number}:method:{study_method}",
                axis="METHOD",
                key=study_method,
                useful=method,
                features=None,
            ))

    return tuple(out)


def _next_learning_rate(
    state: WorkLearningState,
    reward: int,
    feature_digest: str,
) -> float:
    if state.last_work_reward is None:
        return state.learning_rate
    if reward != state.last_work_reward:
        return max(state.min_learning_rate, state.learning_rate * 0.5)
    if feature_digest != state.last_feature_digest:
        return min(state.max_learning_rate, state.learning_rate * 1.1)
    return state.learning_rate


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_return_ids)
    kind_success = dict(state.kind_success)
    kind_failure = dict(state.kind_failure)
    method_success = dict(state.method_success)
    method_failure = dict(state.method_failure)
    feature_weights = {
        name: float(state.feature_weights.get(name, 0.0))
        for name in FEATURE_NAMES
    }

    current = state

    for returned in extract_explicit_returns(prs):
        if returned.return_id in seen:
            continue

        if returned.axis == "KIND_AND_FEATURE":
            kind_bucket = kind_success if returned.useful else kind_failure
            kind_bucket[returned.key] = kind_bucket.get(returned.key, 0) + 1

            assert returned.features is not None
            reward = 1 if returned.useful else -1
            lr_used = current.learning_rate
            for name, active in returned.features.items():
                if active:
                    feature_weights[name] = max(
                        -current.max_abs_weight,
                        min(
                            current.max_abs_weight,
                            feature_weights[name] + lr_used * reward,
                        ),
                    )

            pattern_digest = digest({
                name: bool(returned.features[name]) for name in FEATURE_NAMES
            })
            current = WorkLearningState(
                seen_return_ids=current.seen_return_ids,
                kind_success=kind_success,
                kind_failure=kind_failure,
                method_success=method_success,
                method_failure=method_failure,
                feature_weights=feature_weights,
                learning_rate=_next_learning_rate(
                    current, reward, pattern_digest
                ),
                min_learning_rate=current.min_learning_rate,
                max_learning_rate=current.max_learning_rate,
                max_abs_weight=current.max_abs_weight,
                last_work_reward=reward,
                last_feature_digest=pattern_digest,
            )
        elif returned.axis == "METHOD":
            method_bucket = method_success if returned.useful else method_failure
            method_bucket[returned.key] = method_bucket.get(returned.key, 0) + 1
        else:
            continue

        seen.add(returned.return_id)

    return WorkLearningState(
        seen_return_ids=tuple(sorted(seen)),
        kind_success=kind_success,
        kind_failure=kind_failure,
        method_success=method_success,
        method_failure=method_failure,
        feature_weights=feature_weights,
        learning_rate=current.learning_rate,
        min_learning_rate=current.min_learning_rate,
        max_learning_rate=current.max_learning_rate,
        max_abs_weight=current.max_abs_weight,
        last_work_reward=current.last_work_reward,
        last_feature_digest=current.last_feature_digest,
    )


def target_barriers(prs: Iterable[Mapping[str, Any]]) -> tuple[TargetBarrier, ...]:
    out: list[TargetBarrier] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = _CYCLE_TITLE.match(title)
        if not match:
            continue
        state_name = str(pr.get("state", "")).upper()
        outcome_at = pr.get("mergedAt") or pr.get("closedAt")
        out.append(TargetBarrier(
            kind=match.group(1).upper(),
            number=int(match.group(2)),
            cycle_pr_number=int(pr["number"]),
            cycle_state=state_name,
            outcome_at=str(outcome_at) if outcome_at else None,
        ))
    return tuple(sorted(out, key=lambda x: (x.kind, x.number, x.cycle_pr_number)))


def target_markers(prs: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted({
        (barrier.kind, barrier.number)
        for barrier in target_barriers(prs)
        if barrier.cycle_state == "OPEN"
    }))


def active_autonomous_cycle(prs: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        barrier.cycle_state == "OPEN"
        for barrier in target_barriers(prs)
    )
