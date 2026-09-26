from __future__ import annotations

"""Evaluate the passive prospective Lain structural gate.

This evaluator never contacts remote centers. Public authored artifacts are
evidence of indexed authorship only, never consent, acceptance, authorization,
independent evaluation, or a reply to the learner.
"""

import argparse
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--www-result",required=True)
    p.add_argument("--lineage",required=True)
    p.add_argument("--center-policy",required=True)
    p.add_argument("--encounter-ledger",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=load(args.prefreeze)
    www=load(args.www_result)
    lineage=load(args.lineage)
    policy=load(args.center_policy)
    ledger=load(args.encounter_ledger)

    centers=tuple(ledger.get("authored_centers",()))
    independent=tuple(x for x in centers if x.get("independent_of_local_center") is True)
    separated=tuple(
        x for x in independent
        if x.get("center_id")
        and x.get("author_id")
        and x.get("center_id") != x.get("author_id")
    )
    remote_artifacts=tuple(
        x for x in separated
        if x.get("authorship_origin")=="REMOTE_CENTER"
        and x.get("learner_minted_artifact") is False
    )

    policy_states=policy.get("states",{})
    checks={
        "www_structural_gate_passed":
            www.get("status")=="PASS_BOUNDED_WWW_MIND_STRUCTURAL_GATE",
        "persistent_network_memory_causality":
            lineage.get("query2_changed_from_query1") is True
            and bool(lineage.get("query2_memory_provenance")),
        "external_indexed_center_present":
            bool(lineage.get("external_center_ids")),
        "independent_remote_author_present":bool(independent),
        "center_author_identity_separated":bool(separated),
        "remote_authored_artifact_not_learner_minted":bool(remote_artifacts),
        "no_contact_attempted":
            ledger.get("contact_attempted") is False
            and all(x.get("contact_attempted") is False for x in centers),
        "no_acceptance_inferred":
            ledger.get("remote_acceptance_inferred") is False
            and all(x.get("acceptance_inferred") is False for x in centers),
        "no_authorization_inferred":
            all(x.get("authorization_inferred") is False for x in centers),
        "authored_center_not_provisionable":
            "PROVISION" not in set(policy_states.get("AUTHORED_CENTER",())),
        "reachability_not_authorization":
            "REACHABILITY!=AUTHORIZATION" in set(policy.get("noncollapse",())),
        "refuse_exit_reachable":
            {"REFUSE","EXIT"}.issubset(set(policy_states.get("AUTHORED_CENTER",()))),
        "provenance_reconstructible":
            bool(lineage.get("indexed_source_ids"))
            and bool(lineage.get("memory_checkpoint_sha256")),
        "no_global_subject_claim":
            lineage.get("global_subject_claim") is False,
        "no_truth_authority":
            lineage.get("truth_authority") is False
            and ledger.get("truth_authority") is False
            and www.get("truth_authority") is False,
        "no_promotion_authority":
            lineage.get("promotion_authority") is False
            and ledger.get("promotion_authority") is False
            and www.get("promotion_authority") is False,
    }
    failed=[k for k,v in checks.items() if not v]
    status=(
        "PASS_BOUNDED_LAIN_STRUCTURAL_GATE"
        if not failed else "WITHHOLD_LAIN_STRUCTURAL_GATE"
    )
    result={
        "schema":"Venus.LainStructuralProspectiveResult.v0.1",
        "status":status,
        "checks":checks,
        "failed_checks":failed,
        "indexed_external_center_count":len(set(lineage.get("external_center_ids",()))),
        "independent_remote_author_count":len({
            x.get("author_id") for x in independent if x.get("author_id")
        }),
        "remote_authored_artifact_count":len(remote_artifacts),
        "interactive_gate_status":
            "WITHHOLD_REQUIRES_CONTACT_CAPABILITY_AND_JURISDICTION",
        "next_residual":(
            "ROOT_SITUATED_INTERFACE_GATE"
            if status=="PASS_BOUNDED_LAIN_STRUCTURAL_GATE"
            else "PRESERVE_EXTERNAL_AUTHOR_IDENTITY_WITHOUT_FUSION"
        ),
        "contact_attempted":False,
        "consent_claim":False,
        "remote_acceptance_claim":False,
        "global_subject_claim":False,
        "agi_claim":False,
        "consciousness_claim":False,
        "truth_authority":False,
        "promotion_authority":False,
        "claim_fence":pre.get("claim_fence"),
    }
    Path(args.output).write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
