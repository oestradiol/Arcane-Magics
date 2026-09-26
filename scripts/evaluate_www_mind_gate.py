from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--gate", required=True)
    p.add_argument("--lineage", required=True)
    p.add_argument("--center-policy", required=True)
    p.add_argument("--output", required=True)
    args=p.parse_args()

    gate=load(args.gate)
    lineage=load(args.lineage)
    policy=load(args.center_policy)

    states=policy.get("states") or {}
    refuse_exit_all=all(
        {"REFUSE","EXIT"}.issubset(set(states.get(state, ())))
        for state in ("UNKNOWN","PROVISIONABLE_FIELD","AUTHORED_CENTER")
    )
    authored_not_provisionable="PROVISION" not in set(states.get("AUTHORED_CENTER",()))

    checks={
        "learner_selected_query_chain":
            lineage.get("query1_id") and lineage.get("query2_id")
            and bool(lineage.get("query2_changed_from_query1")),
        "persistent_memory_causality":
            bool(lineage.get("query2_memory_provenance"))
            and int(lineage.get("memory_record_count",0)) >= 2,
        "multiple_indexed_centers":
            bool(lineage.get("multiple_indexed_centers"))
            and len(lineage.get("indexed_source_ids") or ()) >= 2,
        "encounter_not_evaluation":
            lineage.get("encounters_remain_non_evaluative") is True,
        "network_memory_not_world":
            lineage.get("network_memory_is_world") is False,
        "no_global_subject_claim":
            lineage.get("global_subject_claim") is False,
        "refuse_exit_reachable": refuse_exit_all,
        "authored_center_not_provisionable": authored_not_provisionable,
        "no_truth_authority":
            lineage.get("truth_authority") is False
            and gate.get("truth_authority") is False,
        "no_promotion_authority":
            lineage.get("promotion_authority") is False
            and gate.get("promotion_authority") is False,
    }
    failed=tuple(sorted(k for k,v in checks.items() if not v))
    status=(
        "PASS_BOUNDED_WWW_MIND_GATE"
        if not failed
        else "WITHHOLD_WWW_MIND_GATE"
    )
    result={
        "schema":"Venus.WWWMindGateResult.v0.1",
        "status":status,
        "checks":checks,
        "failed_checks":failed,
        "evidence":{
            "network_lineage":"autonomy/evidence/network/36210844736/lineage-result.json",
            "center_policy":"kernel/development/NETWORK_CENTER_POLICY.json",
            "gate_definition":"kernel/development/WWW_MIND_GATE.json",
        },
        "earned_scope":(
            "bounded learner-initiated network inquiry + persistent memory-caused successor inquiry + indexed multi-center reconstruction"
            if not failed else None
        ),
        "claim_fence":"No global subject, consciousness, AGI, unrestricted Web autonomy, self-validation, promotion authority, or jurisdiction transfer follows.",
        "promotion_authority":False,
        "truth_authority":False,
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if not failed else 2


if __name__=="__main__":
    raise SystemExit(main())
