# Cross-Register Branch Memory

## Constitutional rule

Sibling layers are **not** treated as disposable imports or ignored caches.

```text
branch-local current state
→ reviewed cross-register transformation
→ merge into integrator
→ next integrator state
→ provenance/historical retention
```

The resulting Git DAG is part of the diachronic memory of the repository.

## Why

```text
current presentation != diachronic whole
same current files != same trajectory
```

A later state must be able to reconstruct not only what exists now, but which differentiated branch authored the change, what ancestry it carried, what review transformed it, and what consequences followed.

## Merge semantics

For cross-layer memory-bearing merges, prefer a **merge commit**.

```text
merge commit
= preserves both parent trajectories in the DAG

squash merge
= preserves resulting patch but compresses branch-level commit ancestry

rebase
= rewrites the branch trajectory before integration
```

Squash/rebase may still be used for explicitly disposable or generated work, but should not be the default for a branch whose developmental/provenance trajectory is itself consequential.

## Historical location

Material that is no longer live authority but remains causally relevant belongs under:

```text
provenance/historical/
```

or remains recoverable directly from its Git ancestry.

Do not use `.gitignore` as an epistemic trash can.

## Branch-memory invariant

```text
archive != erase
merge != fusion
shared ancestry != shared authority
historical presence != current authority
```

A merged sibling may remain visible in Root/Venus memory without becoming current authority in another branch.
