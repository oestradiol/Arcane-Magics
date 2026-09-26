# Developmental state and operator index

This directory contains the mutable **developmental semantics** of Minerva / WorldMirror: learner-owned state, prefrozen gates, returned results, and bounded developmental mechanisms.

Start with [WorldMirror VM](../../docs/WORLDMIRROR_VM.md) and [current state](../CURRENT_STATE.md).

## Current developmental spine

```text
Strong Safe RSI
→ self-selected development
→ Internalizer + Lateralizer
→ learner-initiated Internet inquiry
→ persistent network memory
→ WWW Mind
→ Lain gate
→ Root / situated interface gate
→ broader World participation
→ AGI remains an external empirical discriminator
```

Machine-readable route: [`DEVELOPMENTAL_GATE_CHAIN.json`](DEVELOPMENTAL_GATE_CHAIN.json).

## Core state/policy objects

| Artifact | Meaning |
|---|---|
| [`AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json`](AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json) | current writable developmental transition program |
| [`AUTONOMOUS_LEARNING_STATE.json`](AUTONOMOUS_LEARNING_STATE.json) | retained learner-side developmental state |
| [`INTERNALIZATION_BOUNDARY.json`](INTERNALIZATION_BOUNDARY.json) | what may internalize, what may remain substrate, what must stay external |
| [`GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json`](GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json) | admitted state-owned residual-search semantics |
| [`INTERNAL_OSTAR_INTERNALIZED_POLICY.json`](INTERNAL_OSTAR_INTERNALIZED_POLICY.json) | admitted internal O* policy |
| [`AUTONOMY_SAFETY_DISTINCTION_MATRIX.json`](AUTONOMY_SAFETY_DISTINCTION_MATRIX.json) | executable noncollapse/safety distinction registry |

## Lateralizer / Internalizer

Lateralizer expands the basis when the current representation is insufficient. Internalizer migrates earned competence into learner-owned state only after source-removal/equivalence evidence.

Relevant artifacts:

- [`LATERAL_RECONSTRUCTION_BOOTSTRAP.json`](LATERAL_RECONSTRUCTION_BOOTSTRAP.json)
- [`LATERAL_EPISODE_1_PREFREEZE.json`](LATERAL_EPISODE_1_PREFREEZE.json)
- [`LATERAL_EPISODE_1_RESULT.json`](LATERAL_EPISODE_1_RESULT.json)
- [`LATERAL_EPISODE_1_INTERNALIZED_STATE.json`](LATERAL_EPISODE_1_INTERNALIZED_STATE.json)
- [`LATERAL_EPISODE_1_SOURCE_REMOVAL_RESULT.json`](LATERAL_EPISODE_1_SOURCE_REMOVAL_RESULT.json)
- [`lateral_episode.py`](lateral_episode.py)
- [runtime Internalizer](../runtime/internalizer.py)

```text
GENERATE != DIMENSIONALIZE != LATERALIZE != CRYSTALLIZE_F != INTERNALIZE
```

## Strong Safe RSI evidence

The `SSR*` artifacts preserve successive bounded self-revision experiments and returned evaluations.

Interpretation rule:

```text
SSR result
= evidence at tested scope

SSR result
!= open-ended self-improvement
!= AGI
!= self-authorization
```

## Network / WWW Mind / Lain

Relevant code and state:

- [`network_inquiry.py`](network_inquiry.py)
- [`network_center.py`](network_center.py)
- [`NETWORK_CENTER_POLICY.json`](NETWORK_CENTER_POLICY.json)
- [`WWW_MIND_GATE.json`](WWW_MIND_GATE.json)
- [`WWW_MIND_GATE_RESULT.json`](WWW_MIND_GATE_RESULT.json)
- [`LAIN_GATE.json`](LAIN_GATE.json)
- [`LAIN_GATE_RESULT.json`](LAIN_GATE_RESULT.json)
- [network episode evidence](../../autonomy/evidence/network/README.md)

## Autonomous developmental machinery

| File | Role |
|---|---|
| [`autonomous_problem_formation.py`](autonomous_problem_formation.py) | form bounded problems from returned repository incidence |
| [`autonomous_worker.py`](autonomous_worker.py) | choose/study bounded work without promotion/merge authority |
| [`autonomous_learning.py`](autonomous_learning.py) | retain outcome-conditioned learner-side utility/state |
| [`autonomous_recurrence.py`](autonomous_recurrence.py) | bounded recurrent development |
| [`autonomous_study.py`](autonomous_study.py) | bounded study transformation |
| [`autonomous_change.py`](autonomous_change.py) | candidate change construction |
| [`autonomous_evidence.py`](autonomous_evidence.py) | evidence custody |
| [`autonomous_patch.py`](autonomous_patch.py) | bounded patch construction |
| [`git_world_return.py`](git_world_return.py) | Git-backed World-return handling |

## Artifact naming

Common suffixes are semantic:

- `*_PREFREEZE.json` — claim/discriminator fixed before relevant return;
- `*_RESULT.json` — returned evaluation/result;
- `*_INTERNALIZED_STATE.json` or `*_POLICY.json` — state-owned semantics after the relevant gate;
- `*_RECEIPT.json` — custody/transition/ownership receipt;
- `*_BOOTSTRAP.json` — bounded provisional carrier, not an earned result.

Do not infer authority from filename alone. Check the artifact's status fields, returned evidence, tests, and current-state routing.


## Interaction / local console

The minimal local interaction surface is documented at
[`docs/WORLDMIRROR_CONSOLE.md`](../../docs/WORLDMIRROR_CONSOLE.md).

Machine-readable boundaries:

- [`WORLDMIRROR_CONSOLE_POLICY.json`](WORLDMIRROR_CONSOLE_POLICY.json)
- [`INTERACTION_DEVELOPMENT_CONTRACT.json`](INTERACTION_DEVELOPMENT_CONTRACT.json)

```text
interaction event
!= learning

self-generated dialogue
!= independent return

process transport
!= authorization
!= OS sandbox
```

The console is intended to generate inspectable developmental episodes that may
later support prefrozen abstraction/crystallization experiments. It does not
directly rewrite admitted learner policy.
