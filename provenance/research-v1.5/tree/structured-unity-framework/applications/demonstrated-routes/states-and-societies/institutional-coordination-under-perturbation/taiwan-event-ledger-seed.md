# Taiwan Event Ledger Seed

## Purpose

This file is the current archive-clean public event ledger for the Taiwan comparator branch.

It is not a full Taiwan route. It is a bounded official seed built to test whether the same route-local logic can support a denser external comparison.

## Current posture

Current status: `extended comparative ledger`

This seed remains conservative:

- only official Taiwan CDC / CECC materials with fixed archives are admitted
- the current focus is activation, border control, quarantine support, quarantine compliance, and one direct public-alignment surface
- the seed is functionally matched to the New Zealand route, not date-matched

## Summary list

| Event ID | Date | Short description |
|---|---|---|
| `tw-a-001` | `2020-01-20` | CECC activated as cross-agency command centre |
| `tw-a-002` | `2020-01-21` | first imported case identified through onboard quarantine and routed to designated hospital |
| `tw-a-003` | `2020-01-22` | Taoyuan Airport Response Center formed to implement CECC border-quarantine measures |
| `tw-p-013` | `2020-02-01` | entry response measures convened for travelers from outbreak areas |
| `tw-p-006` | `2020-02-08` | entry home-quarantine requirements tightened for specified transit and endemic-area travelers |
| `tw-p-014` | `2020-02-14` | Entry Quarantine System launched for passenger health declaration and home quarantine |
| `tw-p-015` | `2020-03-11` | outbreak response measures launched for 48th confirmed case |
| `tw-p-016` | `2020-03-14` | travel notice raised to Level 3 for Schengen countries with quarantine requirement |
| `tw-p-001` | `2020-02-15` | home-quarantine support and daily follow-up expectations clarified |
| `tw-p-002` | `2020-03-18` | foreign-entry restrictions and local-district quarantine procedure announced |
| `tw-p-003` | `2020-03-22` | airline passenger transit through Taiwan suspended |
| `tw-p-017` | `2020-03-24` | 20 imported cases response with contact tracing and quarantine reinforcement |
| `tw-p-004` | `2020-03-27` | home quarantine/isolation rules, local care/support centres, and sanctions clarified |
| `tw-p-010` | `2020-03-29` | health-agency notification and medical-care routing observed during home quarantine |
| `tw-p-011` | `2020-04-01` | people under home quarantine barred from domestic flight or ferry travel to offshore islands and transit ban extended |
| `tw-p-007` | `2020-04-01` | cumulative penalties and group-quarantine escalation clarified for quarantine breaches |
| `tw-p-012` | `2020-04-01` | phased social-distancing measures announced with conditional mandatory-rule surface |
| `tw-p-008` | `2020-04-02` | symptomatic inbound travelers routed by epidemic-prevention taxis to designated testing locations |
| `tw-p-009` | `2020-04-14` | Europe and Americas returnees required to notify health officials and use quarantine hotels where needed |
| `tw-p-005` | `2020-04-23` | direct-flight restrictions and transit ban extended |

## Seed events

### `tw-a-001`

- `timestamp_or_date`: `2020-01-20`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: activation of the CECC and cross-agency command-centre support
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-cecc-activation-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the architecture anchor. It makes early command-centre activation explicit and already links cross-agency support, quarantine, and public-information activity.

### `tw-a-002`

- `timestamp_or_date`: `2020-01-21`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `border-control coordination`; `public-service system coordination`; `public-information coordination`
- `action_type`: first imported case is identified through onboard quarantine and routed to a designated hospital with local-health-authority notification
- `dependency_type`: `information or reporting dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-first-imported-case-onboard-quarantine-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event gives the Taiwan branch an early implementation-observed border-to-health-routing surface. It makes the comparator less dependent on later March quarantine material for its first concrete implementation chain.

### `tw-a-003`

- `timestamp_or_date`: `2020-01-22`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `strategic executive coordination`; `public-health policy and command`; `public-service system coordination`; `public-information coordination`
- `action_type`: Taoyuan Airport Response Center is formed to implement CECC border-quarantine measures at the main point of entry
- `dependency_type`: `directive or authority dependency`; `resource or logistics dependency`; `information or reporting dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `none recorded`
- `source_citation`: `src-taiwan-airport-ihr`
- `confidence_note`: `medium-high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event exposes a distinct airport operating layer rather than leaving Taiwan's early branch as command-centre activation plus later bulletins. It improves border and logistics visibility without forcing a broader architecture rewrite.

### `tw-p-006`

- `timestamp_or_date`: `2020-02-08`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `public-health policy and command`; `border-control coordination`; `public-information coordination`
- `action_type`: entry home-quarantine requirements are tightened for Hong Kong and Macau transit and for travelers returning from specified epidemic areas
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-all-travelers-home-quarantine-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event thickens the early border-to-quarantine routing chain before the later support note. It makes the comparator less dependent on retrospective architecture plus later March escalation even though it is not yet a universal entry restriction.

### `tw-p-001`

- `timestamp_or_date`: `2020-02-15`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: clarification of home-quarantine support, daily follow-up, and airport/port notification expectations
- `dependency_type`: `information or reporting dependency`; `public-communication dependency`; `directive or authority dependency`
- `implementation_marker`: `implementation clarified`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-home-quarantine-support-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This is an early support-and-follow-up event rather than only a border headline. It shows quarantine as a routed care and reporting arrangement.

### `tw-p-002`

- `timestamp_or_date`: `2020-03-18`
- `issuing_unit`: `strategic executive coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: restriction of foreign entry and routing of travelers into home-quarantine procedure through local district offices
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-entry-restrictions-home-quarantine-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the clearest bounded event for the Taiwan border-plus-local-administration routing chain.

