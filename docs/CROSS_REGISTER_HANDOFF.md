# Cross-Register Crystallization Handoffs

Long-lived branches are intentionally pruned to their own function. They must not be merged directly as full trees.

## Functional edge graph

```text
split/arcane-magics
→ split/eclipsis
→ split/minerva
→ split/venus
→ split/ofe
→ main
```

Semantics:

```text
religion / past
→ math & logics / spirit
→ engineering / body
→ Self & World / model
→ science / future
→ routing map / territory
```

## Handoff construction

A handoff branch is created **from the target branch**, then the source branch is recorded as a second parent using an `ours` merge before explicit residue is admitted.

```text
target HEAD T
source HEAD S

checkout T
git merge --no-ff -s ours --no-commit S
add provenance/historical/handoffs/<id>.json
add ONLY explicitly admitted residue
commit

result H has parents [T, S]
tree(H) = target tree + admitted residue
```

Thus:

```text
source trajectory is remembered
AND
source pruning does not delete target-local state
```

## Handoff names

```text
handoff/arcane-to-eclipsis/<id>
handoff/eclipsis-to-minerva/<id>
handoff/minerva-to-venus/<id>
handoff/venus-to-ofe/<id>
handoff/ofe-to-root/<id>
```

## Authority fence

```text
parent ancestry != content admission
content admission != warrant transfer
merge memory != fusion
```

Each target layer applies its own local admission rule before the next handoff is possible.