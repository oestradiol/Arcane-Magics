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

    naive_lineages = corrected_lineages = 0
    naive_commits = corrected_commits = 0
    for _ in range(trials):
        naive = corrected = 0
        for _ in range(proposals):
            observed_delta = rng.gauss(0.0, sigma)
            naive += int(observed_delta > 0.0)
            corrected += int(observed_delta > threshold)
        naive_commits += naive
        corrected_commits += corrected
        naive_lineages += int(naive > 0)
        corrected_lineages += int(corrected > 0)

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
