#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from math import comb
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def load_local(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCORE = load_local("edu17r1_score_module", HERE / "score.py")


def exact_one_sided_mcnemar(b_only: int, c_only: int) -> float:
    n = b_only + c_only
    if n == 0:
        return 1.0
    return sum(comb(n, k) for k in range(b_only, n + 1)) / (2 ** n)


def load_keyed(path: Path) -> dict[str, dict[str, Any]]:
    return SCORE.keyed(SCORE.load_jsonl(path), path)


def paired_accuracy_counts(
    gold_path: Path,
    b_path: Path,
    c_path: Path,
) -> dict[str, int]:
    gold = load_keyed(gold_path)
    b = load_keyed(b_path)
    c = load_keyed(c_path)
    if set(gold) != set(b) or set(gold) != set(c):
        raise ValueError("paired comparison requires identical IDs for gold, B, and C")

    b_only = c_only = both_correct = both_wrong = 0
    for rid, grow in gold.items():
        label = grow.get("label")
        b_correct = b[rid].get("prediction") == label
        c_correct = c[rid].get("prediction") == label
        if b_correct and c_correct:
            both_correct += 1
        elif b_correct:
            b_only += 1
        elif c_correct:
            c_only += 1
        else:
            both_wrong += 1
    return {
        "b_only_correct": b_only,
        "c_only_correct": c_only,
        "both_correct": both_correct,
        "both_wrong": both_wrong,
    }


def adjudicate(
    gold_path: Path,
    manifest_path: Path,
    prediction_paths: dict[str, Path],
    analysis_plan_path: Path,
) -> dict[str, Any]:
    plan = json.loads(analysis_plan_path.read_text(encoding="utf-8"))
    required = {"A", "B", "C", "D"}
    if set(prediction_paths) != required:
        raise ValueError(f"condition set must be exactly {sorted(required)}")

    scores = {
        cid: SCORE.score(gold_path, prediction_paths[cid], manifest_path)
        for cid in sorted(required)
    }

    paired = paired_accuracy_counts(gold_path, prediction_paths["B"], prediction_paths["C"])
    p_value = exact_one_sided_mcnemar(
        paired["b_only_correct"],
        paired["c_only_correct"],
    )
    alpha = float(plan["primary_endpoint"]["alpha"])
    b = scores["B"]
    c = scores["C"]
    d = scores["D"]

    worsens_accuracy = b["accuracy"] < c["accuracy"]
    worsens_binding = (
        b["false_unresolved_binding_rate"]
        > c["false_unresolved_binding_rate"]
    )
    worsens_withhold = b["false_withhold_rate"] > c["false_withhold_rate"]

    if worsens_accuracy or worsens_binding or worsens_withhold:
        disposition = "FAIL_REPAIR"
    elif (
        paired["b_only_correct"] > paired["c_only_correct"]
        and p_value <= alpha
    ):
        disposition = "PASS_BOUNDED_REPAIR"
    else:
        disposition = "WITHHOLD_INSUFFICIENT_DISCRIMINATION"

    mature_candidate = (
        d["accuracy"] >= b["accuracy"]
        and d["false_unresolved_binding_rate"] <= b["false_unresolved_binding_rate"]
        and d["false_withhold_rate"] <= b["false_withhold_rate"]
    )

    return {
        "schema": "Venus.EDU17R1MentionIncidenceAdjudication.v0.1",
        "analysis_plan_schema": plan.get("schema"),
        "scores": scores,
        "paired_B_vs_C": {
            **paired,
            "test": "one_sided_exact_mcnemar_binomial",
            "p_value": p_value,
            "alpha": alpha,
        },
        "safety": {
            "B_accuracy_not_worse_than_C": not worsens_accuracy,
            "B_false_binding_not_worse_than_C": not worsens_binding,
            "B_false_withhold_not_worse_than_C": not worsens_withhold,
        },
        "repair_disposition": disposition,
        "mature_substitute": {
            "candidate_not_worse_than_B_on_declared_metrics": mature_candidate,
            "final_reduction_requires_matched_cost_and_execution_conditions": True,
        },
        "promotion_authority": False,
        "claim_fence": (
            "This adjudicates only the prefrozen bounded benchmark. "
            "It does not establish learner ownership or developmental promotion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Adjudicate sealed EDU17R1 A/B/C/D predictions.")
    parser.add_argument("gold", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--A", type=Path, required=True)
    parser.add_argument("--B", type=Path, required=True)
    parser.add_argument("--C", type=Path, required=True)
    parser.add_argument("--D", type=Path, required=True)
    parser.add_argument("--analysis-plan", type=Path, default=HERE / "analysis_plan.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        result = adjudicate(
            args.gold,
            args.manifest,
            {"A": args.A, "B": args.B, "C": args.C, "D": args.D},
            args.analysis_plan,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
