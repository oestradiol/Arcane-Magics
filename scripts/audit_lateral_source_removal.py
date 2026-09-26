from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--state",required=True)
    p.add_argument("--faces",required=True)
    p.add_argument("--proposal",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    root=Path(__file__).resolve().parents[1]
    state_path=root/args.state
    faces_path=root/args.faces
    proposal_path=root/args.proposal
    executor_path=root/"kernel/runtime/token_knn.py"

    state=json.loads(state_path.read_text(encoding="utf-8"))
    faces=json.loads(faces_path.read_text(encoding="utf-8"))
    proposal=json.loads(proposal_path.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        shutil.copy2(executor_path,td/"token_knn.py")
        shutil.copy2(state_path,td/"state.json")
        shutil.copy2(faces_path,td/"faces.json")
        shutil.copy2(proposal_path,td/"proposal.json")

        verifier=td/"verify.py"
        verifier.write_text(
'''import importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("token_knn",HERE/"token_knn.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

state=json.loads((HERE/"state.json").read_text())
faces=json.loads((HERE/"faces.json").read_text())
proposal=json.loads((HERE/"proposal.json").read_text())
expected={int(x["pr_number"]):("1" if x["lateral"] else "0") for x in proposal["holdout_predictions"]}

pred={}
for row in faces["rows"]:
    pred[int(row["pr_number"])]=mod.execute(state,row["tokens"])
assert pred==expected,(pred,expected)

# Consistent alpha-renaming of every opaque token must preserve decisions.
all_tokens=sorted({t for ex in state["program"]["examples"] for t in ex["tokens"]} | {t for row in faces["rows"] for t in row["tokens"]})
rename={t:f"q{i:04d}" for i,t in enumerate(all_tokens)}
state2=json.loads(json.dumps(state))
for ex in state2["program"]["examples"]:
    ex["tokens"]=[rename[t] for t in ex["tokens"]]
faces2=json.loads(json.dumps(faces))
for row in faces2["rows"]:
    row["tokens"]=[rename[t] for t in row["tokens"]]
pred2={int(row["pr_number"]):mod.execute(state2,row["tokens"]) for row in faces2["rows"]}
assert pred2==expected,(pred2,expected)

print(json.dumps({"predictions":pred,"alpha_renamed_predictions":pred2},sort_keys=True))
''',
            encoding="utf-8",
        )
        proc=subprocess.run(
            [sys.executable,"-I",str(verifier)],
            cwd=td,
            capture_output=True,
            text=True,
        )
        if proc.returncode!=0:
            raise SystemExit(proc.stdout+"\n"+proc.stderr)
        isolated=json.loads(proc.stdout)

        if (td/"lateral_episode.py").exists():
            raise SystemExit("capability-specific scaffold leaked into isolated bundle")

    expected={int(x["pr_number"]):("1" if x["lateral"] else "0") for x in proposal["holdout_predictions"]}
    isolated_predictions={int(k):str(v) for k,v in isolated["predictions"].items()}
    alpha_predictions={int(k):str(v) for k,v in isolated["alpha_renamed_predictions"].items()}
    behavior_equivalent=isolated_predictions==expected
    alpha_invariant=alpha_predictions==expected
    status=(
        "PASS_EPISODE1_SOURCE_REMOVAL_EQUIVALENCE_PENDING_FRESH_TRANSFER"
        if behavior_equivalent and alpha_invariant
        else "FAIL_EPISODE1_SOURCE_REMOVAL_EQUIVALENCE"
    )
    result={
        "schema":"Venus.LateralSourceRemovalResult.v0.1",
        "status":status,
        "capability_id":state["capability_id"],
        "state_sha256":sha256_file(state_path),
        "source_scaffold":"kernel/development/lateral_episode.py",
        "source_scaffold_sha256":sha256_file(root/"kernel/development/lateral_episode.py"),
        "generic_executor":"kernel/runtime/token_knn.py",
        "generic_executor_sha256":sha256_file(executor_path),
        "original_scaffold_in_isolated_bundle":False,
        "behavior_equivalent_after_removal":behavior_equivalent,
        "alpha_rename_invariant":alpha_invariant,
        "successor_reconstructible":True,
        "source_provenance_preserved":True,
        "fresh_transfer_return_external":False,
        "internalization_receipt_minted":False,
        "next_residual":"FRESH_RENAMED_TRANSFER_RETURN_FOR_INTERNALIZATION",
        "promotion_authority":False,
        "truth_authority":False,
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
