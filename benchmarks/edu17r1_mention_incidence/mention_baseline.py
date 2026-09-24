#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

TRIGGERS = re.compile(r"\b(unknown|uncertain|uncertainty|unresolved|not known|cannot rule out|limitations?)\b", re.I)

def predict(text: str) -> str:
    return "incidence" if TRIGGERS.search(text) else "non_incidence"

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("dev.jsonl")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    tp=fp=tn=fn=0
    for row in rows:
        pred=predict(row["text"])
        gold=row["label"]
        tp += pred=="incidence" and gold=="incidence"
        fp += pred=="incidence" and gold=="non_incidence"
        tn += pred=="non_incidence" and gold=="non_incidence"
        fn += pred=="non_incidence" and gold=="incidence"
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    print(json.dumps({"n":len(rows),"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":precision,"recall":recall,"f1":f1},indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
