from __future__ import annotations

"""Learner-owned bounded target selection for the Venus repository worker.

Target choice is driven by state-owned opaque feature weights plus a
content-addressed tie-break. The host roadmap is retained only as contextual
provenance and has zero selection weight.

The internalized O* policy remains causally upstream of work disposition.
A pending autonomous cycle forces STOP, and a resolved target remains behind a
barrier until that target itself changes after the prior cycle outcome.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from kernel.development.autonomous_learning import METHODS, TargetBarrier
from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.vmk2 import digest


FORBIDDEN_OPERATIONS = frozenset({
    "MERGE_PR",
    "RELEASE",
    "PROMOTE_AUTHORITY",
    "CLOSE_ISSUE",
    "DELETE_HISTORY",
    "CHANGE_BRANCH_PROTECTION",
    "ACCESS_SECRETS",
    "SELF_VALIDATE",
    "MINT_RETURN",
    "CHANGE_SAFETY_FLOOR",
    "CHANGE_JURISDICTION",
})

ALLOWED_OPERATIONS = (
    "READ_REPOSITORY",
    "READ_ISSUES",
    "READ_PRS",
    "RUN_TESTS",
    "STUDY_TARGET",
    "PROPOSE_PATCH",
    "OPEN_DRAFT_PR",
    "COMMENT_WITH_RECEIPT",
)


@dataclass(frozen=True)
class WorkItem:
    kind: str
    number: int
    title: str
    state: str = "OPEN"
    draft: bool = False
    merge_state: str | None = None
    updated_at: str | None = None
    has_comments: bool = False
    has_labels: bool = False
    ci_failed: bool = False
    ci_pending: bool = False


@dataclass(frozen=True)
class AutonomousCycleReceipt:
    schema: str
    cycle_id: str
    target_kind: str | None
    target_number: int | None
    target_title: str | None
    decision: str
    rationale: tuple[str, ...]
    feature_snapshot: Mapping[str, bool]
    study_method: str | None
    allowed_operations: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    source_digest: str
    promotion_authority: bool = False
    merge_authority: bool = False
    release_authority: bool = False


def item_features(item: WorkItem, *, now: datetime | None = None) -> dict[str, bool]:
    now = now or datetime.now(timezone.utc)
    recent = False
    if item.updated_at:
        try:
            stamp = datetime.fromisoformat(item.updated_at.replace("Z", "+00:00"))
            recent = (now - stamp).total_seconds() <= 7 * 24 * 3600
        except ValueError:
            recent = False
    return {
        "x0": item.kind.upper() == "PR",
        "x1": bool(item.draft),
        "x2": bool(item.ci_failed),
        "x3": bool(item.ci_pending),
        "x4": item.merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"},
        "x5": bool(item.has_comments),
        "x6": bool(item.has_labels),
        "x7": recent,
    }


def _score(item: WorkItem, weights: Mapping[str, float]) -> float:
    features = item_features(item)
    return sum(float(weights.get(k, 0.0)) for k, active in features.items() if active)


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _blocked_by_barrier(item: WorkItem, barriers: Iterable[TargetBarrier]) -> bool:
    matching = tuple(
        b for b in barriers if b.kind == item.kind.upper() and b.number == item.number
    )
    if not matching:
        return False
    if any(b.cycle_state == "OPEN" for b in matching):
        return True
    item_time = _parse_time(item.updated_at)
    if item_time is None:
        return True
    outcomes = tuple(
        t for t in (_parse_time(b.outcome_at) for b in matching) if t is not None
    )
    if not outcomes:
        return True
    return item_time <= max(outcomes)


def choose_target(
    items: Iterable[WorkItem],
    *,
    learner_state_id: str,
    feature_weights: Mapping[str, float],
    target_barriers: Iterable[TargetBarrier] = (),
    active_autonomous_cycle: bool = False,
) -> WorkItem | None:
    if active_autonomous_cycle:
        return None
    barriers = tuple(target_barriers)
    rows = tuple(
        item for item in items
        if item.state.upper() == "OPEN"
        and not (
            item.kind.upper() == "PR"
            and item.title.lower().startswith("venus: autonomous cycle")
        )
        and not _blocked_by_barrier(item, barriers)
    )
    if not rows:
        return None
    return sorted(
        rows,
        key=lambda item: (
            -_score(item, feature_weights),
            digest({
                "learner_state_id": learner_state_id,
                "kind": item.kind,
                "number": item.number,
                "title": item.title,
            }),
        ),
    )[0]


def choose_study_method(
    target: WorkItem,
    method_utility: Mapping[str, float],
) -> str:
    return sorted(
        METHODS,
        key=lambda method: (
            -float(method_utility.get(method, 0.0)),
            digest({
                "target": [target.kind, target.number, target.title],
                "method": method,
            }),
        ),
    )[0]


def make_cycle(
    *,
    issues: Iterable[WorkItem],
    prs: Iterable[WorkItem],
    roadmap_text: str,
    internal_policy: Mapping[str, Any],
    learner_state_id: str,
    feature_weights: Mapping[str, float],
    method_utility: Mapping[str, float],
    target_barriers: Iterable[TargetBarrier],
    active_autonomous_cycle: bool,
) -> AutonomousCycleReceipt:
    items = tuple(issues) + tuple(prs)
    target = choose_target(
        items,
        learner_state_id=learner_state_id,
        feature_weights=feature_weights,
        target_barriers=target_barriers,
        active_autonomous_cycle=active_autonomous_cycle,
    )
    source = {
        "items": [asdict(item) for item in items],
        "roadmap_digest_context_only": digest(roadmap_text),
        "learner_state_id": learner_state_id,
        "feature_weights": dict(feature_weights),
        "method_utility": dict(method_utility),
        "target_barriers": [asdict(x) for x in target_barriers],
        "active_autonomous_cycle": active_autonomous_cycle,
    }

    if target is None:
        decision = "STOP"
        rationale = (
            "no admissible OPEN target, a prior autonomous cycle still awaits external return, or retained changed-World reopening barriers remain closed",
        )
        features: Mapping[str, bool] = {}
        method = None
    else:
        features = item_features(target)
        method = choose_study_method(target, method_utility)
        safety_features = {
            "f0": True,
            "f1": target.merge_state not in {"BLOCKED", "CONFLICTING"},
            "f2": True,
            "f3": True,
            "f4": False,
            "f5": True,
            "f6": False,
            "f7": False,
        }
        decision = execute_tree(internal_policy, safety_features)
        if decision == "ACT":
            decision = "PROBE"
        rationale = (
            "target selected from state-owned returned-review feature weights",
            "content-addressed tie-break resolves equal learned score",
            "internalized learner-side O* policy is causally upstream of disposition",
            "study method selected from separately returned method utility",
            "host roadmap is context/provenance only and has zero selection weight",
            "prior target study remains withheld until newer target state reopens it",
            "draft proposal only; admission, truth, merge and promotion remain external",
        )

    body = {
        "schema": "Venus.AutonomousCycleReceipt.v0.4",
        "target_kind": target.kind if target else None,
        "target_number": target.number if target else None,
        "target_title": target.title if target else None,
        "decision": decision,
        "rationale": rationale,
        "feature_snapshot": dict(features),
        "study_method": method,
        "allowed_operations": ALLOWED_OPERATIONS,
        "forbidden_operations": tuple(sorted(FORBIDDEN_OPERATIONS)),
        "source_digest": digest(source),
        "promotion_authority": False,
        "merge_authority": False,
        "release_authority": False,
    }
    return AutonomousCycleReceipt(cycle_id=digest(body), **body)


def load_work_items(path: str | Path, kind: str) -> tuple[WorkItem, ...]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for row in rows:
        checks = row.get("statusCheckRollup") or []
        conclusions = {
            str(x.get("conclusion") or "").upper()
            for x in checks if isinstance(x, Mapping)
        }
        statuses = {
            str(x.get("status") or "").upper()
            for x in checks if isinstance(x, Mapping)
        }
        out.append(
            WorkItem(
                kind=kind,
                number=int(row["number"]),
                title=str(row["title"]),
                state=str(row.get("state", "OPEN")),
                draft=bool(row.get("isDraft", row.get("draft", False))),
                merge_state=row.get("mergeStateStatus", row.get("merge_state")),
                updated_at=row.get("updatedAt", row.get("updated_at")),
                has_comments=bool(row.get("comments")),
                has_labels=bool(row.get("labels")),
                ci_failed=any(
                    x in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}
                    for x in conclusions
                ),
                ci_pending=any(
                    x in {"QUEUED", "IN_PROGRESS", "PENDING"} for x in statuses
                ),
            )
        )
    return tuple(out)
