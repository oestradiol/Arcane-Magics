from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load_module(name: str, rel: str):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {rel}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

old=load_module("commutative_binding","kernel/development/cognitive_theater_binding_order.py")
new=load_module("ordered_binding","kernel/development/cognitive_theater_ordered_binding.py")


def load(rel: str):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))


def score(prefreeze: dict, learner, *, ordered: bool) -> dict:
    state=learner.learn_state(prefreeze) if ordered else learner.learn_binding_state(prefreeze,n=3)
    rows=[]
    correct=0
    withholds=0
    per_task={}
    per_face={}
    for task in prefreeze["tasks"]:
        tid=task["id"]
        per_task[tid]={"correct":0,"total":0,"withholds":0}
        for face,examples in task["heldout_examples"].items():
            per_face.setdefault(face,{"correct":0,"total":0,"withholds":0})
            for row in examples:
                out=(
                    learner.predict(state,task_id=tid,face=face,surface=row["surface"])
                    if ordered
                    else learner.predict_binding(state,task_id=tid,face=face,surface=row["surface"])
                )
                ok=out["binding"]==row["gold"]
                correct+=int(ok)
                withholds+=int(out["binding"] is None)
                per_task[tid]["total"]+=1
                per_task[tid]["correct"]+=int(ok)
                per_task[tid]["withholds"]+=int(out["binding"] is None)
                per_face[face]["total"]+=1
                per_face[face]["correct"]+=int(ok)
                per_face[face]["withholds"]+=int(out["binding"] is None)
                rows.append({
                    "task_id":tid,"face":face,"gold":row["gold"],"prediction":out["binding"],
                    "status":out["status"],"correct":ok,"assignment_margin":out.get("assignment_margin",0.0),
                })
    total=len(rows)
    return {"correct":correct,"total":total,"accuracy":correct/total if total else 0.0,"withholds":withholds,"per_task":per_task,"per_face":per_face,"rows":rows}


def evaluate()->dict:
    pre=load("kernel/development/COGNITIVE_THEATER_BINDING_ORDER_FRESH2_PREFREEZE.json")
    comm=score(pre,old,ordered=False)
    seq=score(pre,new,ordered=True)
    return {
      "schema":"Venus.CognitiveTheaterBindingOrderFresh2Result.v0.1",
      "status":"RETURNED_FRESH2_LOCAL_DEVELOPMENTAL_COMPARISON",
      "issue_ref":206,
      "commutative":comm,
      "ordered":seq,
      "accuracy_delta":seq["accuracy"]-comm["accuracy"],
      "independent_external_evaluation":False,
      "general_theater_claim":False,
      "music_prosody_claim":False,
      "internalization_claim":False,
      "promotion_authority":False,
      "truth_authority":False,
    }

if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
