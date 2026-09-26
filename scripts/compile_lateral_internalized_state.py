from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

# Capability-specific scaffold is allowed only at compilation.
from kernel.development.lateral_episode import (
    relation_expanded_tokens,
    path_tokens,
)


SALT="VENUS_LATERAL169_INTERNALIZED_V1"


def opaque(token: str) -> str:
    return hashlib.sha256((SALT+"|"+token).encode("utf-8")).hexdigest()[:24]


def combined_tokens(row):
    raw=set(relation_expanded_tokens(row))|set(path_tokens(row))
    return sorted(opaque(x) for x in raw)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--result",required=True)
    p.add_argument("--state-output",required=True)
    p.add_argument("--holdout-output",required=True)
    args=p.parse_args()

    dataset=json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    result=json.loads(Path(args.result).read_text(encoding="utf-8"))
    if result.get("status")!="PASS_BOUNDED_LATERAL_MISSING_COORDINATE":
        raise SystemExit("earned bounded lateral result required")
    if result.get("selected_face")!="path_topology":
        raise SystemExit("compiler currently binds only the earned selected face")

    examples=[
        {
            "example_id":f"pr:{row['pr_number']}",
            "tokens":combined_tokens(row),
            "decision":"1" if bool(row["train_label"]) else "0",
        }
        for row in dataset["train"]
    ]
    state={
        "schema":"Venus.StateOwnedTokenKNN.v0.1",
        "capability_id":"LATERAL169_EPISODE1_PROJECTION_POLICY",
        "origin":{
            "source_scaffold":"kernel/development/lateral_episode.py",
            "earned_result":"kernel/development/LATERAL_EPISODE_1_RESULT.json",
            "selected_face":"path_topology",
            "cross_face_residual_ids":result["cross_face_residual_ids"],
        },
        "program":{
            "metric":"JACCARD",
            "k":3,
            "exact_tie_decision":"0",
            "token_namespace":"OPAQUE_SHA256_24",
            "examples":examples,
        },
        "ownership":{
            "state_owned":True,
            "general_lateralizer_claim":False,
            "promotion_authority":False,
        },
        "external_nonconsumable":[
            "WORLD_RETURN","EVIDENCE_IDENTITY","EVALUATOR","AUTHORITY",
            "JURISDICTION","STOP_WITHHOLD","ROLLBACK_PARENT_CUSTODY"
        ],
        "internalization_contract":{
            "semantics_owner":"LEARNER_STATE",
            "capability_specific_python_runtime_dependency":False,
            "generic_executor":"kernel/runtime/token_knn.py",
            "source_python_reference_is_provenance_only":True,
            "boundary_ref":"kernel/development/INTERNALIZATION_BOUNDARY.json",
            "status":"CANDIDATE_PENDING_SOURCE_REMOVAL_AND_FRESH_TRANSFER",
        },
    }
    holdout={
        "schema":"Venus.OpaqueTokenFaceBundle.v0.1",
        "capability_id":state["capability_id"],
        "adapter_role":"EXTERNAL_FACE_NORMALIZATION",
        "rows":[
            {"pr_number":row["pr_number"],"tokens":combined_tokens(row)}
            for row in dataset["holdout"]
        ],
        "labels_present":False,
        "promotion_authority":False,
    }
    Path(args.state_output).write_text(json.dumps(state,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(args.holdout_output).write_text(json.dumps(holdout,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
