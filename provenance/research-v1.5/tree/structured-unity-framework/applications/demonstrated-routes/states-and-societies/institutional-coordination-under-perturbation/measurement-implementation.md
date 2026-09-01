# Measurement Implementation

## Purpose

This file locks the first route-local implementation of `I`, `C`, `L`, and `U` for the New Zealand demonstrated route.

It is documentation-first. It is not a universal formula set for every later route.

## Scope rule

This implementation is valid only for the current New Zealand route unless a later route explicitly reuses and re-justifies the same choices.

It does **not** introduce:

- domain-general thresholds
- one scalar for `U`
- transfer claims across every future application domain

## Event-base rule

Use only events admitted under the current source-control rule:

- official or oversight source from Families `A-F`
- live URL verified
- exact fixed archive URL verified
- event materially adds boundary, timing, implementation, or dependency detail

The current baseline for this implementation is the public `38`-event ledger.

## `I` implementation

### Unit set

Use the locked `7` `sigma1` units for this route:

- strategic executive coordination
- public-health policy and command
- emergency-management coordination
- public-service system coordination
- border-control coordination
- enforcement and compliance
- public-information coordination

### Edge rule

For each coded event bundle:

- count one directed edge from the issuing unit to each receiving unit named in the event
- do not count self-loops
- do not weight one receiver more heavily than another inside the same event bundle

### Reported `I` proxies

Report all of these together:

1. `active_edge_count`
   - count of directed edges with at least one observed event
2. `occupied_edge_ratio`
   - `active_edge_count / 42`
   - `42` is the number of possible directed non-self edges among `7` units
3. `participation_breadth`
   - count of units active as issuer or receiver / `7`
4. `weighted_cross_cluster_share`
   - total cross-cluster edge occurrences / total edge occurrences
   - use the current `sigma2` clustering:
     - strategic coordination: strategic executive coordination; public-service system coordination
     - response operations: public-health policy and command; emergency-management coordination; border-control coordination; enforcement and compliance
     - public alignment: public-information coordination
5. `issuing_concentration`
   - highest issuing-unit event count / total coded events
   - always report the identity of that issuer, not only the fraction

### `I` interpretation rule

Do not collapse these proxies into one universal score.

Use them as a dashboard for asking:

- is the route fragmented or selective but integrated?
- is integration hub-centred or flat?
- is routing trapped inside one cluster or substantially cross-cluster?

## `C` implementation

### Reported `C` proxies

Report all of these together:

1. `issuing_centre_stability`
   - top issuer share in the whole window under study
   - whether the same issuer remains dominant across the key windows being compared
2. `sequence_continuity`
   - whether the major transition chain can be read as ordered escalation, implementation thickening, easing preparation, and de-escalation rather than abrupt reversals
3. `contradiction_surface`
   - explicit direct contradiction events currently coded in the ledger
   - current implementation is binary and descriptive: present / not yet clearly coded
4. `public_information_coupling`
   - PI-marked events / total events
   - public-information receiving share / total events

### `C` interpretation rule

Do not treat coherence as consensus, success, or correctness.

For this route, `C` means:

- a stable enough issuing surface
- an ordered enough transition chain
- no already-coded direct reversal that breaks the sequence
- persistent coupling to public-information coordination rather than backstage-only order

## `L` implementation

### Valid lag-pair rule

Count a lag pair only if:

- the earlier event is an explicit announcement, review-preparation, legal-handoff, or date-setting event
- the later event is an explicit implementation-start or implementation-observed event
- both belong to the same transition chain
- the pairing is visible in the public source base without inventing hidden intermediate events

### Missingness rule

- do **not** zero-fill missing pairs
- do **not** force pairing when the route only shows one side of the transition
- keep missingness visible rather than pretending false temporal precision

### Reported `L` summary

Report:

- the valid paired gaps
- median paired gap
- observed range
- whether the route mixes short staging with longer preparation windows

## `U` implementation

`U` is reported as a route-local dashboard, not a scalar.

The current route-level `U` readout is the conjoint view of:

- `I` structural shape
- `C` sequence and stability
- `L` staging and dispersion
- window comparison across Comparator A, the main perturbation interval, and Comparator B

### `U` interpretation rule

For this route, `U` asks:

- does the system behave as more than a loose aggregate at this window and scale?
- what form does that coordination take?
- how does that form differ across windows?

It does **not** claim:

- a universal unity score
- a final ranking of regimes
- direct phenomenology

## Relation to existing first-pass docs

The current first-pass companion docs remain valid as route-local readouts. They should now be read as:

- first-pass companions aligned with this implementation
- still coarse where missingness or event density is not yet strong enough

Primary companions:

- [First-Pass `I` Summary](first-pass-i-summary.md)
- [First-Pass `C` Summary](first-pass-c-summary.md)
- [First-Pass `L` Summary](first-pass-l-summary.md)
- [First-Pass Window Comparison](first-pass-window-comparison.md)
- [First-Pass Sensitivity and Null Note](first-pass-sensitivity-and-null-note.md)

## Status

`first route-local structured evidence organizer`
