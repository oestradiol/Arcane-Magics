# First-Pass `L` Summary

## Purpose

This file is the first bounded latency summary for the New Zealand demonstrated route.

It uses only date-grain pairings that are already visible in the public baseline ledger. The point is not to force precision. The point is to see whether the route already shows meaningful non-zero lags between major coordination decisions and their implementation.

## Rule for this pass

This `L` summary uses only clearly paired date-grain transitions that the current public baseline can support publicly.

Confirmed staged pairs in the seed:

- `2020-03-23` escalation announcement -> `2020-03-25` Level 4 implementation
- `2020-04-20` Level 3 move-date announcement -> `2020-04-28` Level 3 implementation
- `2020-05-06` Alert Level 2 preparation -> `2020-05-14` Level 2 implementation
- `2020-05-12` transition-period planning briefing -> `2020-05-14` Level 2 implementation
- `2020-05-11` Level 2 announcement -> `2020-05-14` Level 2 implementation
- `2020-05-13` transition-period legal handoff -> `2020-05-14` Level 2 implementation

These are still coarse. They are enough for a first bounded lag read, not for a final latency measurement.

The newly admitted DPMC events around `2020-03-31`, `2020-04-02`, `2020-04-09`, `2020-04-14`, `2020-04-21`, `2020-04-22`, `2020-05-04`, `2020-05-06`, `2020-05-11`, and `2020-05-12` thicken the implementation context around these pairs. Under the current route-local pairing rule, the `2020-05-06` Level 2 preparation paper and the `2020-05-12` transition-period planning briefing remain the clearest additional clean public pairings on the de-escalation side.

## Current paired gaps

| Pair | Start | End | Date-grain gap |
|---|---|---|---:|
| Escalation staging | `2020-03-23` | `2020-03-25` | `2` days |
| Level 3 transition staging | `2020-04-20` | `2020-04-28` | `8` days |
| Level 2 preparation staging | `2020-05-06` | `2020-05-14` | `8` days |
| Transition-period planning to Level 2 | `2020-05-12` | `2020-05-14` | `2` days |
| Level 2 staging | `2020-05-11` | `2020-05-14` | `3` days |
| Legal handoff into Level 2 | `2020-05-13` | `2020-05-14` | `1` day |

### Simple summary

- paired gaps observed: `1`, `2`, `2`, `3`, `8`, `8` days
- date-grain median paired gap: `2.5` days
- observed range: `1-8` days

## First minimal `L` reading

The most defensible current reading is:

**The seed route already shows short-to-moderate non-zero staging lags, which suggests a coordination system that is neither instantaneous nor randomly delayed, but operating through compressed and variable preparation intervals. The current lag surface now spans acute escalation, two longer easing-preparation intervals, transition planning, legal handoff into de-escalation, and a denser review context around the Level 2 shift.**

That matters because:

- the route is not treating decision and implementation as the same moment
- the route can already distinguish announcement-side shifts from implementation-side shifts
- the system appears to use deliberate staging windows at major transition points
- the easing side of the route can involve longer preparation than the acute lockdown shift

## Why this matters

This is the first point where latency stops being just a theoretical category in the package.

Even with only date-grain public pairings, the route can already say something concrete:

- major transition events tend to be staged over short intervals
- those intervals are small enough to support crisis compression
- but they are not zero, so the route should not collapse decision and implementation into one time point

## Limits

This first pass still lacks:

- time-of-day precision
- unit-specific lag chains
- event-pair abundance outside major transition points
- robust missingness treatment
- any serious comparison of lag dispersion across windows beyond the first conjoint pass

## Next best step

The next practical move is to:

1. keep distinguishing announcement, legal activation, and observed implementation more carefully
2. add more direct implementation-chain events only when they satisfy the live-plus-fixed-archive rule
3. then test whether the main interval's broader lag spread survives denser coding and boundary cuts

## Handoff Statement

This operationalization traces: **SP temporal field/sequence** → **IA distinction propagation delays** → **UD L (Latency via announcement-implementation lag pairs)**

## Status

`first-pass L summary`
