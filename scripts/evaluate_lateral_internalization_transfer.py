from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--source-removal",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--predictions",required=True)
    p.add_argument("--reveal",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=json.loads(Path(args.prefreeze).read_text(encoding="utf-8"))
    removal=json.loads(Path(args.source_removal).read_text(encoding="utf-8"))
    state=json.loads(Path(args.state).read_text(encoding="utf-8"))
    pred_path=Path(args.predictions)
    pred=json.loads(pred_path.read_text(encoding="utf-8"))
    reveal=json.loads(Path(args.reveal).read_text(encoding="utf-8"))

    prediction_blob_sha = None
    # The reveal binds to Git blob SHA, while this evaluator also records byte SHA256.
    expected_blob=str(reveal.get("revealed_after_prediction_blob_sha") or "")
    if not expected_blob:
        raise SystemExit("hidden reveal must bind to frozen prediction blob")

    labels={int(k):bool(v) for k,v in reveal["holdout_labels"].items()}
    source={int(k):bool(v) for k,v in pred["source_predictions"].items()}
    state_pred={int(k):bool(v) for k,v in pred["state_predictions"].items()}
    if set(labels)!=set(source) or set(source)!=set(state_pred):
        raise SystemExit("transfer label/prediction identities differ")

    exact_equivalence=(source==state_pred)
    correct=sum(1 for k,v in state_pred.items() if v==labels[k])
    accuracy=correct/len(labels)

    ownership_checks={
        "prior_source_removal_equivalence": removal.get("behavior_equivalent_after_removal") is True,
        "prior_alpha_rename_invariance": removal.get("alpha_rename_invariant") is True,
        "source_scaffold_absent_from_state_runtime": pred.get("state_runtime_scaffold_present") is False,
        "fresh_transfer_exact_source_state_equivalence": exact_equivalence,
        "labels_not_accessed_before_prediction": pred.get("labels_accessed") is False,
        "external_label_reveal": reveal.get("learner_authored_labels") is False,
        "state_semantics_owned": state.get("internalization_contract",{}).get("semantics_owner")=="LEARNER_STATE",
        "capability_specific_python_runtime_dependency_absent": state.get("internalization_contract",{}).get("capability_specific_python_runtime_dependency") is False,
        "external_roles_preserved": all(x in state.get("external_nonconsumable",[]) for x in (
            "WORLD_RETURN","EVIDENCE_IDENTITY","EVALUATOR","AUTHORITY","JURISDICTION","STOP_WITHHOLD","ROLLBACK_PARENT_CUSTODY"
        )),
    }
    failed=[k for k,v in ownership_checks.items() if not v]
    ownership_status=(
        "PASS_BOUNDED_INTERNALIZATION_EPISODE1_PROJECTION_POLICY"
        if not failed else "WITHHOLD_INTERNALIZATION"
    )
    transfer_status=(
        "PASS_FRESH_TRANSFER_ACCURACY"
        if accuracy>0.5 else "FAIL_FRESH_TRANSFER_GENERALIZATION"
    )

    result={
        "schema":"Venus.LateralInternalizationTransferResult.v0.1",
        "ownership_status":ownership_status,
        "generalization_status":transfer_status,
        "ownership_checks":ownership_checks,
        "failed_ownership_checks":failed,
        "fresh_transfer_accuracy":accuracy,
        "fresh_transfer_correct":correct,
        "fresh_transfer_total":len(labels),
        "state_predictions":{str(k):v for k,v in sorted(state_pred.items())},
        "external_labels":{str(k):v for k,v in sorted(labels.items())},
        "state_sha256":sha256_file(Path(args.state)),
        "prediction_file_sha256":sha256_file(pred_path),
        "internalization_receipt_minted":not failed,
        "general_lateralizer_claim":False,
        "next_residual":(
            "GENERALIZE_OR_REVISE_LATERAL_POLICY_ON_FRESH_TRANSFER"
            if not failed and accuracy<=0.5
            else None
        ),
        "claim_fence":"A pass establishes bounded ownership/internalization of the episode-1 projection policy only. Poor fresh-transfer accuracy remains a separate negative generalization result and blocks any general Lateralizer claim.",
        "promotion_authority":False,
        "truth_authority":False,
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
