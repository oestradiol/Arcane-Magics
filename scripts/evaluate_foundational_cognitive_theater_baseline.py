#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kernel.runtime.calibrated_retrieval import LabeledExample, predict

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SEED.json"
DEFAULT_PREFREEZE = ROOT / "kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SURFACE_BASELINE_PREFREEZE.json"


def _examples(seed: dict[str, Any], face: str, *, omit_face: str | None = None) -> list[LabeledExample]:
    rows: list[LabeledExample] = []
    for relation in seed["relations"]:
        rid = relation["relation_id"]
        for candidate_face in seed["faces"]:
            if omit_face is not None:
                if candidate_face == omit_face:
                    continue
            elif candidate_face != face:
                continue
            for i, text in enumerate(relation["surfaces"][candidate_face]["train"]):
                rows.append(
                    LabeledExample(
                        example_id=f"{candidate_face}:{rid}:train:{i}",
                        text=text,
                        label=rid,
                        provenance_id=f"teaching:{candidate_face}:{rid}:{i}",
                    )
                )
    return rows


def _heldout(seed: dict[str, Any], face: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for relation in seed["relations"]:
        rid=relation["relation_id"]
        for text in relation["surfaces"][face]["heldout"]:
            out.append((rid, text))
    return out


def _score(seed: dict[str, Any], method: dict[str, Any], face: str, *, cross_face: bool) -> dict[str, Any]:
    train = _examples(seed, face, omit_face=face if cross_face else None)
    correct=0
    withholds=0
    rows=[]
    for rid, text in _heldout(seed, face):
        out=predict(method, train, text)
        ok=out.label == rid
        correct += int(ok)
        withholds += int(out.label is None)
        rows.append(
            {
                "relation_id":rid,
                "prediction":out.label,
                "status":out.status,
                "correct":ok,
                "neighbors":list(out.neighbors),
                "scores":list(out.scores),
            }
        )
    total=len(rows)
    return {
        "face":face,
        "correct":correct,
        "total":total,
        "accuracy":0.0 if total == 0 else correct/total,
        "withholds":withholds,
        "rows":rows,
    }


def evaluate(seed_path: Path = DEFAULT_SEED, prefreeze_path: Path = DEFAULT_PREFREEZE) -> dict[str, Any]:
    seed=json.loads(seed_path.read_text(encoding="utf-8"))
    pre=json.loads(prefreeze_path.read_text(encoding="utf-8"))
    method=dict(pre["method"])
    method.pop("executor", None)

    native=[_score(seed, method, face, cross_face=False) for face in seed["faces"]]
    cross=[_score(seed, method, face, cross_face=True) for face in seed["faces"]]

    native_correct=sum(x["correct"] for x in native)
    native_total=sum(x["total"] for x in native)
    cross_correct=sum(x["correct"] for x in cross)
    cross_total=sum(x["total"] for x in cross)
    native_accuracy=native_correct/native_total
    cross_accuracy=cross_correct/cross_total
    threshold=float(pre["discriminator"]["surface_baseline_insufficient_if_cross_face_accuracy_below"])

    status=(
        "FAIL_SURFACE_ONLY_CROSS_FACE_INVARIANCE"
        if cross_accuracy < threshold
        else "SURFACE_BASELINE_CLEARS_NUMERIC_THRESHOLD_BUT_NOT_INTERNALIZATION"
    )
    return {
        "schema":"Venus.FoundationalCognitiveTheaterSurfaceBaselineResult.v0.1",
        "issue_ref":seed["issue_ref"],
        "status":status,
        "method":pre["method"],
        "native":{
            "correct":native_correct,
            "total":native_total,
            "accuracy":native_accuracy,
            "withholds":sum(x["withholds"] for x in native),
            "per_face":native,
        },
        "leave_one_face_out":{
            "correct":cross_correct,
            "total":cross_total,
            "accuracy":cross_accuracy,
            "withholds":sum(x["withholds"] for x in cross),
            "per_face":cross,
        },
        "threshold":threshold,
        "interpretation":"Current generic surface retrieval retains much within-face lexical structure but does not reconstruct the relation reliably when a representational theater is withheld. This is a returned baseline residual for richer cognitive-theater learning, not a language or semantic failure claim.",
        "next_residual":"LEARN_RELATIONAL_THEATER_STATE_BEYOND_SURFACE_SIMILARITY",
        "internalization_claim":False,
        "general_language_claim":False,
        "cultural_cognition_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
    }


def main() -> int:
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
