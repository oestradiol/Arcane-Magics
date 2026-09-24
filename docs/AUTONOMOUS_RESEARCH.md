# Bounded autonomous research on GitHub

Venus-Minerva can run continuously, but autonomy is split into two layers.

## Layer 1 — deterministic steward

GitHub Actions may continuously run repository audits, verify authority/current-state invariants, inspect the public frontier queue, and emit a machine-readable steward report. This layer needs no model credentials.

## Layer 2 — model-backed research worker

A future model-backed worker may consume the frontier queue and attempt bounded research episodes, but it must obey this contract.

### Allowed

- select one open lane;
- read current authority and relevant source material;
- create a fresh branch;
- freeze one bounded question before seeing the result;
- run derivations, experiments, searches, formalization, or code changes;
- preserve failures and WITHHOLD outcomes;
- open a draft pull request for review.

### Forbidden

- direct push to `main`;
- force-push over published history;
- changing `prototype/CURRENT_STATE.md` merely because a newer artifact exists;
- promoting its own output to theorem, SOTA, physics, AGI, or consciousness;
- deleting negative evidence;
- using an execution receipt as independent return;
- treating self-generated evaluation as external verification;
- silently importing Canonical planning as Venus-Minerva authority.

### Promotion rule

A model-generated artifact remains a proposal until repository-local admission updates the appropriate authority/current-state surface.

```text
frontier task
-> prefreeze
-> bounded work
-> result
-> audit
-> draft PR
-> review / external return
-> explicit admission
-> authority update
```

## Suggested branch shape

`venus/<lane>/<YYYYMMDD>/<short-question>`

## Suggested proposal layout

```text
research/proposals/<episode>/
  PREFREEZE.md
  RESULT.md
  EVIDENCE/
  REPRODUCE.md
```

A failed episode should still be committed when it exposes a separator, invalid assumption, irreducible ambiguity, or useful negative result.

## Why draft PRs instead of self-merging?

Because the project distinguishes generation, evaluation, external return, authorization, and promotion. The automation should embody that distinction rather than merely describe it.

## "Cook forever" mode

```text
scheduled steward
-> choose bounded debt
-> model worker attempts one episode
-> draft PR
-> external/human review
-> merge or reject
-> next episode
```

This can run indefinitely without granting the worker unilateral authority over the research record.
