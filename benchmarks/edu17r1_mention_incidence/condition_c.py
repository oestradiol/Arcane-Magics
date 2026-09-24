#!/usr/bin/env python3
from __future__ import annotations
"""Condition C: discriminator ablation.

The learned semantic-ingress discriminator is removed. The carrier falls back
to the preserved inherited mention detector that reproduced EDU17R1's public
failure family.
"""
import argparse, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("edu17r1_mention_baseline",HERE/"mention_baseline.py")
baseline=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(baseline)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("blind_jsonl")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    out=[]
    for line in Path(args.blind_jsonl).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        if "label" in row or "rationale" in row:
            raise ValueError("condition C requires blind rows")
        out.append({"id":row["id"],"prediction":baseline.predict(row["text"])})
    Path(args.output).write_text(
        "\n".join(json.dumps(x,sort_keys=True) for x in out)+"\n",
        encoding="utf-8",
    )
if __name__=="__main__":
    main()
