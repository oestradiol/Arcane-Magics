# Public provenance

Public provenance preserves the source relations needed to reconstruct current claims without publishing private archives or treating every historical commit as part of the current release surface.

## What belongs here

- project-origin, participant-return, historical-priority, later-constraint, convergence, formal-inheritance, publication-freeze, and model/tool distinctions where they matter publicly;
- public-safe source maps;
- migration or retype records that materially change current interpretation;
- content hashes or release identifiers where useful;
- historical regression identifiers;
- explicit unknowns and source gaps.

See [Credit relations](../knowledge/credit/CREDIT_RELATIONS.md) for the public taxonomy and [Operator Genealogy](../knowledge/evidence/OPERATOR_GENEALOGY.md) for comparative recurrence.

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

The public-history gate was closed at a scoped release-ref level on 1 September 2026. The audited public tree was placed on a fresh parentless root; all maintained non-main branches were deleted; no tags remain. Public history from the maintained release refs therefore begins at the sanitized Venus-Minerva root rather than at the predecessor Research DAG.

This does not claim deletion of provider-managed pull-request refs, Actions records, caches, or retention objects. Those are platform surfaces outside the maintained release-ref graph. Any future maintained branch or tag that reconnects backstage/predecessor history reopens the gate.

See [PUBLIC_HISTORY_POLICY.md](PUBLIC_HISTORY_POLICY.md).
