#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"scripts/audit_causal_distinctions.py"
SPEC=importlib.util.spec_from_file_location("causal_shared",BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load shared causal auditor")
shared=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)

MATRIX=ROOT/"provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json"
COVERAGE=ROOT/"docs/TEST_COVERAGE_MATRIX.md"
SCOPE=ROOT/"kernel/development/MINERVA_CAUSAL_AUDIT_SCOPE.json"

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
    errors=[]
    data=json.loads(MATRIX.read_text(encoding="utf-8"))
    scope=json.loads(SCOPE.read_text(encoding="utf-8"))
    foreign=scope["foreign_source_paths"]

    if data.get("schema")!="Venus.HistoricalDistinctionTestMatrix.v1":
        errors.append("historical distinction matrix has wrong schema")
    rows=data.get("rows",[])
    if not rows:
        errors.append("historical distinction matrix has no rows")

    seen=set()
    distinctions=[]
    local_sources=0
    foreign_sources=0
    for i,row in enumerate(rows,1):
        missing=sorted(shared.REQUIRED_FIELDS-set(row))
        if missing:
            errors.append(f"row {i}: missing fields {missing}")
            continue
        rid=row["id"]
        if rid in seen:
            errors.append(f"duplicate distinction id: {rid}")
        seen.add(rid)
        distinctions.append(row["distinction"])
        if row["status"] not in shared.ALLOWED_STATUS:
            errors.append(f"{rid}: invalid status {row['status']}")
        if not row["later_dependents"]:
            errors.append(f"{rid}: later_dependents must be explicit")
        for rel in shared.source_paths(row["source_artifact"]):
            if rel.startswith(("issue ","issues/","review +","historical ","Canonical","R191_")):
                continue
            custody, resolved = classify_source_ref(rel, foreign)
            if custody == "foreign":
                foreign_sources += 1
            elif (ROOT/resolved).exists():
                local_sources += 1
            else:
                errors.append(f"{rid}: unscoped missing source artifact: {rel}")

        test_path=row.get("test_id_path")
        if row["status"]=="COVERED" and not test_path:
            errors.append(f"{rid}: COVERED requires test_id_path")
        if test_path and "::" not in test_path and ";" not in test_path and not test_path.startswith(("issue ","scripts/")):
            if not (ROOT/test_path).exists():
                errors.append(f"{rid}: mapped test/audit missing: {test_path}")

    normalized="\n".join(distinctions).lower()
    for concept in shared.REQUIRED_CONCEPTS:
        if concept.lower() not in normalized:
            errors.append(f"matrix missing required causal concept: {concept}")
    if len(rows)<30:
        errors.append(f"historical archaeology unexpectedly shrank to {len(rows)} rows; expected >=30")

    if not COVERAGE.exists():
        errors.append("missing docs/TEST_COVERAGE_MATRIX.md")
    else:
        text=COVERAGE.read_text(encoding="utf-8",errors="replace")
        numbers={int(n) for n in re.findall(r"#(\d+)",text)}
        for n in range(4,38):
            if n not in numbers:
                errors.append(f"TEST_COVERAGE_MATRIX.md missing issue #{n}")

    if errors:
        print("MINERVA CAUSAL DISTINCTION / COVERAGE AUDIT FAIL")
        for error in errors:
            print("- "+error)
        return 1
    print(
        "MINERVA CAUSAL DISTINCTION / COVERAGE AUDIT PASS "
        f"({len(rows)} whole-repo distinctions structurally checked; "
        f"{local_sources} local source references checked; "
        f"{foreign_sources} foreign source references jurisdiction-mapped, not locally passed)"
    )
    return 0

if __name__=="__main__":
    raise SystemExit(main())
