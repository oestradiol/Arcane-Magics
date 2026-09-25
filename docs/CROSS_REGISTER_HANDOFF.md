# Cross-Register Crystallization Handoffs

Long-lived layer branches are intentionally pruned to their native current state. Therefore they must **not** be merged directly into one another as ordinary full-tree branches.

## Why

```text
split/ofe intentionally lacks Minerva runtime
split/venus intentionally lacks Root-only memory surfaces

direct git merge
-> may interpret deliberate absence as deletion
-> destroys target-local current state
```

## Handoff construction

A cross-register integration branch is created **from the target**, then records the source branch as a second parent using an `ours` merge before any admitted content is added.

```text
target HEAD T
source HEAD S

checkout T
git merge --no-ff -s ours --no-commit S
add provenance/historical/handoffs/<id>.json
add ONLY explicitly admitted source residue
commit

result H has parents [T, S]
tree(H) = target tree + admitted residue
```

This gives us both things we need:

```text
source trajectory is remembered in Git ancestry
AND
source branch pruning does not delete target-local state
```

## Naming

```text
handoff/ofe-to-venus/<id>
handoff/eclipsis-to-venus/<id>
handoff/arcane-to-venus/<id>
handoff/minerva-to-venus/<id>
handoff/venus-to-root/<id>
```

## Causal order

```text
ground/Minerva source
-> target-based handoff to Venus
-> Venus Scientific Future gate
-> independent/evaluator return
-> target-based handoff from Venus to Root
-> Root memory integration
```

## Authority fence

Recording a source commit as a merge parent preserves memory; it does not promote all source claims or files.

```text
parent ancestry != content admission
content admission != warrant transfer
merge memory != fusion
```