### `tw-p-003`

- `timestamp_or_date`: `2020-03-22`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `border-control coordination`; `public-information coordination`
- `action_type`: suspension of airline passenger transit through Taiwan
- `dependency_type`: `directive or authority dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-transit-ban-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is a clean border-intensification event and a useful matched contrast with New Zealand's later transit and border tightening.

### `tw-p-004`

- `timestamp_or_date`: `2020-03-27`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: clarification of home-quarantine and home-isolation rules, local care/support routing, and sanction language
- `dependency_type`: `legal or compliance dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation clarified`
- `public_information_marker`: `enforcement or compliance communication`
- `source_citation`: `src-taiwan-home-quarantine-isolation-regulations-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This makes the Taiwan branch less purely border-focused. It exposes local support centres, daily follow-up, and sanction logic in one official surface.

### `tw-p-010`

- `timestamp_or_date`: `2020-03-29`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `public-service system coordination`; `public-information coordination`
- `action_type`: health agencies are notified during home quarantine, medical care is arranged, and household contacts are placed into home isolation in confirmed imported-case handling
- `dependency_type`: `information or reporting dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-home-quarantine-health-agency-routing-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This is the clearest implementation-observed event yet in the Taiwan branch. It makes one conservative lag pair visible by showing the March 18 quarantine-routing chain not only announced, but later observed in health-agency notification and medical-care handling during home quarantine.

### `tw-p-011`

- `timestamp_or_date`: `2020-04-01`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: people under home quarantine are prohibited from domestic flight or ferry travel to offshore islands and the passenger-transit ban is extended to April 30
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-home-quarantine-domestic-travel-ban-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event improves the Taiwan branch's transport and local-routing visibility. It shows the quarantine regime reaching beyond inbound screening into domestic movement control for offshore-island travel while also carrying the transit-ban continuity forward.

### `tw-p-007`

- `timestamp_or_date`: `2020-04-01`
- `issuing_unit`: `enforcement and compliance`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: cumulative penalties and group-quarantine escalation clarified for home quarantine and home isolation breaches
- `dependency_type`: `legal or compliance dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `implementation clarified`
- `public_information_marker`: `enforcement or compliance communication`
- `source_citation`: `src-taiwan-cumulative-penalties-home-quarantine-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event improves the comparator's implementation-side thickness beyond border restriction headlines. It makes sanction logic and quarantine enforcement more legible as routed coordination rather than background compliance noise.

### `tw-p-012`

- `timestamp_or_date`: `2020-04-01`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `public-service system coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: phased social-distancing measures are announced with voluntary guidance first and conditional mandatory rules if needed later
- `dependency_type`: `public-communication dependency`; `legal or compliance dependency`; `information or reporting dependency`
- `implementation_marker`: `official guidance update`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-social-distancing-measures-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event gives the Taiwan branch a clearer public-alignment surface inside the acute window. It reduces the sense that the comparator is only border and quarantine administration by adding one direct public-behavior coordination layer.

### `tw-p-008`

- `timestamp_or_date`: `2020-04-02`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: symptomatic inbound travelers at airport or port routed by epidemic-prevention taxis to designated testing and medical-evaluation locations starting April 3
- `dependency_type`: `directive or authority dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-symptomatic-travelers-designated-location-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds a cleaner operational routing chain between the border surface and downstream medical handling. It improves functional separation inside the Taiwan branch without requiring a broader architecture rewrite.

### `tw-p-009`

- `timestamp_or_date`: `2020-04-14`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: inbound travelers from Europe and the Americas required to notify health officials before return and use quarantine hotels when home conditions are unsuitable
- `dependency_type`: `directive or authority dependency`; `resource or logistics dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-quarantine-hotels-europe-americas-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event gives the Taiwan branch a more visible quarantine-logistics layer. It makes the comparator less command-centre thin by exposing accommodation and vulnerability-management routing inside the border-control chain.

