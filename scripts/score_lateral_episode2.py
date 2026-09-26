from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def git_blob_sha(path: Path) -> str:
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\\0"+raw).hexdigest()


def evaluate(prefreeze: dict, proposal: dict, reveal: dict, *, proposal_blob_sha: str) -> dict:
    if prefreeze.get("schema")!="Venus.LateralEpisode2Prefreeze.v0.1":
        raise ValueError("unsupported episode-2 prefreeze")
    if prefreeze.get("status")!="PREFROZEN_BEFORE_LEARNER_HOLDOUT_FACE_ACQUISITION":
        raise ValueError("episode-2 prefreeze status invalid")
    if proposal.get("schema")!="Venus.LateralEpisode2Proposal.v0.1" or int(proposal.get("episode",0))!=2:
        raise ValueError("episode-2 frozen proposal required")
    if proposal.get("holdout_labels_accessed") is not False:
        raise ValueError("proposal accessed hidden labels")
    if reveal.get("schema")!="Venus.LateralEpisode2HiddenReveal.v0.1" or int(reveal.get("episode",0))!=2:
        raise ValueError("episode-2 external reveal required")
    if reveal.get("revealed_after_proposal_sha")!=proposal_blob_sha:
        raise ValueError("hidden reveal is not bound to frozen proposal blob")
    if reveal.get("learner_authored_labels") is not False:
        raise ValueError("learner-authored labels are inadmissible")
    if reveal.get("promotion_authority") is not False or reveal.get("truth_authority") is not False:
        raise ValueError("reveal may not carry promotion/truth authority")

    expected=tuple(int(x) for x in prefreeze["fresh_holdout_universe"]["selected_pr_numbers"])
    predictions={int(k):bool(v) for k,v in proposal["holdout_predictions"].items()}
    labels={int(k):bool(v) for k,v in reveal["holdout_labels"].items()}
    if set(predictions)!=set(expected) or set(labels)!=set(expected):
        raise ValueError("episode-2 identities differ from prefrozen holdout")
    if len(predictions)!=int(proposal.get("fresh_holdout_count",0)):
        raise ValueError("proposal holdout count mismatch")

    correct=sum(int(predictions[n]==labels[n]) for n in expected)
    total=len(expected)
    accuracy=correct/total if total else 0.0
    rule=prefreeze["pass_rule"]
    minimum=float(rule["minimum_holdout_accuracy"])
    prior=float(rule["must_exceed_episode1_internalized_transfer_accuracy"])
    revision_pass=accuracy>=minimum and accuracy>prior

    selected=dict(proposal["selected_policy"])
    faces=tuple(str(x) for x in selected.get("faces",()))
    lateral_faces=tuple(x for x in faces if x!="relation_expanded")
    status=(
        "PASS_BOUNDED_EPISODE2_POLICY_REVISION"
        if revision_pass else "WITHHOLD_EPISODE2_POLICY_REVISION"
    )
    lateral_status=(
        "RETAINED_IN_SELECTED_REVISION"
        if lateral_faces else "NOT_RETAINED_BY_SELECTED_REVISION"
    )
    next_residual=(
        "PROPOSE_NEW_INDEPENDENT_FACE_UNDER_FRESH_PREFREEZE"
        if revision_pass and not lateral_faces
        else "REPEAT_DISJOINT_TRANSFER_BEFORE_GENERALIZATION"
        if revision_pass
        else "REVISE_POLICY_WITHOUT_GENERALIZATION_CLAIM"
    )

    return {
        "schema":"Venus.LateralEpisode2Result.v0.1",
        "episode":2,
        "status":status,
        "selected_policy":selected,
        "selected_lateral_faces":list(lateral_faces),
        "lateral_face_status":lateral_status,
        "holdout_accuracy":accuracy,
        "holdout_correct":correct,
        "holdout_total":total,
        "prior_transfer_accuracy":prior,
        "absolute_improvement_over_prior_transfer":accuracy-prior,
        "minimum_holdout_accuracy":minimum,
        "minimum_accuracy_met":accuracy>=minimum,
        "prior_transfer_exceeded":accuracy>prior,
        "predictions":{str(n):predictions[n] for n in expected},
        "external_labels":{str(n):labels[n] for n in expected},
        "proposal_blob_sha":proposal_blob_sha,
        "evaluation_owner":"PREFROZEN_EXTERNAL_GITHUB_MERGED_STATE_EVALUATOR",
        "bounded_policy_revision_claim":revision_pass,
        "general_lateralizer_claim":False,
        "internalization_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
        "next_residual":next_residual,
        "claim_fence":(
            "A PASS establishes only that one prefrozen revision chosen from prior returned labels "
            "reached the declared bounded episode-2 holdout threshold and improved over the 1/8 transfer. "
            "Because the selected policy retained no independent lateral face, this result does not establish "
            "general Lateralizer competence or generalization of the episode-1 lateral coordinate."
        ),
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--proposal",required=True)
    p.add_argument("--reveal",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=json.loads(Path(args.prefreeze).read_text(encoding="utf-8"))
    proposal_path=Path(args.proposal)
    proposal=json.loads(proposal_path.read_text(encoding="utf-8"))
    reveal=json.loads(Path(args.reveal).read_text(encoding="utf-8"))
    result=evaluate(pre,proposal,reveal,proposal_blob_sha=git_blob_sha(proposal_path))
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
