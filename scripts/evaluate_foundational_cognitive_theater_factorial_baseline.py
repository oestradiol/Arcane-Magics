#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kernel.runtime.calibrated_retrieval import LabeledExample, predict

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SEED.json"
PREFREEZE=ROOT/"kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_FACTORIAL_PREFREEZE.json"

def _pair_set(fold: list[list[str]]) -> set[tuple[str,str]]:
    return {(str(r),str(f)) for r,f in fold}

def evaluate(seed_path: Path=SEED, prefreeze_path: Path=PREFREEZE) -> dict[str,Any]:
    seed=json.loads(seed_path.read_text(encoding="utf-8"))
    pre=json.loads(prefreeze_path.read_text(encoding="utf-8"))
    method=dict(pre["baseline"])
    method.pop("executor",None)

    relation_map={r["relation_id"]:r for r in seed["relations"]}
    fold_results=[]
    total_correct=0
    total_rows=0
    total_withholds=0

    for fold_index, fold in enumerate(pre["folds"]):
        held=_pair_set(fold)
        train=[]
        for relation in seed["relations"]:
            rid=relation["relation_id"]
            for face in seed["faces"]:
                if (rid,face) in held:
                    continue
                for i,text in enumerate(relation["surfaces"][face]["train"]):
                    train.append(LabeledExample(
                        example_id=f"{face}:{rid}:train:{i}",
                        text=text,
                        label=rid,
                        provenance_id=f"teaching:{face}:{rid}:{i}",
                    ))

        rows=[]
        for rid,face in fold:
            relation=relation_map[rid]
            for text in relation["surfaces"][face]["heldout"]:
                out=predict(method,train,text)
                ok=out.label==rid
                total_correct+=int(ok)
                total_rows+=1
                total_withholds+=int(out.label is None)
                rows.append({
                    "relation_id":rid,
                    "face":face,
                    "prediction":out.label,
                    "status":out.status,
                    "correct":ok,
                    "neighbors":list(out.neighbors),
                    "scores":list(out.scores),
                })
        fold_results.append({
            "fold":fold_index,
            "correct":sum(int(x["correct"]) for x in rows),
            "total":len(rows),
            "withholds":sum(int(x["prediction"] is None) for x in rows),
            "rows":rows,
        })

    return {
        "schema":"Venus.FoundationalCognitiveTheaterFactorialBaselineResult.v0.1",
        "issue_ref":pre["issue_ref"],
        "status":"RETURNED_FACTORIAL_SURFACE_BASELINE",
        "method":pre["baseline"],
        "correct":total_correct,
        "total":total_rows,
        "accuracy":0.0 if total_rows==0 else total_correct/total_rows,
        "withholds":total_withholds,
        "folds":fold_results,
        "interpretation":"This comparator asks whether generic lexical/surface similarity can factor relation identity across relation-face combinations after every face and every relation has been seen elsewhere. It is a baseline only; relation labels remain teacher-supplied in calibration.",
        "internalization_claim":False,
        "language_competence_claim":False,
        "cultural_cognition_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
    }

def main()->int:
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