### `tw-p-005`

- `timestamp_or_date`: `2020-04-23`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `border-control coordination`; `enforcement and compliance`; `public-information coordination`
- `action_type`: extension of direct-flight restrictions and passenger-transit ban
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `implementation continued`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-transit-extension-2020`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This supplies continuity for the acute border-control window instead of leaving the bounded tranche as a one-shot closure sequence.

### `tw-p-013`

- `timestamp_or_date`: `2020-02-01`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `strategic executive coordination`; `public-health policy and command`; `public-information coordination`
- `action_type`: entry response measures convened for travelers from outbreak areas including expert meeting and differentiated entry procedures
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-entry-response-2020-02-01`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This event fills the early February gap between airport activation and the February 8 quarantine tightening. It makes the Taiwan branch less dependent on a single February border event by exposing early differentiated-entry coordination.

### `tw-p-014`

- `timestamp_or_date`: `2020-02-14`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: Entry Quarantine System launched for passenger health declaration and home quarantine information system to expedite immigration clearance
- `dependency_type`: `directive or authority dependency`; `information or reporting dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation initiated`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-entry-quarantine-system-2020-02-14`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`

Why it matters:

This event distinguishes the quarantine information system launch from the February 15 support clarification. It makes the Taiwan border-logistics chain thicker by exposing the technical infrastructure that enables later quarantine routing.

### `tw-p-015`

- `timestamp_or_date`: `2020-03-11`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `strategic executive coordination`; `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: outbreak response measures launched for 48th confirmed case including epidemiological investigation and contact tracing
- `dependency_type`: `information or reporting dependency`; `public-communication dependency`; `resource or logistics dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-outbreak-response-2020-03-11`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event fills the March gap between February quarantine clarification and March 18 entry restrictions. It exposes implementation-observed contact-tracing coordination before the major border escalation.

### `tw-p-016`

- `timestamp_or_date`: `2020-03-14`
- `issuing_unit`: `border-control coordination`
- `receiving_units`: `strategic executive coordination`; `public-health policy and command`; `border-control coordination`; `public-information coordination`
- `action_type`: travel notice raised to Level 3 for Schengen countries with mandatory 14-day home quarantine for arriving travelers
- `dependency_type`: `directive or authority dependency`; `legal or compliance dependency`; `public-communication dependency`
- `implementation_marker`: `decision announced`
- `public_information_marker`: `official guidance update`
- `source_citation`: `src-taiwan-schengen-level3-2020-03-14`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event adds a distinct regional targeting layer to the border escalation. It makes the Taiwan comparator's border-tightening sequence more granular than a single March 18 announcement.

### `tw-p-017`

- `timestamp_or_date`: `2020-03-24`
- `issuing_unit`: `public-health policy and command`
- `receiving_units`: `strategic executive coordination`; `public-health policy and command`; `public-service system coordination`; `border-control coordination`; `public-information coordination`
- `action_type`: 20 imported cases response with epidemiological investigation, contact tracing, and quarantine reinforcement for Navy cluster
- `dependency_type`: `information or reporting dependency`; `resource or logistics dependency`; `public-communication dependency`
- `implementation_marker`: `implementation observed`
- `public_information_marker`: `major public briefing`
- `source_citation`: `src-taiwan-navy-cluster-response-2020-03-24`
- `confidence_note`: `high`
- `scale_tag`: `sigma1`; `sigma2`; `sigma3`

Why it matters:

This event fills the late March gap between March 22 transit suspension and March 27 quarantine regulations. It exposes implementation-observed cluster-response coordination and thickens the acute window without requiring later de-escalation material.

## Current readout cues

- total seeded events: `20`
- active `sigma1` units visible: `6 / 7`
- active directed edges: `21`
- weighted cross-cluster edge share: `43 / 73 = 0.59`
- mean receiving breadth: `3.6`
- issuing concentration: `public-health policy and command` issues `9 / 20`; `border-control coordination` issues `9 / 20` seeded events
- public-information coordination receives `20 / 20` seeded events

## Current limit

The Taiwan branch is still thinner than the New Zealand route and still lacks a distinct emergency-management layer, even after the early airport and public-alignment additions. It now carries a denser early border-health chain and more function-specific issuing than the original starter tranche, but it still supports only one conservative lag pair and it is still not enough for a strong comparative conclusion.

## Status

`extended comparative ledger`
