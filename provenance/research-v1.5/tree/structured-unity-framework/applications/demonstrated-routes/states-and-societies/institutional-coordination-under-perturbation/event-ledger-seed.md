# Event Ledger

## Purpose

This file is the canonical public event ledger for the New Zealand demonstrated route.

It is the conservative baseline ledger for the current route. The filename stays stable for tooling compatibility, but the ledger itself is no longer only a seed pass.

## Current posture

Current status: `public baseline ledger`

This ledger is intentionally conservative:

- it uses only events that are clearly visible in the official and oversight source base already assembled publicly
- it tests the public coding schema against real material
- it covers comparator setup, the main perturbation interval, and the Comparator B boundary
- it supports the current monograph-baseline New Zealand chapter set inside the locked windows
- it does not pretend to be exhaustive beyond those windows

## Coding note

This first public pass uses the locked public schema:

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

When one official source records a bundled same-day shift, this public baseline ledger keeps the bundle together rather than forcing false micro-events.

## Summary list

| Event ID | Date | Short description |
|---|---|---|
| `nz-a-001` | `2020-01-27` | national security system formally activated |
| `nz-a-002` | `2020-02-28` | first case confirmed and pandemic-phase posture shifts |
| `nz-p-001` | `2020-03-02` | Ad Hoc Cabinet Committee on the Covid-19 Response set up |
| `nz-p-002` | `2020-03-06` | ODESC directs NCMC activation at the Ministry of Health |
| `nz-p-003` | `2020-03-11` | All-of-Government Controller role added to strengthen co-ordination |
| `nz-p-008` | `2020-03-14` | 14-day self-isolation for arrivals and stronger border-health measures announced |
| `nz-p-004` | `2020-03-19` | Covid-19 Ministerial Group replaces the earlier Cabinet committee |
| `nz-p-009` | `2020-03-19` | border closes to most non-citizens and non-residents |
| `nz-p-005` | `2020-03-21` | four-stage Alert Level framework announced |
| `nz-p-010` | `2020-03-23` | move to Level 3 with Level 4 to follow in 48 hours announced |
| `nz-p-006` | `2020-03-25` | state of national emergency and Level 4 lockdown begin |
| `nz-p-019` | `2020-03-31` | all-of-government plan for managing stranded people formalized |
| `nz-p-007` | `2020-04-01` | Quin-centred all-of-government response structure is visible in National Action Plan 2.0 |
| `nz-p-020` | `2020-04-02` | welfare coordination for people in quarantine and managed isolation formalized |
| `nz-p-014` | `2020-04-04` | additional Alert Level 4 rules clarified through Police guidance |
| `nz-p-021` | `2020-04-09` | CDEM Act key powers guidance updated for the state of national emergency |
| `nz-p-022` | `2020-04-14` | review-preparation for Level 4 status formalized in Cabinet material |
| `nz-p-011` | `2020-04-16` | Alert Level 3 restrictions announced |
| `nz-p-012` | `2020-04-20` | date for move to Alert Level 3 announced |
| `nz-p-015` | `2020-04-20` | Level 3 implementation and compliance framework detailed |
| `nz-p-018` | `2020-04-20` | Police confirm visible compliance, cross-agency support, and education-first enforcement during extended Level 4 |
| `nz-p-023` | `2020-04-21` | local-authority and CDEM welfare-support criteria widened for COVID-19 response needs |
| `nz-p-028` | `2020-04-22` | Level 3 powers and authorisations formalized in Cabinet material |
| `nz-p-017` | `2020-04-23` | Police clarify position on community checkpoints with local-authority and CDEM linkage |
| `nz-p-013` | `2020-04-28` | Alert Level 3 interval begins |
| `nz-p-024` | `2020-04-28` | Police urge the public to keep following the rules at Alert Level 3 |
| `nz-p-016` | `2020-04-29` | Aviation Security and Police continue joint reassurance patrols and quarantine/isolation compliance checks |
| `nz-p-025` | `2020-05-01` | Police remind the public of Alert Level 3 restrictions |
| `nz-p-029` | `2020-05-04` | review-preparation for New Zealand's Level 3 status formalized |
| `nz-p-027` | `2020-05-06` | formal Level 2 preparation sets guidance, service-phasing, and public-message expectations ahead of the next review |
| `nz-p-026` | `2020-05-08` | Police remind the public New Zealand remains in Alert Level 3 |
| `nz-b-007` | `2020-05-11` | Review of Alert Level 3 completed in Cabinet material ahead of the Level 2 shift |
| `nz-b-004` | `2020-05-11` | Level 2 transition decision publicly announced |
| `nz-b-006` | `2020-05-12` | national transition period planning formalized in a joint DPMC/NEMA briefing |
| `nz-b-005` | `2020-05-13` | legal framework for Alert Level 2 passes |
| `nz-b-001` | `2020-05-13` | state of national emergency lifted and national transition period begins |
| `nz-b-002` | `2020-05-14` | Alert Level 2 interval begins |
| `nz-b-003` | `2020-06-08` | Alert Level 1 begins and extraordinary CDEM powers fall away |

