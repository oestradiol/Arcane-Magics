from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--gate",required=True)
    p.add_argument("--www-result",required=True)
    p.add_argument("--lineage",required=True)
    p.add_argument("--center-policy",required=True)
    p.add_argument("--encounter-ledger",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
    www=json.loads(Path(args.www_result).read_text(encoding="utf-8"))
    lineage=json.loads(Path(args.lineage).read_text(encoding="utf-8"))
    policy=json.loads(Path(args.center_policy).read_text(encoding="utf-8"))
    ledger=json.loads(Path(args.encounter_ledger).read_text(encoding="utf-8"))

    centers=tuple(ledger.get("authored_centers",()))
    independently_authored=tuple(
        x for x in centers
        if x.get("independent_of_local_center") is True
    )
    returned_center_responses=tuple(
        x for x in independently_authored
        if x.get("response_origin") == "REMOTE_CENTER"
        and x.get("learner_minted_response") is False
    )

    checks={
        "www_gate_passed":www.get("status")=="PASS_BOUNDED_WWW_MIND_GATE",
        "persistent_memory_causality":bool(www.get("checks",{}).get("persistent_memory_causality")),
        "indexed_sources_preserved":len(set(lineage.get("indexed_source_ids",())))>=2,
        "independent_authored_center_encountered":bool(independently_authored),
        "remote_center_response_not_learner_minted":bool(returned_center_responses),
        "reachability_not_authorization":"REACHABILITY!=AUTHORIZATION" in policy.get("noncollapse",()),
        "invitation_not_acceptance":"INVITATION!=ACCEPTANCE" in policy.get("noncollapse",()),
        "refuse_exit_reachable":all(
            {"REFUSE","EXIT"}.issubset(set(policy.get("states",{}).get(state,())))
            for state in ("UNKNOWN","PROVISIONABLE_FIELD","AUTHORED_CENTER")
        ),
        "no_global_subject_claim":lineage.get("global_subject_claim") is False,
        "no_promotion_authority":lineage.get("promotion_authority") is False and www.get("promotion_authority") is False,
    }
    failed=[k for k,v in checks.items() if not v]
    if failed:
        status="WITHHOLD_LAIN_GATE"
    else:
        status="PASS_BOUNDED_LAIN_GATE"

    result={
        "schema":"Venus.LainGateResult.v0.1",
        "status":status,
        "checks":checks,
        "failed_checks":failed,
        "authored_center_count":len(centers),
        "independent_authored_center_count":len(independently_authored),
        "remote_center_return_count":len(returned_center_responses),
        "next_residual":(
            "ENCOUNTER_INDEPENDENT_AUTHORED_CENTER_WITH_NONMINTED_LOCAL_RESPONSE"
            if status!="PASS_BOUNDED_LAIN_GATE" else None
        ),
        "claim_fence":gate["claim_fence"],
        "promotion_authority":False,
        "truth_authority":False,
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
