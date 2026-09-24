#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from mention_baseline import predict

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
            raise ValueError("condition A requires blind rows")
        out.append({"id":row["id"],"prediction":predict(row["text"])})
    Path(args.output).write_text(
        "\n".join(json.dumps(x,sort_keys=True) for x in out)+"\n",
        encoding="utf-8",
    )
if __name__=="__main__":
    main()
