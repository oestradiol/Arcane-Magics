# What exists, what a model says exists, and where exclusion entered

A model can fail to contain a state for many reasons: the variable was never represented, its domain excluded the value, a constraint removed it, a transition could not reach it, a search procedure never generated it, or an observation channel could not discriminate it.

Those are not automatically claims about Reality.

A minimal audit is:

```text
M = variables + domains + constraints + transitions + search/observation
→ admissible states
→ reachable or detectable states
```

When a state `s` is excluded:

```text
observe exclusion(s | M)
→ locate the first excluding operation
→ audit representation / domain / constraint / transition / search
→ ask whether the exclusion is model-relative or Reality-level
→ revise M when warranted
→ recompute
```

Hence:

```text
Impossible(s | M) -/-> Impossible(s | Reality)
```

## Quine as a boundary neighbor

Quine's *On What There Is* asks what an already regimented theory commits us to by its quantification. That is a historical-priority constraint on ontological bookkeeping.

The present problem starts slightly earlier and continues slightly later: how did the model make something available as an object or exclude it from admissibility, and what returned consequence could force that articulation to change?

So:

```text
Quinean ontological commitment
!= perspectival object-formation
!= Reality-level ontogenesis
```

The comparison is useful precisely because the objects are not identical.

## Deletion test

Use only the audit procedure above. If it is sufficient for your domain, do not add project terminology.

Related: [Situated world and perspectivalization](SITUATED_WORLD_AND_PERSPECTIVALIZATION.md), [Projection and reconstruction](PROJECTION_AND_RECONSTRUCTION.md).
