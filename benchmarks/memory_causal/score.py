#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

def load(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: score.py GOLD.jsonl PREDICTIONS.jsonl")
        return 2
    gold={r["id"]:r for r in load(Path(sys.argv[1]))}
    pred={r["id"]:r for r in load(Path(sys.argv[2]))}
    missing=sorted(set(gold)-set(pred))
    extra=sorted(set(pred)-set(gold))
    if missing or extra:
        print(json.dumps({"error":"id mismatch","missing":missing,"extra":extra},indent=2))
        return 1
    correct=0
    by_class={}
    for rid,g in gold.items():
        p=pred[rid].get("action")
        ok=p==g["gold"]
        correct+=int(ok)
        slot=by_class.setdefault(g["class"],{"n":0,"correct":0})
        slot["n"]+=1
        slot["correct"]+=int(ok)
    out={"n":len(gold),"correct":correct,"accuracy":correct/len(gold) if gold else 0.0,"by_class":by_class}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
