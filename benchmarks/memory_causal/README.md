# Memory as Causal Learning Benchmark

Issue #15 asks whether VenusMemory changes later admissible behavior rather than merely storing history.

This benchmark is intentionally sequential:

```text
episode / returned state
-> retained memory condition
-> later task
-> action
```

A storage system earns no learning credit merely because the earlier episode can be retrieved. The scored question is whether the retained state causes the later action to respect the current rule, revocation, negative result, or premise boundary.

## Public development split

`dev.jsonl` is public and therefore **not promotion evidence**. It exercises:
- stale rule replacement;
- revocation;
- negative-result reuse;
- consumed/superseded history;
- premise awareness;
- provenance-sensitive action;
- conflicting updates;
- abstention when no lawful current rule exists.

## Required matched conditions

At minimum:

1. VenusMemory/full retained structure;
2. raw append-only replay;
3. equal-size recent context;
4. summary memory;
5. simple retrieval/RAG;
6. no memory.

Ablate separately:
- parent/dependency edges;
- dispositions;
- residuals;
- negative branches;
- provenance;
- replacement/consumption relations.

## Metrics

- later task success;
- stale-action rate;
- revoked-action rate;
- false permission rate;
- correct abstention;
- negative-result reuse;
- cost / tokens / latency;
- improvement over sequence index.

## Claim fence

A synthetic sequential benchmark can establish a bounded causal memory effect. It does not by itself establish general lifelong learning.
