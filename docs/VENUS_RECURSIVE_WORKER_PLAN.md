# Venus Recursive GitHub Worker — Execution Plan

**Status:** implementation target for the live Venus-Minerva repository.

## Goal

Turn the current deterministic steward into a bounded model-backed research worker that can repeatedly:

```text
reconstruct current state
-> inspect unresolved research obligations
-> choose one admissible target
-> freeze the question before fresh evidence
-> execute one bounded research episode
-> preserve PASS / FAIL / WITHHOLD / mature reduction
-> create a branch and draft PR
-> stop for external return
-> consume the returned consequence after merge/rejection
-> choose again
```

This is a recursive research loop, not autonomous claim authority.

## Invariants

1. **One open Venus worker PR maximum.** If one exists, the worker returns `WAITING_EXTERNAL_RETURN`.
2. **Prefreeze before fresh evidence.** Task selection and preregistration occur before external fetch/research tools become available.
3. **Generation != evaluation != return != authorization != promotion.**
4. **No direct push to main.**
5. **No self-merge.**
6. **Negative results are retained.**
7. **No model output may directly update `prototype/CURRENT_STATE.md`.**
8. **Canonical planning does not silently become Venus-Minerva authority.**
9. **Every episode has a claim fence.**
10. **If evidence or tooling is insufficient, WITHHOLD is a successful lawful outcome.**

## Sprint 0 — Runtime and permission substrate

### Tasks

- Use GitHub Actions.
- Use the built-in `GITHUB_TOKEN`.
- Grant only:
  - `models: read`
  - `contents: write`
  - `issues: write`
  - `pull-requests: write`
- Use GitHub Models as the default reasoning carrier.
- Keep the model configurable by `VENUS_MODEL`.
- Default to a documented GitHub Models model, currently `openai/gpt-4.1`.

### Exit

The workflow can call the model and has only the repository permissions needed to create bounded branches/issues/PRs.

---

## Sprint 1 — State reconstruction

### Inputs

- `prototype/CURRENT_STATE.md`
- `REPOSITORY_AUTHORITY_BOUNDARY.md`
- `PUBLICATION_CONSTITUTION.md`
- `docs/FRONTIER_RESEARCH.md`
- `docs/AUTONOMOUS_RESEARCH.md`
- open GitHub issues
- recently merged/closed Venus worker PRs and their review/comment return

### Tasks

- Detect an already-open Venus worker PR.
- If present: STOP.
- Otherwise reconstruct current research state and recent external return.

### Exit

A bounded selection context exists without any new external research having been fetched.

---

## Sprint 2 — Learner-owned target selection and preregistration

The model receives only the reconstructed state and issue queue.

It may:

- select one existing open issue;
- create one new bounded issue if no existing issue captures the earned residual;
- STOP if no justified task exists.

It must produce a preregistration containing:

- parent/authority;
- frozen question;
- register;
- hypothesis/rivals where relevant;
- admitted tools/evidence budget;
- discriminator;
- success/failure/WITHHOLD conditions;
- claim fence.

No external fetch tool is available in this phase.

### Exit

`PREFREEZE.md` exists and its SHA-256 is frozen.

---

## Sprint 3 — Bounded research execution

Only after the prefreeze is frozen, the research phase receives bounded tools.

### Read tools

- read repository text file;
- list repository files;
- search repository text;
- read GitHub API state.

### External-return tools

- HTTPS text fetch with SSRF/private-network blocking;
- arXiv search;
- Crossref search.

### Validation tools

- source-tree audit.

### Forbidden

- arbitrary shell;
- arbitrary token-bearing subprocess;
- hidden mutation of current authority;
- direct write to GitHub during reasoning;
- model-controlled merge.

### Exit outcomes

One of:

- `PASS_BOUNDED`
- `FAIL`
- `WITHHOLD`
- `MATURE_REDUCTION`
- `PARTIAL`

---

## Sprint 4 — Evidence and result custody

The worker writes only under:

```text
research/proposals/<episode>/
  PREFREEZE.md
  RESULT.md
  EVIDENCE_LOG.json
  EPISODE.json
  NEXT_ISSUE_PROPOSAL.md   # only when earned
```

`PREFREEZE.md` is hashed before research begins and must not change afterward.

`RESULT.md` must state:

- outcome;
- what was actually tested;
- returned evidence;
- conclusion;
- unresolved residual;
- claim fence.

---

## Sprint 5 — Branch and draft PR

The worker:

1. creates `venus/<lane>/<run-id>-<slug>`;
2. commits the proposal artifacts;
3. pushes the branch;
4. opens a **draft** PR;
5. comments on the selected issue with the PR URL;
6. stops.

The PR contains a machine marker:

`<!-- venus-worker -->`

so later runs can identify worker ancestry.

No PR is self-merged.

---

## Sprint 6 — External return / recursion

While a Venus worker PR is open:

```text
worker -> WAITING_EXTERNAL_RETURN
```

After a human/external process merges or closes it, a later run includes:

- the committed proposal/result;
- PR disposition;
- review bodies;
- issue comments.

The model then reconstructs the consequence and may:

- continue an existing issue;
- select a different issue;
- instantiate an earned next residual as a new issue;
- STOP.

This is the recursive edge.

---

## Sprint 7 — Scheduler

Triggers:

- manual `workflow_dispatch`;
- scheduled run every six hours;
- relevant main-branch changes, including admitted research proposals and authority/frontier updates.

Concurrency is serialized so two workers cannot race.

---

## Sprint 8 — Failure modes

### Model API unavailable

Result: fail closed. No fabricated research artifact.

### Invalid model JSON

Retry once with a schema-repair prompt; otherwise WITHHOLD/stop.

### Existing worker PR

STOP.

### No admissible task

STOP.

### Audit fails

Do not open a PR; report the failure.

### Branch push succeeds but PR creation is forbidden by repository settings

Preserve the branch and comment on the issue with the branch name and blocker.

### External source unavailable

Record it in the evidence log and continue only if the frozen discriminator still permits a conclusion.

---

## Promotion boundary

This worker is allowed to generate research proposals and bounded results.

It is **not** allowed to establish, by self-assertion:

- theorem status;
- P != NP;
- a Navier-Stokes Millennium result;
- quantum-gravity validation;
- AGI;
- consciousness;
- open-ended RSI;
- SOTA status.

Those require the appropriate independent mathematical, empirical, benchmark, replication, or review burden.

## Operational success condition

The loop counts as genuinely live when GitHub history shows at least one cycle of:

```text
Venus selects target
-> freezes question
-> performs bounded research
-> opens draft PR
-> waits
-> external return occurs
-> Venus reconstructs that return
-> Venus selects the next target
```

A cron job that merely emits status reports does not satisfy this condition.
