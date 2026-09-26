#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"scripts/audit_construct_dispositions.py"
SPEC=importlib.util.spec_from_file_location("construct_shared",BASE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load shared construct auditor")
shared=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)

PATH=ROOT/"docs/CONSTRUCT_DISPOSITIONS.json"
SCOPE=ROOT/"kernel/development/MINERVA_CONSTRUCT_AUDIT_SCOPE.json"

def classify_source_ref(rel: str, foreign: dict[str, str]) -> tuple[str, str]:
    # Branch-qualified provenance references are already explicit custody:
    # split/venus:path, split/eclipsis:path, etc.
    if rel.startswith("split/") and ":" in rel:
        branch, inner = rel.split(":", 1)
        if branch == "split/minerva":
            return ("local", inner)
        return ("foreign", rel)
    if rel in foreign:
        return ("foreign", rel)
    return ("local", rel)

def main()->int:
    data=json.loads(PATH.read_text(encoding="utf-8"))
    scope=json.loads(SCOPE.read_text(encoding="utf-8"))
    foreign=scope["foreign_evidence_paths"]
    errors=[]
    seen=set()
    local_count=0
    foreign_count=0

    for row in data.get("dispositions",[]):
        cid=row.get("id")
        if not cid or cid in seen:
            errors.append(f"invalid/duplicate construct id: {cid}")
        seen.add(cid)
        if row.get("status") not in shared.ALLOWED:
            errors.append(f"{cid}: invalid status {row.get('status')}")
        if row.get("genealogy_preserved") is not True:
            errors.append(f"{cid}: genealogy must remain preserved")
        for rel in row.get("evidence",[]):
            if rel.startswith("issues/"):
                continue
            custody, resolved = classify_source_ref(rel, foreign)
            if custody == "foreign":
                foreign_count += 1
            elif (ROOT/resolved).exists():
                local_count += 1
            else:
                errors.append(f"{cid}: unscoped missing evidence path: {rel}")
        if row.get("status") in {"MATURELY_SUBSUMED_AT_T","NO_LONGER_REQUIRED_LIVE"}:
            if not row.get("mature_substitute"):
                errors.append(f"{cid}: subsumed/retired status requires mature_substitute")
            if row.get("independent_residual") not in {"NONE","SUBSUMED"}:
                errors.append(f"{cid}: retired status cannot retain an untyped residual")

    if errors:
        print("MINERVA CONSTRUCT DISPOSITION AUDIT FAIL")
        for e in errors:
            print("- "+e)
        return 1

    print(
        "MINERVA CONSTRUCT DISPOSITION AUDIT PASS "
        f"({len(seen)} constructs; {local_count} local evidence references; "
        f"{foreign_count} foreign references jurisdiction-mapped, not locally passed)"
    )
    return 0

if __name__=="__main__":
    raise SystemExit(main())
