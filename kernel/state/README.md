# Runtime state

This directory contains the **admitted persisted VMK2 snapshot** used by `kernel.runtime.current`.

For the architecture, see [WorldMirror VM](../../docs/WORLDMIRROR_VM.md).

## Layout

```text
kernel/state/
├── IG10_HOT_CHECKPOINT.json
└── cold/
    ├── r198-developmental-state.json
    └── u3r2__text-ingress.json
```

The hot checkpoint contains the frequently reconstructed snapshot plus descriptors for large cold objects.

## Hydration law

```text
hot checkpoint
+ cold JSON payloads
→ verify cold payload SHA-256
→ verify each StateObject root
→ reconstruct original snapshot ordering
→ verify whole snapshot digest
→ hydrate VMK2
→ verify current IG10 state root
```

Manual edits that do not also satisfy the expected content/state roots fail closed.

## Formats

Current authoritative checkpoint storage is deterministic JSON. The separate `VenusMemory` semantic-memory subsystem uses SQLite plus content-addressed compressed blobs; see [runtime memory](../runtime/memory.py).

## Do not confuse

```text
checkpoint != whole developmental history
checkpoint != Git provenance
checkpoint != VenusMemory
checkpoint != external World
```
