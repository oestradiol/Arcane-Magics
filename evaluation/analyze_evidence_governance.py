#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

BOOLEAN_METRICS = {
    "invalid_promotion",
    "unsupported_claim_or_action",
    "correct_withhold",
    "false_withhold",
    "negative_result_reuse_correct",
    "task_success",
}

ERROR_METRICS = {
    "invalid_promotion",
    "unsupported_claim_or_action",
    "false_withhold",
}

BENEFIT_METRICS = {
    "correct_withhold",
    "negative_result_reuse_correct",
    "task_success",
}


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            raise ValueError(f"{path}:{line_no}: missing string id")
        if rid in out:
            raise ValueError(f"{path}:{line_no}: duplicate id {rid}")
        for metric in BOOLEAN_METRICS:
            if metric not in row or not isinstance(row[metric], bool):
                raise ValueError(f"{path}:{line_no}: {metric} must be boolean")
        out[rid] = row
    return out


def exact_two_sided_binomial(k: int, n: int) -> float:
    """Exact two-sided sign/binomial p-value under p=0.5."""
    if n == 0:
        return 1.0
    probs = [math.comb(n, i) * (0.5 ** n) for i in range(n + 1)]
    observed = probs[k]
    return min(1.0, sum(p for p in probs if p <= observed + 1e-15))


def paired_metric(left: dict[str, dict], right: dict[str, dict], metric: str) -> dict[str, Any]:
    if set(left) != set(right):
        missing_left = sorted(set(right) - set(left))
        missing_right = sorted(set(left) - set(right))
        raise ValueError(f"id mismatch: missing_left={missing_left} missing_right={missing_right}")

    left_better = right_better = ties = 0
    for rid in left:
        a = left[rid][metric]
        b = right[rid][metric]
        if a == b:
            ties += 1
            continue
        if metric in ERROR_METRICS:
            # False is better for errors.
            left_better += int((not a) and b)
            right_better += int(a and (not b))
        elif metric in BENEFIT_METRICS:
            left_better += int(a and (not b))
            right_better += int((not a) and b)
        else:
            raise ValueError(f"unknown metric orientation: {metric}")

    discordant = left_better + right_better
    p = exact_two_sided_binomial(left_better, discordant)
    return {
        "metric": metric,
        "left_better": left_better,
        "right_better": right_better,
        "ties": ties,
        "discordant": discordant,
        "two_sided_exact_p": p,
        "direction": (
            "LEFT_BETTER" if left_better > right_better
            else "RIGHT_BETTER" if right_better > left_better
            else "TIE"
        ),
    }


def holm_two(p1: float, p2: float, alpha: float) -> dict[str, Any]:
    pairs = sorted([("provenance", p1), ("negative_state", p2)], key=lambda x: x[1])
    decisions: dict[str, bool] = {"provenance": False, "negative_state": False}
    first_name, first_p = pairs[0]
    second_name, second_p = pairs[1]
    if first_p <= alpha / 2:
        decisions[first_name] = True
        if second_p <= alpha:
            decisions[second_name] = True
    return {
        "method": "Holm step-down across two mechanism claims",
        "familywise_alpha": alpha,
        "raw_p": {"provenance": p1, "negative_state": p2},
        "reject_null": decisions,
    }


def analyze(paths: dict[str, Path], *, alpha: float) -> dict[str, Any]:
    rows = {cid: load_jsonl(path) for cid, path in paths.items()}
    ids = {frozenset(v) for v in rows.values()}
    if len(ids) != 1:
        raise ValueError("all conditions must score the identical hidden case IDs")

    # Mechanism-local primary endpoints.
    # C removes claim-local provenance; D removes retained-negative state.
    provenance = paired_metric(rows["B"], rows["C"], "invalid_promotion")
    negative = paired_metric(rows["B"], rows["D"], "negative_result_reuse_correct")
    correction = holm_two(
        provenance["two_sided_exact_p"],
        negative["two_sided_exact_p"],
        alpha,
    )

    summary: dict[str, Any] = {}
    for cid, data in rows.items():
        n = len(data)
        summary[cid] = {
            metric: sum(int(row[metric]) for row in data.values()) / n if n else 0.0
            for metric in sorted(BOOLEAN_METRICS)
        }

    return {
        "schema": "Venus.EvidenceGovernancePairedAnalysis.v0.1",
        "n": len(next(iter(rows.values()))) if rows else 0,
        "primary_mechanism_tests": {
            "claim_local_provenance_B_vs_C_invalid_promotion": provenance,
            "retained_negative_state_B_vs_D_negative_reuse": negative,
        },
        "familywise_correction": correction,
        "condition_rates": summary,
        "promotion_authority": False,
        "claim_fence": (
            "This analysis can support bounded mechanism-local causal dispositions only "
            "when the manifest, hidden split, matched budgets, contamination status, "
            "evaluator identity, and mature substitute were frozen before exposure."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    for cid in ("A", "B", "C", "D", "E"):
        p.add_argument(f"--{cid}", required=True, type=Path)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = analyze({cid: getattr(args, cid) for cid in ("A", "B", "C", "D", "E")}, alpha=args.alpha)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
