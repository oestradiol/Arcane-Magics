# Federation and Layers v0.2

> **Terminology note:** "Federation," "subsystems," and related infrastructure terms are organizational metaphors. They describe the repository's structure using systems vocabulary, not claims that the research itself constitutes a computational system.

## Purpose

Consolidated governance for Research/ repository: federated subsystem architecture, minimization/renewal cycles, and implementation layer discipline.

## Core Principles

### Verification Philosophy

**"Doubt the verifier."** All governance is inspectable, revisable, and self-referencing only through bounded recursion. AI is unreliable and drifts; humans are unreliable and burn out. Good research needs good validation—so we keep the verification policy but make it elegant.

### Federation

Each major part owns its local truth:
- Root governance coordinates, does not absorb
- SUF owns academic truth
- Knowledge owns atlas structure  
- Tools owns validation logic

### Minimization

Growth phases followed by deliberate **recompression**:
1. Freeze unnecessary expansion
2. Audit duplication, drift, stale surfaces
3. Recompress by deleting, merging, archiving
4. Rebuild indexes
5. Validate
6. Reopen only when simpler and clearer

**Success condition:** Repository is easier to operate than before, not just restructured.

---

## Subsystem Map

| Subsystem | Owner | Scope | Entry Surface |
|-----------|-------|-------|---------------|
| root-governance | Research root | umbrella routing, release hygiene | GOVERNANCE_CORE_v0_2.json |
| structured-unity-framework | SUF package | academic truth, route posture | structured-unity-framework/START_HERE.md |
| knowledge | Knowledge package | atlas, study routes | knowledge/README.md |
| tools | Tools package | read-only validation | tools/README.md |

Cross-subsystem edits require explicit handoff: provenance, summary, target, status, change_class.

---

## Implementation Layers

Choose the narrowest adequate layer. Keep durable truth, machine coordination, environment control, and orchestration logic separated.

| Layer | Medium | Use For | Don't Use For |
|-------|--------|---------|---------------|
| 1: Human truth | Markdown | package truth, arguments, handoff | executable logic |
| 2: Machine protocol | JSON | canonical state, registries, policy data | human-facing nuance |
| 3: Environment | Nix | reproducible env, runtimes | application logic |
| 4: Orchestration | Python | parsing, validation, workflows | hiding governance state |
| 5: Entrypoints | Shell | thin wrappers, convenience | durable core logic |

---

## Actor Navigation

| Actor | Reads First | Authority |
|-------|-------------|-----------|
| human-operator | owning subsystem state, GOVERNANCE_CORE for cross-subsystem | objectives, irreversible approvals |
| external-agent | AGENTS.md → owning subsystem → GOVERNANCE_CORE | bounded operator, file-based recovery |
| validator | GOVERNANCE_CORE → REGISTRY_MANIFEST → local inputs | deterministic support, not meaning authority |

**Trust order:** subsystem surfaces > GOVERNANCE_CORE > REGISTRY_MANIFEST > validation outputs > supportive prose > prompt memory.

---

## Renewal Trigger

Pause expansion when:
- current/supportive files duplicate each other
- agent startup cost rises from surface proliferation
- stale notes survive after newer surfaces exist
- validators pass but navigation degrades
- more effort remembering structure than using it

---

## Related

- `GOVERNANCE_CORE_v0_2.json` — canonical machine-readable state
- `REGISTRY_MANIFEST_v0_2.json` — file catalog and integrity
