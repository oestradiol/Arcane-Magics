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
import hashlib
import json
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
    cycle_carrier_kind: str = "PR"


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
        "schema": "Venus.AutonomousLearningState.v0.4",
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


def _return_time(review: Mapping[str, Any]) -> str:
    return str(
        review.get("submittedAt")
        or review.get("submitted_at")
        or review.get("createdAt")
        or review.get("created_at")
        or ""
    )


def _return_fingerprint(
    *,
    carrier_kind: str,
    carrier_number: int,
    login: str,
    body: str,
    returned_at: str,
) -> str:
    payload = {
        "carrier_kind": carrier_kind.upper(),
        "carrier_number": int(carrier_number),
        "author": login,
        "body": body,
        "submitted_at": returned_at,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def extract_explicit_returns(
    carriers: Iterable[Mapping[str, Any]],
) -> tuple[tuple[str, str, str, bool], ...]:
    """Return (return_id, axis, key, useful) from explicit external carrier returns."""
    out: list[tuple[str, str, str, bool]] = []
    for carrier in carriers:
        title = str(carrier.get("title", ""))
        match = _CYCLE_TITLE.match(title)
        if not match:
            continue
        kind = match.group(1).upper()
        carrier_number = int(carrier["number"])
        carrier_kind = str(carrier.get("_carrier_kind") or "PR").upper()
        returned_items = carrier.get("reviews") or carrier.get("comments") or ()
        for index, review in enumerate(returned_items):
            login = _review_login(review)
            if not login or login.lower() in SELF_REVIEW_LOGINS:
                continue
            body = _review_body(review)
            returned_at = _return_time(review)
            if not returned_at:
                # A stable external return identity requires provenance time.
                # Fail closed rather than silently keying learning to list order.
                continue
            fingerprint = _return_fingerprint(
                carrier_kind=carrier_kind,
                carrier_number=carrier_number,
                login=login,
                body=body,
                returned_at=returned_at,
            )
            return_prefix = f"return:{fingerprint}"

            useful = USEFUL_MARKER in body
            unhelpful = UNHELPFUL_MARKER in body
            if useful != unhelpful:
                out.append((
                    f"{return_prefix}:work",
                    "KIND",
                    kind,
                    useful,
                ))

            for mindex, mm in enumerate(METHOD_RE.finditer(body)):
                method = mm.group(1).upper()
                disposition = mm.group(2).upper()
                out.append((
                    f"{return_prefix}:method:{mindex}:{method}",
                    "METHOD",
                    method,
                    disposition == "USEFUL",
                ))
    return tuple(out)


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    """Compatibility name: accepts PR or issue cycle-carrier records."""
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
            cycle_carrier_kind=str(pr.get("_carrier_kind") or "PR").upper(),
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
