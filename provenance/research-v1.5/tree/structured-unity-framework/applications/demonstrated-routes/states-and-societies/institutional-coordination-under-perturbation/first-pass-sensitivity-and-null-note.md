# First-Pass Sensitivity and Null Note

## Purpose

This file is the current bounded sensitivity and null check for the New Zealand demonstrated route.

It does **not** claim full robustness. It asks a narrower question:

does the route's current bounded gain survive reasonable perturbations and null framings, or does it collapse as soon as the ledger is stressed?

Primary companions:

- [Event Ledger Seed](event-ledger-seed.md)
- [Measurement Implementation](measurement-implementation.md)
- [First-Pass Seed Readout](first-pass-seed-readout.md)
- [First-Pass Window Comparison](first-pass-window-comparison.md)

## Rule for this pass

This note now works from the current `38`-event public ledger and keeps the bounded check set at `14` tests total:

- `10` perturbation checks
- `4` null framings

The point is still modest: test whether the route immediately falls apart under plausible stress, not whether it is already measurement-complete.

## Baseline reference

Current baseline:

- `38` total coded events
- `29` main-interval events
- `strategic executive coordination` issues `25 / 38`
- `public-information coordination` receives `33 / 38`
- weighted cross-cluster routing = `107 / 142 = 0.75`

## Sensitivity check 1: remove the most architecture-heavy observation events

Perturbation:

- remove `nz-a-001`
- remove `nz-p-007`

What survives:

- `36` coded events remain
- the main interval still contains `28` events
- `strategic executive coordination` still issues `23 / 36`
- `public-information coordination` still receives `31 / 36`
- all `7 / 7` `sigma1` units still remain active

Reading:

The route does not depend only on a couple of architecture-observation events. The hub-centred shape and the public-information pattern remain visible without them.

## Sensitivity check 2: reassign one implementation paper away from the strategic centre

Perturbation:

- reassign `nz-p-015` from `strategic executive coordination` to `public-service system coordination`

What survives:

- `strategic executive coordination` still issues `24 / 38`
- inside the main interval, the strategic centre still issues `18 / 29`
- `public-information coordination` still receives `33 / 38`
- all `7 / 7` units remain active

Reading:

The route becomes slightly less monopolized by the strategic centre, which is exactly why this perturbation matters. But the route still reads as hub-centred rather than flat.

## Sensitivity check 3: split one bundled escalation event into two same-day events

Perturbation:

- split `nz-p-010` into:
  - a Level 3 transition announcement event
  - a Level 4-in-48-hours escalation-preparation event

What survives:

- the ledger rises from `38` to `39` events
- `strategic executive coordination` rises to `26 / 39`
- the main interval rises from `29` to `30` events
- `public-information coordination` still receives `34 / 39`
- the route still preserves non-zero lag between the `2020-03-23` announcement side and the `2020-03-25` implementation side

Reading:

The route does not flatten under same-day splitting. If anything, the acute escalation chain looks more visibly sequenced.

## Sensitivity check 4: remove the Comparator B legal-handoff event

Perturbation:

- remove `nz-b-005`

What survives:

- Comparator B still contains `6` coded events
- Comparator B still keeps `6 / 7` active units
- Comparator B still has explicit public-information markers in `4 / 6` remaining events
- the lower-acuity transition window still looks more coherent and denser than Comparator A

Reading:

Comparator B becomes thinner, but it does not collapse into a mere labeling artifact.

## Sensitivity check 5: boundary-cut perturbation

Perturbation:

- remove `nz-p-019`
- remove `nz-p-023`

Why these two:

- they sit on the welfare and boundary-handling edge of the implementation layer
- a skeptical reader could argue they are helpful thickening rather than core coordination

What survives:

- `36` coded events remain
- the main interval still contains `27` events
- `strategic executive coordination` still issues `24 / 36`
- `public-information coordination` still receives `32 / 36`

Reading:

The route loses some welfare and boundary detail, but the main structural payoff still holds.

## Sensitivity check 6: `sigma2` cluster-reassignment perturbation

Perturbation:

- reclassify `public-service system coordination` from the strategic cluster into the response-operations cluster

What changes:

- weighted cross-cluster routing rises from `107 / 142 = 0.75` to `120 / 142 = 0.85`

Reading:

The integration reading does **not** depend on one favorable `sigma2` placement. Under this reassignment, the cross-cluster signal becomes stronger, not weaker. That means the current clustering choice is conservative for the route's integration claim.

## Sensitivity check 7: chronology-gap / missingness perturbation

Perturbation:

- remove `nz-p-023` as if the local-authority/CDEM welfare-support paper were missing from the public record

What survives:

- the ledger falls only to `37` events
- the main interval still contains `28` events
- `strategic executive coordination` still issues `25 / 37`
- `public-information coordination` still receives `33 / 37`

Reading:

The route does not depend on perfect completeness in one late-April implementation paper. Missingness weakens detail, but not the current bounded gain.

## Sensitivity check 8: interval-boundary perturbation

Perturbation:

- remove `nz-p-019`
- remove `nz-p-020`

Why these two:

