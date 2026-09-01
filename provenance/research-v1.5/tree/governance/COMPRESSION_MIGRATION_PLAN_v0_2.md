# Governance Compression Migration Plan v0.2

## Objective

Compress 13 governance files → 5 core files (62% reduction) while preserving "verify the verification, doubt the verifier" philosophy.

## Current State (13 files)

### Registries (4 files - redundant)
- `CURRENT_SURFACES_REGISTRY_v0_1.json` — canonical current file list
- `SUBSYSTEM_REGISTRY_v0_1.json` — subsystem ownership + validation clusters
- `AUTHORITATIVE_INTEGRITY_MANIFEST_v0_1.json` — SHA256 hashes of current files
- `REPOSITORY_FILE_REGISTRY_v0_1.json` — full repo catalog (350 files)
- `PACKAGE_STATE_SUMMARY_v0_1.json` — version metadata

### Policy (3 files - overlapping)
- `FEDERATED_SUBSYSTEM_PROTOCOL_v0_1.md` — federation rules
- `PACKAGE_MINIMIZATION_POLICY_v0_1.md` — renewal cycles
- `IMPLEMENTATION_LAYER_POLICY_v0_1.md` — layer stack

### Index/Control (5 files)
- `AUTHORITATIVE_INDEX_v0_1.md` — routing surface
- `AUTHORITATIVE_SOURCES_v0_1.json` — citation registry
- `CURRENT_CLAIM_EXPECTATIONS_v0_1.json` — claim status matrix
- `AGENT_EDIT_SCOPE_POLICY_v0_1.json` — edit rules
- `REPOSITORY_EDIT_BASELINE_v0_1.json` — edit tracking

## Target State (5 files)

| New File | Consolidates |
|----------|---------------|
| `GOVERNANCE_CORE_v0_2.json` | CURRENT_SURFACES_REGISTRY + SUBSYSTEM_REGISTRY + AGENT_EDIT_SCOPE + authoritative index |
| `REGISTRY_MANIFEST_v0_2.json` | FILE_REGISTRY + PACKAGE_STATE_SUMMARY + derived INTEGRITY_MANIFEST |
| `FEDERATION_AND_LAYERS_v0_2.md` | FEDERATED_SUBSYSTEM_PROTOCOL + PACKAGE_MINIMIZATION_POLICY + IMPLEMENTATION_LAYER_POLICY |
| `AUTHORITATIVE_SOURCES_v0_2.json` | AUTHORITATIVE_SOURCES (unchanged) |
| `CURRENT_CLAIM_EXPECTATIONS_v0_2.json` | CURRENT_CLAIM_EXPECTATIONS (unchanged) |

## Migration Steps

### Phase 1: Validation Tool Update (blocking)
1. Update `research-tools` to consume `GOVERNANCE_CORE_v0_2.json`
2. Derive `INTEGRITY_MANIFEST` at runtime from `GOVERNANCE_CORE.current_surfaces` + `REGISTRY_MANIFEST.catalog`
3. Derive subsystem validation clusters from `GOVERNANCE_CORE.subsystems.scope_prefixes`
4. Test: `research-tools validate governance` passes

### Phase 2: Soft Transition
1. Keep v0.1 files in place
2. Add v0.2 files as "draft"
3. Update root `AUTHORITATIVE_INDEX_v0_1.md` to reference both versions with note: "v0.2 is target; v0.1 is current active"

### Phase 3: Hard Switch
1. Rename v0.1 files to `.archived_v0_1.{ext}`
2. Update all internal references
3. Run full validation: `research-tools validate all`
4. Update `CHANGELOG.md`

### Phase 4: Cleanup
1. After 1-2 release cycles with no issues, delete archived v0.1 files
2. Update tooling to remove v0.1 compatibility code

## Derivation Rules (Preserve Verification)

### INTEGRITY_MANIFEST (derived, not stored)
```python
def derive_integrity_manifest():
    current_files = load_json("GOVERNANCE_CORE_v0_2.json")["current_surfaces"]
    full_catalog = load_json("REGISTRY_MANIFEST_v0_2.json")["files"]
    return {
        file: full_catalog[file]["sha256"]
        for file in current_files
    }
```

### Subsystem Validation Clusters (derived, not stored)
```python
def derive_validation_cluster(subsystem_id):
    subsystem = load_json("GOVERNANCE_CORE_v0_2.json")["subsystems"][subsystem_id]
    # Use scope_prefixes + entry/state surfaces to determine validation set
    return resolve_scope_to_files(subsystem["scope_prefixes"])
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Tooling breaks | Phase 1: update tools before touching files |
| Lost verification | Derive integrity at runtime; keep full catalog |
| Navigation confusion | Soft transition: both versions visible |
| Agent cold-start failure | Keep `AGENTS.md` path stable |

## Success Criteria

- [ ] `research-tools validate governance` passes on v0.2
- [ ] `research-tools validate all` passes
- [ ] Agent cold-start sequence unchanged
- [ ] File count: 13 → 5 governance files
- [ ] No loss of verification capability
- [ ] Repository simpler to navigate

---

**Status:** Migration plan drafted, awaiting Phase 1 tooling update.
