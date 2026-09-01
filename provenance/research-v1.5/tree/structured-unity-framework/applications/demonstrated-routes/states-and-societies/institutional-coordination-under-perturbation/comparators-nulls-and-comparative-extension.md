# Comparators, Nulls, and Comparative Extension

## Comparator A - ordinary-governance baseline

Window: `2019-11-01` to `2020-01-31`

Purpose:

- provide a same-system pre-perturbation baseline
- distinguish crisis-specific coordination from ordinary governance activity
- preserve institutional continuity while lowering perturbation intensity

## Comparator B - lower-acuity de-escalation contrast

Window: `2020-05-14` to `2020-06-07`

Purpose:

- compare the high-acuity lockdown arc with a lower-acuity de-escalation period inside the same broad response cycle
- test whether the route can detect meaningful changes in integration, coherence, and latency rather than treating the whole crisis interval as one undifferentiated block
- hold the overall case boundary steady while reducing response intensity

Implementation note:

This window is aligned to the official alert-level chronology used in the Office of the Auditor-General and Royal Commission source base. If event-ledger assembly exposes a source-level timestamp discrepancy, adjust by at most one day and record the reason explicitly.

## Nulls

### Structural null

**Dependency shuffle / relation-preserving size null**

Test whether structured dependency matters beyond mere system size and event volume.

### Temporal null

**Sequence shuffle null**

Test whether temporal organization matters beyond event content alone.

### Sensitivity nulls to keep available

- cluster-reassignment sensitivity
- boundary-perturbation sensitivity
- lag-randomization sensitivity
- coding-rule perturbation sensitivity

## Robustness plan

Check the route against:

- alternate edge cuts around interval boundaries
- unit merges and splits at `sigma1`
- alternative cluster assignments at `sigma2`
- primary and backup proxy bundles
- missingness and chronology gaps
- official-core versus extended-core boundary variants

## Comparative shortlist

### Taiwan

Use as the recommended first comparator for:

- stronger SARS-era preparedness and earlier command-centre activation
- sharper comparison on early border management, tracing, and coordination speed
- a public official source base through the Taiwan CDC and CECC that makes timing and command architecture visible

Comparability limits:

- prior epidemic experience materially changes the baseline
- legal and surveillance arrangements differ from New Zealand's public-law environment
- unit matching must stay functional rather than formal

Current state:

- [Taiwan Comparator Design](taiwan-comparator-design.md)
- [Taiwan Official Corpus Inventory](taiwan-official-corpus-inventory.md)
- [Taiwan Event Ledger Seed](taiwan-event-ledger-seed.md)
- [First NZ-Taiwan Comparison Note](first-nz-taiwan-comparison-note.md)

### Australia

Use as the recommended federal contrast for:

- intergovernmental coordination complexity through National Cabinet and AHPPC
- distributed implementation pressure across states and territories
- an official public source base through the Commonwealth Government COVID-19 Response Inquiry and Australian government health material

Comparability limits:

- federal structure changes the route topology
- state variation complicates one-to-one unit matching
- a bounded Australian route should likely focus on Commonwealth coordination or a deliberately delimited jurisdictional subset

## Status

`active comparative branch`
