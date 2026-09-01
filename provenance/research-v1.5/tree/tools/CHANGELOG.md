# Changelog

## Unreleased

- removed stale v0.1 governance references from launch-gate and tooling/front-door docs after the v0.2 governance compression
- governance validation now ignores live worktree and generated operational artifacts such as `.git/`, `tools/out/`, and local cache directories
- added a first federated validation-cluster prototype with subsystem-owned reports for root governance, SUF active core, Knowledge, and tooling/release checks
- moved subsystem cluster ownership metadata into machine-readable governance state, with tooling now deriving cluster specs from canonical governance instead of hardcoding them in Python

## `1.1.0` - 2026-04-18

Current tooling snapshot aligned to the `v1.4.0` three-case bounded closure umbrella release.

### Included in this snapshot

- version surfaces aligned to the `v1.1.0` release line
- status-surface validation aligned to the monograph-baseline New Zealand wording and current hosted version
- New Zealand summary parsing made tolerant of the public-ledger wording while keeping the canonical metric checks read-only

## `1.0.1` - 2026-04-02

Current bounded public tooling snapshot inside the umbrella `Research/` repository.

### Included in this snapshot

- direct public status-surface validation for the current hosted release point
- updated NZ and Taiwan route and report tests for the current `38`/`29`/`15` public baseline
- NZ-Taiwan issuing-concentration reporting fixed so tied top issuers render correctly
- documented the tooling-ready validation scope for current `main`
- aligned the tooling backlog to the long-range monograph and bounded-closure phase ladder while keeping docs canonical and tools read-only

## `1.0.0` - 2026-04-02

First bounded public tooling snapshot inside the umbrella `Research/` repository.

### Included in this snapshot

- repository-wide Markdown link validation
- source-registry structure and archive validation
- New Zealand route parsing and published-metric validation
- Taiwan comparator parsing and published-metric validation
- Knowledge package integrity checks
- version-surface validation for the public packages and tools metadata
- release-readiness reporting
