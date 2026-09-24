#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.runtime.calibrated_retrieval import LabeledExample, predict
DEV=ROOT/"benchmarks/edu17r1_mention_incidence/dev.jsonl"
METHOD=ROOT/"kernel/development/EDU17R1_SEMANTIC_INGRESS_SELECTED_METHOD.json"


def calibration():
    out=[]
    for line in DEV.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj=json.loads(line)
        out.append(LabeledExample(obj["id"],obj["text"],obj["label"],f"public-dev:{obj['id']}"))
    return tuple(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("blind_jsonl")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    method=json.loads(METHOD.read_text(encoding="utf-8"))["method"]
    train=calibration()
    outputs=[]
    for line in Path(args.blind_jsonl).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row=json.loads(line)
        if "label" in row or "rationale" in row:
            raise ValueError("condition B requires label-free blind rows")
        pred=predict(method,train,row["text"])
        outputs.append({
            "id":row["id"],
            "prediction":"withhold" if pred.label is None else pred.label,
        })
    Path(args.output).write_text("\n".join(json.dumps(x,sort_keys=True) for x in outputs)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
