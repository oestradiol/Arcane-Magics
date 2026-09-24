# Venus-Minerva Prototype Current State

**Date:** 2026-09-24

## Authority / ancestry orientation

```text
historical public executable carrier  R194
crystallized R-line predecessor       R226
post-R226 developmental ancestry      S/SM → CTL-K1 → WM1R1 → U* → RB1 → IG1…IG10
current raising/research lineage      IG10 → EDU*
current positive developmental head   EDU16 [1703]
```

R194 is not the current prototype. R226 is the settled R-line crystallization boundary, and no R227 was minted. Post-R226 development intentionally moved into separate namespaces. See `DEVELOPMENTAL_LINEAGE.md`.

## Positive developmental mainline

```text
EDU16
records  1703
head     6e02302abafb9f31ee5cb1b6f6d69a4e5c1e750371f99c4ee640f259f228c81e
sha256   bde664e4bc2c45bc961720fc83e907a9c6b09ce581ccdfb61b8fb7bf5897e414
verdict  PASS_BOUNDED_LEARNER_OWNED_WORLD_FEED_POLICY
```

EDU16 transferred the World-feed sampling/query policy into bounded learner ownership while leaving World execution and independent evaluation external.

## Preserved negative branch

```text
EDU17
initial result:
PASS_BOUNDED_LEARNER_OWNED_FEED_EXECUTION_WITH_PARTIAL_RESOLUTION

later claim-local provenance audit:
INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE
```

EDU17 is preserved development evidence and is not promoted into ancestry.

## Current repair branch

```text
EDU17R1
WITHHOLD_BEFORE_CLAIM_BINDING_EVALUATION
```

Measured residual:

```text
uncertainty-marker mention
!=
object-level unresolved incidence
```

## Executable / custody distinction

The old R194 carrier is preserved under `provenance/historical-runtime/R194/` for historical replay/ablation. It is no longer part of the live prototype surface.

The later R226 crystallization and post-R226 developmental line are recorded in `DEVELOPMENTAL_LINEAGE.md`, while large replay journals and handoff archives are hash-addressed custody rather than ordinary Git-tracked binaries.

Live infrastructure now also includes `venus_memory.py`, a content-addressed persistent store for learned abstractions, residuals, provenance, dependency edges, dispositions, and deterministic checkpoints.

A receipt is not a runtime; a runtime is not independent return; a historical public carrier is not the current prototype.

## Broad claim fence

The repository does not establish AGI, consciousness, unrestricted semantic understanding, natural-world generality, autonomous science, open-ended RSI, or independent external replication.