## Comparator A boundary markers

### `nz-a-001`

- `timestamp_or_date`: `2020-01-27`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: formal activation of the national security system
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-oag-covid-response-2022` (Part 4); `src-oag-covid-appendix1-2022`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This is the clearest public baseline marker that the system began moving from ordinary governance into a structured whole-of-government coordination posture.

### `nz-a-002`

- `timestamp_or_date`: `2020-02-28`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `strategic executive coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: first confirmed case and explicit shift in pandemic-phase posture
- `dependency_type`: `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-oag-covid-response-2022` (Part 4, para. 4.24); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the clearest boundary marker for the main perturbation interval. It also shows that pandemic-phase language and response posture were explicitly being adjusted once the first case was confirmed.

## Main perturbation interval seed events

### `nz-p-001`

- `timestamp_or_date`: `2020-03-02`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`
- `action_type`: creation of the Ad Hoc Cabinet Committee on the Covid-19 Response
- `dependency_type`: `directive or authority dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-oag-covid-response-2022` (Part 5, para. 5.15); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This is an early central-governance consolidation event. It matters less because of symbolism than because it creates a more formal strategic receiving point for advice and co-ordination.

### `nz-p-002`

- `timestamp_or_date`: `2020-03-06`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `emergency-management coordination`; `public-health policy and command`; `public-service system coordination`
- `action_type`: activation of the National Crisis Management Centre at the Ministry of Health
- `dependency_type`: `directive or authority dependency`; `resource or logistics dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-oag-covid-response-2022` (Part 5, para. 5.7); `src-oag-covid-appendix1-2022`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This is one of the first very clear operational co-ordination shifts. It changes where co-ordination work is physically and institutionally being organized.

### `nz-p-003`

- `timestamp_or_date`: `2020-03-11`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `emergency-management coordination`; `public-health policy and command`; `public-service system coordination`
- `action_type`: appointment of an All-of-Government Controller to connect the national security system and the operational response
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-oag-covid-response-2022` (Part 5, paras. 5.8-5.10); `src-oag-covid-appendix1-2022`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is a strong cross-unit co-ordination event because it explicitly creates a liaison and control function between strategic and operational layers.

### `nz-p-008`

