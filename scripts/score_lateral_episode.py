from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.development.lateral_episode import (
    LateralProposal,
    Prediction,
    score_hidden_labels,
)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--proposal",required=True)
    p.add_argument("--reveal",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pobj=json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    predictions=tuple(Prediction(**x) for x in pobj["holdout_predictions"])
    proposal=LateralProposal(
        schema=pobj["schema"],
        selected_face=pobj["selected_face"],
        train_scores=pobj["train_scores"],
        selected_train_gain=float(pobj["selected_train_gain"]),
        cross_face_residual_ids=tuple(int(x) for x in pobj["cross_face_residual_ids"]),
        preserved_face_sources=pobj["preserved_face_sources"],
        holdout_predictions=predictions,
        holdout_label_accessed=bool(pobj["holdout_label_accessed"]),
        internalization_claim=bool(pobj["internalization_claim"]),
        promotion_authority=bool(pobj["promotion_authority"]),
    )

    reveal=json.loads(Path(args.reveal).read_text(encoding="utf-8"))
    if reveal.get("revealed_after_proposal_sha") != "f78209434a6820ca369751ec2eeba5baf98460ac":
        raise SystemExit("hidden reveal is not bound to the frozen proposal blob")
    labels={int(k):bool(v) for k,v in reveal["holdout_labels"].items()}
    result=dict(score_hidden_labels(proposal,labels))
    result["proposal_blob_sha"]="f78209434a6820ca369751ec2eeba5baf98460ac"
    result["hidden_reveal_ref"]=args.reveal
    result["evaluation_owner"]="PREFROZEN_EXTERNAL_EVALUATOR"
    result["claim_fence"]="Result is bounded to episode 1 routing reconstruction. A pass does not establish general Lateralizer competence or Internalizer credit."
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
