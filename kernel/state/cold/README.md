# Cold VMK2 state

Large state objects split out of the hot checkpoint live here.

Each object is referenced by `../IG10_HOT_CHECKPOINT.json` with:

- object identity;
- original position;
- expected state root;
- payload SHA-256;
- dependency information.

`kernel.runtime.current.reconstruct_snapshot()` verifies both the payload hash and the VMK2 state root before reinserting a cold object.

These files are persisted state, not free-form documentation. Editing one without a corresponding admitted checkpoint update should make hydration fail.
