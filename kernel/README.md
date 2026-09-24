# Venus-Minerva kernel

`kernel/` is the live executable center of the repository. It contains only objects that currently change execution, state reconstruction, governance, learning storage, or custody. Historical implementations, failed branches, and superseded scaffolds live under `provenance/`.

## What the kernel actually does

The live kernel has five concrete responsibilities:

```text
persistent state
-> retain local relational/history state

research routing
-> turn live residuals into bounded questions, rivals, and discriminators

governed action/return
-> separate authorization, execution receipts, external return, and promotion

reconstruction
-> allow implicated machinery to become an explicit revision object

successor custody
-> preserve parentage, provenance, negative branches, and exact state identity
```

Historical project labels such as WorldMirror, RSM/N2, bounded RSI, and CTL compress parts of those responsibilities. They are not required to understand or execute the kernel.

The local center is specified more formally in `VENUS_INCIDENCE_LAW.tex`. `WORLDMIND.md` describes the distributed carrier/coordination target without promoting many networked centers into one global subject.

## Boot

```bash
python -m kernel.runtime.current
```

Boot verifies and hydrates the exact IG10 VMK2 state from a compact hot checkpoint plus two content-addressed cold payloads. It does not replay the 118.8 MB trajectory on every run.

## State layers

- `CURRENT_STATE.md`: runtime/developmental authority boundary.
- `state/`: exact compact runtime checkpoint.
- `development/EDU_CURRENT.json`: later developmental authority overlay.
- `custody/`: exact hashes/manifests for replay assets.
- `runtime/`: generic VMK2, persistent memory, and checkpoint loader.

`runtime/memory.py` stores learned abstractions, residuals, provenance, dependency edges, dispositions, and deterministic checkpoints by content identity. `CONSUMED` preserves the old object and points to its replacement.

Git source and admitted kernel state are Venus-Minerva authority. Canonical remains donor/research/provenance material until explicitly admitted here.
