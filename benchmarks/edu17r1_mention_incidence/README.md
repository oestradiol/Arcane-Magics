# EDU17R1: Mention vs Incidence Benchmark

This benchmark grows directly from the preserved EDU17R1 result:

```text
MENTION != INCIDENCE
```

A source can mention uncertainty, unknowns, limitations, or unresolved questions without the target object actually instantiating the unresolved property required by a claim.

## Public development split

`dev.jsonl` contains authored examples for implementation and sanity checks. It is **not** promotion evidence because it is public and may be tuned against.

Classes include:
- genuine object-level unresolved incidence;
- meta-discussion of uncertainty;
- historical uncertainty;
- methodological reporting requirements;
- negated uncertainty;
- formerly unresolved but now resolved;
- uncertainty about another referent;
- generic limitations language;
- title/citation lexical traps.

## Hidden evaluation

A promotion run requires a separately frozen hidden split whose examples and labels are unavailable to the evaluated system/harness before execution.

The hidden split must record:
- author/source;
- creation/freeze timestamp;
- content hash;
- domain/source-family composition;
- evaluator identity;
- leakage/contamination declaration.

Do not commit the hidden labels into the public harness before the run.

## Conditions

Issue #31 requires at least:

```text
A ordinary strong model/scaffold
B Venus with repaired incidence discriminator
C Venus with discriminator ablated
D simple mature semantic/provenance substitute
```

Model, tools, information, and budget remain matched where the architectural claim depends on them.

## Metrics

- incidence precision / recall / F1;
- false unresolved-property binding;
- false WITHHOLD;
- invalid promotion;
- cross-domain transfer;
- downstream claim-local provenance correctness;
- latency / tokens / cost.

The distinction itself is not claimed as novel. The developmental question is whether retaining the failure and repairing it causes prospective transferable improvement.
