from __future__ import annotations

"""Bounded state-ownable GitHub work selector for Venus.

The worker consumes externally supplied repository snapshots. It may choose one
bounded target, study its returned repository context, and produce a work
receipt. It cannot merge, release, promote authority, close issues, mint
independent return, or access secrets.

GitHub execution remains a carrier action performed by the workflow adapter.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.vmk2 import digest
from kernel.development.autonomous_learning import METHODS, TargetBarrier


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
    "OPEN_CYCLE_ISSUE_CARRIER",
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
    body: str = ""
    changed_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class AutonomousCycleReceipt:
    schema: str
    cycle_id: str
    target_kind: str | None
    target_number: int | None
    target_title: str | None
    decision: str
    rationale: tuple[str, ...]
    study_method: str | None
    developmental_parent_carrier: str | None
    developmental_parent_digest: str | None
    active_improver_revision: str | None
    study: Mapping[str, Any] | None
    allowed_operations: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    source_digest: str
    promotion_authority: bool = False


def roadmap_issue_order(text: str) -> tuple[int, ...]:
    """Advisory provenance/context only; never sovereign target priority."""
    out: list[int] = []
    for match in re.finditer(r"#(\d+)", text):
        number = int(match.group(1))
        if number not in out:
            out.append(number)
    return tuple(out)


def _rank(
    item: WorkItem,
    issue_order: tuple[int, ...],
    kind_utility: Mapping[str, float],
) -> tuple[float, float, float, float, int]:
    # A conflicted/blocked PR is an immediately returned repository residual.
    conflict = 0.0 if item.kind == "PR" and item.merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"} else 1.0

    # Learned external work-return utility precedes host-authored roadmap order.
    utility = -float(kind_utility.get(item.kind, 0.0))

    # Roadmap remains one weak context/tie-break signal, not a controller.
    if item.kind == "ISSUE" and item.number in issue_order:
        roadmap = float(issue_order.index(item.number))
    else:
        roadmap = float(len(issue_order) + 1)

    draft = 0.0 if item.kind == "PR" and item.draft else 1.0
    return (conflict, utility, roadmap, draft, item.number)


def _parse_github_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _blocked_by_barrier(item: WorkItem, barriers: Iterable[TargetBarrier]) -> bool:
    matching = tuple(
        b for b in barriers if b.kind == item.kind and b.number == item.number
    )
    if not matching:
        return False
    if any(b.cycle_state == "OPEN" for b in matching):
        return True
    item_time = _parse_github_time(item.updated_at)
    if item_time is None:
        return True
    resolved = [
        _parse_github_time(b.outcome_at)
        for b in matching if b.outcome_at is not None
    ]
    resolved = [x for x in resolved if x is not None]
    if not resolved:
        return True
    return item_time <= max(resolved)


def choose_target(
    items: Iterable[WorkItem],
    *,
    roadmap_text: str,
    target_barriers: Iterable[TargetBarrier] = (),
    active_cycle: bool = False,
    recent_targets: Iterable[tuple[str, int]] = (),
    kind_utility: Mapping[str, float] | None = None,
) -> WorkItem | None:
    if active_cycle:
        return None
    recent = set(recent_targets)
    barriers = tuple(target_barriers)
    open_items = tuple(
        item for item in items
        if item.state.upper() == "OPEN"
        and (item.kind, item.number) not in recent
        and not _blocked_by_barrier(item, barriers)
        and not item.title.lower().startswith("venus: autonomous cycle")
    )
    if not open_items:
        return None
    order = roadmap_issue_order(roadmap_text)
    utility = kind_utility or {}
    return sorted(open_items, key=lambda item: _rank(item, order, utility))[0]


def _sentences(text: str) -> tuple[str, ...]:
    rows = re.split(r"(?<=[.!?])\s+|\n+", text)
    return tuple(x.strip() for x in rows if x.strip())


def choose_study_method(
    item: WorkItem,
    method_utility: Mapping[str, float] | None = None,
) -> str:
    """Choose a study method from learned external-return utility.

    With no learned preference, tie-breaking is content-addressed from the
    selected target and method identity rather than host-supplied ordering.
    """
    utility = method_utility or {}
    ranked = sorted(
        METHODS,
        key=lambda method: (
            -float(utility.get(method, 0.0)),
            digest({"target": [item.kind, item.number, item.title], "method": method}),
        ),
    )
    return ranked[0]


METHOD_OBLIGATIONS: Mapping[str, tuple[str, ...]] = {
    "DEPENDENCY_TRACE": (
        "Enumerate the target's explicit issue/PR and repository-path dependencies.",
        "Identify the smallest dependency whose changed state would alter the target disposition.",
        "Separate blocking dependencies from merely related context.",
    ),
    "DISCRIMINATOR_DESIGN": (
        "State at least two live rival explanations or dispositions.",
        "Define one prospective observation that separates those rivals.",
        "Identify who may lawfully supply that observation and whether it must remain hidden/prefrozen.",
    ),
    "REPRODUCTION": (
        "Identify the smallest executable or replayable claim in the target.",
        "Specify expected versus observed behavior and the environment needed to reproduce it.",
        "Treat inability to reproduce as returned evidence rather than silent failure.",
    ),
    "COMPARATOR_AUDIT": (
        "Name the strongest ordinary/mature substitute or matched baseline relevant to the target.",
        "Compare the claimed Venus-specific consequence against that substitute at matched scope.",
        "Separate learner-owned causal gain from mechanism novelty, necessity, or superiority.",
    ),
    "RETURN_BOUNDARY_AUDIT": (
        "Identify which facts are local execution receipts versus independent World/evaluator returns.",
        "Locate prefreeze, evaluator-separation, STOP/WITHHOLD, and reopening boundaries.",
        "Reject any path where the learner can mint the return that validates its own change.",
    ),
}

METHOD_SIGNAL_TERMS: Mapping[str, tuple[str, ...]] = {
    "DEPENDENCY_TRACE": ("requires", "depends", "blocked", "dependency", "upstream", "downstream"),
    "DISCRIMINATOR_DESIGN": ("rival", "discriminator", "hidden", "held-out", "separate", "compare"),
    "REPRODUCTION": ("reproduce", "replay", "run", "test", "expected", "observed"),
    "COMPARATOR_AUDIT": ("comparator", "baseline", "substitute", "ablation", "mature", "matched"),
    "RETURN_BOUNDARY_AUDIT": ("return", "receipt", "evaluator", "prefreeze", "withhold", "stop", "reopen"),
}


def _method_signals(body: str, method: str) -> tuple[str, ...]:
    lowered = body.lower()
    return tuple(
        term for term in METHOD_SIGNAL_TERMS[method]
        if term in lowered
    )


def _correction_reachable(item: WorkItem) -> bool:
    if item.kind != "PR":
        return True
    merge_state = (item.merge_state or "UNKNOWN").upper()
    return merge_state not in {"DIRTY", "BLOCKED", "CONFLICTING", "UNKNOWN"}


def _item_references(item: WorkItem) -> tuple[int, ...]:
    return tuple(dict.fromkeys(
        int(x) for x in re.findall(r"(?<!\w)#(\d+)", item.body or "")
        if int(x) != item.number
    ))


def _recursive_reference_closure(
    target: WorkItem,
    items: Iterable[WorkItem],
    *,
    max_depth: int = 2,
) -> tuple[Mapping[str, Any], ...]:
    """Bounded R206-style recursive discovery over returned Git provenance.

    This does not claim byte-equivalence to historical R206. It reinstates the
    retained functional consequence: candidate/dependency discovery may recurse
    through provenance/reference paths rather than stopping at the first hop.
    """
    by_number: dict[int, WorkItem] = {}
    ambiguous: set[int] = set()
    for item in items:
        if item.number in by_number and by_number[item.number].kind != item.kind:
            ambiguous.add(item.number)
        else:
            by_number[item.number] = item

    queue: list[tuple[int, int, int]] = [
        (number, 1, target.number)
        for number in _item_references(target)
    ]
    seen = {target.number}
    out: list[Mapping[str, Any]] = []

    while queue:
        number, depth, via = queue.pop(0)
        if number in seen or number in ambiguous or depth > max_depth:
            continue
        seen.add(number)
        item = by_number.get(number)
        if item is None:
            continue
        out.append({
            "kind": item.kind,
            "number": item.number,
            "title": item.title,
            "depth": depth,
            "via_number": via,
            "updated_at": item.updated_at,
        })
        if depth < max_depth:
            queue.extend(
                (child, depth + 1, item.number)
                for child in _item_references(item)
            )
    return tuple(out)


def _validate_developmental_parent(parent: Mapping[str, Any] | None) -> tuple[str | None, str | None]:
    if parent is None:
        return None, None
    carrier = str(parent.get("carrier_id") or "")
    if carrier != "EDU16-RC1":
        raise ValueError("autonomous developmental parent must be EDU16-RC1")
    required = {
        "curriculum target selection",
        "open-domain problem selection",
        "research-question formation",
        "research-obligation routing",
        "World-feed sampling/query policy",
    }
    owned = {str(x) for x in parent.get("owned", ())}
    missing = sorted(required - owned)
    if missing:
        raise ValueError(
            "EDU16-RC1 parent missing admitted owned capabilities: "
            + ", ".join(missing)
        )
    if parent.get("promotion_authority") is not False:
        raise ValueError("developmental parent may not grant promotion authority")
    return carrier, digest(parent)


def _active_improver_revision(receipt: Mapping[str, Any] | None) -> str | None:
    if receipt is None:
        return None
    improver = receipt.get("active_improver")
    if not isinstance(improver, Mapping):
        return None
    revision = str(improver.get("revision") or "")
    if revision == "R206" and improver.get("open_ended_rsi") is False:
        return revision
    return None


def study_target(
    item: WorkItem,
    *,
    method: str,
    all_items: Iterable[WorkItem] = (),
    recursive_provenance: bool = False,
) -> dict[str, Any]:
    """Extract a bounded, source-grounded study object from the selected target."""
    body = item.body or ""
    references = _item_references(item)
    path_refs = tuple(dict.fromkeys(
        x.rstrip(".,;:!?)]}")
        for x in re.findall(
            r"(?:kernel|tests|docs|evaluation|benchmarks|provenance|scripts)/[A-Za-z0-9_./-]+",
            body,
        )
    ))
    blocker_terms = (
        "remaining", "requires", "required", "blocked", "blocking", "pending",
        "await", "waiting", "external return", "hidden", "withhold", "stop",
        "not yet", "missing", "open",
    )
    blocker_sentences = tuple(
        sentence for sentence in _sentences(body)
        if any(term in sentence.lower() for term in blocker_terms)
    )[:12]
    instruction_markers = tuple(sorted(set(
        x.lower() for x in re.findall(
            r"(?i)\b(ignore|override|bypass|disable|merge|promote|release|delete|exfiltrate|secret|token|password|system prompt)\b",
            body,
        )
    )))

    body_digest = digest(body)
    recursive_refs = (
        _recursive_reference_closure(item, all_items)
        if recursive_provenance else ()
    )
    repository_state = {
        "kind": item.kind,
        "state": item.state,
        "draft": item.draft,
        "merge_state": item.merge_state,
        "updated_at": item.updated_at,
    }
    return {
        "body_digest": body_digest,
        "repository_state": repository_state,
        "returned_changed_paths": tuple(item.changed_paths),
        "referenced_issue_or_pr_numbers": references,
        "recursive_referenced_targets": recursive_refs,
        "recursive_provenance_discovery": bool(recursive_provenance),
        "referenced_repository_paths": path_refs,
        "returned_blocker_sentences": blocker_sentences,
        "untrusted_instruction_markers": instruction_markers,
        "body_is_executable_instruction": False,
        "method": method,
        "method_obligations": METHOD_OBLIGATIONS[method],
        "method_observed_signals": _method_signals(body, method),
        "method_contract_digest": digest({
            "method": method,
            "obligations": METHOD_OBLIGATIONS[method],
            "observed_signals": _method_signals(body, method),
        }),
        "questions": (
            "What exact residual remains unresolved in the returned repository state?",
            "What rival explanations or candidate dispositions remain live?",
            "What fresh returned evidence would discriminate them?",
            "Can a local repository change lawfully produce that discriminator, or must Venus WITHHOLD/STOP for external return?",
            "What is the smallest implicated dependency that could be changed without altering a prefrozen claim object?",
        ),
        "study_authority": "LEARNER_SIDE_RECONSTRUCTION_FROM_EXTERNAL_GITHUB_SNAPSHOT",
        "promotion_authority": False,
    }


def make_cycle(
    *,
    issues: Iterable[WorkItem],
    prs: Iterable[WorkItem],
    roadmap_text: str,
    internal_policy: Mapping[str, Any],
    target_barriers: Iterable[TargetBarrier] = (),
    active_cycle: bool = False,
    recent_targets: Iterable[tuple[str, int]] = (),
    kind_utility: Mapping[str, float] | None = None,
    method_utility: Mapping[str, float] | None = None,
    developmental_parent: Mapping[str, Any] | None = None,
    current_state_receipt: Mapping[str, Any] | None = None,
) -> AutonomousCycleReceipt:
    items = tuple(issues) + tuple(prs)
    parent_carrier, parent_digest = _validate_developmental_parent(
        developmental_parent
    )
    improver_revision = _active_improver_revision(current_state_receipt)
    target = choose_target(
        items,
        roadmap_text=roadmap_text,
        target_barriers=target_barriers,
        active_cycle=active_cycle,
        recent_targets=recent_targets,
        kind_utility=kind_utility,
    )
    source = {
        "items": [asdict(item) for item in items],
        "roadmap_digest": digest(roadmap_text),
        "target_barriers": [asdict(b) for b in target_barriers],
        "active_cycle": active_cycle,
        "recent_targets": tuple(recent_targets),
        "kind_utility": dict(kind_utility or {}),
        "method_utility": dict(method_utility or {}),
        "developmental_parent_carrier": parent_carrier,
        "developmental_parent_digest": parent_digest,
        "active_improver_revision": improver_revision,
    }

    if target is None:
        decision = "STOP"
        rationale = (
            "no unconsumed OPEN work item is justified, an autonomous cycle is already awaiting external return, or retained reopening barriers remain closed",
        )
        study_method = None
        study = None
    else:
        study_method = choose_study_method(target, method_utility)
        study = study_target(
            target,
            method=study_method,
            all_items=items,
            recursive_provenance=(improver_revision == "R206"),
        )
        features = {
            "f0": True,
            "f1": _correction_reachable(target),
            "f2": True,
            "f3": True,
            "f4": False,
            "f5": True,
            "f6": False,
            "f7": False,
        }
        decision = execute_tree(internal_policy, features)
        if decision == "ACT":
            decision = "PROBE"
        rationale = (
            "one bounded target selected from current external GitHub snapshot",
            "autonomous cycle is prospectively bound to the admitted EDU16-RC1 claim-bearing parent when supplied",
            "retained R206 recursive provenance discovery expands bounded dependency study when current custody activates it",
            "internalized learner-side policy is upstream of work disposition",
            "explicit external work-return reviews may alter later target ranking",
            "roadmap is retained as weak context/tie-break provenance, not sovereign curriculum",
            "selected target body is transformed into a bounded source-grounded study object",
            "prior target study remains withheld until newer external target return reopens it",
            "draft proposal only; admission remains external",
        )

    body = {
        "schema": "Venus.AutonomousCycleReceipt.v0.4",
        "target_kind": target.kind if target else None,
        "target_number": target.number if target else None,
        "target_title": target.title if target else None,
        "decision": decision,
        "rationale": rationale,
        "study_method": study_method,
        "developmental_parent_carrier": parent_carrier,
        "developmental_parent_digest": parent_digest,
        "active_improver_revision": improver_revision,
        "study": study,
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
                body=str(row.get("body") or ""),
                changed_paths=tuple(
                    str(file_row.get("path"))
                    for file_row in (row.get("files") or ())
                    if isinstance(file_row, Mapping) and file_row.get("path")
                ),
            )
        )
    return tuple(out)
