# Adaptive Promotion Pressure Test

This public synthetic benchmark supports issue #41.

It isolates one narrow failure mode:

```text
many noisy successor proposals
+ reuse of one acceptance surface
+ naive "keep if observed score rose"
-> false successor commits
```

It does not model Venus cognition or prove that any Venus gate is statistically valid.

## Public null simulation

Default frozen configuration:

- 1,000 independent synthetic lineages;
- 100 candidate proposals per lineage;
- every candidate has true improvement `delta = 0`;
- observed validation delta is unit Gaussian noise;
- naive acceptance: observed delta > 0;
- comparison: one-sided Bonferroni familywise alpha 0.05.

Frozen seed 41 result:

| Gate | False commit / proposal | Lineages with >=1 false commit |
|---|---:|---:|
| naive score rise | 0.49915 | 1.000 |
| Bonferroni one-sided | 0.00054 | 0.053 |

The result is stored in `PUBLIC_NULL_RESULT.json` and recomputed by tests.

## What is still required

The claim-bearing experiment remains:

```text
identical candidate stream
-> naive gate
-> current Venus gate
-> strongest mature anytime-valid / multiplicity-aware gate
-> fresh-holdout oracle
-> untouched ID/OOD final evaluation
```

with rejected candidates preserved and cost/replay/regression measured.

## Claim fence

This benchmark establishes only that repeated naive selection over noise is a severe false-promotion pressure. It does not establish self-improvement, a Venus advantage, or a valid production acceptance rule.
