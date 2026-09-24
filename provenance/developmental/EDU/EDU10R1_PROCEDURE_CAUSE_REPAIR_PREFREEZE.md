# EDU10R1 — Procedure/Cause Residual Repair Prefreeze

**Date:** 2026-09-24
**Class:** bounded developmental engineering repair; no science/FORM/Root/AGI/consciousness/autonomous-science/unrestricted-semantics/open-ended-RSI promotion
**Parent:** EDU8 self-directed source expansion [1624]
**Development-only negative donor:** EDU10 EPA Air Sensor role-composition failure
**EDU10 status:** non-parent / WITHHOLD

## Measured defect

EDU10's five-way generic role classifier confused a procedural question ("how is X tested/evaluated?") with a causal-mechanism question. The mature lexical comparator was not beaten, and one bounded evidence task had precision 1/3.

## Frozen repair

Retain the entire EDU10 base role model unchanged.

Add one residual discriminator only for the `METHOD`/`MECHANISM` ambiguity:

```text
base five-way question role
→ if role ∈ {METHOD, MECHANISM}:
     generic contrastive PROCEDURE↔CAUSE classifier
→ corrected role
```

The residual is trained only on target-free ordinary examples. No EPA/Air-Sensor terms or held-out-domain words are privileged.

Repair-spec SHA-256: `56df736e76d17a5570736da3c6f827c7a64376b08a31bf0de41a38374c033bb6`.

## Held-out selection

Only after this prefreeze, acquire one **fresh official U.S. public-health/science source family** not used in EDU1–EDU10. It must expose at least:
- a method/procedure passage,
- a result/finding passage,
- at least two same-topic distractor passages.

Source identity/excerpts and hidden gold are frozen before learner scoring.

## Frozen retrieval

The EDU10 retrieval formula and selection threshold remain unchanged:

```text
score = 0.55 * lexical_topic_similarity
      + 0.45 * P(document_role = corrected_question_role)

select score >= max(0.12, 0.65 * max_score), up to 3 excerpts
```

## Gates

PASS requires:
1. proposal before hidden relevance evaluation;
2. repaired role-compositional F1 >= lexical-only F1 on every held-out task;
3. strict F1 improvement on at least one held-out task;
4. full hidden-gold coverage on METHOD and RESULT tasks;
5. precision >= 1/2 on each bounded task;
6. every evidence item source-provenanced;
7. no hidden relevance labels in learner state;
8. ProjectState unchanged;
9. inherited VMK2 roots conserved;
10. exact restart.

## Failure rule

No post-heldout tuning. Any failure preserves EDU10R1 as a negative sibling.

## Claim fence

PASS would establish only bounded transfer of a generic procedure-vs-cause repair into one fresh official source world. It would not establish unrestricted semantics, natural-world generality, autonomous science, AGI, consciousness, or open-ended RSI.
