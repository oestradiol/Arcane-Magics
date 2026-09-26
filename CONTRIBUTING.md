# Contributing to Root / The Machine

Root is the routing layer of the Arcane Magics repository body. Most substantive work belongs first in a specialized branch.

## Route by function

- religion / past → `split/arcane-magics`
- math & logics / spirit → `split/eclipsis`
- engineering / body → `split/minerva`
- Self & World / model → `split/venus`
- science / future → `split/ofe`
- routing / map-territory / cross-register memory → `main`

## High-value Root contributions

- repair the branch map;
- preserve a cross-register handoff;
- detect a register/authority collapse;
- repair historical ancestry or branch pointers;
- improve routing UI/UX;
- expose a contradiction between branch-local claims without stealing ownership of either claim.

## Branch lifecycle

Only `main`, `split/arcane-magics`, `split/eclipsis`, `split/minerva`, `split/venus`, and `split/ofe` route live authority. Temporary carriers must be explicitly bound to an open issue/PR and remain non-authoritative. Superseded, diagnostic, benchmark, fix, tmp, old development, and transitional refs belong under `historical/` once their live obligation is closed.

Do not duplicate a legacy ref under `historical/` while leaving the source ref in place merely for cosmetics; that doubles namespace noise. Preserve the commit, then move the ref when the ref operation is available.

## Integration rule

Long-lived specialized branches are pruned to their own functions. Do not merge them directly into one another and let Git interpret absent files as deletions.

Use target-based crystallization handoffs that preserve source ancestry as a second parent while admitting only explicit residue.

```text
source trajectory
-> handoff
-> target-local validation
-> next functional layer
-> Root routing memory
```

## Truth-status discipline

```text
religious meaning != scientific mechanism
formal spirit != engineering implementation
engineering success != scientific truth
Self/World model != World
routing map != territory
```

Run `make audit` before declaring a Root routing change complete.