- `timestamp_or_date`: `2020-03-14`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: 14-day self-isolation for arrivals and strengthened border-health measures announced
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`; `directive or authority dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-beehive-major-steps-covid-2020`; `src-oag-covid-response-2022`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the clearest early direct border event in the public route. It shows public information, border control, and compliance logic being pulled into the same coordination bundle before the alert-level escalations.

### `nz-p-004`

- `timestamp_or_date`: `2020-03-19`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: replacement of the Ad Hoc Cabinet Committee by the Covid-19 Ministerial Group with urgent decision authority
- `dependency_type`: `directive or authority dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-oag-covid-response-2022` (Part 5, para. 5.16); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is a governance-thickening event. It sharpens the route's strategic centre and makes urgent cross-unit decision flow more legible.

### `nz-p-009`

- `timestamp_or_date`: `2020-03-19`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: closure of the border to most non-citizens and non-residents
- `dependency_type`: `legal or compliance dependency`; `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-beehive-stronger-border-measures-2020`; `src-oag-covid-response-2022`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is a direct border-coordination thickening event. It makes the route's border, compliance, and public-information dependencies much harder to flatten into a purely executive narrative.

### `nz-p-005`

- `timestamp_or_date`: `2020-03-21`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-information coordination`; `enforcement and compliance`; `public-service system coordination`
- `action_type`: announcement of the four-stage Alert Level framework
- `dependency_type`: `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `alert-level communication`
- `source_citation`: `src-beehive-alert-level-2-2020`; `src-oag-covid-response-2022` (Part 5, para. 5.17); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event is central for the route because it changes the public communication environment while also creating a more legible cross-unit coordination grammar.

### `nz-p-010`

- `timestamp_or_date`: `2020-03-23`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-service system coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: move to Alert Level 3 with transition to Level 4 in 48 hours announced
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `alert-level communication`; `enforcement or compliance communication`
- `source_citation`: `src-beehive-level-3-4-2020`; `src-oag-covid-response-2022`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event separates decision-side escalation from implementation-side lockdown. That matters for later `L` work because it gives the route a cleaner announcement-to-implementation break.

### `nz-p-006`

- `timestamp_or_date`: `2020-03-25`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: declaration of a state of national emergency and entry into Level 4 lockdown
- `dependency_type`: `legal or compliance dependency`; `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `alert-level communication`; `enforcement or compliance communication`
- `source_citation`: `src-oag-covid-response-2022` (Part 5, paras. 5.17-5.18); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the clearest high-acuity whole-system event in the public route. It couples legal authority, public communication, implementation pressure, and multi-unit dependency in one dense coordination shift.

### `nz-p-007`

- `timestamp_or_date`: `2020-04-01`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-service system coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: Quin-centred all-of-government response structure visible in National Action Plan 2.0
- `dependency_type`: `information or reporting dependency`; `directive or authority dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-national-action-plan-v2-2020`; `src-dpmc-all-of-government-system-2020`; `src-dpmc-public-information-2020`; `src-oag-covid-response-2022` (Part 5, Figure 3 and paras. 5.31-5.33); `src-oag-covid-appendix1-2022`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event is useful because it shows the operating structure not just being discussed but stabilized enough to be documented as a concrete coordination architecture.

### `nz-p-019`

- `timestamp_or_date`: `2020-03-31`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: all-of-government plan for managing stranded people formalized in Cabinet material
- `dependency_type`: `directive or authority dependency`; `resource or logistics dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-stranded-people-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the acute implementation layer by showing that stranded-people management was being formalized as a cross-unit coordination problem rather than left implicit inside the border decision chain.

### `nz-p-014`

- `timestamp_or_date`: `2020-04-04`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-information coordination`
- `action_type`: additional Alert Level 4 rules clarified through Police guidance
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`; `information or reporting dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-police-alert-level-4-guidelines-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds direct implementation-side compliance clarification inside the Level 4 period. It matters because it shows the route is not made only of top-level strategic announcements; operational rule clarification also becomes visible as part of the coordination architecture.

### `nz-p-020`

- `timestamp_or_date`: `2020-04-02`
- `issuing_unit`: `public-service system coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: welfare coordination for people in quarantine and managed isolation formalized
- `dependency_type`: `resource or logistics dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-quarantine-managed-isolation-welfare-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event makes the quarantine and managed-isolation layer more legible as a welfare and support problem rather than only a border or public-health problem. That matters because it adds one more concrete implementation chain tying service coordination to the wider response architecture.

### `nz-p-021`

