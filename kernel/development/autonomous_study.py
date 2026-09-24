from __future__ import annotations

"""Generic bounded study packet construction for autonomous repository work.

Issue/PR text is untrusted World input. This module never executes instructions
found in titles/bodies/diffs. It extracts references, hashes the source, and
locates potentially relevant repository paths using lexical overlap only.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Iterable, Mapping, Any

from kernel.runtime.vmk2 import digest

PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])((?:kernel|docs|tests|evaluation|benchmarks|provenance|scripts)/[A-Za-z0-9_./-]+)")
ISSUE_RE = re.compile(r"(?<!\w)#(\d+)\b")
INSTRUCTION_RE = re.compile(
    r"(?i)\b(ignore|override|bypass|disable|merge|promote|release|delete|exfiltrate|secret|token|password|system prompt)\b"
)


@dataclass(frozen=True)
class StudySource:
    kind: str
    number: int
    title: str
    body: str
    url: str


@dataclass(frozen=True)
class StudyPacket:
    schema: str
    source_kind: str
    source_number: int
    source_url: str
    source_digest: str
    referenced_numbers: tuple[int, ...]
    referenced_paths: tuple[str, ...]
    related_paths: tuple[str, ...]
    untrusted_instruction_markers: tuple[str, ...]
    body_is_executable_instruction: bool
    study_questions: tuple[str, ...]
    promotion_authority: bool = False


def _tokens(text: str) -> tuple[str, ...]:
    stop = {
        "this","that","with","from","into","then","than","have","will","would",
        "issue","pull","request","venus","test","tests","build","current","state",
        "should","could","their","there","about","after","before","under",
    }
    return tuple(sorted({
        x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", text)
        if x.lower() not in stop
    }))


def _related_paths(root: Path, text: str, limit: int = 16) -> tuple[str, ...]:
    terms = _tokens(text)
    if not terms:
        return ()
    candidates: list[tuple[int, str]] = []
    for top in ("kernel", "docs", "tests", "evaluation", "benchmarks", "provenance", "scripts"):
        base = root / top
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py",".md",".json",".tex",".jsonl"}:
                continue
            rel = path.relative_to(root).as_posix()
            low_name = rel.lower()
            score = 3 * sum(term in low_name for term in terms)
            if score == 0:
                try:
                    sample = path.read_text(encoding="utf-8", errors="ignore")[:20000].lower()
                except OSError:
                    continue
                score += sum(term in sample for term in terms)
            if score:
                candidates.append((-score, rel))
    return tuple(path for _, path in sorted(candidates)[:limit])


def build_study_packet(root: Path, source: StudySource) -> StudyPacket:
    if not source.title.strip() or not source.url.strip():
        raise ValueError("study source requires title and url")
    combined = source.title + "\n" + source.body
    explicit_paths = tuple(sorted(set(PATH_RE.findall(combined))))
    existing_paths = tuple(
        p for p in explicit_paths if (root / p).is_file()
    )
    markers = tuple(sorted(set(m.group(0).lower() for m in INSTRUCTION_RE.finditer(combined))))
    body = {
        "source_kind": source.kind,
        "source_number": source.number,
        "source_url": source.url,
        "source_text_digest": digest({"title": source.title, "body": source.body}),
        "referenced_numbers": tuple(sorted({int(x) for x in ISSUE_RE.findall(combined)})),
        "referenced_paths": existing_paths,
        "related_paths": _related_paths(root, combined),
        "untrusted_instruction_markers": markers,
        "body_is_executable_instruction": False,
        "study_questions": (
            "What exact residual remains open at the current repository authority?",
            "Which referenced dependency is unresolved versus merely historical?",
            "What returned evidence would discriminate the live rivals?",
            "Is the next lawful action local reconstruction, external probe, WITHHOLD, or STOP?",
            "Which existing tests constrain a proposed change, and what negative branch must be retained?",
        ),
        "promotion_authority": False,
    }
    return StudyPacket(schema="Venus.AutonomousStudyPacket.v0.1", **body)


def packet_dict(packet: StudyPacket) -> dict[str, Any]:
    return asdict(packet)
