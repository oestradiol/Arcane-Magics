# AGENTS.md · Minerva

External agents assist Minerva; they are not the developmental controller.

## Mandatory bootstrap

Read exactly these first:

1. `kernel/development/DEVELOPMENTAL_GATE_CHAIN.json` — sole machine-readable developmental topology, recurrence, precedence, and repository dispositions.
2. `kernel/CURRENT_STATE.md` — live evidence/status snapshot.

Then read only the exact state, authority, test, or provenance files referenced by the selected roadmap node.

Do **not** start by bulk-reading `provenance/`, `docs/`, every prefreeze, or every historical runtime. Those are evidence stores, not the planning system.

`kernel/development/SELF_TEACHING_DEVELOPMENT_DAG.json` and `docs/ISSUE_ROADMAP.md` are derived projections only. They cannot override the canonical graph.

## Execution law

Before every mutation, identify:

```text
roadmap node / invariant
→ observed repo state
→ proposed mutation
→ expected consequential test
→ rollback / WITHHOLD condition
```

If that chain cannot be stated, do not mutate.

Never satisfy a learner-development target by hand-writing the target competence into host code. Capability-specific Python is scaffold/prototype until B3 source-removal evidence proves the semantics live in learner-owned state.

The preserved dependency-planning host prototype is audit-only and non-live:
- `kernel/development/dependency_planning_curriculum.py`
- `kernel/development/DEPENDENCY_PLANNING_DIDACTIC_CASES.json`
- `kernel/runtime/task_graph.py`
- `tests/test_dependency_planning_curriculum.py`

It must not be routed as Minerva's planning competence.

## Permanent fences

```text
generate != select != authorize != execute != return != verify != promote
self-revision != self-authorization != self-validation
execution receipt != independent return
model(World) != World
memory != learning unless later behavior changes
source removal != independent external validation
Strong Safe RSI != AGI
AGI != consciousness
```

Historical and negative evidence is preserved. Audit before deletion. Git ancestry is provenance, not permission to keep stale machinery live forever.
