# Minerva Global Repository Operation

Minerva is branch-local in claim authority but **repository-global in operational visibility**.

It needs access to:

- sibling branch heads and diffs;
- merge ancestry;
- `provenance/historical/`;
- GitHub Actions state;
- evaluation/workflow configuration;
- cross-branch dependency and authority maps;
- current Root/Venus state;
- its own self/world model and developmental receipts.

This is not authority collapse.

```text
can inspect != can claim
can route != can authorize
can operate on repository != owns every register
```

## Repository as modeled World

The repository is one important engineered environment through which Minerva receives and acts on returned state.

```text
Git DAG
+ branch heads
+ PR review
+ CI / Actions
+ provenance
→ repository-side World model
→ Minerva inference / judgment / proposal
```

External World remains larger than Git.

## PR integration

A merged PR changes the shared historical carrier. Minerva may therefore use merge ancestry as developmental memory, but must preserve:

```text
author(branch)
!= reviewer
!= merger
!= evaluator
!= external return
```

GitHub Actions may execute checks and transformations; successful execution is not independent verification unless the relevant evaluator/source independence has actually been established.
