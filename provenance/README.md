# Public provenance

Public provenance preserves the distinctions required to reconstruct current claims without publishing private archives or treating every historical commit as part of the current release surface.

## What belongs here

- project-origin vs historical-priority distinctions;
- public-safe source maps;
- migration/retype records that materially change current interpretation;
- content hashes or release identifiers where useful;
- historical regression identifiers;
- explicit unknowns and source gaps.

## What does not belong here by default

- raw private archives;
- identifying personal trajectories;
- private participant material;
- full predecessor working trees merely because they existed;
- stale implementation state that no longer changes current reconstruction.

## Git history is a public surface

```text
clean current tree -/-> clean reachable public history
private provenance preservation -/-> public predecessor-history publication
```

A future clean public release must pass a history-sanitation gate. Until then, the current repository history is historical infrastructure, not a claim that every reachable predecessor state was intentionally selected for public preservation.

See [`PUBLIC_HISTORY_POLICY.md`](PUBLIC_HISTORY_POLICY.md).
