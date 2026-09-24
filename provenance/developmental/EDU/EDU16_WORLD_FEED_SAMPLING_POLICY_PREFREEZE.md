# EDU16 — Learner-Owned World-Feed Sampling Policy Prefreeze

**Date:** 2026-09-24
**Class:** bounded self-curriculum engineering
**Parent:** EDU15R1 self-preregistration/gate-ownership PASS [1699]

## Measured scaffold

EDU14 proved bounded learner-owned source/problem selection *inside* a six-query feed, but the host supplied all six query strings. The remaining local scaffold is therefore the World-feed sampling/query policy, not World execution itself.

## Ownership audit

Learner-owned: curriculum target selection, gate proposal, problem selection, research-question formation, evidence role/budget, obligation routing.

Candidate host function:
`WORLD_FEED_SAMPLING_POLICY` — internalizable and locally testable.

Constitutionally external:
`WORLD_INTERFACE_EXECUTION`, `INDEPENDENT_EVALUATION`, and authorization beyond read-only research.

## Policy-generation constraints

The learner may use only source families/provenance already encountered in its developmental history plus its own past selection history. The host supplies no new query string.

A valid policy must:
- prefer under-selected source families rather than handpicked preferred answers;
- sample at least three domains;
- generate exact query strings deterministically before World execution;
- preserve official-source provenance;
- allow STOP if no actionable residual is returned;
- preserve all EDU15R1 preregistration gates;
- leave World execution and independent evaluation external.

## Claim fence

PASS establishes only bounded feed-policy/query generation. It does not establish autonomous science, unrestricted semantics, natural-world generality, AGI, consciousness, or open-ended RSI.
