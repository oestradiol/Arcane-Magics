# Runtime index

This directory contains the **generic execution substrate** of the Minerva / WorldMirror engineering body.

For the whole architecture, start at [WorldMirror VM](../../docs/WORLDMIRROR_VM.md).

```text
runtime/
= governed execution + hydration + storage + generic learned-policy interpreters

runtime/
!= all learner semantics
!= World / Other
!= promotion authority
```

## Files by responsibility

| File | Responsibility |
|---|---|
| [`vmk2.py`](vmk2.py) | governed state-transition kernel: evidence, returns, jurisdiction, state roots, transition receipts, projections/reopening |
| [`current.py`](current.py) | reconstruct and hydrate the admitted hot/cold runtime snapshot |
| [`memory.py`](memory.py) | persistent content-addressed semantic memory: SQLite index + compressed large objects |
| [`transform_program.py`](transform_program.py) | generic data-driven TransformProgram executor |
| [`internalizer.py`](internalizer.py) | source-removal/internalization receipts and O*/Anti-Minerva boundary checks |
| [`internalized_search.py`](internalized_search.py) | generic execution of admitted internalized search state |
| [`internal_ostar.py`](internal_ostar.py) | generic execution of admitted internal O* policy |
| [`induced_policy.py`](induced_policy.py) | execute state-owned induced policies |
| [`bounded_recurrence.py`](bounded_recurrence.py) | bounded recurrence execution |
| [`calibrated_retrieval.py`](calibrated_retrieval.py) | bounded retrieval/calibration substrate |
| [`token_knn.py`](token_knn.py) | small generic token-neighborhood mechanism |
| [`auth.py`](auth.py) | runtime authorization helpers |
| [`canonical.py`](canonical.py) | canonical serialization/hash helpers |\n| [`interaction_store.py`](interaction_store.py) | raw-first chronological interaction custody backed by VenusMemory |\n| [`process_bridge.py`](process_bridge.py) | optional argv/cwd/timeout process transport; **not** an OS sandbox |\n| [`structured_template_machine.py`](structured_template_machine.py) | generic execution of state-owned structured-template programs |
| [`transform_program_repair_search.py`](transform_program_repair_search.py) | search over TransformProgram repairs |
| [`transform_program_multi_repair.py`](transform_program_multi_repair.py) | bounded multi-repair composition |
| [`transform_program_successor.py`](transform_program_successor.py) | successor TransformProgram construction |

## Persistence boundary

Runtime code is mostly replaceable substrate. Learned capability semantics should live in state/policy objects when internalization is claimed.

```text
generic executor may remain Python
capability-specific teacher/donor dependency may not remain
for an internalized-capability claim
```

See [`../development/INTERNALIZATION_BOUNDARY.json`](../development/INTERNALIZATION_BOUNDARY.json).

## Boot

```bash
python -m kernel.runtime.current
```

The boot path verifies checkpoint and cold-state digests before hydration.

## Noncollapse

```text
execute != authorize
execute != verify
Python module != internalized competence
runtime state != external World
receipt != return
```
