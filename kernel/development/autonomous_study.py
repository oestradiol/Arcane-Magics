from __future__ import annotations

"""Repository-local study packet construction for autonomous cycles.

The study phase consumes externally returned target text plus the checked-out
repository. It identifies related live files by lexical overlap and freezes a
bounded evidence packet. It does not claim to solve the target or promote state.
"""

from dataclasses import dataclass, asdict
import hashlib
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
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


@dataclass(frozen=True)
class ReproductionReceipt:
    schema: str
    cycle_id: str
    target_kind: str
    target_number: int
    target_digest: str
    selected_test: str | None
    selection_terms: tuple[str, ...]
    selection_score: int
    command: tuple[str, ...]
    expected_exit_code: int | None
    observed_exit_code: int | None
    timed_out: bool
    stdout_sha256: str | None
    stderr_sha256: str | None
    stdout_tail: str
    stderr_tail: str
    python_version: str
    platform: str
    status: str
    execution_receipt: bool = True
    independent_return: bool = False
    evaluation_authority: bool = False
    promotion_authority: bool = False


def _bounded_text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _reproduction_candidates(root: Path, terms: tuple[str, ...]) -> tuple[tuple[int, str], ...]:
    tests = root / "tests"
    if not tests.is_dir():
        return ()
    scored: list[tuple[int, str]] = []
    for path in sorted(tests.glob("test_*.py")):
        rel = path.relative_to(root).as_posix()
        path_lower = rel.lower()
        try:
            sample = path.read_text(encoding="utf-8", errors="ignore")[:40000].lower()
        except OSError:
            continue
        path_hits = sum(1 for term in terms if term in path_lower)
        content_hits = sum(1 for term in terms if term in sample)
        score = 4 * path_hits + content_hits
        if score:
            scored.append((score, rel))
    return tuple(sorted(scored, key=lambda row: (-row[0], row[1])))


def run_bounded_reproduction(
    root: Path,
    *,
    cycle_id: str,
    target: StudyTarget,
    timeout_seconds: int = 45,
) -> ReproductionReceipt:
    """Execute one repository-local admitted unittest selected from target context.

    The target text can influence lexical selection only. It can never provide
    a command, argument, environment variable, path outside tests/test_*.py, or
    authority. This receipt is local execution evidence, never independent
    World/evaluator return.
    """
    root = root.resolve()
    terms = _terms(target.title + "\n" + target.body)
    candidates = _reproduction_candidates(root, terms)
    target_digest = digest({
        "kind": target.kind,
        "number": target.number,
        "title": target.title,
        "body": target.body,
        "changed_files": target.changed_files,
    })
    if not candidates:
        return ReproductionReceipt(
            schema="Venus.AutonomousReproductionReceipt.v0.1",
            cycle_id=cycle_id,
            target_kind=target.kind,
            target_number=target.number,
            target_digest=target_digest,
            selected_test=None,
            selection_terms=terms,
            selection_score=0,
            command=(),
            expected_exit_code=None,
            observed_exit_code=None,
            timed_out=False,
            stdout_sha256=None,
            stderr_sha256=None,
            stdout_tail="",
            stderr_tail="",
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            status="WITHHOLD_NO_REPLAYABLE_TEST",
        )

    score, rel = candidates[0]
    if not re.fullmatch(r"tests/test_[A-Za-z0-9_]+\.py", rel):
        raise ValueError(f"unsafe reproduction candidate: {rel}")
    module = rel[:-3].replace("/", ".")
    command = (sys.executable, "-m", "unittest", module)

    env = dict(os.environ)
    sensitive = ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY")
    for key in tuple(env):
        if any(marker in key.upper() for marker in sensitive):
            env.pop(key, None)

    try:
        proc = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            env=env,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        status = (
            "PASS_REPRODUCED_CURRENT_MAIN"
            if proc.returncode == 0
            else "FAIL_REPRODUCTION_MISMATCH"
        )
        return ReproductionReceipt(
            schema="Venus.AutonomousReproductionReceipt.v0.1",
            cycle_id=cycle_id,
            target_kind=target.kind,
            target_number=target.number,
            target_digest=target_digest,
            selected_test=rel,
            selection_terms=terms,
            selection_score=score,
            command=command,
            expected_exit_code=0,
            observed_exit_code=proc.returncode,
            timed_out=False,
            stdout_sha256=_bounded_text_digest(stdout),
            stderr_sha256=_bounded_text_digest(stderr),
            stdout_tail=stdout[-2000:],
            stderr_tail=stderr[-2000:],
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            status=status,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return ReproductionReceipt(
            schema="Venus.AutonomousReproductionReceipt.v0.1",
            cycle_id=cycle_id,
            target_kind=target.kind,
            target_number=target.number,
            target_digest=target_digest,
            selected_test=rel,
            selection_terms=terms,
            selection_score=score,
            command=command,
            expected_exit_code=0,
            observed_exit_code=None,
            timed_out=True,
            stdout_sha256=_bounded_text_digest(stdout),
            stderr_sha256=_bounded_text_digest(stderr),
            stdout_tail=stdout[-2000:],
            stderr_tail=stderr[-2000:],
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            status="WITHHOLD_REPRODUCTION_TIMEOUT",
        )