- they are the strongest left-side implementation-thickening events inside the post-lockdown build-out

What survives:

- `36` coded events remain
- the main interval still contains `27` events
- `strategic executive coordination` still issues `24 / 36`
- `public-information coordination` still receives `31 / 36`

Reading:

Even if the early-April implementation thickening were thinner than currently coded, the route would still retain a dense main interval with a visible strategic centre and strong public-information involvement.

## Sensitivity check 9: backup-proxy substitution check

Perturbation:

- treat `src-police-covid-major-events-2020` as the sole surviving support surface for `nz-p-024`
- leave the dedicated `src-police-level-3-following-rules-2020` page out of the coded backup

What survives:

- the ledger remains at `38` events
- the main interval remains at `29` events
- the event set and route metrics remain unchanged

Reading:

The route does not depend on one dedicated Police page for the late-April continuity claim. The backup chronology surface is enough to preserve the event without changing the structure.

## Sensitivity check 10: official-core versus extended-core boundary comparison

Perturbation:

- compare the earlier `30`-event official core against the current `38`-event extended official ledger

What changes:

- total events rise from `30` to `38`
- main-interval events rise from `23` to `29`
- `public-information coordination` receiving share rises from `25 / 30` to `33 / 38`
- weighted cross-cluster routing shifts only from `86 / 113 = 0.76` to `107 / 142 = 0.75`

Reading:

The route's bounded gain survives extension. The added continuity, authority-routing, and review events change density and timing detail more than they change the basic structural story.

## Null check 11: treat public-information coordination as downstream messaging only

Null framing:

public-information coordination is only an output wrapper around "real" executive action and should not count as part of the route's working coordination architecture.

Why the null is weak:

- `public-information coordination` receives `33 / 38` coded events
- it remains active across late-April Police guidance, the formal Level 3 authority-routing and review papers, the transition-planning briefing, Comparator B legal handoff, and the move to Level 1
- it is visible not only at acute alert-level transitions but also in compliance guidance, checkpoint governance, and continuity reminders

Reading:

To preserve this null, a reader has to discard a large amount of visible routing activity.

## Null check 12: collapse decision and implementation into the same moment

Null framing:

decision and implementation are effectively the same moment, so lag should not count as a meaningful category.

Why the null is weak:

- the current public ledger still contains paired gaps of `1`, `2`, `2`, `3`, `8`, and `8` days
- those pairs span both acute escalation and later easing transitions
- the added review material thickens the de-escalation context without erasing the staged gaps

Reading:

This null erases visible structure that is already present even at date grain.

## Null check 13: lag-flattening null

Null framing:

the observed paired gaps are too small and too few to matter, so the route should be read as if all major transitions were same-day or operationally instantaneous.

Why the null is weak:

- the current lag surface still shows both compressed short staging and two longer `8`-day preparation intervals
- the median paired gap is now `2.5` days rather than `0`
- flattening the lag surface destroys the distinction between acute escalation, transition planning, and legal handoff

Reading:

The lag surface is still coarse, but it is not empty. A zero-lag reading is less faithful to the public record than a short-to-moderate staging reading.

## Null check 14: full sequence-shuffle null on the main interval

Null framing:

the main interval's order does not matter; it is only a dense bag of crisis events.

Why the null is weak:

- the current main interval still reads as ordered escalation, implementation thickening, authority-review preparation, easing preparation, and late-transition continuity
- shuffling destroys the visible `2020-03-23 -> 2020-03-25`, `2020-04-20 -> 2020-04-28`, and Comparator B staging chains
- once order is destroyed, the route loses coherence but not density, which shows that sequence is doing real analytical work

Reading:

This null is useful precisely because it fails: the route's current payoff depends on ordered coordination structure, not only event accumulation.

## First bounded conclusion

The most defensible current sensitivity/null reading is:

**The route's current bounded gains survive architecture-event removal, issuer reassignment, same-day splitting, Comparator B legal-handoff removal, welfare/boundary cuts, chronology-gap perturbation, interval-boundary thinning, source-backup substitution, and official-core versus extended-core comparison. They also remain stronger than the four flattest null framings currently available.**

What survives coarse perturbation:

- the route remains hub-centred
- the main interval remains dense
- public-information coordination remains structurally central
- Comparator B remains analytically real rather than a pure labeling artifact

What survives measurement-aligned perturbation:

- the integration claim does not depend on one favorable `sigma2` clustering
- the coherence claim does not depend on one bundled same-day event
- the current structural gain survives extension from the earlier `30`-event core to the `38`-event ledger

What still remains weak:

- the lag surface is still date-grain and sparse
- the route still lacks document-level contradiction coding
- the Taiwan comparison is now materially denser, but it remains bounded relative to the New Zealand branch

## Next best step

The next practical move is to:

1. keep adding direct D-family `D` and `E` events only under the live-plus-fixed-archive rule
2. rerun the same robustness frame after a later Taiwan de-escalation tranche or second comparator route is in place
3. then move from bounded robustness checks toward a more explicit measurement-stage perturbation program

## Status

`expanded first-pass sensitivity and null note`
