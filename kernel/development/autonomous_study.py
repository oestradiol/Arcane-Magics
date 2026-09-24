from __future__ import annotations

"""Repository-local + returned-state study packets for autonomous cycles.

The study phase consumes externally returned target state plus the checked-out
repository. It identifies related live files, preserves CI/review/merge pressure,
and freezes a bounded evidence packet before any autonomous Git write.

It does not solve the target, merge anything, or promote state.
"""

from dataclasses import dataclass
from pathlib import Path
import re

from kernel.runtime.vmk2 import digest


STOP = frozenset({
    "about","after","before","build","from","into","that","this","with","without",
    "issue","pull","request","test","tests","venus","current","state","open",
})


@dataclass(frozen=True)
class StudyTarget:
    kind: str
    number: int
    title: str
    body: str
    changed_files: tuple[str, ...] = ()
    failed_checks: tuple[str, ...] = ()
    pending_checks: tuple[str, ...] = ()
    review_states: tuple[str, ...] = ()
    comment_count: int = 0
    label_count: int = 0
    merge_state: str | None = None


@dataclass(frozen=True)
class StudyPacket:
    schema: str
    study_id: str
    target_kind: str
    target_number: int
    target_title: str
    target_digest: str
    disposition: str
    search_terms: tuple[str, ...]
    related_paths: tuple[str, ...]
    changed_files: tuple[str, ...]
    failed_checks: tuple[str, ...]
    pending_checks: tuple[str, ...]
    review_states: tuple[str, ...]
    residual_markers: tuple[str, ...]
    observations: tuple[str, ...]
    next_operations: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    promotion_authority: bool = False
    merge_authority: bool = False
    release_authority: bool = False


def _terms(text: str) -> tuple[str, ...]:
    words = {
        w.lower()
        for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text)
        if w.lower() not in STOP
    }
    return tuple(sorted(words))[:32]


def _related(root: Path, terms: tuple[str, ...], limit: int = 20) -> tuple[str, ...]:
    scored: list[tuple[int, str]] = []
    for name in ("kernel", "tests", "docs", "evaluation", "benchmarks", "provenance"):
        base = root / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py",".json",".md",".tex"}:
                continue
            rel = path.relative_to(root).as_posix()
            score = sum(3 for term in terms if term in rel.lower())
            try:
                sample = path.read_text(encoding="utf-8", errors="ignore")[:30000].lower()
            except OSError:
                continue
            score += sum(1 for term in terms if term in sample)
            if score:
                scored.append((-score, rel))
    return tuple(path for _, path in sorted(scored)[:limit])


def make_study_packet(root: Path, target: StudyTarget) -> StudyPacket:
    terms = _terms(target.title + "\n" + target.body)
    related = _related(root, terms)
    lower = target.body.lower()
    markers = tuple(
        marker for marker in (
            "remaining", "missing", "pending", "blocked", "withhold",
            "external return", "independent evaluator", "hidden", "rollback",
            "reopen", "unresolved",
        )
        if marker in lower
    )

    observations: list[str] = []
    next_ops = ["READ_REPOSITORY", "RUN_TESTS"]
    merge_state = (target.merge_state or "").upper()

    if target.kind.upper() == "PR":
        if target.changed_files:
            observations.append(f"{len(target.changed_files)} changed files returned by GitHub")
            next_ops.append("STUDY_PATCH")
        if target.failed_checks:
            observations.append("external CI contains returned failures")
            next_ops.append("LOCALIZE_RETURNED_FAILURE")
        if target.pending_checks:
            observations.append("external evaluation is still pending")
        if "CHANGES_REQUESTED" in {x.upper() for x in target.review_states}:
            observations.append("external review requested changes")
            next_ops.append("BIND_REVIEW_TO_DEPENDENCY")
        if merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"}:
            observations.append("PR has unresolved structural merge pressure")
            next_ops.append("REOPEN_STRUCTURAL_CONFLICT")
    else:
        observations.append(
            f"issue snapshot contains {target.comment_count} comments and {target.label_count} labels"
        )
        next_ops.append("STUDY_TARGET")

    if target.failed_checks:
        disposition = "REPAIR_RETURNED_FAILURE"
    elif target.pending_checks:
        disposition = "WAIT_EXTERNAL_RETURN"
    elif merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"}:
        disposition = "REOPEN_STRUCTURAL_CONFLICT"
    else:
        disposition = "PROBE"

    next_ops.append("PROPOSE_PATCH_OR_WITHHOLD")

    stop = (
        "STOP if only missing discriminator is externally authored/evaluated",
        "WITHHOLD if repository evidence does not distinguish live rivals",
        "WAIT if a required external evaluation is still pending",
        "do not alter frozen hidden-evaluation objects after exposure",
        "do not treat local execution receipt as independent return",
        "do not convert local study into merge/promotion/release authority",
    )

    payload = {
        "kind": target.kind,
        "number": target.number,
        "title": target.title,
        "body": target.body,
        "changed_files": target.changed_files,
        "failed_checks": target.failed_checks,
        "pending_checks": target.pending_checks,
        "review_states": target.review_states,
        "comment_count": target.comment_count,
        "label_count": target.label_count,
        "merge_state": target.merge_state,
    }
    body = {
        "schema": "Venus.AutonomousStudyPacket.v0.2",
        "target_kind": target.kind,
        "target_number": target.number,
        "target_title": target.title,
        "target_digest": digest(payload),
        "disposition": disposition,
        "search_terms": terms,
        "related_paths": related,
        "changed_files": target.changed_files,
        "failed_checks": target.failed_checks,
        "pending_checks": target.pending_checks,
        "review_states": target.review_states,
        "residual_markers": markers,
        "observations": tuple(observations),
        "next_operations": tuple(dict.fromkeys(next_ops)),
        "stop_conditions": stop,
        "promotion_authority": False,
        "merge_authority": False,
        "release_authority": False,
    }
    return StudyPacket(study_id=digest(body), **body)
