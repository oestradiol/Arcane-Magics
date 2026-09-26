from __future__ import annotations

"""Derive an inert authored-center ledger from returned network encounters.

This does not contact remote centers and does not infer acceptance, consent,
authorization, personhood, or evaluative authority.
"""

import argparse
import json
from pathlib import Path

LOCAL_CENTER_ID="github-repo:oestradiol/Arcane-Magics"
LOCAL_AUTHOR_IDS=frozenset({
    "github-user:oestradiol",
    "github-user:github-actions[bot]",
    "arcane-magics:minerva",
})


def build(encounters: list[dict]) -> dict:
    rows=[]
    seen=set()
    for encounter in encounters:
        for source in encounter.get("sources",()):
            center_id=str(source.get("center_id") or "")
            author_id=str(source.get("author_id") or "")
            source_id=str(source.get("source_id") or "")
            if not center_id or not author_id or not source_id:
                continue
            key=(center_id,author_id,source_id)
            if key in seen:
                continue
            seen.add(key)
            independent=(
                center_id != LOCAL_CENTER_ID
                and author_id not in LOCAL_AUTHOR_IDS
                and source.get("learner_minted_artifact") is False
            )
            rows.append({
                "center_id":center_id,
                "author_id":author_id,
                "author_login":str(source.get("author_login") or ""),
                "author_type":str(source.get("author_type") or ""),
                "author_association":str(source.get("author_association") or ""),
                "source_id":source_id,
                "source_class":str(source.get("source_class") or ""),
                "independent_of_local_center":independent,
                "authorship_origin":"REMOTE_CENTER" if independent else "LOCAL_OR_UNRESOLVED",
                "learner_minted_artifact":bool(source.get("learner_minted_artifact",False)),
                "directed_to_learner":False,
                "contact_attempted":False,
                "acceptance_inferred":False,
                "authorization_inferred":False,
                "response_to_learner_claim":False,
            })
    independent=[x for x in rows if x["independent_of_local_center"]]
    return {
        "schema":"Venus.AuthoredCenterEncounterLedger.v0.2",
        "local_center_id":LOCAL_CENTER_ID,
        "local_author_ids":sorted(LOCAL_AUTHOR_IDS),
        "authored_centers":rows,
        "independent_authored_artifact_count":len(independent),
        "contact_attempted":False,
        "remote_acceptance_inferred":False,
        "truth_authority":False,
        "promotion_authority":False,
        "claim_fence":"Public authored artifacts witness indexed external authorship only. They are not consent, acceptance, a reply to the learner, independent evaluation, or authority transfer.",
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--encounter",action="append",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    encounters=[json.loads(Path(x).read_text(encoding="utf-8")) for x in args.encounter]
    Path(args.output).write_text(
        json.dumps(build(encounters),indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
