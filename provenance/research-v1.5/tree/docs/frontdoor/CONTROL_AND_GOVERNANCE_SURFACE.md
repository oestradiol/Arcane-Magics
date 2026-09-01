# Control and governance surface

This is the shortest current map of how the root repository stays bounded, current, hard to drift by accident, and readable without inflating package claims.

> **Terminology note:** Terms like "federation," "subsystems," "handoffs," and "boot" are organizational metaphors describing the repository's structure using systems-engineering vocabulary, not ontological claims about the research itself.

## Table of contents
- [Core rule](#core-rule)
- [Current truth surfaces](#current-truth-surfaces)
- [Checks before use](#checks-before-use)
- [How the repository resists sprawl](#how-the-repository-resists-sprawl)
- [Federated architecture](#federated-architecture)
- [Renewal cycle](#renewal-cycle)
- [Refactor-wall transition](#refactor-wall-transition)
- [Knowledge write-back and ingestion](#knowledge-write-back-and-ingestion)
- [Navigation scopes and trust order](#navigation-scopes-and-trust-order)
- [Skeptical audit](#skeptical-audit)
- [Self-reference and convergence](#self-reference-and-convergence)
- [Trust and style](#trust-and-style)
- [Honest limit](#honest-limit)
- [Provenance](#provenance)

## Core rule

No repository-level claim should be stronger than the current package boundaries, current governance files, and current validation surfaces.

## Current truth surfaces

Use these to see what is current and authoritative:
- `../../governance/AUTHORITATIVE_INDEX_v0_2.md`
- `../../governance/GOVERNANCE_CORE_v0_2.json`
- `../../governance/REGISTRY_MANIFEST_v0_2.json`
- `../../governance/FEDERATION_AND_LAYERS_v0_2.md`
- `../../governance/AUTHORITATIVE_SOURCES_v0_2.json`
- `../../governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json`
- `../../structured-unity-framework/START_HERE.md`

## Checks before use

Run these from the repository root:
- `python package_doctor.py`
- `python research_launch_gate.py`
- `research-tools validate all` (full validation suite)

Supporting audits:
- `python tools/audit_current_surfaces.py`
- `python tools/audit_repository_file_registry.py`
- `python tools/audit_current_claims.py`
- `python tools/audit_repository_minimality.py`
- `python tools/audit_routing_surfaces.py`
- `python tools/audit_edit_scope.py`

## Release checklist

Before treating the repository as current and governed:

1. `package_doctor.py` and `research_launch_gate.py` pass
2. `research-tools validate all` passes (including ground-truth validators)
3. Root and SUF integrity manifests regenerate cleanly
4. New root files added to `governance/REGISTRY_MANIFEST_v0_2.json` and SUF `REPOSITORY_FILE_REGISTRY_v0_1.json`
5. Root docs route to package surfaces rather than duplicating package state
6. Current claim expectations still match the bounded public posture

## How the repository resists sprawl

- `../../governance/GOVERNANCE_CORE_v0_2.json`
- `../../governance/REGISTRY_MANIFEST_v0_2.json`
- `../../governance/FEDERATION_AND_LAYERS_v0_2.md`
- `../../governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json`

Rule: no root file without a clear routing, governance, licensing, citation, or operational job. Current surfaces, subsystem scopes, actor classes, trust order, edit scope, renewal-cycle triggers, and derived integrity now route through the v0.2 consolidated governance stack rather than through separate v0.1 policy files.

## Federated architecture

This repository should behave like a federation of bounded subsystems, not a monolith.

Root should mainly:

- route between packages
- keep package roles explicit
- hold umbrella governance and release hygiene

Packages and operator layers should mainly own themselves:

- `structured-unity-framework/` owns academic-core truth
- `knowledge/` owns atlas structure and route logic
- `tools/` owns read-only validation and reporting

Shared protocol between parts should remain simple and explicit:

- human-readable entry surfaces
- machine-readable scope and ownership registry
- current-state and authoritative files where relevant
- local validation or review path
- file-referenced handoffs
- explicit edit-scope boundaries for cross-part changes

The more the repository grows, the more important it is that new code, tests, and maintenance helpers land close to the subsystem they protect rather than accumulating in root by convenience.

## Renewal cycle

This repository should not grow by addition alone.

When structure starts carrying too much stale routing, duplicate support text, legacy scaffolding, or startup burden, governance should force a bounded recompression-and-rebirth pass:

1. pause unnecessary expansion
2. audit where duplication, drift, or navigational burden has accumulated
3. merge, delete, archive, shorten, or reroute stale material
4. rebuild the current handoff and validation surfaces
5. reopen work only after the repository is simpler and validation passes again

The point is not aesthetic minimalism for its own sake. The point is to keep long-lived structure from becoming its own source of operational failure.

Renewal passes should not only compress surfaces. They should also look for missing recursion, stale validators, blind spots in self-coverage, and subsystems that can test or govern others but not themselves. A rebirth pass is only complete when it improves structural correctness at the core rather than just making the tree smaller.

## Refactor-wall transition

The repository should treat "prototype" and "restructure" as different modes.

Switch into a refactor wall or restructure pass when one or more of these appear:

- the same ownership or scope truth is being maintained in more than one durable place
- navigation depth or startup burden keeps increasing even when validation still passes
- subsystem ownership becomes ambiguous during normal edits
- validators need growing numbers of exceptions to stay useful
- handoff packets become longer because the structure is no longer doing enough of the work

At that point, the goal is not to add more policy. The goal is to collapse duplicated truth, re-center authoritative surfaces, simplify routing, and only then reopen additive work.

## Knowledge write-back and ingestion

Durable research deltas should not remain only in chat or private scratch.

Minimum write-back packet for durable findings:

- provenance or source anchor
- short summary
- target subsystem and file reference
- status such as candidate, working, or accepted
- whether the delta changes governance, architecture, knowledge content, or only local execution context

Prompt-local reasoning is disposable. Durable state belongs in repository surfaces with references.

## Navigation scopes and trust order

Navigation should follow both actor class and scope class.

Actor classes:

- human operator
- external memoryless agent
- subsystem-local validator or tool worker

Scope classes:

- local file or note scope
- subsystem scope
- cross-subsystem coordination scope
- root-governance scope

Default trust order:

1. authoritative and current surfaces in the owning subsystem
2. machine-readable registries that describe routing, scope, and ownership
3. validation outputs and package-state summaries
4. supportive prose and historical notes
5. prompt-local memory

Actors should navigate by scope, not by convenience.

## Skeptical audit

The repository should default to adversarial honesty rather than cooperative drift. Human proposals, agent proposals, and inherited structure should all be treated as possibly incomplete, possibly wrong, or insufficiently grounded until checked against files, tests, sources, or explicit review.

Useful questions during audit:

- what is assumed here but not yet grounded
- what can validate this claim or surface
- what part can evaluate others but cannot yet evaluate itself
- what has become stale while still looking current
- where is the system agreeing too easily instead of challenging itself

## Self-reference and convergence

The system should improve its own governance using what it learns.

That means:

- research about the system should be allowed to change the policy that governs the system
- renewal cycles should include verification and optimization of governance, tooling, scaffolding, and handoff logic, not only content cleanup
- self-reference is allowed only with explicit grounding, bounded scope, and validation, so it becomes disciplined recursion rather than runaway meta-work
- convergence is the target: over time the structure should become more coherent, more complete at the right level, and harder to drift silently

Different agents and proto-agents have different strengths and weaknesses. Governance should therefore assume heterogeneity from the start and require interfaces, trust boundaries, and validation paths that do not depend on one specific cognitive style or one specific model family.

### Main risks that still matter
1. A current root file can still be subtly misleading even if it passes routing checks.
2. Governance can prove file roles without proving that package claims are scientifically correct.
3. `knowledge/` can still drift toward SUF-overforegrounding if note discipline weakens.
4. Validation tooling can prove consistency and release hygiene without proving truth.
5. Future changes can still introduce new failure modes not yet tracked by current audits.

### What is already in place against those risks
- current-vs-supportive file roles are explicit
- current repository surfaces are indexed and hashed
- file-registry and root-allowlist checks exist
- SUF remains the academic core instead of being flattened into the umbrella
- read-only validation remains separate from substantive research claims
- root state duplication has been minimized so package truth stays package-local

### What remains true anyway
- repository governance is not scientific truth adjudication
- package-local academic claims still belong primarily to SUF
- human review remains necessary

## Trust and style

Root front-door writing should:
- route clearly between packages
- avoid duplicate long-form SUF state
- stay specific and bounded
- avoid hype, overclaiming, and generic assistant-like filler

## Honest limit

These controls increase coherence, traceability, and release hygiene. They do not guarantee scientific truth and they do not replace careful human judgment.

## Provenance

This current file consolidates the roles previously carried by:
- `COHERENCE_AND_CONTROL_SURFACE.md`
- `SKEPTICAL_AUDIT_AND_HARDENING.md`
- `TRUST_AND_STYLE_POLICY.md`