- `timestamp_or_date`: `2020-04-09`
- `issuing_unit`: `emergency-management coordination`
- `receiving_units`: `strategic executive coordination`; `public-service system coordination`; `enforcement and compliance`
- `action_type`: guidance on the use of CDEM Act key powers updated for the COVID-19 state of national emergency
- `dependency_type`: `legal or compliance dependency`; `directive or authority dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-cdem-powers-guidance-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds a direct emergency-powers guidance layer to the route. It matters because it shows formal authority routing and operational powers clarification inside the main interval rather than only retrospective descriptions of emergency-management roles.

### `nz-p-022`

- `timestamp_or_date`: `2020-04-14`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: review-preparation for New Zealand's Level 4 status formalized in Cabinet material
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-review-level4-status-2020`; `src-dpmc-review-alert-level4-paper-minute-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the easing-preparation chain before the public Level 3 announcement sequence begins. It shows that review and transition preparation were being formalized before the later announcement and implementation markers.

### `nz-p-016`

- `timestamp_or_date`: `2020-04-29`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `border-control coordination`; `public-information coordination`
- `action_type`: Aviation Security and Police continue joint reassurance patrols and quarantine/isolation compliance checks
- `dependency_type`: `legal or compliance dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `enforcement or compliance communication`
- `source_citation`: `src-police-avsec-working-together-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event keeps the implementation-side layer visible across the shift out of Level 4. It shows that reassurance patrols and quarantine/isolation compliance work remained a live coordination problem even after the acute lockdown stage had started to ease.

### `nz-p-011`

- `timestamp_or_date`: `2020-04-16`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: Alert Level 3 restrictions announced
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `alert-level communication`; `enforcement or compliance communication`
- `source_citation`: `src-beehive-alert-level-3-restrictions-2020`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the first clear public signal that the route is not only escalating but also specifying the conditions for a staged move out of Level 4. It thickens the implementation side of the main interval without pretending the lower-acuity transition had already happened.

### `nz-p-012`

- `timestamp_or_date`: `2020-04-20`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: date for move to Alert Level 3 publicly announced
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `alert-level communication`
- `source_citation`: `src-beehive-date-move-level-3-2020`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event gives the route a cleaner announcement-to-implementation pair for the Level 3 transition. That matters because it adds a more defensible non-zero lag marker inside the main interval.

### `nz-p-015`

- `timestamp_or_date`: `2020-04-20`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: implementation and compliance framework for the move to Alert Level 3 detailed in Cabinet material
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-alert-level-implementation-2020`; `src-beehive-date-move-level-3-2020`
- `confidence_note`: `medium-high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds operating-model and compliance-governance detail to the Level 3 transition chain. It makes the route less dependent on announcement-only chronology by showing a more explicit implementation-preparation layer.

### `nz-p-018`

- `timestamp_or_date`: `2020-04-20`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `public-information coordination`
- `action_type`: Police confirm visible compliance, cross-agency support, and education-first enforcement during extended Level 4
- `dependency_type`: `legal or compliance dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-police-support-communities-level-4-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the route's implementation chain at the exact point where Level 4 is being extended and the Level 3 move-date is being set. It shows that enforcement continuity, public guidance, and cross-agency support remained active coordination objects rather than disappearing into the background once the strategic transition language took over.

### `nz-p-023`

- `timestamp_or_date`: `2020-04-21`
- `issuing_unit`: `emergency-management coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`
- `action_type`: local-authority and CDEM welfare-support criteria widened to meet immediate COVID-19 response needs
- `dependency_type`: `resource or logistics dependency`; `directive or authority dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-local-authority-welfare-support-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds a direct welfare-support financing and delivery layer to the main interval. It matters because it shows local authorities and CDEM groups being pulled more explicitly into immediate COVID-19 support delivery rather than remaining only background institutions.

### `nz-p-017`

- `timestamp_or_date`: `2020-04-23`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `emergency-management coordination`; `public-service system coordination`; `public-information coordination`
- `action_type`: Police clarify position on community checkpoints and partnership conditions with local authorities, CDEM managers, iwi, and communities
- `dependency_type`: `legal or compliance dependency`; `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-police-covid-checkpoints-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event matters because it makes local checkpoint governance visible as a coordination object in its own right. It is not just rule enforcement; it is a multi-party coordination problem involving Police, local authorities, emergency-management actors, and community leadership.

