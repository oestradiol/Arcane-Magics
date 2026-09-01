# SUF Analysis-Ready Tooling

## Purpose

This directory contains v1.5 analysis-ready tooling for the Structured Unity Framework.

Tools are **read-only** — they derive from canonical Markdown docs and do not rewrite public prose.

## Tool Categories

### `exports/`
Structured data exports from canonical Markdown sources.

- `ledger-to-json.py` — Convert event ledgers to JSON
- `source-registry-to-csv.py` — Export source registry to CSV
- `cross-case-metrics.json` — Generated three-case summary metrics

### `validators/`
Deterministic validation of claims against canonical docs.

- `validate-ledger-counts.py` — Verify event counts match claims
- `validate-closure-note.py` — Verify cross-case claims against ledgers (public-information centrality, health-executive bridge, implementation distribution, border sequence)

### Root tools

- `validate-all.py` — Unified runner that executes exports + validators and reports aggregated results

### `research-ops/` (v1.6)
Maintenance support tooling for long-term repo health.

- `check-artifact-completeness.py` — Verify monograph and evidence map integrity
- `check-backlog-hygiene.py` — Detect stale entries and surface freshness issues
- `check-discovery-state.py` — Track source resolution and pending discoveries
- `generate-handoff-packet.py` — Create future-agent handoff packets

### `generators/`
Deterministic table/figure generation for monograph-facing docs.

- `generate-metric-companions.py` — Auto-generate I/C/L/U metrics from ledger corpus
- `generate-event-table.py` — Create summary tables from ledgers
- `generate-source-family-chart.py` — Source distribution visualization data
- `generate-comparison-matrix.py` — Cross-case metric matrices

## Usage

All tools read from `../` (canonical docs) and write to `./exports/` (derived artifacts).

```bash
# Run all validations (recommended)
python3 tools/validate-all.py

# Export full 76-event corpus to JSON/CSV
python3 tools/exports/ledger-to-json.py --corpus --output tools/exports/corpus.json
python3 tools/exports/ledger-to-json.py --corpus --format csv --output tools/exports/corpus.csv

# Validate specific claims
python3 tools/validators/validate-closure-note.py --corpus tools/exports/corpus.json
python3 tools/validators/validate-ledger-counts.py --ledger-json tools/exports/corpus.json --expected 71 --case "Corpus"
```

**Environment**: Python 3.8+ required. No external dependencies (standard library only).

## Status

`v1.5 analysis-ready tooling COMPLETE — 76-event corpus validated`

- 38 New Zealand events ✓
- 20 Taiwan events ✓  
- 18 Australia federal events ✓
- Cross-case pattern validation ✓
- I/C/L/U metric companions auto-generated ✓
