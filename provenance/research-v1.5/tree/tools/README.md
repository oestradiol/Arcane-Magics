# Research Tools

## Purpose

This package provides reproducible, read-only research-support tooling for the `Research/` repository.

Current snapshot: `1.1.0` dated `2026-04-18`.

Hosted package URL: [oestradiol/Research/tree/main/tools](https://github.com/oestradiol/Research/tree/main/tools)

The current scope covers Structured Unity Framework route and source work, status-surface consistency, Knowledge package integrity, version-surface consistency, and repository-wide Markdown link validation across `Research/`. It validates current public research surfaces and generates deterministic read-only reports for human review. It is part of the repo-complete trust layer, not an adjudicator of the framework's truth.

This package does **not**:

- rewrite public docs automatically
- make interpretation decisions for the research
- bypass human validation

## Current scope

Current support includes:

- Markdown link validation across `Research/`
- source-registry shape and archive validation
- New Zealand route parsing and consistency checks
- Taiwan bounded-comparator parsing and consistency checks
- public status-surface mismatch checks against current route and comparison metrics
- Knowledge package entry/index integrity checks
- version, changelog, and citation-surface consistency checks
- governance consistency validation (registry integrity, version consistency)
- integrity manifest generation from CURRENT_SURFACES_REGISTRY
- release-readiness reporting
- deterministic read-only report generation

## Workflow model

- Nix provides the interpreter and base toolchain.
- `.venv` lives inside this directory and is local-only.
- Generated outputs live under `out/`.
- Public docs remain human-authored.

## Setup

```bash
cd Research/tools
nix develop
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-build-isolation -e .[dev]
ruff check .
pytest
```

## Commands

```bash
research-tools validate links
research-tools validate archives
research-tools validate knowledge
research-tools validate source-registry
research-tools validate versions
research-tools validate status-surfaces
research-tools validate route --route nz
research-tools validate route --route taiwan
research-tools validate all
research-tools validate clusters

research-tools report nz-summary
research-tools report nz-window-comparison
research-tools report nz-lag-surface
research-tools report nz-taiwan-summary
research-tools report taiwan-lag-limit
research-tools report taiwan-summary
research-tools report release-readiness
```

## Output policy

- validation commands are read-only with respect to repo-tracked Research docs
- report commands write Markdown under `out/`
- generated outputs are provisional and require human review
- mismatches are reported, not auto-applied

## Federated cluster layer

The tooling now includes a federated validation-cluster layer:

- `root-governance`
- `suf-active-core`
- `knowledge-package`
- `tooling-release`

Use `research-tools validate clusters` to inspect subsystem-owned validation groupings without flattening every check into one undifferentiated run.

Cluster ownership, entry surfaces, source-file groupings, actor classes, and trust order are now derived from `../governance/GOVERNANCE_CORE_v0_2.json`. Python keeps the runner logic, while the public subsystem map lives in the consolidated governance surface instead of being duplicated in code and prose.

## Governance

Important tooling decisions are tracked in:

- `CHANGELOG.md`
- `docs/architecture.md`
- `docs/validation-policy.md`
- `docs/backlog.md`
- `docs/sprint-log.md`
- `docs/adr/`

## Status

`tooling-ready read-only validation active`
