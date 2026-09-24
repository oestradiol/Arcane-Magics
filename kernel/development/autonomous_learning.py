from __future__ import annotations

"""Bounded learning state for autonomous work selection.

Only externally returned GitHub outcomes update this state. The state may alter
future target selection, but it never grants merge/promotion authority.

Target-level recurrence is also retained: a studied target remains blocked after
an autonomous cycle resolves until that target receives a newer GitHub update.
"""

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class WorkLearningState:
    seen_cycle_prs: tuple[int, ...]
    kind_success: Mapping[str, int]
    kind_failure: Mapping[str, int]

    def utility(self, kind: str) -> float:
        success = int(self.kind_success.get(kind, 0))
        failure = int(self.kind_failure.get(kind, 0))
        total = success + failure
        return 0.0 if total == 0 else (success - failure) / total


@dataclass(frozen=True)
class TargetBarrier:
    kind: str
    number: int
    cycle_pr_number: int
    cycle_state: str
    outcome_at: str | None


_CYCLE_TITLE = re.compile(r"venus: autonomous cycle (issue|pr)-(\d+)$", re.I)


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_cycle_prs=(),
        kind_success={"ISSUE": 0, "PR": 0},
        kind_failure={"ISSUE": 0, "PR": 0},
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    return WorkLearningState(
        seen_cycle_prs=tuple(int(x) for x in obj.get("seen_cycle_prs", ())),
        kind_success={str(k): int(v) for k, v in obj.get("kind_success", {}).items()},
        kind_failure={str(k): int(v) for k, v in obj.get("kind_failure", {}).items()},
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.1",
        "seen_cycle_prs": list(state.seen_cycle_prs),
        "kind_success": dict(state.kind_success),
        "kind_failure": dict(state.kind_failure),
        "promotion_authority": False,
    }


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_cycle_prs)
    success = dict(state.kind_success)
    failure = dict(state.kind_failure)

    for pr in prs:
        number = int(pr["number"])
        if number in seen:
            continue
        title = str(pr.get("title", ""))
        match = _CYCLE_TITLE.match(title)
        if not match:
            continue
        state_name = str(pr.get("state", "")).upper()
        merged = bool(pr.get("mergedAt"))
        if state_name == "OPEN":
            continue
        kind = match.group(1).upper()
        if merged:
            success[kind] = success.get(kind, 0) + 1
        else:
            failure[kind] = failure.get(kind, 0) + 1
        seen.add(number)

    return WorkLearningState(
        seen_cycle_prs=tuple(sorted(seen)),
        kind_success=success,
        kind_failure=failure,
    )


def target_barriers(prs: Iterable[Mapping[str, Any]]) -> tuple[TargetBarrier, ...]:
    """Retain target-level STOP/WITHHOLD until a newer target update returns."""
    out: list[TargetBarrier] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = _CYCLE_TITLE.match(title)
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


def target_markers(prs: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, int], ...]:
    """Compatibility view for currently open autonomous cycles."""
    return tuple(
        sorted({
            (b.kind, b.number)
            for b in target_barriers(prs)
            if b.cycle_state == "OPEN"
        })
    )
