from __future__ import annotations

"""Bounded state-ownable GitHub work selector for Venus.

The worker consumes externally supplied repository snapshots. It may choose one
bounded target and produce a work receipt. It cannot merge, release, promote
authority, close issues, mint independent return, or access secrets.

GitHub execution remains a carrier action performed by the workflow adapter.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

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


@dataclass(frozen=True)
class AutonomousCycleReceipt:
    schema: str
    cycle_id: str
    target_kind: str | None
    target_number: int | None
    target_title: str | None
    decision: str
    rationale: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    source_digest: str
    promotion_authority: bool = False


def roadmap_issue_order(text: str) -> tuple[int, ...]:
    out: list[int] = []
    for match in re.finditer(r"#(\d+)", text):
        number = int(match.group(1))
        if number not in out:
            out.append(number)
    return tuple(out)


def _rank(item: WorkItem, issue_order: tuple[int, ...]) -> tuple[int, int, int]:
    if item.kind == "PR" and item.merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"}:
        return (0, 0, item.number)
    if item.kind == "ISSUE" and item.number in issue_order:
        return (1, issue_order.index(item.number), item.number)
    if item.kind == "PR":
        return (2, 0 if item.draft else 1, item.number)
    return (3, 0, item.number)


def choose_target(
    items: Iterable[WorkItem],
    *,
    roadmap_text: str,
    recent_targets: Iterable[tuple[str, int]] = (),
) -> WorkItem | None:
    recent = set(recent_targets)
    open_items = tuple(
        item for item in items
        if item.state.upper() == "OPEN" and (item.kind, item.number) not in recent
    )
    if not open_items:
        return None
    order = roadmap_issue_order(roadmap_text)
    return sorted(open_items, key=lambda item: _rank(item, order))[0]


def make_cycle(
    *,
    issues: Iterable[WorkItem],
    prs: Iterable[WorkItem],
    roadmap_text: str,
    internal_policy: Mapping[str, Any],
    recent_targets: Iterable[tuple[str, int]] = (),
) -> AutonomousCycleReceipt:
    items = tuple(issues) + tuple(prs)
    target = choose_target(items, roadmap_text=roadmap_text, recent_targets=recent_targets)
    source = {
        "items": [asdict(item) for item in items],
        "roadmap_digest": digest(roadmap_text),
        "recent_targets": tuple(recent_targets),
    }

    if target is None:
        decision = "STOP"
        rationale = ("no unconsumed OPEN work item is justified",)
    else:
        # Opaque learner-side coordinates. External access, correction
        # reachability and revision reachability are supplied by the adapter;
        # authorization remains local to the declared GitHub write scope.
        features = {
            "f0": True,
            "f1": target.merge_state not in {"BLOCKED", "CONFLICTING"},
            "f2": True,
            "f3": True,
            "f4": False,
            "f5": True,
            "f6": False,
            "f7": False,
        }
        decision = execute_tree(internal_policy, features)
        if decision == "ACT":
            # An unresolved target is never treated as already evidenced.
            decision = "PROBE"
        rationale = (
            "one bounded target selected from current external GitHub snapshot",
            "internalized learner-side policy is upstream of work disposition",
            "draft proposal only; admission remains external",
        )

    body = {
        "schema": "Venus.AutonomousCycleReceipt.v0.1",
        "target_kind": target.kind if target else None,
        "target_number": target.number if target else None,
        "target_title": target.title if target else None,
        "decision": decision,
        "rationale": rationale,
        "allowed_operations": ALLOWED_OPERATIONS,
        "forbidden_operations": tuple(sorted(FORBIDDEN_OPERATIONS)),
        "source_digest": digest(source),
        "promotion_authority": False,
    }
    return AutonomousCycleReceipt(cycle_id=digest(body), **body)


def load_work_items(path: str | Path, kind: str) -> tuple[WorkItem, ...]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for row in rows:
        out.append(
            WorkItem(
                kind=kind,
                number=int(row["number"]),
                title=str(row["title"]),
                state=str(row.get("state", "OPEN")),
                draft=bool(row.get("isDraft", row.get("draft", False))),
                merge_state=row.get("mergeStateStatus", row.get("merge_state")),
                updated_at=row.get("updatedAt", row.get("updated_at")),
            )
        )
    return tuple(out)
