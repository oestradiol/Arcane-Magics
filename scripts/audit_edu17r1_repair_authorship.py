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
    elif candidate_status=="AUTHORED_FROZEN":
        candidate=ROOT/"kernel/development/EDU17R1_REPAIR_CANDIDATE.json"
        receipt=ROOT/"kernel/development/EDU17R1_REPAIR_OWNERSHIP_RECEIPT.json"
        if not candidate.exists() or not receipt.exists():
            errors.append("AUTHORED_FROZEN requires candidate and ownership receipt")
        if controller.get("available") is not True or not controller.get("operation"):
            errors.append("AUTHORED_FROZEN requires admitted developmental controller operation")
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
