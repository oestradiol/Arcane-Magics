# Architecture

> **Terminology note:** "Federation," "subsystems," and related terms are organizational metaphors describing the repository's structure through systems-engineering vocabulary rather than making ontological claims about the research.

## Purpose

`Research/tools/` is a read-only tooling layer for validating and summarizing research artifacts in `Research/`.

The current public scope still centers on the SUF route work, but now also includes public status-surface checks, Knowledge package checks, version-surface validation, and release-readiness reporting for the full public repo.

## Module boundaries

- `models/`: typed data structures for sources, ledgers, summaries, and validation results
- `parse/`: Markdown parsers for source registry entries, ledger events, and links
- `validate/`: pure validation checks that return structured results
- `reports/`: deterministic read-only summary generation
- `workflows/`: command-level orchestration for combined checks

## Federation and integration rule

`Research/tools/` is one subsystem in a larger federated repository.

That means:

- tooling should stay read-only over the public docs
- package-local truth should remain in the package being validated
- future checks should be grouped near the domain they protect when that keeps ownership clearer
- umbrella workflows may aggregate results, but should not erase local module or package boundaries

If future test clusters are added for multiple packages, the preferred shape is:

- local tests or validators near each package or module family
- stable shared result structures and command interfaces
- optional umbrella orchestration that composes those results without centralizing authorship or truth ownership

## Current federated cluster prototype

The first live prototype now groups validation into subsystem-owned clusters:

- `root-governance`
- `suf-active-core`
- `knowledge-package`
- `tooling-release`

Cluster metadata now comes from `../governance/GOVERNANCE_CORE_v0_2.json`, while tooling code only keeps execution logic and result rendering. That resolves the earlier duplication wall between public subsystem policy and Python-owned cluster metadata without re-expanding governance into multiple near-duplicate files.

## Data flow

1. path resolution from `paths.py`
2. Markdown parsing into typed models
3. validation and metric computation
4. read-only report rendering to `out/`

## Current route assumptions

- New Zealand is the primary validated route
- Taiwan is the current bounded comparator
- route metrics are derived from public Markdown, not an external database
- public status and payoff surfaces are treated as published interfaces and validated as such
- Taiwan comparator files currently live inside the same case directory as the New Zealand route package

## Output rule

The tooling may compute, compare, and report. It may not rewrite public docs.

## Status

`architecture locked for the tooling-ready tranche`
