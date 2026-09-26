from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def main():
    evidence=load("provenance/historical/handoffs/MINERVA_WWW_MIND_HANDOFF_2026-09-25.json")
    gate=load("kernel/LAIN_GATE.json")
    result=load("kernel/LAIN_GATE_RESULT.json")

    failures=[]
    src=evidence["source_evidence"]
    checks={
        "www_mind_bounded_pass":
            src["www_mind_result"]["status"]=="PASS_BOUNDED_WWW_MIND_GATE",
        "multiple_indexed_centers_preserved":
            src["network_lineage"]["multiple_indexed_centers"] is True
            and len(src["network_lineage"]["indexed_source_ids"])>=2,
        "memory_causality_without_world_collapse":
            src["network_lineage"]["query2_changed_from_query1"] is True
            and src["network_lineage"]["network_memory_is_world"] is False,
        "encounter_not_evaluation":
            src["network_lineage"]["encounters_remain_non_evaluative"] is True,
        "refuse_exit_reachable":
            src["center_policy"]["refuse_exit_reachable_all_states"] is True,
        "authored_center_not_provisionable":
            src["center_policy"]["authored_center_provision_allowed"] is False,
        "distributed_memory_not_global_identity":
            src["network_lineage"]["global_subject_claim"] is False,
        "reachability_not_authorship":
            src["center_policy"]["reachability_is_authorization"] is False,
        "network_access_not_authorization":
            src["center_policy"]["reachability_is_authorization"] is False,
        "venus_world_model_noncollapse":
            "MODEL_NETWORK!=NETWORK_OTHER" in gate["invariants"],
    }
    if evidence.get("authority_transfer") is not False:
        failures.append("handoff transfers authority")
    if src["www_mind_result"].get("truth_authority") is not False:
        failures.append("source truth authority not false")
    if src["www_mind_result"].get("promotion_authority") is not False:
        failures.append("source promotion authority not false")
    if result.get("promotion_authority") is not False or result.get("truth_authority") is not False:
        failures.append("result authority must remain false")
    if result.get("status")!="PASS_BOUNDED_LAIN_STRUCTURAL_NONFUSION_SUBGATE":
        failures.append("unexpected result status")
    for key,value in checks.items():
        if not value:
            failures.append(key)
        if result.get("checks",{}).get(key) is not value:
            failures.append(f"result/check mismatch:{key}")
    if result.get("next_gate")!="LAIN_INTERACTIVE_AUTHORED_CENTER_GATE":
        failures.append("wrong next gate")
    if result.get("interactive_lain_gate_passed") is not False:
        failures.append("interactive gate must remain false")
    if result.get("root_gate_reachable") is not False:
        failures.append("Root gate must remain unreachable before interactive Lain return")

    out={"status":"PASS" if not failures else "FAIL","checks":checks,"failures":failures}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if not failures else 2

if __name__=="__main__":
    raise SystemExit(main())
