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
from pathlib import Path
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
TRACE_CONFIG_RE = re.compile(
    r"VENUS_TRACE_CONFIG_RETURN:\s*([A-Z0-9_-]+):\s*(USEFUL|UNHELPFUL)",
    re.I,
)
SELF_REVIEW_LOGINS = frozenset({
    "github-actions[bot]",
    "venus-developmental-worker",
    "venus-autonomous-steward",
})
_CYCLE_TITLE = re.compile(r"venus: autonomous cycle (issue|pr)-(\d+)$", re.I)
_RETURN_AUTHORITY_PATH = Path(__file__).with_name("AUTONOMOUS_RETURN_AUTHORITY.json")


def authorized_return_logins() -> frozenset[str]:
    obj = json.loads(_RETURN_AUTHORITY_PATH.read_text(encoding="utf-8"))
    if obj.get("schema") != "Venus.AutonomousReturnAuthority.v0.1":
        raise ValueError("unsupported autonomous return-authority schema")
    if obj.get("autonomy_may_modify") is not False:
        raise ValueError("autonomous worker may not own return-authority mutation")
    if obj.get("promotion_authority") is not False:
        raise ValueError("return authority may not grant promotion authority")
    rows = frozenset(str(x).strip().lower() for x in obj.get("authorized_reviewer_logins", ()) if str(x).strip())
    if not rows:
        raise ValueError("at least one authorized external reviewer is required")
    if "*" in rows:
        raise ValueError("wildcard reviewer authority is forbidden")
    if rows & SELF_REVIEW_LOGINS:
        raise ValueError("self-review identity may not be authorized as external learning return")
    return rows


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
    trace_config_success: Mapping[str, int]
    trace_config_failure: Mapping[str, int]

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

    def trace_config_utility(self, config_id: str) -> float:
        return self._utility(
            self.trace_config_success,
            self.trace_config_failure,
            config_id,
        )

    def trace_config_attempts(self, config_id: str) -> int:
        return int(self.trace_config_success.get(config_id, 0)) + int(
            self.trace_config_failure.get(config_id, 0)
        )


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_return_ids=(),
        kind_success={"ISSUE": 0, "PR": 0},
        kind_failure={"ISSUE": 0, "PR": 0},
        method_success={m: 0 for m in METHODS},
        method_failure={m: 0 for m in METHODS},
        trace_config_success={},
        trace_config_failure={},
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
        trace_config_success={
            str(k): int(v)
            for k, v in (obj.get("trace_config_success") or {}).items()
        },
        trace_config_failure={
            str(k): int(v)
            for k, v in (obj.get("trace_config_failure") or {}).items()
        },
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.5",
        "seen_return_ids": list(state.seen_return_ids),
        "kind_success": dict(state.kind_success),
        "kind_failure": dict(state.kind_failure),
        "method_success": dict(state.method_success),
        "method_failure": dict(state.method_failure),
        "trace_config_success": dict(state.trace_config_success),
        "trace_config_failure": dict(state.trace_config_failure),
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
    *,
    authorized_logins: Iterable[str] | None = None,
) -> tuple[tuple[str, str, str, bool], ...]:
    """Return eligible learning signals from explicit authorized external returns."""
    authority = (
        authorized_return_logins()
        if authorized_logins is None
        else frozenset(str(x).strip().lower() for x in authorized_logins if str(x).strip())
    )
    if not authority or "*" in authority:
        raise ValueError("learning-return authority must be explicit and non-wildcard")
    if authority & SELF_REVIEW_LOGINS:
        raise ValueError("self-review identity cannot authorize its own learning return")
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
            login_l = login.lower()
            if not login or login_l in SELF_REVIEW_LOGINS:
                continue
            if login_l not in authority:
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

            method_returns: dict[str, list[tuple[int, str]]] = {}
            for mindex, mm in enumerate(METHOD_RE.finditer(body)):
                method = mm.group(1).upper()
                disposition = mm.group(2).upper()
                method_returns.setdefault(method, []).append((mindex, disposition))
            for method, rows in sorted(method_returns.items()):
                dispositions = {disposition for _, disposition in rows}
                if len(dispositions) != 1:
                    # One returned review cannot train both sides of the same
                    # method axis. Ambiguity is retained as no learning signal.
                    continue
                first_index = min(index for index, _ in rows)
                disposition = next(iter(dispositions))
                out.append((
                    f"{return_prefix}:method:{first_index}:{method}",
                    "METHOD",
                    method,
                    disposition == "USEFUL",
                ))

            trace_returns: dict[str, list[tuple[int, str]]] = {}
            for tindex, tm in enumerate(TRACE_CONFIG_RE.finditer(body)):
                config_id = tm.group(1).upper()
                disposition = tm.group(2).upper()
                trace_returns.setdefault(config_id, []).append((tindex, disposition))
            for config_id, rows in sorted(trace_returns.items()):
                dispositions = {disposition for _, disposition in rows}
                if len(dispositions) != 1:
                    continue
                first_index = min(index for index, _ in rows)
                disposition = next(iter(dispositions))
                out.append((
                    f"{return_prefix}:trace:{first_index}:{config_id}",
                    "TRACE_CONFIG",
                    config_id,
                    disposition == "USEFUL",
                ))
    return tuple(out)


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
    *,
    authorized_logins: Iterable[str] | None = None,
) -> WorkLearningState:
    """Compatibility name: accepts PR or issue cycle-carrier records."""
    seen = set(state.seen_return_ids)
    kind_success = dict(state.kind_success)
    kind_failure = dict(state.kind_failure)
    method_success = dict(state.method_success)
    method_failure = dict(state.method_failure)
    trace_config_success = dict(state.trace_config_success)
    trace_config_failure = dict(state.trace_config_failure)

    for return_id, axis, key, useful in extract_explicit_returns(
        prs,
        authorized_logins=authorized_logins,
    ):
        if return_id in seen:
            continue
        if axis == "KIND":
            bucket = kind_success if useful else kind_failure
        elif axis == "METHOD":
            bucket = method_success if useful else method_failure
        elif axis == "TRACE_CONFIG":
            bucket = trace_config_success if useful else trace_config_failure
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
        trace_config_success=trace_config_success,
        trace_config_failure=trace_config_failure,
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
