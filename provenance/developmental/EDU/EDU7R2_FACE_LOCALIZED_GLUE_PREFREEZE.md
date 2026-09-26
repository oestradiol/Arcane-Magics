# EDU7R2 — Face-Localized Glue Prefreeze

**Date:** 2026-09-24
**Class:** bounded developmental-engineering representation test
**Parent:** EDU6R1 [1575]
**Preserved negative siblings:** EDU7, EDU7R1

## Trigger

EDU7R1 localized remaining failures to cross-talk between correct partial role classifiers when every classifier consumed the entire multi-clause scenario. The next test changes no learned semantic bank. It changes only the representation path:

```text
whole scenario
→ generic clause segmentation
→ each face evaluates each clause independently
→ each face inhabits the clause yielding its strongest supported local classification
→ face states are glued into one disposition
```

This is the neutral engineering form of the donor document's `face-relative state → Glue` construction.

## Frozen constraints

- Reproduce EDU7R1 face models exactly.
- No additional training examples.
- No project/donor labels enter the classifiers.
- Clause segmentation is punctuation-only and contains no semantic rules.
- For each face, choose the clause with maximum classifier confidence; ties use source order.
- Preserve EDU7 and EDU7R1 as negative siblings.
- Claim-bearing evaluation uses fresh H31–H44 only.
- Earlier heldouts are regression diagnostics only.

## Comparators

```text
M0  whole-scenario factor inference [EDU7R1 representation]
M1  face-localized clause inference + Glue
M2  opaque neutral graph with identical M1 mechanics
```

PASS requires M1 to improve over M0 on fresh H31–H44, preserve receipt/return and description/authorization noncollapse, remain consequence-equivalent to M2 under opaque relabeling, conserve ProjectState/pre-existing VMK2 roots, and restart exactly.

## Claim fence

A PASS would support a bounded causal benefit for **face-localized partial-state inference before typed gluing**. It would not privilege Polyhedral names, establish consciousness/AGI, or promote THEOPHEN/PHYS claims.
