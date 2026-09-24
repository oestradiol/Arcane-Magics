#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math


def exact_two_sided_binomial_p(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    probs = [math.comb(n, i) * (0.5 ** n) for i in range(n + 1)]
    observed = probs[k]
    return min(1.0, sum(p for p in probs if p <= observed + 1e-15))


def rejection_region(n: int, alpha: float) -> set[int]:
    return {
        k for k in range(n + 1)
        if k > n / 2 and exact_two_sided_binomial_p(k, n) <= alpha
    }


def binom_prob(n: int, k: int, p: float) -> float:
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))


def power_for_discordant_pairs(n_discordant: int, *, win_probability: float, alpha: float) -> float:
    if not (0.5 < win_probability <= 1.0):
        raise ValueError("win_probability must be in (0.5, 1]")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0, 1)")
    region = rejection_region(n_discordant, alpha)
    return sum(
        binom_prob(n_discordant, k, win_probability)
        for k in region
    )


def minimum_discordant_pairs(
    *,
    win_probability: float,
    alpha: float,
    target_power: float,
    max_pairs: int = 10000,
) -> tuple[int, float]:
    if not (0 < target_power < 1):
        raise ValueError("target_power must be in (0, 1)")
    for n in range(1, max_pairs + 1):
        power = power_for_discordant_pairs(
            n, win_probability=win_probability, alpha=alpha
        )
        if power >= target_power:
            return n, power
    raise ValueError("target power not reached within max_pairs")


def plan(
    *,
    win_probability: float,
    discordance_rate: float,
    familywise_alpha: float,
    target_power: float,
) -> dict:
    if not (0 < discordance_rate <= 1):
        raise ValueError("discordance_rate must be in (0, 1]")
    # Conservative first Holm step for two claims.
    per_claim_alpha = familywise_alpha / 2
    n_discordant, attained = minimum_discordant_pairs(
        win_probability=win_probability,
        alpha=per_claim_alpha,
        target_power=target_power,
    )
    total_cases = math.ceil(n_discordant / discordance_rate)
    return {
        "schema": "Venus.PairedPowerPlan.v0.1",
        "assumptions": {
            "conditional_left_win_probability_given_discordance": win_probability,
            "expected_discordance_rate": discordance_rate,
            "familywise_alpha": familywise_alpha,
            "per_claim_conservative_alpha": per_claim_alpha,
            "target_power": target_power,
        },
        "minimum_expected_discordant_pairs": n_discordant,
        "minimum_total_cases_at_expected_discordance": total_cases,
        "attained_power_at_discordant_pair_count": attained,
        "warning": (
            "Planning only. Assumptions must be justified prospectively; "
            "observed hidden results may not be used to retroactively choose them."
        ),
        "promotion_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Prospective power planner for paired Venus mechanism tests.")
    p.add_argument("--win-probability", type=float, required=True,
                   help="P(full Venus wins | pair is discordant), must exceed 0.5")
    p.add_argument("--discordance-rate", type=float, required=True,
                   help="Expected fraction of hidden cases on which paired conditions differ")
    p.add_argument("--familywise-alpha", type=float, default=0.05)
    p.add_argument("--target-power", type=float, default=0.8)
    args = p.parse_args()
    try:
        result = plan(
            win_probability=args.win_probability,
            discordance_rate=args.discordance_rate,
            familywise_alpha=args.familywise_alpha,
            target_power=args.target_power,
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
