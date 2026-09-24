# R179 VMK-1 -> current VMK2 compatibility ledger

**Status:** historical compatibility / regression surface  
**Date:** 2026-09-24  
**Current authority:** none by itself

This ledger asks a narrow question:

```text
which R179 VMK-1 constitutional consequences
remain enforced, are refined, are only partially represented,
or remain open in the current VMK2 reference/runtime?
```

It does not assume that a later kernel name inherits every earlier guarantee.

| VMK-1 consequence | Current VMK2 disposition | Current surface | Notes |
|---|---|---|---|
| execution receipt != external return | **PRESERVED / REFINED** | `ExecutionReceipt`, `VerifiedReturn`, `ReturnRole` | ActionReturn requires a prior execution receipt; encounter return remains separately typed |
| effect success != NPR/world-side success | **PRESERVED AT ENGINEERING BOUNDARY** | execution receipt + separately ingested evidence/return | execution cannot mint a return |
| return must remain bound to returned evidence | **REFINED** | transition payload digest must match verified-return evidence | current VMK2 makes return->mutation binding executable |
| return replay must fail closed | **REFINED** | consumed nonce | portal transition is single-use |
| WORD/reconstruction != state-changing PORTAL | **REFINED / EXECUTABLE** | `PolicyMode.WORD/PORTAL` | WORD does not mutate or spend return nonce |
| jurisdiction / authority binding | **PARTIALLY PRESERVED** | `JurisdictionReceipt`, `TransitionPolicy` | internal receipt binding/validity is enforced; external issuer authentication remains open |
| legitimacy checks | **PRESERVED INTERNALLY** | `LegitimacyReceipt` | status, target/actor, validity, withdrawal fail closed |
| pacing / turn ownership | **PRESERVED / REIFIED** | `TurnLease` | explicit time window and contamination boundary |
| nonpreauthorship / external source warrant | **PARTIAL / TRUST BOUNDARY OPEN** | evidence source + assessor + return source binding | source identifiers are represented, but cryptographic principal/source authentication is not yet provided |
| LICENSE_NOT fail-close semantics | **NO ONE-FOR-ONE LIVE OBJECT** | jurisdiction/legitimacy failures provide narrower fail-close cases | do not claim semantic equivalence without a typed warrant layer |
| compensation after returned consequence | **NOT ONE-FOR-ONE IN BARE VMK2** | none in `kernel/runtime/vmk2.py` | must be supplied by higher developmental machinery or reintroduced explicitly if claimed |
| full-fidelity typed state persistence | **PARTIAL / DIFFERENT REPRESENTATION** | `StateObject`, canonical roots, dependency closure | current state custody is stricter in some respects but not a direct serialization of all VMK-1 typed semantic objects |
| dependency-local consequence | **REFINED** | dependency closure + sibling-root conservation | unaffected siblings cannot silently mutate |
| lawful compression under declared future family | **PRESERVED / REIFIED** | `ProjectionReceipt` | explicit future family + evidence handles |
| reopening under new future separator | **REFINED** | strict future-family expansion + evidence-bound separator | current VMK2 requires immutable evidence for separator |

## Compatibility law

A VMK-1 guarantee may be marked inherited only when a current executable or formally specified mechanism preserves the same operative consequence.

```text
same vocabulary
-/-> compatibility

later implementation
-/-> inherited warrant

compatibility
= consequence preserved at declared index
```

Rows marked PARTIAL or OPEN remain obligations. They are not failures of the current kernel unless a current claim requires the stronger VMK-1 consequence.

## Highest-value residuals

The compatibility pass leaves three notable live burdens:

1. **external authentication**: represented source/authority identifiers are not authenticated principals;
2. **warrant semantics**: VMK-1's general epistemic `LICENSE_NOT` object is not identical to current jurisdiction/legitimacy denial;
3. **compensation**: bare VMK2 does not expose the one-for-one post-return compensation object carried by VMK-1.

These should be handled by explicit higher-layer ownership or new executable objects if later claims depend on them, not by silently treating VMK2 as a complete semantic superset.

## Claim fence

This is a compatibility ledger, not a new kernel promotion. Historical VMK-1 remains provenance; IG10/VMK2-derived state remains the current exact runtime checkpoint.
