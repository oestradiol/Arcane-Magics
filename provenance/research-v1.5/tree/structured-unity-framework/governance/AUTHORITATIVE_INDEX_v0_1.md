# AUTHORITATIVE INDEX

This file tells you which SUF package surfaces are live and which ones are merely supportive.

## Versioning convention

The `_v0_1` suffix on files in this directory is the **governance-scheme version**, not a content version. The SUF-local governance scheme is stable at v0.1 by design; it does **not** follow the umbrella's v0.1 → v0.2 compression migration, because this subsystem is small enough that the compressed umbrella scheme (5 files replacing 13) does not pay for itself here. Individual files in this directory track their own content versions internally (see `registry_version` / `version` fields in the JSON files).

If future growth justifies it, SUF may adopt the umbrella v0.2 scheme; until then, `_v0_1` is **current, not deprecated**.

## Current truth

For SUF-specific current surfaces, see `CURRENT_SURFACES_REGISTRY_v0_1.json` in this directory. For root repository governance, see `../../governance/GOVERNANCE_CORE_v0_2.json`.

## Live front door
- `../README.md`
- `../START_HERE.md`
- `../docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md`
- `../docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md`
- `../docs/frontdoor/SCIENTIFIC_GROUNDING_AND_LIMITS.md`

## Live governance files

See root `../../governance/GOVERNANCE_CORE_v0_2.json` for umbrella current surfaces. Key SUF governance surfaces:
- `AUTHORITATIVE_INDEX_v0_1.md` (this file - routing surface)
- `CURRENT_SURFACES_REGISTRY_v0_1.json` (SUF-local current file list)
- `AUTHORITATIVE_SOURCES_v0_1.json` (entrypoint routing)
- `PACKAGE_STATE_SUMMARY_v0_1.json` (package status)
- `PACKAGE_MINIMIZATION_POLICY_v0_1.md` (renewal rules)

## Canonical long-form current docs
- `../docs/project-status.md`
- `../docs/current-execution-order.md`
- `../docs/pending-inventory.md`
- `../docs/frontdoor/claims-and-boundaries.md`
- `../docs/frontdoor/FRAMEWORK_OVERVIEW_AND_READING_GUIDE.md`
- `../docs/argument/CONTRIBUTION_AND_POSITIONING.md`
- `../docs/audit/OBJECTIONS_AND_EVIDENCE_STATUS.md`
- `../docs/monograph/SUPPORT_PACKAGE.md`

## Rule
If a file is not listed as live here or marked current in the SUF `CURRENT_SURFACES_REGISTRY_v0_1.json`, do not treat it as the present-tense package truth surface. The `_v0_1` governance-scheme suffix is **current by design** at this subsystem scope (see **Versioning convention** above); it is not a deprecation marker.
