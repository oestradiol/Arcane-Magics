# Agentic Knowledge System (AKS) Boundary

## What AKS Is

The **Agentic Knowledge System (AKS)** is research infrastructure for human+AI collaboration. It is **not part of SUF** — it is the system that enables SUF research to be conducted effectively.

**SUF** = academic framework for unity-like organization (the research product)  
**AKS** = collaboration infrastructure (the research process)

## Why AKS Exists

Research projects using AI assistance face recurring problems:

- **Context loss**: Each AI session starts without memory of previous work
- **Provenance gaps**: Unclear what outputs came from which inputs
- **Drift risk**: AI-generated content silently polluting human-curated knowledge
- **Validation gaps**: No systematic way to check consistency across sessions

AKS addresses these through explicit protocols rather than ad hoc prompting.

## Core AKS Components

### 1. Dual-Layer Architecture

| Layer | Location | Purpose |
|-------|----------|---------|
| **Public** (`Research/`) | Git-tracked | Academic products, frameworks, evidence, documentation |
| **Private** (`Internal/`) | Outside public repo | Operator context, stronger formulations, agent memory, work-in-progress |

**Bridge**: `Translation Decision Map.md` — the only file allowed to reference both layers

### 2. Compressed Notation (Internal/)

Agent memory externalization using symbolic shorthand:
- `OBJ{...}` = current objective
- `C!{...}` = hard constraints  
- `R@{commit}` = repo anchor
- `D+{...}` = durable deltas landed
- `V+` / `V?` = validation state

Defined in `Internal/delta/language-policy.md`. Human-readable prose in `Research/`; compressed notation in `Internal/`.

### 3. Cold-Start Protocol

Agents entering the system follow a strict boot sequence:
1. Read `AGENTS.md`
2. Read `Translation Decision Map.md`
3. Read `Internal/active/agent-instructions.md`
4. Then read relevant public package surfaces

This prevents agents from generating their own maps or assumptions.

### 4. Governance Validators

Automated checks for repository health:
- `package_doctor.py` — basic repository validation
- `research_launch_gate.py` — release readiness checks
- `governance_consistency.py` — cross-surface consistency validation

## What AKS Achieves

| Achievement | How | Status |
|-------------|-----|--------|
| **Explicit provenance** | File references, commit anchors, agent provenance in compressed notation | Working |
| **Bounded agent roles** | Agents as operators (not authorities); human operator owns final decisions | Documented; enforcement partial |
| **Recursive improvement** | Validated outputs fold back into system via durable deltas | Partial — still manual |
| **Graceful degradation** | System works without tooling if needed | Not tested |

## AKS/SUF Separation Rules

### AKS Language Stays in AKS

- Boot sequences, cold-start, handoffs, subsystems, federation
- Compressed notation (`OBJ{...}`, `C!{...}`)
- Agent role definitions, autonomy rules

### SUF Uses Academic Language
- Frameworks, research programs, methods, routes, packages
- Human-readable prose
- Standard academic citation and argumentation

**No OS/infrastructure terminology in SUF public documentation.**

## Public/Private Boundary

| Content Type | Location | Publication Rule |
|--------------|----------|------------------|
| SUF academic work | `Research/structured-unity-framework/` | Immediate — default public |
| Knowledge atlas | `Research/knowledge/` | Immediate — default public |
| AKS infrastructure | `Internal/` | Your explicit approval required |
| Draft/WIP | `Internal/` or feature branch | Your explicit approval required |
| Private reasoning | `Internal/` | Never — operator delta only |

## Cross-References

- AKS prototype design: `Internal/delta/aks-prototype.md`
- Language policy: `Internal/delta/language-policy.md`
- Agent instructions: `Internal/active/agent-instructions.md`
- Bridge file: `Translation Decision Map.md`
- SUF framework: `Research/structured-unity-framework/`

## Status

AKS is a **working infrastructure layer with an active sibling repo**, not a finished or closed system. It enables current research but continues to evolve. SUF validity does not depend on AKS — SUF stands on its empirical base and theoretical architecture, not on the infrastructure used to build it.

---

*Last updated: 2026-04-17 (post Devil's-Advocate review)*
