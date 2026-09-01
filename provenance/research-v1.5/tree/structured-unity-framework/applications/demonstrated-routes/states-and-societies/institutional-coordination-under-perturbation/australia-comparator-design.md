# Australia Federal Comparator Design

## Purpose

This file defines the bounded Australia federal comparator for Phase 2 of the SUF empirical thickening program.

Australia provides a federal-structured comparison to New Zealand's unitary state coordination. The comparator focuses on federal-level coordination (AHPPC, National Cabinet, PM&C) rather than state-level implementation to maintain clean unit mapping and minimize friction.

## Scope decision

**Federal-only admission rule:**

- ✅ **Admitted:** AHPPC statements, National Cabinet transcripts, PM&C communiques, federal travel restrictions, national coordination decisions
- ❌ **Excluded:** State health department direct actions, state enforcement, local implementation (except as reported through federal sources)

**Rationale:**

1. Captures Australia's distinctive federal coordination architecture (AHPPC + National Cabinet federalism)
2. Matches NZ comparator's "strategic executive" focus for clean comparison
3. Provides bounded 18-22 event target without scope creep
4. Strengthens comparative claim: NZ unitary vs Australia federal both show public-information centrality

## Window boundary

**Acute window:** February 2020 – May 2020

- Start: AHPPC first COVID statement (February 5, 2020)
- End: Asymptomatic testing guidance (May 14, 2020) or National Cabinet transition signals

**Window rationale:**

- Functionally matched to NZ and Taiwan acute windows
- Captures activation, border tightening, quarantine establishment, and public-alignment coordination
- Excludes later vaccine rollout and prolonged de-escalation (different coordination logic)

## Source admission criteria

Same as NZ/Taiwan rule:

1. Live official URL verified
2. Fixed archive URL verified (Wayback or official archive)
3. Official or oversight material only
4. Adds boundary, timing, implementation, or dependency detail

**Primary source families:**

- **AHPPC statements** (health.gov.au) — health advice and coordination chronology
- **National Cabinet transcripts** (pmc.gov.au) — political coordination decisions
- **PM&C communiques** (pmc.gov.au) — federal coordination announcements

## Event target

**Pre-commit: 18-22 events**

Target distribution:
- AHPPC statements: 8-10 events (health advisory layer)
- National Cabinet transcripts: 6-8 events (political coordination layer)
- PM&C/Implementation: 4-6 events (federal execution layer)

**Anti-scope-creep rule:**

- State-level events only if explicitly reported through National Cabinet/AHPPC as coordinated federal-state action
- No retrospective sources beyond May 2020 in initial tranche
- No Royal Commission material in initial tranche (retrospective/oversight for later if needed)

## Unit architecture mapping

**sigma1 unit translation:**

| Australian structure | SUF sigma1 mapping |
|---------------------|-------------------|
| National Cabinet | `strategic executive coordination` |
| AHPPC | `public-health policy and command` + `public-information coordination` |
| PM&C | `strategic executive coordination` (administrative support) |
| Federal Health Department | `public-health policy and command` |
| State/Territory reps in National Cabinet | `public-service system coordination` (when acting as federal-state bridge) |

## Expected coordination patterns

**Hypothesis (to be tested):**

Australia's federal structure will show:
- More explicit `information or reporting dependency` between AHPPC and National Cabinet
- Stronger `public-information coordination` receiving from both health and executive streams
- Potential lag between AHPPC advice and National Cabinet decision (opportunity for `L` measurement)

**Null/alternative frameworks:**

- Executive-command-only: National Cabinet as decisive, AHPPC as advisory window-dressing
- State-dominant: Federal layer as coordinating facade, real action at state level (excluded by scope rule, but testable through federal reporting)

## Status

`federal comparator design — scope defined, pending source discovery`