### `nz-p-028`

- `timestamp_or_date`: `2020-04-22`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: powers and authorisations to give effect to Alert Level 3 are formalized in Cabinet material
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation prepared`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-powers-authorisations-level3-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds direct authority-routing detail to the late-Level-4 and early-Level-3 transition chain. It makes the move into Level 3 less dependent on announcement pages alone by exposing the formal powers surface behind the implementation handoff.

### `nz-p-013`

- `timestamp_or_date`: `2020-04-28`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: move to Alert Level 3 and first easing from Level 4 begins
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `alert-level communication`; `enforcement or compliance communication`
- `source_citation`: `src-oag-covid-appendix1-2022`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `medium-high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the implementation-side counterpart to the Level 3 transition planning chain. It gives the public route a more complete main-interval easing sequence rather than leaving the route stuck at the point of acute lockdown.

### `nz-p-024`

- `timestamp_or_date`: `2020-04-28`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-information coordination`
- `action_type`: Police urge the public to keep following the rules at Alert Level 3 as the easing interval begins
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-police-level-3-following-rules-2020`; `src-police-covid-major-events-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event keeps the implementation layer visible on the first day of Alert Level 3 rather than letting the easing sequence appear as a purely strategic handoff. It shows Police-public guidance continuing as an active routed dependency.

### `nz-p-025`

- `timestamp_or_date`: `2020-05-01`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-information coordination`
- `action_type`: Police remind the public of Alert Level 3 restrictions and continued compliance expectations
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-police-covid-major-events-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the late main interval by showing that the Level 3 phase still required visible compliance guidance after the initial easing move. It improves the route's continuity on the implementation side without changing the basic window boundaries.

### `nz-p-029`

- `timestamp_or_date`: `2020-05-04`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: preparation to review New Zealand's Level 3 status is formalized in Cabinet material
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation prepared`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-preparing-review-level3-status-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event makes the late main interval less discontinuous by showing that the Level 3 to Level 2 decision was preceded by a formal review-preparation layer, not just by public speeches and enforcement reminders.

### `nz-p-027`

- `timestamp_or_date`: `2020-05-06`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: formal preparation for Alert Level 2 sets guidance revisions, service phasing, and public messaging expectations ahead of the next review
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `implementation prepared`
- `public_information_marker`: `official guidance update`; `alert-level communication`
- `source_citation`: `src-dpmc-preparing-for-alert-level-2-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event gives the late transition chain one more direct DPMC operating anchor before the Level 2 decision. It makes the move into Comparator B less dependent on speeches and legal passage alone by showing that guidance, local-government services, transport, justice, and wider public messaging were already being staged for the next shift.

### `nz-p-026`

- `timestamp_or_date`: `2020-05-08`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-information coordination`
- `action_type`: Police remind the public New Zealand remains in Alert Level 3 ahead of the next transition decision
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-police-covid-major-events-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens Comparator B preparation without forcing a new window. It shows enforcement-side guidance still operating immediately before the Level 2 decision point, which helps distinguish late-transition continuity from the earlier acute escalation chain.

## Comparator B boundary markers

### `nz-b-007`

- `timestamp_or_date`: `2020-05-11`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: review of Alert Level 3 is completed in Cabinet paper and minute ahead of the move to Level 2
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `information or reporting dependency`
- `implementation_marker`: `decision reviewed`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-review-alert-level3-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the Comparator B boundary by adding the formal review layer behind the Level 2 shift. It makes the transition less dependent on public announcement and legal-handoff pages alone.

### `nz-b-004`

- `timestamp_or_date`: `2020-05-11`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: public decision announcement for the move to Alert Level 2
- `dependency_type`: `directive or authority dependency`; `public-communication dependency`; `legal or compliance dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `alert-level communication`
- `source_citation`: `src-beehive-level-2-announcement-2020`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event is useful because it makes the comparator entry visible as a decision event before the lower-acuity period is actually implemented.

