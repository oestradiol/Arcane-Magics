from __future__ import annotations

"""Bounded state-ownable GitHub work selector for Venus.

Target choice is driven by learner state plus content-addressed tie-breaking,
not by host-authored roadmap priority. The roadmap remains readable context only.

The worker may study one target and freeze a draft work receipt. It cannot merge,
release, promote authority, close issues, mint independent return, or access
secrets. GitHub execution remains a carrier action performed by the workflow.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

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
    "PROPOSE_STATE_PATCH",
    "OPEN_DRAFT_PR",
    "COMMENT_WITH_RECEIPT",
)

FEATURE_NAMES = tuple(f"x{i}" for i in range(8))


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
    related_paths: tuple[str, ...]
    study_protocol: tuple[str, ...]
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
            t = datetime.fromisoformat(item.updated_at.replace("Z", "+00:00"))
            recent = (now - t).total_seconds() <= 7 * 24 * 3600
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
    return sum(float(weights.get(k, 0.0)) for k, value in features.items() if value)


def choose_target(
    items: Iterable[WorkItem],
    *,
    learner_state_id: str,
    feature_weights: Mapping[str, float],
    active_autonomous_cycle: bool = False,
) -> WorkItem | None:
    """Choose one open target, or STOP while a prior cycle awaits return."""
    if active_autonomous_cycle:
        return None

    rows = tuple(
        item for item in items
        if item.state.upper() == "OPEN"
        and not (
            item.kind.upper() == "PR"
            and item.title.lower().startswith("venus: autonomous cycle")
        )
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


def _related_paths(repo_root: Path, title: str, limit: int = 12) -> tuple[str, ...]:
    import re

    stop = {
        "the", "and", "for", "with", "from", "into", "that", "this",
        "test", "build", "venus", "add", "let",
    }
    terms = tuple(sorted({
        x.lower() for x in re.findall(r"[A-Za-z0-9_]+", title)
        if len(x) >= 4 and x.lower() not in stop
    }))
    if not terms:
        return ()

    scored: list[tuple[int, str]] = []
    for root_name in ("kernel", "docs", "tests", "evaluation", "benchmarks", "provenance"):
        base = repo_root / root_name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".json", ".tex"}:
                continue
            rel = path.relative_to(repo_root).as_posix()
            name = rel.lower()
            score = 3 * sum(term in name for term in terms)
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")[:20000].lower()
            except OSError:
                continue
            score += sum(term in content for term in terms)
            if score:
                scored.append((-score, rel))
    return tuple(path for _, path in sorted(scored)[:limit])


def make_cycle(
    *,
    issues: Iterable[WorkItem],
    prs: Iterable[WorkItem],
    internal_policy: Mapping[str, Any],
    learner_state_id: str,
    feature_weights: Mapping[str, float],
    active_autonomous_cycle: bool,
    repo_root: str | Path,
    roadmap_text: str = "",
) -> AutonomousCycleReceipt:
    items = tuple(issues) + tuple(prs)
    target = choose_target(
        items,
        learner_state_id=learner_state_id,
        feature_weights=feature_weights,
        active_autonomous_cycle=active_autonomous_cycle,
    )
    source = {
        "items": [asdict(item) for item in items],
        "roadmap_digest": digest(roadmap_text),
        "learner_state_id": learner_state_id,
        "feature_weights": dict(feature_weights),
        "active_autonomous_cycle": active_autonomous_cycle,
    }

    if target is None:
        decision = "STOP"
        rationale = (
            "no admissible OPEN target or a prior autonomous cycle still awaits external return",
        )
        features: Mapping[str, bool] = {}
        related: tuple[str, ...] = ()
    else:
        # Opaque internal-O* coordinates are supplied by the external adapter.
        # Initial snapshot is enough to study, never enough to self-certify.
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
            "one bounded target selected from current external GitHub snapshot",
            "selection used state-owned returned-outcome preference, not roadmap priority",
            "internalized learner-side O* policy is upstream of work disposition",
            "roadmap is study context only and carries no target-selection authority",
            "draft proposal only; admission remains external",
        )
        features = item_features(target)
        related = _related_paths(Path(repo_root), target.title)

    study_protocol = (
        "reconstruct current repository disposition from live authority and related paths",
        "locate existing tests, preserved failures, and current claim fence",
        "identify the smallest unresolved causal discriminator",
        "state which fresh external return would separate the live rivals",
        "prefer WITHHOLD or STOP over claim inflation when the discriminator is not executable",
    )

    body = {
        "schema": "Venus.AutonomousCycleReceipt.v0.2",
        "target_kind": target.kind if target else None,
        "target_number": target.number if target else None,
        "target_title": target.title if target else None,
        "decision": decision,
        "rationale": rationale,
        "feature_snapshot": dict(features),
        "related_paths": related,
        "study_protocol": study_protocol,
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
                ci_failed=any(x in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"} for x in conclusions),
                ci_pending=any(x in {"QUEUED", "IN_PROGRESS", "PENDING"} for x in statuses),
            )
        )
    return tuple(out)
