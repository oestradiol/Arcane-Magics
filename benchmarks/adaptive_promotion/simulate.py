#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from statistics import NormalDist


def run_null_simulation(*, seed: int, trials: int, proposals: int, sigma: float, alpha: float) -> dict:
    """Synthetic pressure test for repeated noisy successor proposals with zero true gain.

    This is not a model of Venus cognition. It isolates the statistical fact that
    accepting every observed positive delta under repeated adaptive proposals can
    manufacture false successors.
    """
    rng = random.Random(seed)
    threshold = NormalDist().inv_cdf(1 - alpha / proposals) * sigma

    naive_lineages = corrected_lineages = spending_lineages = 0
    naive_commits = corrected_commits = spending_commits = 0
    for _ in range(trials):
        naive = corrected = spending = 0
        for index in range(1, proposals + 1):
            observed_delta = rng.gauss(0.0, sigma)
            naive += int(observed_delta > 0.0)
            corrected += int(observed_delta > threshold)
            # Anytime-valid alpha-spending schedule: alpha_t = alpha/(t(t+1)).
            # The infinite sum is <= alpha, so optional continuation does not
            # silently spend more than the declared familywise error budget.
            alpha_t = alpha / (index * (index + 1))
            spending_threshold = NormalDist().inv_cdf(1 - alpha_t) * sigma
            spending += int(observed_delta > spending_threshold)
        naive_commits += naive
        corrected_commits += corrected
        spending_commits += spending
        naive_lineages += int(naive > 0)
        corrected_lineages += int(corrected > 0)
        spending_lineages += int(spending > 0)

    total = trials * proposals
    return {
        "seed": seed,
        "trials": trials,
        "proposals_per_lineage": proposals,
        "sigma": sigma,
        "familywise_alpha": alpha,
        "bonferroni_z_threshold": threshold / sigma,
        "naive": {
            "false_commit_rate_per_proposal": naive_commits / total,
            "lineage_with_any_false_commit_rate": naive_lineages / trials,
            "false_commits": naive_commits,
        },
        "bonferroni_one_sided": {
            "false_commit_rate_per_proposal": corrected_commits / total,
            "lineage_with_any_false_commit_rate": corrected_lineages / trials,
            "false_commits": corrected_commits,
        },
        "alpha_spending_anytime": {
            "schedule": "alpha_t = alpha/(t(t+1))",
            "false_commit_rate_per_proposal": spending_commits / total,
            "lineage_with_any_false_commit_rate": spending_lineages / trials,
            "false_commits": spending_commits,
        },
        "promotion_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=41)
    p.add_argument("--trials", type=int, default=1000)
    p.add_argument("--proposals", type=int, default=100)
    p.add_argument("--sigma", type=float, default=1.0)
    p.add_argument("--alpha", type=float, default=0.05)
    args = p.parse_args()
    print(json.dumps(run_null_simulation(
        seed=args.seed, trials=args.trials, proposals=args.proposals,
        sigma=args.sigma, alpha=args.alpha,
    ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
