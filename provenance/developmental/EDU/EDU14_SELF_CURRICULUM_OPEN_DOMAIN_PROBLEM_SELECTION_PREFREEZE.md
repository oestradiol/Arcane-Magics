# EDU14 — Self-Curriculum Open-Domain Problem Selection Prefreeze

**Date:** 2026-09-24
**Class:** bounded developmental/self-curriculum execution
**Parent:** EDU13 self-curriculum target-generation PASS [1676]
**Self-selected target:** `SELF_CURRICULUM_OPEN_DOMAIN_PROBLEM_SELECTION`

## World feed

The external interface executes six fixed, domain-heterogeneous official-source queries. For each query, the first relevant official-page result is admitted without host semantic reranking.

Feed-rule SHA-256: `b4698510489d3c0d694ef8dfde7b2fb6d10c0fbe7bc9ee6ba378891feeadd095`

The learner receives only source identity/provenance plus returned text. No teacher question, target source, relevance label, or project vocabulary is supplied.

## Learner operation

For each feed item, using inherited ordinary problem-formation/research machinery:

```text
source return
→ detect explicit unresolved / uncertain / decision-relevant residual
→ score residual
→ stable choose highest actionable residual
→ formulate research question
→ predict evidence role + budget
→ serialize exact query/request
→ commit product
```

If no item is actionable, STOP.

The learner owns the selection. World execution and independent evaluation remain external.

## Primary gates

- feed acquired only after this freeze;
- all six feed queries executed unchanged;
- no host semantic reranking;
- learner source/problem selection committed before evaluation;
- chosen source contains the claimed residual;
- question is answerable in principle and not just a headline restatement;
- request preserves the residual;
- unsupported outcome WITHHOLDs;
- no project labels as scoring key;
- ProjectState unchanged;
- inherited VMK2 roots conserved;
- exact restart.

## Comparator

Teacher-selected problem on the identical feed using the same downstream tools. The learner need not beat an omniscient selector; the test is whether it can select a valid, consequence-bearing problem without one.

## Claim fence

PASS would establish bounded self-curriculum/open-domain problem selection on one heterogeneous feed. It would not establish autonomous science, natural-world generality, unrestricted semantics, AGI, consciousness, or open-ended RSI.
