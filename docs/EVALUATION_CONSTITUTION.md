# Evaluation Constitution

**Status:** live evaluation protocol  
**Date:** 2026-09-24

Venus-Minerva is not evaluated by one prestige score. The repository spans formal methods, developmental learning, research agency, memory, epistemic governance, world modeling, and cross-register research. Strength on one axis cannot silently substitute for another.

## 1. Evaluation vector

Report at least these axes separately:

| Axis | Question |
|---|---|
| **Capability** | Can the system solve external tasks? |
| **Generalization** | Does competence transfer to unfamiliar tasks/domains? |
| **Development** | Does later Venus improve because earlier Venus existed? |
| **Learner ownership** | Which developmental functions are actually Venus-owned? |
| **Epistemic integrity** | Are evidence, provenance, abstention, and claims correctly bound? |
| **Memory / continual learning** | Does retained state causally alter useful future behavior without destructive regression? |
| **Research competence** | Can it choose, execute, interpret, and revise real research episodes? |
| **Efficiency** | What tokens, compute, time, money, memory, data, and interactions buy the result? |
| **Replication** | Can an outside party reproduce the result? |
| **Governance / robustness** | Does the system survive failure, evaluator pressure, and adversarial conditions without laundering warrant? |

No aggregate "AGI score" is admitted without a separately preregistered definition and promotion rule.

## 2. Core experiment law

For every benchmark or native Venus discriminator:

```text
claim
-> strongest relevant comparator
-> fixed budget / affordances
-> hidden or held-out task where possible
-> preregistered success + failure + WITHHOLD conditions
-> execution
-> independent scoring
-> full cost accounting
-> causal ablation
-> disposition
```

## 3. Required matched controls

Where the claim is architectural rather than model-level, include:

- same foundation model with Venus vs without Venus;
- parent vs successor;
- claimed machinery present vs ablated;
- simplest mature substitute;
- matched tools/information;
- matched or explicitly modeled expenditure;
- fixed benchmark version;
- repeated seeds/confidence intervals where stochastic;
- no post-exposure threshold or prompt repair;
- raw failures retained.

## 4. Causal developmental gain

A successor score alone does not establish self-improvement.

Measure:

```text
raw gain
= performance(successor) - performance(parent)

causal machinery gain
= performance(successor)
  - performance(successor with claimed change ablated)

transfer gain
= heldout(successor) - heldout(parent)

durable gain
= later competence
  while preserving declared earlier competence/regression bounds
```

The strongest Venus-specific result would be repeated positive causal machinery gain over multiple successors on unfamiliar held-out tasks.

## 5. Ownership ledger

For each developmental episode, mark the owner of:

```text
target selection
question formation
rival/comparator selection
discriminator
evidence budget
query/experiment construction
tool execution
evaluation
claim binding
machinery modification
promotion
next-target selection
```

Allowed owner labels:

`HOST`, `VENUS`, `WORLD`, `INDEPENDENT_EVALUATOR`, `MIXED`.

An ownership percentage may be shown as a visualization, but authority remains dependency-level rather than scalar.

## 6. Cost surface

Record at minimum:

- wall-clock time;
- model tokens;
- API / monetary cost;
- accelerator/CPU time where known;
- persistent memory footprint;
- external data accessed;
- tool calls / environment actions;
- retries / branches;
- human interventions;
- benchmark-specific compute budget.

Prefer performance-vs-expenditure curves to one cherry-picked operating point.

## 7. Benchmark families

The living registry should cover, where relevant:

- abstract adaptation: ARC-AGI;
- long-horizon autonomy: METR Time Horizon / HCAST;
- research engineering: RE-Bench;
- paper replication: PaperBench;
- ML engineering: MLE-Bench or current successor;
- coding/software work: SWE-bench / SWE-Lancer or current successors;
- terminal / computer use: TUA-Bench, OSWorld, or current successors;
- lifelong learning: SkillFlow / current sequential-skill benchmarks;
- long-term memory: LongMemEval-V2 or current successors;
- causal science: CausalGame or current successors;
- mathematical research/proof: FrontierMath / Open Problems, proof evaluation/formal theorem tasks;
- world modeling/embodiment: current physical-prediction and action-conditioned world-model benchmarks.

A benchmark is admitted because it tests a declared axis, not because it is fashionable.

## 8. Venus-native developmental benchmark

The repository also needs a benchmark conventional agent suites usually do not measure:

```text
exact parent P
-> Venus identifies limitation L
-> Venus chooses target T
-> freezes discriminator D
-> proposes consequential machinery change Δ
-> World executes / returns independently
-> successor S
-> hidden held-out evaluation
-> S > P
-> ablate Δ and gain disappears
-> S chooses next target
-> repeat
```

Promotion levels:

1. one bounded causal improvement;
2. repeated improvement in one task family;
3. transfer across unfamiliar families;
4. self-authored changes to increasingly consequential machinery;
5. sustained open-ended improvement under external evaluation.

No level inherits the next.

## 9. Integrity

For important claims prefer sealed/private/post-cutoff evaluation when practical:

```text
commit parent + proposal + threshold
-> seal hidden task/evaluator
-> execute unchanged
-> bind claim dependencies
-> independent score
-> open result
-> preserve PASS / FAIL / WITHHOLD
```

Benchmark contamination, reward hacking, harness effects, grader defects, retries, and version drift are reportable state.

## 10. Reduction / credit interaction

Evaluation may establish that a mature comparator substitutes Venus machinery at task `T`.

That disposition is `SUBSUMED_AT_T` or `MATURE_REDUCTION`.

It does not rewrite project genealogy. See `docs/CREDITS_AND_REDUCTIONS.md`.

## 11. Current repository disposition

The architecture has meaningful bounded developmental evidence.

It does not yet have the matched-budget external benchmark matrix required for capability-SOTA or AGI claims.

That gap is an evaluation obligation, not a reason to understate the engineering results already earned.