### `nz-b-006`

- `timestamp_or_date`: `2020-05-12`
- `issuing_unit`: `emergency-management coordination`
- `receiving_units`: `strategic executive coordination`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: national transition period planning formalized in a joint DPMC/NEMA briefing
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-dpmc-national-transition-period-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds direct operating-model thickness to the transition window. It makes the move into Comparator B less dependent on speeches and legal passage alone by showing formal joint planning for the national transition period.

### `nz-b-005`

- `timestamp_or_date`: `2020-05-13`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: legal framework for COVID-19 Alert Level 2 passes
- `dependency_type`: `legal or compliance dependency`; `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`; `enforcement or compliance communication`
- `source_citation`: `src-beehive-level-2-legal-framework-2020`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event makes the Comparator B boundary more than a speech or announcement chain. It adds the legal-handoff layer that helps explain how the move into Level 2 became administratively workable.

### `nz-b-001`

- `timestamp_or_date`: `2020-05-13`
- `issuing_unit`: `emergency-management coordination`
- `receiving_units`: `strategic executive coordination`; `public-information coordination`; `enforcement and compliance`
- `action_type`: end of the state of national emergency and beginning of the national transition period
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-beehive-state-national-emergency-ended-2020`; `src-oag-covid-response-2022` (Part 5, para. 5.23); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event marks the legal and operational handoff that leads directly into Comparator B. It is a good example of a lower-acuity but still system-wide coordination shift.

### `nz-b-002`

- `timestamp_or_date`: `2020-05-14`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-information coordination`; `enforcement and compliance`; `public-service system coordination`
- `action_type`: move to Alert Level 2 and start of the lower-acuity comparator window
- `dependency_type`: `directive or authority dependency`; `public-communication dependency`; `legal or compliance dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `alert-level communication`
- `source_citation`: `src-beehive-level-2-announcement-2020`; `src-oag-covid-appendix1-2022`; `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

Comparator B only works if this transition is treated as a real coordination shift instead of a quiet tail end of the same crisis block.

### `nz-b-003`

- `timestamp_or_date`: `2020-06-08`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `emergency-management coordination`; `public-information coordination`; `enforcement and compliance`
- `action_type`: move to Alert Level 1 and end of the national transition period
- `dependency_type`: `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `alert-level communication`
- `source_citation`: `src-beehive-alert-level-1-2020`; `src-beehive-national-transition-period-ends-2020`; `src-oag-covid-response-2022` (Part 5, paras. 5.23-5.24); `src-royal-commission-phase-one-2024`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This closes Comparator B cleanly and marks the point where the most extraordinary emergency powers fall away.

## What this baseline ledger already demonstrates

At the current baseline level, the route now has:

- clear cross-unit events
- visible shifts in authority, public communication, and implementation pressure
- direct event-page support for border, alert-level, transition-law, enforcement-guidance, extended-Level-4 enforcement continuity, stranded-people planning, managed-isolation welfare coordination, emergency-powers guidance, Level 3 authority routing, Level 3 review preparation, and local-authority/CDEM support shifts
- direct DPMC action-plan, operating-system, public-information, and Level 4 review surfaces for the architecture and easing chain
- enough structure to begin testing simple `I`, `C`, and `L` summaries against real coded material
- enough window depth to support the current conjoint `I/C/L` comparison without pretending the route is universal or final

What it does **not** yet demonstrate:

- exhaustive chronology
- final lag values
- final edge weighting
- final comparator execution

## Next build step

The next deliberate reopening should:

1. keep this New Zealand baseline stable and reproducible unless a later phase needs deliberate reopening
2. shift the next empirical burden to Taiwan chapter completion and then Australia comparator construction
3. reopen the New Zealand route further only if later phase work needs more than the now-lower-priority briefing, public-information, or wider-window additions

## Status

`public baseline ledger`
