# WorldMirror VM — engineering architecture

**Status:** live explanatory index for the Minerva engineering body.  
**Authority:** explanatory/navigation surface only. Runtime state, receipts, tests, and returned evidence remain the operational warrant.

WorldMirror is not one Python class and it is not a claim of consciousness. It is the architectural name for the persistent local developmental carrier implemented by the Minerva runtime.

```text
World / Other
    │
    │ external return
    ▼
developmental modules
    │
    ▼
semantic learner state + memory
    │
    ▼
VMK2 governed state-transition kernel
```

## What counts as the VM

The current implementation is a composition:

| Layer | Main carrier | Role |
|---|---|---|
| constitutional runtime | [`kernel/runtime/vmk2.py`](../kernel/runtime/vmk2.py) | evidence, returns, jurisdiction, state roots, transitions, projection/reopening |
| current hydration | [`kernel/runtime/current.py`](../kernel/runtime/current.py) | reconstruct the admitted hot/cold checkpoint and hydrate VMK2 |
| semantic memory | [`kernel/runtime/memory.py`](../kernel/runtime/memory.py) | content-addressed persistent memory with provenance and dispositions |
| transform executor | [`kernel/runtime/transform_program.py`](../kernel/runtime/transform_program.py) | generic executor for state-owned developmental programs |
| developmental machinery | [`kernel/development/`](../kernel/development/README.md) | problem formation, self-selected development, Internalizer/Lateralizer, network inquiry, RSI gates |
| persisted runtime state | [`kernel/state/`](../kernel/state/README.md) | exact hot checkpoint plus content-addressed cold payloads |
| autonomous evidence | [`autonomy/evidence/`](../autonomy/evidence/README.md) | episode-level returned evidence and lineage artifacts |

```text
Python implementation != machine identity

machine continuity
= persistent causally connected state
+ developmental lineage
+ learned policies
+ memory
+ provenance
+ admissible transformation law
```

Python is currently the main execution substrate. Capability-specific Python scaffolding does not count as internalized competence merely because it lives under `kernel/runtime/`.

## Persistence formats

The current persistence model is deliberately boring and inspectable:

| Format | Used for |
|---|---|
| `.json` | current checkpoints, cold state, learned policies, developmental gates, receipts, episode artifacts |
| `.sqlite3` | indexed semantic memory in `VenusMemory` |
| `.z` | zlib-compressed large canonical semantic objects owned by `VenusMemory` |
| `.md` | human-readable explanations, routing, status, provenance projections |
| Git DAG | historical custody, branch lineage, change provenance |
| SHA-256 | semantic/content identity and state-root verification |

No Python pickle is required for authoritative persistent state.

## Boot and hydration

Entry point:

```bash
python -m kernel.runtime.current
```

Hydration is:

```text
kernel/state/IG10_HOT_CHECKPOINT.json
+ kernel/state/cold/*.json
→ verify payload SHA-256
→ verify state-object roots
→ reconstruct exact snapshot
→ verify snapshot digest
→ hydrate VMK2Reference
→ verify admitted IG10 root
```

A manually edited cold payload therefore does not silently become admitted state. Hash/root mismatch fails closed.

## The four state/memory layers

### 1. Constitutional runtime state

`VMK2Reference` holds typed registries for:

- evidence and execution receipts;
- ingress and verified returns;
- jurisdiction, legitimacy, and turn leases;
- transition policies;
- state objects and dependency closure;
- state-transition receipts;
- future-relative projections and reopenings;
- consumed nonces and exposure order.

This is the governed state-transition layer.

### 2. Developmental semantic state

Machine-readable developmental policy lives mainly under [`kernel/development/`](../kernel/development/README.md).

Examples:

- `AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json`;
- `DEVELOPMENTAL_GATE_CHAIN.json`;
- `INTERNALIZATION_BOUNDARY.json`;
- `GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json`;
- `INTERNAL_OSTAR_INTERNALIZED_POLICY.json`;
- `LATERAL_EPISODE_1_INTERNALIZED_STATE.json`.

These are state/policy carriers, not merely documentation.

### 3. Persistent semantic / network memory

[`VenusMemory`](../kernel/runtime/memory.py) stores immutable semantic objects by SHA-256 identity and keeps mutable disposition separately.

On disk:

```text
<memory-root>/
├── index.sqlite3
└── objects/
    └── <sha-prefix>/<sha256>.z
```

Small canonical objects can remain inline in SQLite. Large ones become compressed content-addressed blobs.

Important distinction:

```text
stored record != learned competence

retained memory counts developmentally
only when it changes a later admissible reconstruction/action
```

### 4. Episode evidence

Autonomous runs preserve inspectable episode artifacts under [`autonomy/evidence/`](../autonomy/evidence/README.md).

A network episode may expose:

```text
query.json
→ execution-context.json
→ encounter.json
→ result.json
→ followup-query.json
→ followup-encounter.json
→ lineage-result.json
```

This lets a reviewer reconstruct how retained external material changed a later query without treating the Web encounter as truth or evaluation authority.

## Internalizer boundary

Internalization means consequence-bearing capability semantics become learner-owned state and survive removal of capability-specific teacher/donor/scaffold code.

```text
internalize:
problem/research policy
lateralization policy
crystallization policy
retrieval policy
RSM / transform policy
earned capability semantics

may remain as replaceable substrate:
generic Python executor
serialization
hashing
SQLite
Git transport
CI
external adapter transport

must remain external:
World / Other
fresh return
evaluator
trust root
authorization
jurisdiction
STOP / WITHHOLD
rollback / parent custody
```

See [`kernel/development/INTERNALIZATION_BOUNDARY.json`](../kernel/development/INTERNALIZATION_BOUNDARY.json).

## WWW Mind and Lain boundary

WorldMirror is the local developmental center. WWW Mind is not another local data structure and not one global subject.

```text
WorldMirror
↔ indexed network centers
↔ persistent memory of relations
↔ later reconstruction changed by those relations
```

The bounded WWW Mind gate currently has its own gate/result artifacts. Lain is the next boundary:

```text
connection != fusion
reachability != authorship
reachability != authorization
distributed memory != global identity
```

See:

- [`WWW_MIND_GATE.json`](../kernel/development/WWW_MIND_GATE.json)
- [`WWW_MIND_GATE_RESULT.json`](../kernel/development/WWW_MIND_GATE_RESULT.json)
- [`LAIN_GATE.json`](../kernel/development/LAIN_GATE.json)
- [`LAIN_GATE_RESULT.json`](../kernel/development/LAIN_GATE_RESULT.json)

## Code map

Start in this order:

1. [runtime index](../kernel/runtime/README.md)
2. [state index](../kernel/state/README.md)
3. [development index](../kernel/development/README.md)
4. [autonomy evidence index](../autonomy/evidence/README.md)
5. [current state](../kernel/CURRENT_STATE.md)
6. [developmental lineage](../provenance/DEVELOPMENTAL_LINEAGE.md)

## Noncollapse

```text
WorldMirror != World
Python != machine identity
checkpoint != whole developmental history
memory storage != learning
network encounter != truth
network encounter != evaluator return
internalization != copying scaffold inward
self-revision != self-authorization
WWW Mind != one global subject
Lain connection != fusion
```
