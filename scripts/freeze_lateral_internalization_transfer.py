from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.development.lateral_episode import _combined, _predict
from kernel.runtime.token_knn import execute as execute_state

SALT="VENUS_LATERAL169_INTERNALIZED_V1"

def opaque(token: str) -> str:
    return hashlib.sha256((SALT+"|"+token).encode("utf-8")).hexdigest()[:24]

def state_tokens(row):
    from kernel.development.lateral_episode import relation_expanded_tokens, path_tokens
    raw=set(relation_expanded_tokens(row))|set(path_tokens(row))
    return sorted(opaque(x) for x in raw)

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--visible",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--training",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=json.loads(Path(args.prefreeze).read_text(encoding="utf-8"))
    visible=json.loads(Path(args.visible).read_text(encoding="utf-8"))
    state=json.loads(Path(args.state).read_text(encoding="utf-8"))
    training=json.loads(Path(args.training).read_text(encoding="utf-8"))

    if pre.get("status")!="PREFROZEN_BEFORE_TRANSFER_FACE_ACQUISITION":
        raise SystemExit("transfer prefreeze required")
    expected=[int(x) for x in pre["universe_rule"]["selected_pr_numbers"]]
    rows=visible.get("rows",[])
    got=[int(x["pr_number"]) for x in rows]
    if got!=expected:
        raise SystemExit(f"visible transfer rows do not match prefreeze: {got} != {expected}")
    if visible.get("labels_present") is not False or visible.get("merged_state_present") is not False:
        raise SystemExit("transfer labels leaked before prediction freeze")
    if state.get("ownership",{}).get("state_owned") is not True:
        raise SystemExit("state-owned learner policy required")
    if state.get("internalization_contract",{}).get("capability_specific_python_runtime_dependency") is not False:
        raise SystemExit("candidate state still depends on capability-specific runtime")

    train=tuple(training["train"])
    source_fn=_combined("path_topology")
    predictions=[]
    for row in rows:
        state_pred=execute_state(state,state_tokens(row))
        source_pred="1" if _predict(train,row,source_fn) else "0"
        predictions.append({
            "pr_number":int(row["pr_number"]),
            "state_prediction":state_pred,
            "source_prediction":source_pred,
            "equivalent":state_pred==source_pred,
        })

    result={
        "schema":"Venus.LateralInternalizationTransferPredictions.v0.1",
        "transfer_episode":1,
        "prefreeze_ref":args.prefreeze,
        "visible_ref":args.visible,
        "state_ref":args.state,
        "training_ref":args.training,
        "state_sha256":sha256_file(Path(args.state)),
        "source_scaffold":"kernel/development/lateral_episode.py",
        "source_scaffold_sha256":sha256_file(ROOT/"kernel/development/lateral_episode.py"),
        "generic_executor":"kernel/runtime/token_knn.py",
        "generic_executor_sha256":sha256_file(ROOT/"kernel/runtime/token_knn.py"),
        "prediction_count":len(predictions),
        "predictions":predictions,
        "exact_prediction_equivalence":all(x["equivalent"] for x in predictions),
        "labels_accessed":False,
        "merged_state_accessed":False,
        "internalization_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
