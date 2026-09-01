# Australia Federal Comparator Source Discovery Log

## Purpose

This file records candidate Australia federal sources before they are promoted into the public ledger.

For the current Phase 2 pass, a source is promoted only if:

- it is federal-level official material (AHPPC, National Cabinet, PM&C)
- it falls within the acute window (February 2020 – May 2020)
- it adds boundary, timing, implementation, or dependency detail
- the live public URL is verified
- a fixed archive URL is verified

Unstable candidates stay here and do not enter the ledger.

## Acute window boundary

**Start:** 2020-02-05 (AHPPC first COVID statement)
**End:** 2020-05-14 (AHPPC asymptomatic testing guidance) or National Cabinet transition signals

## Source family categories

### A-family: Command and architecture
- National Cabinet transcripts and communiques
- PM&C coordination announcements
- Australian Health Sector Emergency Response Plan

### B-family: Health advisory
- AHPPC statements and resolutions
- Chief Medical Officer advice

### C-family: Border and quarantine
- Federal travel restrictions
- International border closures
- Quarantine facility announcements

### D-family: Implementation and compliance
- Federal enforcement guidance
- National Cabinet agreed measures

## Current candidate source set

| Candidate source | Family | Date | Event or use target | Live URL | Fixed archive | Decision | Reason |
|---|---|---|---|---|---|---|---|
| `src-australia-ahppc-2020-02-05` | B-family | `2020-02-05` | first AHPPC COVID statement (false assumptions concern) | `verified` | `verified` | `accepted` | early health advisory anchor |
| `src-australia-ahppc-travel-2020-02-13` | B/C-family | `2020-02-13` | travel restrictions resolution | `verified` | `verified` | `accepted` | already in registry |
| `src-australia-ahppc-2020-02-24` | B-family | `2020-02-24` | pandemic risk assessment statement | `verified` | `verified` | `accepted` | early escalation signal |
| `src-australia-ahppc-2020-03-17` | B-family | `2020-03-17` | trajectory comparison statement | `verified` | `verified` | `accepted` | acute phase advisory |
| `src-australia-national-cabinet-2020-03-15` | A-family | `2020-03-15` | cruise ship ban and gathering limits | `verified` | `verified` | `accepted` | major coordination decision |
| `src-australia-national-cabinet-2020-03-22` | A-family | `2020-03-22` | second stage activation | `verified` | `verified` | `accepted` | escalation coordination |
| `src-australia-national-cabinet-2020-03-27` | A/D-family | `2020-03-27` | tenancies and health supply | `verified` | `verified` | `accepted` | implementation coordination |
| `src-australia-national-cabinet-2020-04-03` | A/D-family | `2020-04-03` | childcare and tenancies | `verified` | `verified` | `accepted` | social policy coordination |
| `src-australia-ahppc-2020-03-30` | B-family | `2020-03-30` | advice to National Cabinet on state/territory measures | `verified` | `verified` | `accepted` | pre-NC advisory bridge |
| `src-australia-ahppc-2020-04-03-children` | B-family | `2020-04-03` | statement on COVID-19 in children | `verified` | `verified` | `accepted` | vulnerable population guidance |
| `src-australia-national-cabinet-2020-04-07` | A-family | `2020-04-07` | churches/worship places coordination | `verified` | `verified` | `accepted` | Easter services coordination |
| `src-australia-ahppc-asymptomatic-2020-05-14` | B-family | `2020-05-14` | asymptomatic testing guidance | `verified` | `verified` | `accepted` | late acute advisory |

## Current admission result

This set provides:

- 1 source previously admitted (`src-australia-ahppc-travel-2020-02-02-13`)
- 8 sources newly verified and accepted
- Target window coverage: February through May 2020
- Federal-only scope maintained

**Estimated yield:** 10-14 codeable events from verified sources.

**Phase 2 readiness:** 9 verified sources sufficient to begin ledger construction.

## Next verification steps

1. Verify Wayback archive availability for 8 pending AHPPC/National Cabinet sources
2. Search for additional National Cabinet transcripts (Mar-May 2020)
3. Assess AHPPC statement completeness (check for gaps between Feb 24 and Mar 17)
4. Begin event coding once 5+ sources verified

## Status

`source discovery — 8 candidates pending verification`
