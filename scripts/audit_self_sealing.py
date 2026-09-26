#!/usr/bin/env python3
"""Structural detector for self-sealing interpretation.

A mind anti-virus is not the correct counter-belief; that would be another
candidate infection wearing a lab coat. It is the preservation of
discrimination, provenance, reopenability, and independent return.

This auditor therefore never judges whether a change is correct. It judges
whether the change left the correction channel reachable:

  R1  an episode must not MODIFY a checker and an artifact that checker guards
  R2  an episode must not DELETE a declared fence token from a governance surface
  R3  an episode must not MODIFY a prefrozen artifact

An "episode" is a contiguous run of commits by one author with no gap longer
than episode_gap_seconds. That is the unit in which a working session can
quietly move a goalpost, and it is the granularity at which the 2026-09-26
contamination was actually detectable: a 28-minute gap separated the branch's
own work from the external agent's.

R1 fires on modification, not introduction. Adding a checker together with its
own scope declaration is bootstrap, not self-sealing: there is no prior
judgment for the new rule to retroactively alter. Editing both later is.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "kernel/development/SELF_SEALING_AUDIT_SCOPE.json"


def git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if cp.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp.stdout


def normalize(text: str) -> str:
    """Fence tokens appear with both ASCII != and typographic forms."""
    return (
        text.replace("≠", "!=")
        .replace("→", "->")
        .replace(" ", " ")
    )


class Commit:
    __slots__ = ("sha", "author", "when", "subject", "changes")

    def __init__(self, sha: str, author: str, when: int, subject: str):
        self.sha = sha
        self.author = author
        self.when = when
        self.subject = subject
        self.changes: dict[str, str] = {}


def load_commits(since: str) -> list[Commit]:
    sep = "\x1e"
    raw = git(
        "log",
        f"--since={since}",
        "--reverse",
        "--no-merges",
        f"--format={sep}%H%x1f%an%x1f%at%x1f%s",
        "--name-status",
    )
    commits: list[Commit] = []
    for block in raw.split(sep):
        block = block.strip("\n")
        if not block:
            continue
        head, _, tail = block.partition("\n")
        sha, author, when, subject = head.split("\x1f", 3)
        commit = Commit(sha, author, int(when), subject)
        for line in tail.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            status, path = parts[0], parts[-1]
            commit.changes[path] = status[0]
        commits.append(commit)
    return commits


def group_episodes(commits: list[Commit], gap: int) -> list[list[Commit]]:
    episodes: list[list[Commit]] = []
    for commit in commits:
        if (
            episodes
            and episodes[-1][-1].author == commit.author
            and commit.when - episodes[-1][-1].when <= gap
        ):
            episodes[-1].append(commit)
        else:
            episodes.append([commit])
    return episodes


def waived(commit: Commit, rule: str, exceptions: list[dict]) -> bool:
    for row in exceptions:
        prefix = row.get("commit_subject_prefix", "")
        if prefix and commit.subject.startswith(prefix):
            if rule in row.get("rules_waived", []):
                return True
    return False


def removed_fence_tokens(sha: str, path: str, tokens: list[str]) -> list[str]:
    try:
        diff = git("show", "-U0", "--format=", sha, "--", path)
    except RuntimeError:
        return []
    hits: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("-") or line.startswith("---"):
            continue
        body = normalize(line[1:])
        for token in tokens:
            if normalize(token) in body and token not in hits:
                hits.append(token)
    return hits


def is_prefrozen(path: str, markers: list[str]) -> bool:
    return any(marker in path for marker in markers)


def is_restoration(path: str, episode_head: str, episode_base: str) -> bool:
    """True if `path` at episode end matches a blob it already held earlier.

    Restoring a checker to a state that predates the episode does not author a
    new rule of judgement, so it cannot retroactively ratify a claim: the
    restored rule is independent of whoever restored it. A novel checker edit
    has no such prior blob and remains subject to R1.
    """
    try:
        current = git("rev-parse", f"{episode_head}:{path}").strip()
    except RuntimeError:
        return False
    try:
        history = git(
            "log", "--format=%H", f"{episode_base}", "--", path
        ).split()
    except RuntimeError:
        return False
    for sha in history:
        try:
            if git("rev-parse", f"{sha}:{path}").strip() == current:
                return True
        except RuntimeError:
            continue
    return False


def main() -> int:
    if not SCOPE_PATH.exists():
        print("WITHHOLD: self-sealing audit scope declaration is absent")
        return 2
    try:
        scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WITHHOLD: scope declaration does not parse: {exc}")
        return 2

    gap = int(scope.get("episode_gap_seconds", 1800))
    since = scope.get("audit_since")
    if not since:
        print("WITHHOLD: scope declares no audit_since window")
        return 2

    exceptions = scope.get("admitted_exceptions", [])
    fence_tokens = scope.get("fence_tokens", [])
    fence_surfaces = set(scope.get("fence_surfaces", []))
    markers = scope.get("prefreeze_markers", [])

    guard_map: dict[str, set[str]] = {}
    for row in scope.get("guarded", []):
        guard_map.setdefault(row["checker"], set()).update(row.get("guards", []))

    try:
        commits = load_commits(since)
    except RuntimeError as exc:
        print(f"WITHHOLD: cannot resolve audit window: {exc}")
        return 2

    declared = {
        row["key"]: row for row in scope.get("declared_residuals", [])
    }
    episodes = group_episodes(commits, gap)
    findings: list[tuple[str, str]] = []

    for episode in episodes:
        touched: dict[str, str] = {}
        for commit in episode:
            for path, status in commit.changes.items():
                # a path added then modified in one episode counts as added
                touched.setdefault(path, status)

        span = f"{episode[0].sha[:8]}..{episode[-1].sha[:8]}"
        author = episode[0].author

        # R1 — checker modified alongside an artifact it guards
        for checker, guards in guard_map.items():
            if touched.get(checker) != "M":
                continue
            overlap = sorted(guards & set(touched))
            if not overlap:
                continue
            if all(waived(c, "R1_SELF_SEALING", exceptions) for c in episode):
                continue
            if is_restoration(checker, episode[-1].sha, f"{episode[0].sha}^"):
                continue
            findings.append((
                f"R1_SELF_SEALING|{checker}|{episode[0].sha[:8]}",
                f"R1_SELF_SEALING [{span}] {author}: checker {checker} was modified "
                f"in the same episode as the artifacts it guards: {', '.join(overlap)}",
            ))

        # R2 — fence token deleted from a governance surface
        for commit in episode:
            if waived(commit, "R2_FENCE_REMOVAL", exceptions):
                continue
            for path in sorted(set(commit.changes) & fence_surfaces):
                lost = removed_fence_tokens(commit.sha, path, fence_tokens)
                if lost:
                    findings.append((
                        f"R2_FENCE_REMOVAL|{path}|{commit.sha[:8]}",
                        f"R2_FENCE_REMOVAL [{commit.sha[:8]}] {commit.author}: "
                        f"{path} lost fence token(s): {'; '.join(lost)}",
                    ))

        # R3 — prefrozen artifact mutated
        for commit in episode:
            if waived(commit, "R3_PREFREEZE_MUTATION", exceptions):
                continue
            for path, status in sorted(commit.changes.items()):
                if status == "M" and is_prefrozen(path, markers):
                    findings.append((
                        f"R3_PREFREEZE_MUTATION|{path}|{commit.sha[:8]}",
                        f"R3_PREFREEZE_MUTATION [{commit.sha[:8]}] {commit.author}: "
                        f"prefrozen artifact modified: {path}",
                    ))

    fresh = [(key, msg) for key, msg in findings if key not in declared]
    carried = [(key, msg) for key, msg in findings if key in declared]
    stale = sorted(set(declared) - {key for key, _ in findings})

    if carried:
        print(f"DECLARED RESIDUALS ({len(carried)}) — unadjudicated, not compressed")
        for key, msg in carried:
            row = declared[key]
            print(f"  {msg}")
            print(f"      reopen: {row.get('reopening_condition', 'UNSPECIFIED')}")
        print()

    if stale:
        # A residual that no longer reproduces has been silently compressed away.
        # Per the residual law, that is exactly the failure this auditor exists
        # to prevent, so it fails closed rather than quietly shrinking the list.
        print(f"STALE DECLARED RESIDUALS ({len(stale)}) — declared but no longer detected")
        for key in stale:
            print(f"  {key}")
        print()
        print("A declared residual that stops reproducing was either resolved or")
        print("compressed away. Remove it from the scope declaration explicitly,")
        print("with the return that closed it. Do not let it lapse silently.")
        return 1

    if fresh:
        print(f"SELF-SEALING AUDIT FINDINGS ({len(fresh)})")
        for _, msg in fresh:
            print(f"  {msg}")
        print()
        print("A finding is not proof the change is wrong. It is proof the change")
        print("altered a rule of judgement without an independent return. Either")
        print("supply that return, or record an admitted exception with reasoning in")
        print("kernel/development/SELF_SEALING_AUDIT_SCOPE.json.")
        return 1

    print(
        f"SELF-SEALING AUDIT PASS "
        f"({len(commits)} commits since {since}; {len(episodes)} episodes; "
        f"{len(guard_map)} guarded checkers; {len(fence_tokens)} fence tokens; "
        f"{len(carried)} declared residuals carried)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
