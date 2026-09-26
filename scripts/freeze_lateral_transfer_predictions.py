from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

# External comparator only. This module must not enter the isolated state path.
from kernel.development.lateral_episode import _combined, _predict
from scripts.compile_lateral_internalized_state import combined_tokens


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--train",required=True)
    p.add_argument("--transfer",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=json.loads((ROOT/args.prefreeze).read_text(encoding="utf-8"))
    train_obj=json.loads((ROOT/args.train).read_text(encoding="utf-8"))
    transfer_obj=json.loads((ROOT/args.transfer).read_text(encoding="utf-8"))
    state_path=ROOT/args.state
    state=json.loads(state_path.read_text(encoding="utf-8"))

    if pre.get("status")!="PREFROZEN_BEFORE_TRANSFER_FACE_ACQUISITION":
        raise SystemExit("fresh-transfer prefreeze required")
    expected=[int(x) for x in pre["universe_rule"]["selected_pr_numbers"]]
    got=[int(x["pr_number"]) for x in transfer_obj.get("rows",())]
    if got!=expected:
        raise SystemExit(f"transfer rows differ from prefrozen universe: {got} != {expected}")
    if transfer_obj.get("labels_present") is not False or transfer_obj.get("merged_state_present") is not False:
        raise SystemExit("transfer labels leaked before prediction freeze")

    source_predictions={
        int(row["pr_number"]):bool(_predict(train_obj["train"],row,_combined("path_topology")))
        for row in transfer_obj["rows"]
    }
    opaque_rows=[
        {"pr_number":int(row["pr_number"]),"tokens":combined_tokens(row)}
        for row in transfer_obj["rows"]
    ]

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        shutil.copy2(ROOT/"kernel/runtime/token_knn.py",td/"token_knn.py")
        shutil.copy2(state_path,td/"state.json")
        (td/"faces.json").write_text(json.dumps({"rows":opaque_rows}),encoding="utf-8")
        verifier=td/"verify.py"
        verifier.write_text(
'''import importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("token_knn",H/"token_knn.py")
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
state=json.loads((H/"state.json").read_text())
faces=json.loads((H/"faces.json").read_text())
pred={str(row["pr_number"]):(m.execute(state,row["tokens"])=="1") for row in faces["rows"]}
print(json.dumps(pred,sort_keys=True))
''',
            encoding="utf-8",
        )
        proc=subprocess.run([sys.executable,"-I",str(verifier)],cwd=td,capture_output=True,text=True)
        if proc.returncode!=0:
            raise SystemExit(proc.stdout+"\n"+proc.stderr)
        state_predictions={int(k):bool(v) for k,v in json.loads(proc.stdout).items()}
        scaffold_present=(td/"lateral_episode.py").exists()

    result={
        "schema":"Venus.LateralInternalizationTransferPredictions.v0.1",
        "transfer_episode":1,
        "prefreeze_ref":args.prefreeze,
        "state_sha256":hashlib.sha256(state_path.read_bytes()).hexdigest(),
        "source_scaffold_sha256":hashlib.sha256((ROOT/"kernel/development/lateral_episode.py").read_bytes()).hexdigest(),
        "source_predictions":{str(k):v for k,v in sorted(source_predictions.items())},
        "state_predictions":{str(k):v for k,v in sorted(state_predictions.items())},
        "exact_prediction_equivalence":source_predictions==state_predictions,
        "state_runtime_scaffold_present":scaffold_present,
        "labels_accessed":False,
        "evaluation_owner":"PREFROZEN_EXTERNAL_EQUIVALENCE_EVALUATOR",
        "promotion_authority":False,
        "truth_authority":False,
    }
    if scaffold_present or source_predictions!=state_predictions:
        result["status"]="FAIL_TRANSFER_EQUIVALENCE_BEFORE_LABEL_REVEAL"
    else:
        result["status"]="PASS_TRANSFER_EQUIVALENCE_BEFORE_LABEL_REVEAL"
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
