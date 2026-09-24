#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from kernel.development.edu17r1_repair_contract import bind_candidate, validate_candidate
from scripts.run_edu17r1_semantic_ingress_search import run

ROOT=Path(__file__).resolve().parents[1]
METHOD=ROOT/"kernel/development/EDU17R1_SEMANTIC_INGRESS_SELECTED_METHOD.json"
FAMILY=ROOT/"kernel/development/EDU17R1_SEMANTIC_INGRESS_METHOD_FAMILY.json"
CANDIDATE=ROOT/"kernel/development/EDU17R1_REPAIR_CANDIDATE_FROZEN.json"
RECEIPT=ROOT/"kernel/development/EDU17R1_REPAIR_OWNERSHIP_RECEIPT.json"
RUNTIME=ROOT/"kernel/runtime/calibrated_retrieval.py"
CONDITION=ROOT/"benchmarks/edu17r1_mention_incidence/condition_b.py"


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    result=run()
    winner=result["winner"]
    selected=json.loads(METHOD.read_text(encoding="utf-8"))
    candidate=json.loads(CANDIDATE.read_text(encoding="utf-8"))
    receipt=json.loads(RECEIPT.read_text(encoding="utf-8"))
    errors=validate_candidate(candidate)
    rebound=bind_candidate(candidate)
    runtime_text=RUNTIME.read_text(encoding="utf-8").casefold()
    forbidden=(
        "mention != incidence",
        "uncertainty-marker",
        "object-level unresolved",
        "unknown means",
        "unresolved means",
    )
    gates={
        "public_only": result["input"]=="PUBLIC_DEV_ONLY",
        "hidden_unexposed": result["hidden_evaluation_exposed"] is False,
        "winner_matches_frozen": winner["method"]["id"]==selected["method"]["id"],
        "winner_accuracy_matches": abs(winner["accuracy"]-selected["public_leave_one_out"]["accuracy"])<1e-12,
        "winner_macro_f1_matches": abs(winner["macro_f1"]-selected["public_leave_one_out"]["macro_f1"])<1e-12,
        "selected_method_sha256": sha256(METHOD)==candidate["implementation_identity"]["sha256"],
        "controller_state_sha256": sha256(FAMILY)==candidate["author_controller_state_sha256"],
        "candidate_contract": not errors,
        "ownership_receipt_exact": rebound==receipt,
        "runtime_target_vocabulary_absent": all(x not in runtime_text for x in forbidden),
        "condition_b_exists": CONDITION.exists(),
        "promotion_authority_false": candidate["promotion_authority"] is False and receipt["promotion_authority"] is False,
    }
    return {
        "schema":"Venus.EDU17R1SemanticIngressFreezeAudit.v0.1",
        "status":"PASS_FROZEN_LEARNER_SIDE_PUBLIC_DEV_CANDIDATE" if all(gates.values()) else "FAIL_EDU17R1_SEMANTIC_INGRESS_FREEZE",
        "gates":gates,
        "winner":winner,
        "candidate_id":candidate["candidate_id"],
        "candidate_sha256":receipt["candidate_sha256"],
        "receipt_sha256":receipt["receipt_sha256"],
        "hidden_evaluation_exposed":False,
        "promotion_authority":False,
    }


if __name__=="__main__":
    out=audit()
    print(json.dumps(out,indent=2,sort_keys=True))
    raise SystemExit(0 if out["status"].startswith("PASS_") else 1)
