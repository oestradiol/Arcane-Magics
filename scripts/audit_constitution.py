#!/usr/bin/env python3
"""Enforce kernel/CONSTITUTION.json against the tree.

The 2026-09-26 episode broke rules that were all already written down. None of
them were enforceable. Nine of eleven *_role fields in this repository are
referenced by zero executable files: they describe good practice and decline
nothing. That is why nothing could refuse the contaminating compression.

  K1 DENY_LIST_ENFORCED  every must-remain-outside item is referenced by a live
                         fence or check, or is declared enforcement: NONE
  K2 AUTHORITY_TOTALITY  every tracked path classifies, or fails closed to
                         WITHHOLD; the WITHHOLD count is ratcheted
  K3 NO_PROSE_ONLY_ROLE  a *_role field that claims to govern must name a check
                         referencing it, or be declared descriptive
  K4 LAWS_PRESENT        the permanent noncollapse laws are present, compared
                         with whitespace normalized
  K5 RUNTIME_DISPOSITION every capability-specific runtime module carries a
                         disposition

Comparison is whitespace-normalized throughout. An earlier spaced-form check of
these same laws reported 13 of 15 absent when they were present without spaces
around the operator. A presence check weaker than its name is the defect class
this file exists to prevent.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = ROOT / "kernel/CONSTITUTION.json"

# Enforcement lives in checkers and runtime. Tests VERIFY enforcement; they do
# not constitute it. Scanning tests/ here would mean that merely naming a role
# in a test string counts as governing it -- a check weaker than its name,
# which is the defect class this file exists to prevent. Found by this
# auditor's own negative suite, which mentions three role names and thereby
# made them all look enforced.
CODE_DIRS = ("scripts", "kernel/runtime")
CORPUS_DIRS = ("kernel", "docs", "provenance", "scripts", "tests")
TEXT_EXT = (".json", ".md", ".py", ".yml", ".yaml", ".tex")


def normalize(text: str) -> str:
    text = text.replace("≠", "!=").replace("→", "->")
    return re.sub(r"\s+", "", text).upper()


def read_corpus(dirs: tuple[str, ...], exclude: frozenset[Path] = frozenset()) -> str:
    """Concatenate the tree's text, excluding named files.

    CONSTITUTION.json must be excluded when checking whether its own laws are
    present in the tree, or the check is self-satisfying: the constitution is
    part of the tree, so every law it declares is trivially found in itself.
    Caught by this auditor's negative suite, which appended a nonexistent law
    and watched K4 pass.
    """
    chunks: list[str] = []
    for base in dirs:
        for dirpath, _, filenames in os.walk(ROOT / base):
            if "__pycache__" in dirpath:
                continue
            for name in filenames:
                path = Path(dirpath, name)
                if not name.endswith(TEXT_EXT) or path.resolve() in exclude:
                    continue
                try:
                    chunks.append(path.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue
    return "\n".join(chunks)


def tracked_paths() -> list[str]:
    cp = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip())
    return [p for p in cp.stdout.split() if p]


def role_fields() -> dict[str, list[str]]:
    """Every *_role field carrying a prose string, and where it lives."""
    found: dict[str, list[str]] = {}

    def walk(obj, path: str):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.endswith("_role") and isinstance(value, str):
                    found.setdefault(key, []).append(path)
                else:
                    walk(value, path)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, path)

    for base in ("kernel", "docs"):
        for dirpath, _, filenames in os.walk(ROOT / base):
            if "__pycache__" in dirpath:
                continue
            for name in filenames:
                if not name.endswith(".json"):
                    continue
                p = Path(dirpath, name)
                try:
                    walk(json.loads(p.read_text(encoding="utf-8")), str(p.relative_to(ROOT)))
                except (OSError, json.JSONDecodeError):
                    continue
    return found


def classify(path: str, rules: list[dict]) -> str:
    for rule in rules:
        prefix = rule.get("prefix", "")
        if prefix and path.startswith(prefix):
            return rule["class"]
        exact = rule.get("path", "")
        if exact and path == exact:
            return rule["class"]
    return "WITHHOLD"


def main() -> int:
    if not CONSTITUTION.exists():
        print("WITHHOLD: kernel/CONSTITUTION.json is absent")
        return 2
    try:
        const = json.loads(CONSTITUTION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WITHHOLD: constitution does not parse: {exc}")
        return 2
    if const.get("register") != "LIVE_CONSTITUTION":
        print("WITHHOLD: constitution does not declare register LIVE_CONSTITUTION")
        return 2

    errors: list[str] = []
    notes: list[str] = []

    # Exclude the constitution from its own evidence corpus (see read_corpus).
    corpus = normalize(read_corpus(CORPUS_DIRS, exclude=frozenset({CONSTITUTION.resolve()})))
    code_corpus = read_corpus(CODE_DIRS)

    # ---- K4: the laws are present -------------------------------------------
    block_a = const["block_a_permanent_noncollapse_laws"]
    declared_absent = {row["law"]: row for row in block_a.get("known_absent", [])}
    equivalents = block_a.get("equivalent_forms", {})
    for law in block_a["laws"]:
        forms = [law] + list(equivalents.get(law, []))
        if any(normalize(f) in corpus for f in forms):
            continue
        row = declared_absent.get(law)
        if row is None:
            errors.append(
                f"K4 LAWS_PRESENT: not in tree, no declared equivalent form, and not "
                f"declared absent: {law}"
            )
        elif not str(row.get("reason", "")).strip():
            errors.append(f"K4 LAWS_PRESENT: {law} declared absent without a reason")
        else:
            notes.append(f"law stated in constitution only, absent from tree: {law}")
    # A law declared absent that HAS since appeared must be promoted out of the
    # absent list, or the list would hide real coverage.
    for law, row in declared_absent.items():
        forms = [law] + list(equivalents.get(law, []))
        if any(normalize(f) in corpus for f in forms):
            errors.append(
                f"K4 LAWS_PRESENT: {law} is declared absent but IS present in the tree; "
                f"remove it from known_absent"
            )

    # ---- K1: deny-list is enforced or declared unenforced --------------------
    block_b = const["block_b_deny_list"]
    enforcement = {
        row["item"]: row for row in const.get("deny_list_enforcement", [])
    }
    for item in block_b["must_remain_outside"]:
        row = enforcement.get(item)
        if row is None:
            errors.append(
                f"K1 DENY_LIST_ENFORCED: {item} has no enforcement entry "
                f"(declare a check, or enforcement: NONE with a reason)"
            )
            continue
        mode = row.get("enforcement")
        if mode == "NONE":
            if not str(row.get("reason", "")).strip():
                errors.append(f"K1 DENY_LIST_ENFORCED: {item} declares NONE without a reason")
            else:
                notes.append(f"unenforced by declaration: {item}")
            continue
        ref = row.get("enforced_by", "")
        if not ref:
            errors.append(f"K1 DENY_LIST_ENFORCED: {item} names no enforcing artifact")
        elif not (ROOT / ref).exists():
            errors.append(f"K1 DENY_LIST_ENFORCED: {item} names missing artifact {ref}")

    # ---- K3: no prose-only governing role ------------------------------------
    descriptive = set(const.get("descriptive_roles", []))
    governing = const.get("governing_roles", {})
    unenforced = {
        row["role"]: row for row in const.get("governing_roles_unenforced", [])
    }
    for field, files in sorted(role_fields().items()):
        if field in code_corpus:
            continue
        if field in descriptive:
            notes.append(f"descriptive, not governing: {field}")
            continue
        claim = governing.get(field)
        if claim:
            if not (ROOT / claim).exists():
                errors.append(f"K3 NO_PROSE_ONLY_ROLE: {field} names missing check {claim}")
            elif field not in (ROOT / claim).read_text(encoding="utf-8", errors="replace"):
                errors.append(
                    f"K3 NO_PROSE_ONLY_ROLE: {field} names {claim} but that file "
                    f"does not reference it"
                )
            continue
        row = unenforced.get(field)
        if row is not None:
            if not str(row.get("reopening_condition", "")).strip():
                errors.append(
                    f"K3 NO_PROSE_ONLY_ROLE: {field} declared unenforced without a "
                    f"reopening condition"
                )
            else:
                notes.append(f"GOVERNS BUT UNENFORCED: {field} — {row.get('claims','')}")
            continue
        errors.append(
            f"K3 NO_PROSE_ONLY_ROLE: {field} ({', '.join(files[:2])}) is referenced by no "
            f"executable file and is neither declared descriptive, bound to a check, nor "
            f"declared governing-but-unenforced with a reopening condition"
        )

    # A role declared unenforced that has since been wired up must be promoted,
    # not left in the unenforced list where it would hide a real check.
    for field in sorted(unenforced):
        if field in code_corpus:
            errors.append(
                f"K3 NO_PROSE_ONLY_ROLE: {field} is declared unenforced but IS now "
                f"referenced by code; move it to governing_roles"
            )

    # ---- K2: authority totality, ratcheted ------------------------------------
    block_c = const["block_c_authority_graph"]
    rules = block_c.get("routing", [])
    try:
        paths = tracked_paths()
    except RuntimeError as exc:
        print(f"WITHHOLD: cannot list tracked files: {exc}")
        return 2
    withheld = [p for p in paths if classify(p, rules) == "WITHHOLD"]
    baseline = block_c.get("withhold_baseline")
    if baseline is None:
        errors.append("K2 AUTHORITY_TOTALITY: no withhold_baseline declared")
    elif len(withheld) > baseline:
        errors.append(
            f"K2 AUTHORITY_TOTALITY: {len(withheld)} unclassified paths exceeds "
            f"declared baseline {baseline}. Unclassified fails closed to WITHHOLD; "
            f"the count may shrink but never silently grow."
        )
    else:
        notes.append(
            f"{len(withheld)}/{len(paths)} paths unrouted, failing closed to WITHHOLD "
            f"(baseline {baseline})"
        )

    # ---- K5: runtime disposition ---------------------------------------------
    plan_path = ROOT / "kernel/development/VM_INTERNALIZATION_PHASE_PLAN.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        blob = json.dumps(plan)
        exempt = set(const.get("runtime_disposition_exempt", []))
        undisposed = []
        for p in sorted(Path(ROOT, "kernel/runtime").glob("*.py")):
            rel = str(p.relative_to(ROOT))
            if p.name == "__init__.py" or rel in exempt:
                continue
            if rel not in blob:
                undisposed.append(rel)
        if undisposed:
            for rel in undisposed:
                errors.append(
                    f"K5 RUNTIME_DISPOSITION: {rel} has no disposition in "
                    f"VM_INTERNALIZATION_PHASE_PLAN.json"
                )
    else:
        errors.append("K5 RUNTIME_DISPOSITION: phase plan absent")

    if errors:
        print(f"CONSTITUTION AUDIT FINDINGS ({len(errors)})")
        for item in errors:
            print(f"  {item}")
        print()
        print("A rule that names no enforcing check is documentation, not")
        print("constitution. Either bind it to a check, or declare it unenforced")
        print("with a reason so the gap is visible rather than assumed closed.")
        return 1

    for note in notes:
        print(f"  note: {note}")
    print(
        f"CONSTITUTION AUDIT PASS ({len(block_a['laws'])} laws; "
        f"{len(block_b['must_remain_outside'])} deny-list items; "
        f"{len(role_fields())} role fields; {len(paths)} paths)"
    )
    print("Enforcement is not correctness: PASS means the boundary is declared and")
    print("checked, not that any claim inside it is true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
