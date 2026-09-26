from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD_PATH=ROOT/"kernel/development/cognitive_theater_binding_order.py"
SPEC=importlib.util.spec_from_file_location("cognitive_theater_binding_order",MOD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load cognitive theater binding/order scaffold")
mod=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=mod
SPEC.loader.exec_module(mod)


def load(rel: str):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))


def evaluate() -> dict:
    pre=load("kernel/development/COGNITIVE_THEATER_BINDING_ORDER_PREFREEZE.json")
    state=mod.learn_binding_state(pre,n=3)
    rows=[]
    per_task={}
    per_face={}
    exact=0
    withholds=0

    for task in pre["tasks"]:
        tid=task["id"]
        per_task[tid]={"correct":0,"total":0,"withholds":0}
        for face,examples in task["heldout_examples"].items():
            per_face.setdefault(face,{"correct":0,"total":0,"withholds":0})
            for row in examples:
                out=mod.predict_binding(state,task_id=tid,face=face,surface=row["surface"])
                ok=out["binding"]==row["gold"]
                exact+=int(ok)
                withholds+=int(out["binding"] is None)
                per_task[tid]["total"]+=1
                per_task[tid]["correct"]+=int(ok)
                per_task[tid]["withholds"]+=int(out["binding"] is None)
                per_face[face]["total"]+=1
                per_face[face]["correct"]+=int(ok)
                per_face[face]["withholds"]+=int(out["binding"] is None)
                rows.append({
                    "task_id":tid,"face":face,"surface":row["surface"],
                    "gold":row["gold"],"prediction":out["binding"],"status":out["status"],
                    "correct":ok,"assignment_margin":out.get("assignment_margin"),
                })

    total=len(rows)
    return {
        "schema":"Venus.CognitiveTheaterBindingOrderResult.v0.1",
        "status":"RETURNED_G2_G3_OPAQUE_BINDING_ORDER_CANDIDATE",
        "issue_ref":206,
        "correct":exact,
        "total":total,
        "accuracy":exact/total if total else 0.0,
        "withholds":withholds,
        "per_task":per_task,
        "per_face":per_face,
        "rows":rows,
        "alpha_renamed_opaque_tokens":True,
        "lexical_inventory_matched_within_probe":True,
        "natural_reference_resolution_claim":False,
        "prosody_music_claim":False,
        "general_theater_claim":False,
        "internalization_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
        "next_residual":"CROSS_FACE_COMPOSE_GROUNDED_SYMBOLS_WITH_BINDING_AND_ORDER_THEN_SOURCE_REMOVE",
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
