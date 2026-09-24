from __future__ import annotations

"""Bounded learning state for autonomous work selection.

Only externally returned GitHub outcomes update this state. The state may alter
future target selection, but it never grants merge/promotion authority.
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
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if not match:
            continue
        # Open work is not an outcome yet.
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


def target_markers(prs: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, int], ...]:
    out: list[tuple[str, int]] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if match and str(pr.get("state", "")).upper() == "OPEN":
            out.append((match.group(1).upper(), int(match.group(2))))
    return tuple(sorted(set(out)))
