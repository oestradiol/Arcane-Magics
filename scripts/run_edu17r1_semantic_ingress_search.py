#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from kernel.runtime.calibrated_retrieval import LabeledExample, leave_one_out

ROOT=Path(__file__).resolve().parents[1]
DEV=ROOT/"benchmarks/edu17r1_mention_incidence/dev.jsonl"
STATE=ROOT/"kernel/development/EDU17R1_SEMANTIC_INGRESS_METHOD_FAMILY.json"


def load_examples():
    rows=[]
    for line in DEV.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj=json.loads(line)
        rows.append(LabeledExample(
            example_id=obj["id"],text=obj["text"],label=obj["label"],
            provenance_id=f"public-dev:{obj['id']}"
        ))
    return tuple(rows)


def run():
    state=json.loads(STATE.read_text(encoding="utf-8"))
    rows=load_examples()
    scored=[]
    for method in state["candidates"]:
        result=leave_one_out(method,rows)
        scored.append({
            "method":method,
            "accuracy":result["accuracy"],
            "macro_f1":result["macro_f1"],
            "withholds":result["withholds"],
            "predictions":result["predictions"],
        })
    scored.sort(key=lambda x:(
        -x["macro_f1"],-x["accuracy"],x["withholds"],
        int(x["method"]["complexity"]),x["method"]["id"]
    ))
    winner=scored[0]
    return {
        "schema":"Venus.EDU17R1SemanticIngressPublicDevSearch.v0.1",
        "input":"PUBLIC_DEV_ONLY",
        "public_dev_may_be_tuned_against":True,
        "hidden_evaluation_exposed":False,
        "selection_rule":state["selection_rule"],
        "winner":winner,
        "all_candidates":[
            {
                "method_id":x["method"]["id"],
                "accuracy":x["accuracy"],
                "macro_f1":x["macro_f1"],
                "withholds":x["withholds"],
            } for x in scored
        ],
        "promotion_authority":False,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
