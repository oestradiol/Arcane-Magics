# Research Design

## Purpose

This file locks the New Zealand route to a research-ready provisional design. The bundle is specific enough to support source assembly and coding, while still avoiding fake precision.

## Boundary

The route covers New Zealand's core all-of-government pandemic coordination apparatus during the first acute response cycle.

Included by default:

- central executive coordination
- public-health command and policy core
- emergency-management coordination
- public-service system coordination
- border-control coordination
- enforcement and compliance
- official public-information coordination

Excluded by default:

- international actors outside the core apparatus
- undifferentiated public sentiment
- media as a total field
- downstream actors included only for symbolic prominence

## Unitization and scales

### `sigma1` units

1. strategic executive coordination
2. public-health policy and command
3. emergency-management coordination
4. public-service system coordination
5. border-control coordination
6. enforcement and compliance
7. public-information coordination

### `sigma2` clusters

- strategic coordination
- response operations
- public alignment

### `sigma3`

- whole-system bounded coordination readout

## Temporal windows

- main perturbation interval: `2020-02-28` to `2020-06-08`
- Comparator A: `2019-11-01` to `2020-01-31`
- Comparator B: `2020-05-14` to `2020-06-07`

Comparator B is the lower-acuity de-escalation window. It is anchored to the official alert-level chronology and can shift by at most one day only if a source-level timestamp discrepancy appears during event-ledger assembly.

## Hypothesis family

- `H1`: stronger coordination dependency density and cross-unit participation should support stronger unity-like organization
- `H2`: stronger directive consistency and coordinated sequencing should support more stable unity-like organization
- `H3`: latency should shape when and how unity-like organization appears rather than acting as a simple binary gate
- `H4`: different windows and scales should reveal different degrees and forms of unity-like organization
- `H5`: perturbation should make dependency, coherence, and lag structure more visible than ordinary-governance periods

## Primary measurement bundle

### `I` - integration

Default readout: weighted coordination-dependency graph summaries centered on:

- dependency density
- cross-cluster connectivity
- participation breadth

### `C` - coherence

Default readout: rolling alignment-persistence summaries centered on:

- directive consistency
- stability of coordinated sequencing
- cross-unit convergence

### `L` - latency

Default readout: decision-to-implementation lag summaries centered on:

- median lag by unit and by chain
- dispersion of lag across units and chains
- lag changes across Comparator A, the perturbation interval, and Comparator B

### `U` - unity-like organization

Default readout: a dashboard-style conjoint signature rather than a single scalar. Interpret `U` comparatively against Comparator A and Comparator B and always at explicit `(tau, sigma)`.

## Weakening conditions

The route weakens the current framing if these patterns recur:

- stronger `I` and `C` with no meaningful `U` improvement at any sensible scale
- low-coherence intervals with indistinguishable durable `U` signatures
- latency adding no explanatory value after scale adjustment
- unitization changes radically altering interpretation
- nulls matching or outperforming the structured `I` / `C` / `L` reading

## Research posture

This design is now sufficiently locked for public research use. What remains open are measurement implementation choices, corpus completeness, and later comparative execution, not the basic route architecture.

## Status

`research-ready route`
