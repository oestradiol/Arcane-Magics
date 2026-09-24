from __future__ import annotations

"""Bounded learning state for autonomous work selection and study-method choice.

Only explicit externally authored review returns update this state.
Merge/close status, CI success, execution receipts, and Venus's own comments
are not rewards. Learned preference may alter what Venus studies and how she
studies it; it never grants merge, promotion, truth, or scientific-warrant
authority.

Target recurrence is separately retained: a studied target stays blocked until
its own GitHub state changes after the prior autonomous-cycle outcome.
"""

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping


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

    @staticmethod
    def _utility(success: Mapping[str, int], failure: Mapping[str, int], key: str) -> float:
        s = int(success.get(key, 0))
        f = int(failure.get(key, 0))
        total = s + f
        return 0.0 if total == 0 else (s - f) / total

    def utility(self, kind: str) -> float:
        return self._utility(self.kind_success, self.kind_failure, kind)

    def method_utility(self, method: str) -> float:
        return self._utility(self.method_success, self.method_failure, method)


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_return_ids=(),
        kind_success={"ISSUE": 0, "PR": 0},
        kind_failure={"ISSUE": 0, "PR": 0},
        method_success={m: 0 for m in METHODS},
        method_failure={m: 0 for m in METHODS},
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    # v0.1 used merge/close admission as a reward source. Those counts are
    # invalid under the corrected admission != utility distinction.
    if obj.get("schema") == "Venus.AutonomousLearningState.v0.1":
        return empty_state()
    return WorkLearningState(
        seen_return_ids=tuple(str(x) for x in obj.get("seen_return_ids", ())),
        kind_success={str(k): int(v) for k, v in obj.get("kind_success", {}).items()},
        kind_failure={str(k): int(v) for k, v in obj.get("kind_failure", {}).items()},
        method_success={
            m: int((obj.get("method_success") or {}).get(m, 0)) for m in METHODS
        },
        method_failure={
            m: int((obj.get("method_failure") or {}).get(m, 0)) for m in METHODS
        },
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.3",
        "seen_return_ids": list(state.seen_return_ids),
        "kind_success": dict(state.kind_success),
        "kind_failure": dict(state.kind_failure),
        "method_success": dict(state.method_success),
        "method_failure": dict(state.method_failure),
        "promotion_authority": False,
        "merge_authority": False,
        "truth_authority": False,
        "safety_floor_authority": False,
    }


def _review_login(review: Mapping[str, Any]) -> str:
    author = review.get("author") or {}
    if isinstance(author, Mapping):
        return str(author.get("login") or "")
    return ""


def _review_body(review: Mapping[str, Any]) -> str:
    return str(review.get("body") or "")


def extract_explicit_returns(
    prs: Iterable[Mapping[str, Any]],
) -> tuple[tuple[str, str, str, bool], ...]:
    """Return (return_id, axis, key, useful) from explicit external reviews."""
    out: list[tuple[str, str, str, bool]] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = _CYCLE_TITLE.match(title)
        if not match:
            continue
        kind = match.group(1).upper()
        pr_number = int(pr["number"])
        for index, review in enumerate(pr.get("reviews") or ()):
            login = _review_login(review)
            if not login or login.lower() in SELF_REVIEW_LOGINS:
                continue
            body = _review_body(review)
            review_id = review.get("id") or review.get("submittedAt") or index

            useful = USEFUL_MARKER in body
            unhelpful = UNHELPFUL_MARKER in body
            if useful != unhelpful:
                out.append((
                    f"pr:{pr_number}:review:{review_id}:work",
                    "KIND",
                    kind,
                    useful,
                ))

            for mindex, mm in enumerate(METHOD_RE.finditer(body)):
                method = mm.group(1).upper()
                disposition = mm.group(2).upper()
                out.append((
                    f"pr:{pr_number}:review:{review_id}:method:{mindex}:{method}",
                    "METHOD",
                    method,
                    disposition == "USEFUL",
                ))
    return tuple(out)


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_return_ids)
    kind_success = dict(state.kind_success)
    kind_failure = dict(state.kind_failure)
    method_success = dict(state.method_success)
    method_failure = dict(state.method_failure)

    for return_id, axis, key, useful in extract_explicit_returns(prs):
        if return_id in seen:
            continue
        if axis == "KIND":
            bucket = kind_success if useful else kind_failure
        elif axis == "METHOD":
            bucket = method_success if useful else method_failure
        else:
            continue
        bucket[key] = bucket.get(key, 0) + 1
        seen.add(return_id)

    return WorkLearningState(
        seen_return_ids=tuple(sorted(seen)),
        kind_success=kind_success,
        kind_failure=kind_failure,
        method_success=method_success,
        method_failure=method_failure,
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
    """Compatibility view for currently open autonomous cycles."""
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
