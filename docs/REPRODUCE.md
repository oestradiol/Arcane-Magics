# Reproduce Venus-Minerva

This page separates four different operations that are easy to conflate:

~~~text
repository integrity
!=
runtime replay
!=
formal verification
!=
external scientific/capability replication
~~~

## 1. Reconstruct the current runtime

Requirements: Python 3.12-compatible runtime.

~~~bash
python -m kernel.runtime.current
~~~

This reconstructs and verifies the exact IG10 checkpoint from admitted Git custody.

## 2. Run repository integrity checks

~~~bash
make audit
~~~

This checks the live automated integrity surface: unit/runtime invariants, custody/current-state agreement, Markdown/navigation, historical causal distinctions, issue-to-test coverage, experiment-manifest structure, and release boundaries.

Passing this audit establishes only what those checks test.

## 3. Verify the admitted formal subset

~~~bash
make formal-check
~~~

This checks the current Lean OFE subset, including future-equivalence/setoid structure, test-family monotonicity, sufficient-representation/refinement results, quotient transport, common-refinement sufficiency, separating-family equality, and pulled-back-separator reopening.

Machine-checked correctness of that formal subset does not establish novelty or physical validity.

## 4. Run focused benchmark/invariant checks

Examples:

~~~bash
python -m unittest tests.test_vmk2_invariants
python -m unittest tests.test_historical_regressions
python -m unittest tests.test_edu17r1_benchmark
python -m unittest tests.test_edu17r1_sealed_eval
python -m unittest tests.test_memory_causal_benchmark
~~~

The EDU17R1 and memory benchmarks currently contain public development infrastructure. Public dev performance is not promotion evidence.

## 5. What the repository can currently reproduce

It can reproduce/check:

- exact IG10 runtime reconstruction;
- state-root and custody invariants;
- selected VMK2 governance/reopening invariants;
- persistent memory/custody behavior;
- deterministic finite canonical hashing and digest fixtures;
- preserved EDU16/17/17R1 developmental dispositions;
- historical causal distinctions encoded as regressions;
- issue-to-test ownership;
- the bounded Lean OFE subset;
- benchmark/evaluation harness structure.

It does **not** currently reproduce or establish:

- an exact self-contained EDU16 1703-event runtime replay;
- matched-budget Venus capability superiority;
- autonomous science;
- AGI;
- open-ended recursive self-improvement;
- mathematical novelty;
- QG/physical validity;
- broad independent replication.

Issue #4 owns the EDU16 exact-replay custody gap.

## 6. Sealed external experiments

Matched Venus-vs-baseline experiments should instantiate the repository evaluation contract and preserve:

- exact parent/model/harness;
- tools and information;
- budgets;
- hidden-evaluation custody;
- preregistered PASS/FAIL/WITHHOLD;
- raw trajectories;
- negative/null results;
- evaluator identity;
- no self-granted promotion authority.

The EDU17R1 benchmark provides a concrete sealed-run example under `benchmarks/edu17r1_mention_incidence/`.

## 7. Independent replication

Independent replication requires an outside party or separately controlled process to execute/reconstruct the target under independently typed custody.

Same-project replay, handoff, CI, or reimplementation can be strong reproducibility evidence. They are not automatically independent replication.

See [Evaluation Constitution](EVALUATION_CONSTITUTION.md), [Tests and evidence](TESTS.md), and [Earned Milestones](EARNED_MILESTONES.md).
