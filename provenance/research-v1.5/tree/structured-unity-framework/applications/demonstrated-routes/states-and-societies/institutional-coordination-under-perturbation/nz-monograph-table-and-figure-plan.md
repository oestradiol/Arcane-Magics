# New Zealand Monograph Table and Figure Plan

## Purpose

This note locks the current monograph-facing table and figure plan for the New Zealand core before any later analysis-ready export work.

Canonical values still come from the Markdown route artifacts. This file is only the plan surface.

## Tables

| Planned table | Current source anchors | Stable values now | Validation expectation |
|---|---|---|---|
| Table 1. Window snapshot | `first-pass-seed-readout.md`; `first-pass-window-comparison.md` | `38` total events; `29` main-interval events; `7` Comparator B events | current route and summary validators |
| Table 2. Issuing and receiving-unit participation | `first-pass-seed-readout.md`; `first-pass-i-summary.md` | `25 / 38` strategic-executive issuing share; `33 / 38` public-information receiving share | current route and summary validators |
| Table 3. Late-transition lag pairs | `first-pass-l-summary.md` | `2`, `8`, `8`, `3`, and `2` day pairings | current lag-surface reporting plus human review |
| Table 4. Robustness baseline | `first-pass-sensitivity-and-null-note.md` | `14` checks; `10` perturbations; `4` null framings | route validation plus human review |
| Table 5. Source-family and chapter anchor map | `official-corpus-inventory.md`; `source-discovery-log.md` | monograph-baseline corpus control state | human review plus status-surface consistency |

## Figures

| Planned figure | Current source anchors | Role now |
|---|---|---|
| Figure 1. Escalation timeline | `event-ledger-seed.md` | show the architecture and escalation chain across locked windows |
| Figure 2. Dependency graph snapshot | `first-pass-dependency-graph.md` | show hub-centred cross-cluster routing |
| Figure 3. Window comparison panel | `first-pass-window-comparison.md` | show separation between Comparator A, the main interval, and Comparator B |
| Figure 4. Late-transition staging panel | `first-pass-l-summary.md`; `event-ledger-seed.md` | show the formal review and implementation chain into Level 2 |

## Release-use rule

- do not publish monograph-facing tables or figures with values not already visible in canonical Markdown docs
- do not treat this plan as a structured export layer
- move to deterministic export work only in `v1.5`

## Status

`monograph-baseline table-and-figure plan`
