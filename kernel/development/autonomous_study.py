from __future__ import annotations

"""Repository-local study packet construction for autonomous cycles.

The study phase consumes externally returned target text plus the checked-out
repository. It identifies related live files by lexical overlap and freezes a
bounded evidence packet. It does not claim to solve the target or promote state.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Iterable

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


@dataclass(frozen=True)
class StudyPacket:
    schema: str
    study_id: str
    target_kind: str
    target_number: int
    target_title: str
    target_digest: str
    search_terms: tuple[str, ...]
    related_paths: tuple[str, ...]
    changed_files: tuple[str, ...]
    residual_markers: tuple[str, ...]
    next_operations: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    promotion_authority: bool = False


def _terms(text: str) -> tuple[str, ...]:
    words = {
        w.lower()
        for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text)
        if w.lower() not in STOP
    }
    return tuple(sorted(words))[:32]


def _related(root: Path, terms: tuple[str, ...], limit: int = 20) -> tuple[str, ...]:
    scored: list[tuple[int, str]] = []
    roots = ("kernel", "tests", "docs", "evaluation", "benchmarks", "provenance")
    for name in roots:
        base = root / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py",".json",".md",".tex"}:
                continue
            rel = path.relative_to(root).as_posix()
            score = sum(3 for term in terms if term in rel.lower())
            if score == 0:
                try:
                    sample = path.read_text(encoding="utf-8", errors="ignore")[:30000].lower()
                except OSError:
                    continue
                score = sum(1 for term in terms if term in sample)
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
    next_ops = ["READ_REPOSITORY", "RUN_TESTS"]
    if target.kind.upper() == "PR" and target.changed_files:
        next_ops.append("STUDY_PATCH")
    else:
        next_ops.append("STUDY_TARGET")
    next_ops.append("PROPOSE_PATCH_OR_WITHHOLD")

    stop = (
        "STOP if only missing discriminator is externally authored/evaluated",
        "WITHHOLD if repository evidence does not distinguish live rivals",
        "do not alter frozen hidden-evaluation objects after exposure",
        "do not treat local execution receipt as independent return",
    )
    body = {
        "schema": "Venus.AutonomousStudyPacket.v0.1",
        "target_kind": target.kind,
        "target_number": target.number,
        "target_title": target.title,
        "target_digest": digest({
            "kind": target.kind,
            "number": target.number,
            "title": target.title,
            "body": target.body,
            "changed_files": target.changed_files,
        }),
        "search_terms": terms,
        "related_paths": related,
        "changed_files": target.changed_files,
        "residual_markers": markers,
        "next_operations": tuple(next_ops),
        "stop_conditions": stop,
        "promotion_authority": False,
    }
    return StudyPacket(study_id=digest(body), **body)
