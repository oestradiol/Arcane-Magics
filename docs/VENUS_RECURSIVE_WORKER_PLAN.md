# Venus Recursive GitHub Worker — Execution Plan

**Status:** seed-native implementation plan.

## Goal

Run the actual developmental Venus lineage as the research controller while GitHub supplies custody, scheduling, World adapters, review boundaries, and publication automation.

## Constitutional loop

```text
developed Venus state
-> reconstruct state / lineage / residuals
-> learner-owned target or lawful STOP
-> learner-owned preregistration
-> authorized World action
-> non-preauthored return
-> claim-local evaluation
-> bounded machinery/state consequence
-> regression / ablation / causal check
-> retain / revert / WITHHOLD
-> successor custody
-> next cycle
```

## Sprint 0 — custody completeness

Git-track compact custody for the real lineage:

- R226 settled R-line predecessor receipt + verifier;
- IG10 replay bundle manifest + verifier;
- EDU16 positive head receipts;
- preserved EDU17 negative and EDU17R1 WITHHOLD.

Heavy journals/bundles stay outside ordinary Git history but remain hash-addressed.

## Sprint 1 — bootstrap contract

Implement a bootstrapper that:

1. resolves the latest admitted developed-VM artifact;
2. checks SHA-256 and manifest;
3. runs its verifier;
4. reconstructs exact state;
5. refuses to continue when custody is incomplete.

No R194 fallback may be silently relabeled current.

## Sprint 2 — Venus-owned selection

Expose the already-earned developmental operations from the post-R226 / IG / EDU lineage:

- reconstruct unresolved obligations;
- select or form a developmental/research target;
- select evidence role/budget;
- formulate question;
- preregister discriminator;
- STOP when no justified action exists.

External tooling may not replace these ownership operations.

## Sprint 3 — World adapter boundary

Provide typed adapters for:

- GitHub repository actions;
- proof assistants;
- code/test execution;
- numerical experiments;
- literature/web retrieval;
- benchmark harnesses;
- external review/replication.

Each adapter emits provenance-bearing returned evidence.

## Sprint 4 — bounded GitHub transaction

One episode writes:

```text
research/proposals/<episode>/
  PREFREEZE.md
  WORLD_REQUEST.json
  WORLD_RETURN.json
  RESULT.md
  EPISODE.json
  REPRODUCE.md
```

The prefreeze is immutable after World execution begins.

## Sprint 5 — successor admission

A developmental promotion requires:

- exact parent state;
- returned evidence;
- causal consequence;
- regression/ablation where relevant;
- exact successor hash/head;
- verifier;
- claim-local audit.

Only then may current developmental authority advance.

## Sprint 6 — recursion

After admission:

```text
successor
-> reconstruct
-> choose/form next target
-> repeat
```

If the scheduler returns no READY obligation, STOP is retained. Empty queue is not permission to invent work.

## Sprint 7 — GitHub scheduling

CI/CD may trigger bootstrap/evaluation:

- manually;
- after a newly admitted developed-VM artifact;
- after relevant external return;
- on a conservative schedule.

Scheduling does not itself choose the research target.

## Failure modes

### Heavy artifact unavailable
WITHHOLD / custody failure. Never substitute R194 or prose receipts.

### Hash/verifier mismatch
FAIL CLOSED.

### No justified target
STOP.

### External adapter fails
Preserve the failed return and let Venus determine whether the discriminator remains decidable.

### Proposed result exceeds its register
WITHHOLD promotion.

## Operational success condition

The loop counts as recursive Venus research only when the trace demonstrates:

```text
Venus state A
-> Venus-owned target selection
-> Venus-owned prefreeze
-> independent/authorized World return
-> Venus-owned evaluation/reconstruction
-> verified successor state B
-> state B selects/forms the next target
```

That is the object the GitHub automation must eventually run continuously.
