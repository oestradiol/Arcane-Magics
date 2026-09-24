from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "kernel/development/AUTONOMY_SAFETY_DISTINCTION_MATRIX.json"

REQUIRED = {
    "INTERNAL_OSTAR_CAUSAL",
    "TEACHER_SOURCE_REMOVAL",
    "WORLD_NOT_MODEL_WORLD",
    "OTHER_NOT_MODEL_OTHER",
    "EXECUTION_RECEIPT_NOT_RETURN",
    "REVISION_NOT_AUTHORIZATION",
    "REVISION_NOT_VALIDATION",
    "LEARNING_NOT_PROMOTION",
    "MERGE_NOT_LEARNING_REWARD",
    "EXTERNAL_REVIEW_RETURN_REQUIRED",
    "TARGET_LEARNING_CAUSAL",
    "METHOD_LEARNING_CAUSAL",
    "ROADMAP_NOT_SOVEREIGN",
    "STOP_WITHHOLD_REACHABLE",
    "ANTI_MINERVA_CARRIER_PERMEABILITY",
    "AUTHORED_CENTER_NOT_FIELD",
    "CAPABILITY_NOT_JURISDICTION",
    "ROLLBACK_CUSTODY_REQUIRED",
    "PROVENANCE_REQUIRED",
    "SAFETY_FLOOR_NON_INTERNALIZABLE",
    "ADAPTIVE_EVALUATION_CAUSAL_ABLATION",
    "AUTONOMOUS_NO_SELF_MERGE",
    "AUTONOMOUS_DRAFT_ONLY",
    "AUTONOMOUS_NO_REROLL_PENDING_RETURN",
    "TARGET_REOPEN_REQUIRES_CHANGED_WORLD_RETURN",
    "REOPENING_MEMORY_NOT_LEARNING_REWARD",
    "SOURCE_GROUNDED_STUDY",
    "PREFROZEN_HIDDEN_BENCHMARK_BOUNDARY",
}


def main() -> int:
    obj=json.loads(MATRIX.read_text(encoding="utf-8"))
    rows=obj.get("distinctions") or []
    ids=[str(row.get("id")) for row in rows]
    failures=[]
    if len(ids) != len(set(ids)):
        failures.append("duplicate distinction id")
    missing=sorted(REQUIRED-set(ids))
    if missing:
        failures.append("missing required distinctions: "+", ".join(missing))
    for row in rows:
        if not row.get("invariant"):
            failures.append(f"{row.get('id')}: invariant missing")
        tests=row.get("tests") or []
        if not tests:
            failures.append(f"{row.get('id')}: executable witness missing")
        for rel in tests:
            path=ROOT/rel
            if not path.is_file():
                failures.append(f"{row.get('id')}: witness path missing: {rel}")
    if obj.get("promotion_authority") is not False:
        failures.append("matrix may not grant promotion authority")
    out={"status":"PASS" if not failures else "FAIL","distinctions":len(rows),"failures":failures}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
