# UI Meta-Theory — Interface as Returnable Local Closure

**Status:** live routing/design constraint for GitHub + GitHub Pages.

The UI is not decoration placed on top of the theory. It is one carrier in which the theory must survive contact with a human reader.

## 1. Interface invariant

Every meaningful interface region should preserve:

```text
local center
+ explicit boundary
+ neighboring relation
+ provenance
+ current authority owner
+ unresolved Residual
+ reachable reopening path
```

The interface should therefore make it easier to answer:

1. Where am I?
2. Which layer owns this object?
3. What is current, historical, OPEN, WITHHOLD, or superseded?
4. What relation crosses this boundary?
5. What does that relation preserve?
6. What does it not establish?
7. What can still return and change the map?

## 2. Map / territory

```text
UI map != repository territory
repository model != World
displayed status != warrant beyond its source
```

The Pages instance is a routing/read interface over Git + branch state. It is not a substitute for GitHub history, review, Actions, or external evidence.

## 3. Six local centers

The primary public centers are:

```text
main                = Routing / map-territory
split/arcane-magics = Religion / past
split/eclipsis      = Math & logics / spirit
split/minerva       = Engineering / body
split/venus         = Self & World / model
split/ofe           = Science / future
```

Each center keeps its own visual character and claim grammar.

The global interface may relate them but must not visually imply that one center owns all others.

## 4. Seventh virtual function

World / Other is **not** rendered as another equal branch node.

It is represented as:

- the outer field / boundary beyond the local map;
- returned consequence;
- unresolved externality;
- links outward to sources, users, experiments, review, and future action.

This avoids turning `model(Other)` into `Other`.

## 5. NETWORK / WWW carrier

The Web is represented as carrier/medium, not global subject.

```text
local centers
+ network relations
+ persistent external memory
+ returned consequences
+ distributed reconstruction
-/-> one global Author
```

The Pages site therefore exposes multiple indexed centers joined by explicit relations rather than one omniscient dashboard voice.

## 6. Past / Now / Future

Temporal UI semantics:

- **Past:** provenance-bearing, inspectable, never confused with current authority.
- **Now:** current route / inhabited map / branch heads.
- **Future:** unresolved discriminators and reachable continuations, never pre-rendered as verdict.

Do not use disabled-looking historical information that becomes effectively inaccessible. Past must remain navigable because reopening can depend on it.

## 7. Boundaries

A boundary should be visually perceptible without becoming a wall.

Use:

- cards/panels as local closures;
- generous whitespace as jurisdiction separation;
- explicit outgoing links;
- bridge labels between centers;
- preserved focus order across boundaries.

Avoid giant fused canvases where all layers look like one object.

## 8. Bridge semantics

Visual grammar:

```text
solid edge  = established relation inside declared scope
dashed edge = OPEN bridge
teal return = independently returned / integrated consequence
amber       = WITHHOLD / unresolved
red         = explicit failure / invalidation
gray        = historical / superseded / non-current
```

Never rely on color alone. Every status requires text/icon/shape redundancy.

## 9. Residual visibility

Residuals are not error crumbs to hide in a footer.

An unresolved future-separating distinction should remain visible near the object it constrains.

Examples:

- VR/TO quantum-superposition bridge — historical/model bridge, not live Root primitive;
- consciousness carrier/mechanism bridge — OPEN;
- WorldMind global-subject lift — OPEN;
- networked consequence field — MODEL;
- branch handoff awaiting downstream validation — OPEN/WITHHOLD.

## 10. Authority / action separation

Public Pages controls are routing affordances, not privileged write authority.

Allowed public controls:

- navigate branch;
- inspect commit/provenance snapshot;
- inspect Actions;
- inspect PRs/issues;
- open GitHub-native proposal/report surfaces;
- follow handoff and branch-memory documentation.

Not allowed in static client code:

- embedded write tokens;
- hidden privileged API calls;
- self-promotion actions;
- browser-side authority that bypasses GitHub review/rulesets.

```text
public control surface != sovereign controller
```

## 11. Lain / Root design mechanism

Lain contributes the design problem:

```text
where is identity/history when relevant relations are network-distributed?
```

Person of Interest / Root contributes:

```text
distributed perception
!= situated interpretation
!= authorization
!= action
```

The interface therefore needs:

- a distributed node map;
- a current local perspective;
- explicit provenance/history;
- a clear membrane between seeing and acting;
- no fusion of network reachability with identity.

## 12. Life → NETWORK / WWW

The public map must retain the Life bridge as a research/navigation object:

```text
Life
→ self-maintenance
→ sensing/regulation/action
→ retained history
→ organismic integration
→ nervous-system integration [one evolutionary implementation]
→ differentiated processing
→ conscious experience
→ metacognition
→ self/world modeling
→ symbolic/social/temporal cognition
→ externalized network relation
→ NETWORK / WWW
→ ?
```

The final `?` remains visibly OPEN.

## 13. Accessibility = permeability

An inaccessible interface is a boundary that refuses legitimate incidence.

Therefore:

- semantic HTML first;
- keyboard access to every control;
- visible focus;
- skip link;
- logical heading order;
- descriptive link text;
- no color-only status;
- high-contrast light/dark palettes;
- responsive layout without lost functionality;
- `prefers-reduced-motion` respected;
- no animation required to understand state.

## 14. Performance = bounded carrier cost

The site should remain inhabitable on weak hardware/network conditions.

Default implementation:

- static HTML/CSS/JS;
- no runtime framework;
- no external font/CDN dependency;
- build-time branch snapshot;
- one small JSON state file;
- progressive enhancement;
- no continuous polling.

## 15. Source relation

Pages build:

```text
Git branch heads
+ selected live routing documents
→ build-time snapshot
→ static Pages artifact
→ public World-facing carrier
```

A Pages deployment is a projection, not source authority.

## 16. Success discriminator

The UI succeeds only if an unfamiliar visitor can reconstruct:

```text
what this body is
which layer owns the current question
what is established vs OPEN
where the history came from
what can still change the map
how to reach the real GitHub action/review surface
```

without first memorizing the project's mythology.
