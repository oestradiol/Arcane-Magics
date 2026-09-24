from __future__ import annotations

"""Bounded learning state for autonomous work selection and study-method choice.

Only explicit externally authored review returns update this state.
Merge/close status, CI success, execution receipts, and Venus's own comments
are not rewards. Learned preference may alter what Venus studies and how she
studies it; it never grants merge, promotion, truth, or scientific-warrant
authority.
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
    # v0.1 used merge/close status as reward. Those counts are invalid under
    # the corrected admission != utility distinction and must not migrate.
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

            method_matches = list(METHOD_RE.finditer(body))
            for mindex, mm in enumerate(method_matches):
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


def target_markers(prs: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, int], ...]:
    out: list[tuple[str, int]] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if match and str(pr.get("state", "")).upper() == "OPEN":
            out.append((match.group(1).upper(), int(match.group(2))))
    return tuple(sorted(set(out)))
