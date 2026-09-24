from __future__ import annotations

"""Bounded learning state for autonomous work selection.

Only explicit externally authored work-return reviews update this state.
Merge/close status, CI success, execution receipts, and Venus's own comments
are not learning rewards. The state may alter future target selection but never
grants merge, promotion, truth, or scientific-warrant authority.
"""

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping


USEFUL_MARKER = "VENUS_WORK_RETURN: USEFUL"
UNHELPFUL_MARKER = "VENUS_WORK_RETURN: UNHELPFUL"
SELF_REVIEW_LOGINS = frozenset({
    "github-actions[bot]",
    "venus-developmental-worker",
    "venus-autonomous-steward",
})


@dataclass(frozen=True)
class WorkLearningState:
    seen_return_ids: tuple[str, ...]
    kind_success: Mapping[str, int]
    kind_failure: Mapping[str, int]

    def utility(self, kind: str) -> float:
        success = int(self.kind_success.get(kind, 0))
        failure = int(self.kind_failure.get(kind, 0))
        total = success + failure
        return 0.0 if total == 0 else (success - failure) / total


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_return_ids=(),
        kind_success={"ISSUE": 0, "PR": 0},
        kind_failure={"ISSUE": 0, "PR": 0},
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    # v0.1 compatibility: old seen_cycle_prs are intentionally not treated as
    # learning returns because merge/close status was an invalid reward source.
    return WorkLearningState(
        seen_return_ids=tuple(str(x) for x in obj.get("seen_return_ids", ())),
        kind_success={str(k): int(v) for k, v in obj.get("kind_success", {}).items()},
        kind_failure={str(k): int(v) for k, v in obj.get("kind_failure", {}).items()},
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.2",
        "seen_return_ids": list(state.seen_return_ids),
        "kind_success": dict(state.kind_success),
        "kind_failure": dict(state.kind_failure),
        "promotion_authority": False,
        "merge_authority": False,
        "truth_authority": False,
    }


def _review_login(review: Mapping[str, Any]) -> str:
    author = review.get("author") or {}
    if isinstance(author, Mapping):
        return str(author.get("login") or "")
    return ""


def _review_body(review: Mapping[str, Any]) -> str:
    return str(review.get("body") or "")


def extract_explicit_work_returns(
    prs: Iterable[Mapping[str, Any]],
) -> tuple[tuple[str, str, bool], ...]:
    """Return (return_id, kind, useful) from explicit external reviews only."""
    out: list[tuple[str, str, bool]] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if not match:
            continue
        kind = match.group(1).upper()
        pr_number = int(pr["number"])
        for index, review in enumerate(pr.get("reviews") or ()):
            login = _review_login(review)
            if not login or login.lower() in SELF_REVIEW_LOGINS:
                continue
            body = _review_body(review)
            useful = USEFUL_MARKER in body
            unhelpful = UNHELPFUL_MARKER in body
            if useful == unhelpful:
                continue
            review_id = review.get("id") or review.get("submittedAt") or index
            return_id = f"pr:{pr_number}:review:{review_id}"
            out.append((return_id, kind, useful))
    return tuple(out)


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_return_ids)
    success = dict(state.kind_success)
    failure = dict(state.kind_failure)

    for return_id, kind, useful in extract_explicit_work_returns(prs):
        if return_id in seen:
            continue
        if useful:
            success[kind] = success.get(kind, 0) + 1
        else:
            failure[kind] = failure.get(kind, 0) + 1
        seen.add(return_id)

    return WorkLearningState(
        seen_return_ids=tuple(sorted(seen)),
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
