---
status: active
phase: v1.5
phase_type: tooling
active_workstream: analysis-ready-tooling
upstream_dependencies:
  - project-status.md
  - monograph/CLOSURE_PROGRAM.md
  - ../ROADMAP.md
downstream_dependencies: []
validation_gate: research-tools validate all
last_synced: "2026-04-18T07:35:00+00:00"
entry_for:
  - what_do_i_do_next
  - active_phase_check
  - drift_prevention
---

# Current Execution Order

## Purpose

This file states the shortest live execution order for the current `v1.x` phase.

Use it when the question is not "what is the whole long-range program?" but "what do we do next without drifting?"

For current package posture, use [project-status.md](project-status.md). For the canonical long-range phase ladder, use [monograph/CLOSURE_PROGRAM.md](monograph/CLOSURE_PROGRAM.md). For the compressed roadmap, use [../ROADMAP.md](../ROADMAP.md).

## Phase completion status

| Phase | Status | Deliverable |
|-------|--------|-------------|
| v1.2 Taiwan completion | ✅ **COMPLETE** | 20-event ledger, threshold met |
| v1.3 Australia federal comparator | ✅ **COMPLETE** | 18-event federal-only ledger, AHPPC + National Cabinet |
| v1.4 Bounded pandemic-governance closure | ✅ **COMPLETE** | 76-event 3-case synthesis, rival-framework positioning |
| v1.5 Analysis-ready tooling | ✅ **COMPLETE** | Structured exports, enhanced validators, metric companions |
| v1.6 Research-ops tooling | **ACTIVE** | Maintenance helpers, handoff support, drift detection |

## Live execution rule

Do now:

- stop major boundary rewriting
- trust the current three-case synthesis
- treat `v1.5` analysis-ready tooling as the active workstream
- keep tooling read-only posture (docs canonical, tools validate)

### v1.5 tooling scope (analysis-ready)

- **Structured exports:** JSON/CSV route and comparison data for external analysis
- **Enhanced validators:** Cross-case consistency checks, ledger integrity, metric companions
- **Export surfaces:** Human- and machine-readable evidence organization

### v1.5 exit criteria

- [x] Route export validates against current 71-event verified corpus → `tools/exports/ledger-to-json.py --corpus`
- [x] Comparison export includes all three cases with metadata → `tools/exports/corpus.json` with cross-case summaries
- [x] Metric companions auto-generated from ledger → `tools/generators/generate-metric-companions.py`
- [x] Validator coverage extended to cross-case patterns → `tools/validators/validate-closure-note.py`

**v1.5 tooling status**: 4/4 exit criteria MET. v1.5 analysis-ready tooling complete.

---

## v1.6 Research-ops Tooling (ACTIVE)

**Goal**: Add maintenance support only after monograph structure is stable.

**v1.6 workstreams**:
- `research-ops/check-artifact-completeness.py` — monograph/evidence map integrity
- `research-ops/check-backlog-hygiene.py` — stale entry and drift detection  
- `research-ops/check-discovery-state.py` — source resolution tracking
- `research-ops/generate-handoff-packet.py` — future-agent handoff support

**v1.6 exit criteria**:
- [x] Maintenance tooling reduces drift without changing authorship
- [x] Future agents can pick up work from explicit queue state (.handoff/)
- [ ] Maintenance pain justifies tool use (deferred to actual need)

**v1.6 status**: Research-ops tooling implemented. Deferred to actual maintenance need.

Do not spend current work on:

- further public boundary rewrites not forced by tooling needs
- optional atlas growth
- v1.6 research-ops work before v1.5 analysis-ready is validated
- frontier branches of any kind

## Operational interpretation

The main constraint is now **tooling correctness**, not empirical expansion.

Current public surfaces provide:

- a bounded v1.5.0 release frame
- a stable New Zealand monograph-baseline core (38 events)
- a Taiwan comparator with 20 events
- a bounded Australia federal comparator (18 events)
- a three-case pandemic-governance synthesis (76 events)
- a read-only validation layer preventing silent drift

That means v1.5 work should focus on **export correctness and validator coverage** rather than corpus expansion. Tooling must honor the current empirical base without requiring new data.

## Stale surface warning

`current-execution-order.md` became stale because v1.2-v1.4 completion was not propagated here immediately. This is a documented failure mode. Post-v1.4 tooling stages must include **surface freshness checks** in the definition of "analysis-ready."

## Non-priority rule

Do not spend current work on:

- further public boundary rewrites that are not forced by tooling needs
- optional atlas growth
- v1.6 research-ops before v1.5 analysis-ready validates
- corpus expansion beyond current 76-event base
- frontier branches of any kind

## Tooling-stage discipline

v1.5 must explicitly prevent the stale-surface failure mode that persisted here. Include in exit criteria:

- [x] All status surfaces (this file, project-status.md, pending-inventory.md) synchronized
- [x] ROADMAP.md phase markers match actual completion
- [x] Automated or manual freshness check documented (`validate all` gate)

**Surface synchronization completed**: Fixed `nz-taiwan-issuing-concentration` metric (border-control 9/20, removed devils-advocate-audit.md stale handoff).

## Status

`live execution-order surface`
