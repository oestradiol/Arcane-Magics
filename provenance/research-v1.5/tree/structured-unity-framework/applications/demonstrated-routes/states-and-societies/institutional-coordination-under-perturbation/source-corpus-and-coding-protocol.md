# Source Corpus and Coding Protocol

## Purpose

This file defines the public research corpus and event-coding rules for the New Zealand route.

Working companions:

- [Official Corpus Inventory](official-corpus-inventory.md)
- [Event Ledger Seed](event-ledger-seed.md)

## Source-family rule

Use official and oversight material first. Academic retrospective work is allowed only after the official corpus is assembled.

### Required source families

- `D-family A`: governance and coordination architecture
- `D-family B`: pandemic planning and public-health command material
- `D-family C`: official chronology and alert-level transitions
- `D-family D`: public-service and emergency-management coordination material
- `D-family E`: border, enforcement, and public-information records
- `D-family F`: oversight, audit, and retrospective review
- `D-family G`: academic retrospective and comparative literature, used only after Families A-F are assembled

## Official source base to assemble first

### `D-family A` - governance and coordination architecture

- [src-oag-covid-response-2022](../../../../references/source-registry.md#src-oag-covid-response-2022)
- [src-oag-covid-appendix1-2022](../../../../references/source-registry.md#src-oag-covid-appendix1-2022)
- [src-royal-commission-phase-one-2024](../../../../references/source-registry.md#src-royal-commission-phase-one-2024)

### `D-family B` - planning and public-health command

- [src-nz-moh-managing-covid](../../../../references/source-registry.md#src-nz-moh-managing-covid)
- [src-verrall-rapid-audit-2020](../../../../references/source-registry.md#src-verrall-rapid-audit-2020)
- [src-allen-clarke-phu-deep-dive-2020](../../../../references/source-registry.md#src-allen-clarke-phu-deep-dive-2020)

### `D-family C` - chronology and alert transitions

- [src-oag-covid-appendix1-2022](../../../../references/source-registry.md#src-oag-covid-appendix1-2022)
- [src-royal-commission-phase-one-2024](../../../../references/source-registry.md#src-royal-commission-phase-one-2024)
- [src-beehive-alert-level-2-2020](../../../../references/source-registry.md#src-beehive-alert-level-2-2020)
- [src-beehive-level-3-4-2020](../../../../references/source-registry.md#src-beehive-level-3-4-2020)
- [src-beehive-alert-level-3-restrictions-2020](../../../../references/source-registry.md#src-beehive-alert-level-3-restrictions-2020)
- [src-beehive-date-move-level-3-2020](../../../../references/source-registry.md#src-beehive-date-move-level-3-2020)
- [src-beehive-level-2-announcement-2020](../../../../references/source-registry.md#src-beehive-level-2-announcement-2020)
- [src-beehive-alert-level-1-2020](../../../../references/source-registry.md#src-beehive-alert-level-1-2020)

### `D-family D` - emergency-management and public-service coordination

- [src-nema-agency-overview](../../../../references/source-registry.md#src-nema-agency-overview)
- [src-dpmc-stranded-people-2020](../../../../references/source-registry.md#src-dpmc-stranded-people-2020)
- [src-dpmc-quarantine-managed-isolation-welfare-2020](../../../../references/source-registry.md#src-dpmc-quarantine-managed-isolation-welfare-2020)
- [src-dpmc-cdem-powers-guidance-2020](../../../../references/source-registry.md#src-dpmc-cdem-powers-guidance-2020)
- [src-dpmc-review-level4-status-2020](../../../../references/source-registry.md#src-dpmc-review-level4-status-2020)
- [src-dpmc-local-authority-welfare-support-2020](../../../../references/source-registry.md#src-dpmc-local-authority-welfare-support-2020)
- [src-dpmc-national-transition-period-2020](../../../../references/source-registry.md#src-dpmc-national-transition-period-2020)
- [src-dpmc-alert-level-implementation-2020](../../../../references/source-registry.md#src-dpmc-alert-level-implementation-2020)
- [src-beehive-state-national-emergency-ended-2020](../../../../references/source-registry.md#src-beehive-state-national-emergency-ended-2020)
- [src-beehive-national-transition-period-ends-2020](../../../../references/source-registry.md#src-beehive-national-transition-period-ends-2020)
- public-service coordination material referenced in the OAG and Royal Commission reports

### `D-family E` - border, enforcement, and public information

- [src-beehive-major-steps-covid-2020](../../../../references/source-registry.md#src-beehive-major-steps-covid-2020)
- [src-beehive-stronger-border-measures-2020](../../../../references/source-registry.md#src-beehive-stronger-border-measures-2020)
- [src-police-alert-level-4-guidelines-2020](../../../../references/source-registry.md#src-police-alert-level-4-guidelines-2020)
- [src-police-support-communities-level-4-2020](../../../../references/source-registry.md#src-police-support-communities-level-4-2020)
- [src-police-avsec-working-together-2020](../../../../references/source-registry.md#src-police-avsec-working-together-2020)
- [src-police-covid-checkpoints-2020](../../../../references/source-registry.md#src-police-covid-checkpoints-2020)
- [src-police-level-3-following-rules-2020](../../../../references/source-registry.md#src-police-level-3-following-rules-2020)
- [src-police-covid-major-events-2020](../../../../references/source-registry.md#src-police-covid-major-events-2020)
- [src-beehive-alert-level-3-restrictions-2020](../../../../references/source-registry.md#src-beehive-alert-level-3-restrictions-2020)
- [src-beehive-date-move-level-3-2020](../../../../references/source-registry.md#src-beehive-date-move-level-3-2020)
- [src-beehive-level-2-legal-framework-2020](../../../../references/source-registry.md#src-beehive-level-2-legal-framework-2020)
- [src-beehive-state-national-emergency-ended-2020](../../../../references/source-registry.md#src-beehive-state-national-emergency-ended-2020)
- [src-beehive-national-transition-period-ends-2020](../../../../references/source-registry.md#src-beehive-national-transition-period-ends-2020)
- Royal Commission chapters on border restrictions, quarantine, and public communication
- relevant Police, border, and public-information records cited by the official reviews

### `D-family F` - oversight and review

- Office of the Auditor-General report and appendices
- Royal Commission Phase One report and supporting material
- Ministry of Health rapid review and audit material used for system-level reflection

## Event schema

Every coded event should include these fields:

- `event_id`
- `timestamp_or_date`
- `issuing_unit`
- `receiving_units`
- `action_type`
- `dependency_type`
- `implementation_marker`
- `public_information_marker`
- `source_citation`
- `confidence_note`
- `scale_tag`

## Coding rules

### Event identification

Code only events that materially affect cross-unit coordination, implementation timing, feedback pathways, or whole-system response.

### Dependency coding

Use `dependency_type` to distinguish at least:

- directive or authority dependency
- information or reporting dependency
- resource or logistics dependency
- legal or compliance dependency
- public-communication dependency

### Implementation marker

Use a simple three-level coding:

- `decision announced`
- `implementation initiated`
- `implementation observed`

### Public-information marker

Record whether the event changed the public communication environment through:

- major public briefing
- alert-level communication
- official guidance update
- enforcement or compliance communication

### Confidence note

Use:

- `high`: directly documented in official or oversight material
- `medium`: strongly inferable from aligned official sources
- `provisional`: plausible but still awaiting corroboration

### Scale tag

Use one or more of:

- `sigma1`
- `sigma2`
- `sigma3`

## Inclusion and exclusion rules (judgment-dependent decisions)

### Explicit inclusion criteria

Code an event **only** if it meets **at least one** of:

1. **Cross-unit coordination criterion**: The event involves explicit coordination between two or more distinct organizational units (e.g., DPMC ↔ MoH, Police ↔ NEMA)
2. **Implementation pathway criterion**: The event directly changes who must act, in what order, or with what resources
3. **Feedback loop criterion**: The event establishes or alters a reporting, monitoring, or adjustment pathway
4. **Public communication environment criterion**: The event changes what the public knows, when they know it, or what they're asked to do

### Explicit exclusion criteria

Do **not** code:

1. **Purely symbolic announcements** that repeat previously established coordination without changing pathways (e.g., "reminder that Level 4 continues")
2. **Internal unit deliberations** that do not result in external coordination changes (e.g., DPMC internal planning meeting with no external output)
3. **Retrospective summaries** that do not change ongoing coordination (e.g., end-of-week review that restates what was already done)
4. **Individual expert statements** not representing unit-level coordination (e.g., individual epidemiologist interview unless explicitly designated as official guidance)

### Edge cases with worked examples

| Edge Case | Decision | Rationale |
|---|---|---|
| **Daily press conference with no new guidance** | Exclude: symbolic repetition | No pathway change; purely communicative without coordination shift |
| **Press conference announcing new guidance** | Include: public communication environment | Changes what public knows and what they're asked to do |
| **Internal memo leaked to media** | Exclude: not official coordination | Leak does not represent established coordination pathway |
| **Official tweet clarifying alert level rules** | Include: public communication environment | Official channel changing public knowledge state |
| **DPMC "stranded people" welfare coordination** | Include: cross-unit + implementation pathway | Establishes new coordination between DPMC and other agencies |
| **Academic retrospective published during response** | Exclude: Family G admission rule | Academic sources only after Families A-F assembled |
| **Police checkpoint enforcement guidance** | Include: implementation pathway | Changes operational implementation on the ground |
| **Alert level "reminder" with no changes** | Exclude: symbolic repetition | No dependency, pathway, or communication change |

## Judgment audit notes

### Known judgment-dependent decisions in current ledger

1. **Public-information vs. coordination distinction**: Some events (e.g., Beehive announcements) could be read as either pure messaging or coordination-instruction. Current coding treats them as coordination if they include actionable guidance.
2. **Scale tagging**: Assignment to `sigma1/2/3` involves judgment about level of impact. Current tags reflect issuing unit level (national = sigma3, regional = sigma2, local = sigma1) rather than observed impact.
3. **Confidence notes**: `high`/`medium`/`provisional` assignment varies by source family. D-family A (OAG, Royal Commission) tends toward `high`; D-family E (Police releases) tends toward `medium` due to operational rather than oversight status.

### Alternative reasonable codings

A different researcher might reasonably:
- Exclude 5-10 events currently coded as `public-information` if requiring stricter coordination evidence
- Recode 3-5 events from `medium` to `high` confidence given additional corroboration
- Split 2-3 combined events into separate entries

**Impact on locked payoff**: The payoff sentence (public-information coordination as structurally central) remains robust under these alternative codings; the 33/38 ratio shifts to approximately 28/38-30/38, still supporting the core claim.

## Workflow

1. assemble the official corpus by source family
2. build the event ledger in chronological order
3. assign issuing and receiving units
4. code dependency type and implementation marker
5. assign scale tags
6. add confidence notes and unresolved issues
7. only then construct `I`, `C`, and `L` summaries

## Admission rule for the current hardening tranche

For the current execution pass, a candidate source enters the public route only if:

- it is official or oversight material from Families `A-F`
- it adds boundary, timing, implementation, or dependency detail beyond what is already coded
- the live public source is verified
- a fixed archive exists as an exact URL

Do not promote:

- wildcard Wayback lookup pages
- live pages with no fixed archive
- pages that only restate already-coded chronology without adding implementation or dependency detail

Track unstable or rejected candidates in [Source Discovery Log](source-discovery-log.md) rather than letting them leak into the ledger.

## Status

`research-ready route`
