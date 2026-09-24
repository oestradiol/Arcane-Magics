#!/usr/bin/env python3
from __future__ import annotations
"""Condition D: ordinary mature k-NN semantic substitute.

Independent implementation of the frozen public-calibration method used by B.
It imports neither Venus runtime nor Venus ownership/provenance machinery.
If D matches B, the semantic mechanism is mature-subsumed at this scope.
"""
import argparse, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEV=HERE/"dev.jsonl"
K=3

def features(text):
    return frozenset(re.findall(r"[A-Za-z0-9]+",text.casefold()))

def jaccard(a,b):
    u=a|b
    return 0.0 if not u else len(a&b)/len(u)

def calibration():
    rows=[]
    for line in DEV.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        rows.append((row["id"],row["text"],row["label"]))
    return tuple(rows)

def predict(train,text):
    target=features(text)
    ranked=sorted(
        ((jaccard(target,features(t)),rid,label) for rid,t,label in train),
        key=lambda x:(-x[0],x[1]),
    )[:min(K,len(train))]
    weights={}
    for score,_,label in ranked:
        weights[label]=weights.get(label,0.0)+score
    if not weights or sum(weights.values())<=0:
        return "withhold"
    best=max(weights.values())
    winners=sorted(k for k,v in weights.items() if abs(v-best)<1e-12)
    return winners[0] if len(winners)==1 else "withhold"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("blind_jsonl")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    train=calibration()
    out=[]
    for line in Path(args.blind_jsonl).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        if "label" in row or "rationale" in row:
            raise ValueError("condition D requires blind rows")
        out.append({"id":row["id"],"prediction":predict(train,row["text"])})
    Path(args.output).write_text(
        "\n".join(json.dumps(x,sort_keys=True) for x in out)+"\n",
        encoding="utf-8",
    )
if __name__=="__main__":
    main()
