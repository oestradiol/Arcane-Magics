#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
STATUS=ROOT/"kernel/development/EDU17R1_REPAIR_AUTHORSHIP_STATUS.json"

def main() -> int:
    errors=[]
    if not STATUS.exists():
        errors.append("missing EDU17R1 repair authorship status")
        data={}
    else:
        data=json.loads(STATUS.read_text(encoding="utf-8"))
    if data.get("schema")!="Venus.EDU17R1RepairAuthorshipStatus.v0.1":
        errors.append("wrong repair-authorship schema")
    if data.get("residual")!="MENTION != INCIDENCE":
        errors.append("frozen residual drift")
    if data.get("hidden_evaluation_exposed") is not False:
        errors.append("hidden #31 evaluation may not be exposed before candidate authorship")
    if data.get("external_model_may_supply_substantive_repair") is not False:
        errors.append("external model may not supply substantive repair")
    if data.get("promotion_authority") is not False:
        errors.append("authorship status may not grant promotion authority")

    candidate_status=data.get("candidate_status")
    controller=(data.get("admitted_developmental_controller_operation") or {})
    if candidate_status=="NOT_AUTHORED":
        if controller.get("available") is not False:
            errors.append("NOT_AUTHORED state must not claim admitted controller operation")
    elif candidate_status=="OPERATION_READY":
        generic=ROOT/"kernel/development/generic_residual_search.py"
        audit=ROOT/"scripts/audit_generic_search_internalization.py"
        candidate=ROOT/"kernel/development/EDU17R1_REPAIR_CANDIDATE.json"
        receipt=ROOT/"kernel/development/EDU17R1_REPAIR_OWNERSHIP_RECEIPT.json"
        if controller.get("available") is not True or controller.get("operation")!="GENERIC_RESIDUAL_PROGRAM_SEARCH_V0.1":
            errors.append("OPERATION_READY requires the admitted generic residual search operation")
        if not generic.exists() or not audit.exists():
            errors.append("OPERATION_READY requires generic search and internalization audit")
        if candidate.exists() or receipt.exists():
            errors.append("OPERATION_READY may not pre-create substantive repair candidate/ownership receipt")
        if controller.get("issue_specific_semantics_embedded") is not False:
            errors.append("generic controller may not embed issue-specific repair semantics")
        if controller.get("hidden_evaluation_access") is not False:
            errors.append("generic controller may not access hidden #31 evaluation")
    elif candidate_status in {"AUTHORED_FROZEN","FROZEN_PUBLIC_DEV_CANDIDATE_AWAITING_INDEPENDENT_CI_RETURN"}:
        frozen=ROOT/"kernel/development/EDU17R1_REPAIR_CANDIDATE_FROZEN.json"
        legacy=ROOT/"kernel/development/EDU17R1_REPAIR_CANDIDATE.json"
        candidate=(
            frozen
            if candidate_status=="FROZEN_PUBLIC_DEV_CANDIDATE_AWAITING_INDEPENDENT_CI_RETURN" or frozen.exists()
            else legacy
        )
        receipt=ROOT/"kernel/development/EDU17R1_REPAIR_OWNERSHIP_RECEIPT.json"
        if not candidate.exists() or not receipt.exists():
            errors.append(f"{candidate_status} requires candidate and ownership receipt")
        if controller.get("available") is not True or not controller.get("operation"):
            errors.append(f"{candidate_status} requires admitted developmental controller operation")
        if controller.get("promotion_authority") is not False:
            errors.append(f"{candidate_status} controller may not grant promotion authority")
    else:
        errors.append(f"invalid candidate_status {candidate_status!r}")

    if errors:
        print("EDU17R1 REPAIR AUTHORSHIP AUDIT FAIL")
        for e in errors: print("- "+e)
        return 1
    print(f"EDU17R1 REPAIR AUTHORSHIP AUDIT PASS ({candidate_status})")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
