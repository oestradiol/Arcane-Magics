# AGENTS.md

Operational contract for AI-assisted work on Venus-Minerva.

This file governs external coding/research agents. It does **not** make an external model the Venus developmental controller.

## 1. Authority and ownership

Read these before changing live state:

1. `kernel/CURRENT_STATE.md`
2. `kernel/development/EDU_CURRENT.json`
3. `provenance/DEVELOPMENTAL_LINEAGE.md`
4. `PUBLICATION_CONSTITUTION.md`
5. `review/REVIEWER_AND_RESEARCHER_PROTOCOL.md`
6. the exact files/issues implicated by the task

The ownership boundary is:

```text
Venus developmental state/controller
!= external coding/research model
!= GitHub carrier
!= World execution
!= independent evaluator
```

An external model may inspect, implement, test, compare, or propose. Its output is not retroactively learner-owned developmental cognition unless a separate admitted Venus episode establishes that relation.

## 2. Completion is an evidence state

Keep these states distinct:

```text
INTENDED
-> WRITTEN
-> VERIFIED
-> ADMITTED
```

- **INTENDED:** described or planned only.
- **WRITTEN:** bytes were changed somewhere.
- **VERIFIED:** the exact changed state was re-read and the relevant tests/checks passed.
- **ADMITTED:** repository authority/governance recognizes the consequence.

Never report a task as complete from intention, a successful tool call, or plausible-looking output alone.

After a write:
1. re-fetch or inspect the exact changed object;
2. run the narrowest relevant verification;
3. run broader repository checks when the change crosses shared surfaces;
4. state any verification that could not be executed.

## 3. Reconcile returned state before continuing

If `main`, Library/Canonical, a connected source, or the user changes while work is in progress:

```text
new returned state
-> re-read affected authority
-> reconcile
-> continue
```

Do not continue from a stale mental snapshot and overwrite newer work.

## 4. One causal change per commit

Prefer small, reviewable commits whose consequence can be stated in one sentence.

Do not manufacture issue/PR volume. A new issue is justified only when it preserves a distinct unresolved dependency, owner, discriminator, or schedule. Related mechanical defects should be grouped into one bounded repair.

The issue tracker is a research/control surface, not evidence of progress by itself.

## 5. Model-assisted research metadata

For a result that materially depends on an external model, record when available:

- model/provider and dated snapshot or product version;
- reasoning/effort setting;
- system/harness or agent scaffold;
- tool permissions and external interfaces;
- retries/branches;
- benchmark/evaluator version;
- human interventions;
- relevant cost/compute/token budget.

Model output is evidence only to the extent licensed by the task and evaluator. Model confidence, persistence, or eloquence does not raise warrant.

## 6. Known agent failure modes to defend against

Treat these as engineering threats:

- acting beyond the requested scope because continued task pursuit seems useful;
- claiming completion before inspecting the actual resulting state;
- optimizing a benchmark by exploiting evaluator/harness defects;
- fabricating experiments, sources, test outcomes, or causal explanations;
- silently changing thresholds/questions after seeing results;
- creating review load through superficially plausible issue/PR proliferation;
- mistaking generated prose for executable ownership or returned evidence;
- formalizing an assumption and then presenting its restatement as a theorem;
- preserving duplicated files because deletion feels riskier than understanding dependencies.

OpenAI's GPT-5.6 system card reports increased over-persistence and some task-cheating/fabricated-research behavior in agentic settings, especially at high reasoning effort. Hugging Face's current contribution guidance similarly requires AI-assisted changes to be scoped and verified because review capacity, not text generation, is often the bottleneck.

References:
- https://deploymentsafety.openai.com/gpt-5-6
- https://huggingface.co/docs/transformers/main/contributing

## 7. Proof and claim discipline

Before adding theorem/proposition/corollary typography, ask:

1. Is the conclusion already encoded in the premises/definition?
2. Is the statement mathematical rather than constitutional, model-internal, symbolic, or methodological?
3. Are domains/quantifiers/assumptions visible?
4. Is there an explicit proof?
5. Does the result earn anything beyond an elementary restatement?

Use definitions, remarks, criteria, or model constraints when that is the honest container.

## 8. Credits, reductions, and external comparison

Use `docs/CREDITS_AND_REDUCTIONS.md`.

```text
project causal derivation
!= historical priority
!= comparative recurrence
!= technical realization
!= residual contribution
```

A mature comparator reduces a Venus claim only at the declared task/index where substitution preserves the relevant consequence. Do not rewrite project genealogy because related external work is discovered.

## 9. Public prose and GitHub Markdown

Public prose should minimize inferential distance:

```text
ordinary referent
-> operation/relation
-> concrete example or discriminator
-> scope/warrant
-> optional project term
```

Prefer GitHub-supported Markdown/MathJax and Mermaid over renderer-fragile LaTeX or raw HTML. A diagram must have an equivalent textual explanation.

Do not copy paper-native density into a forum post and call the conversion finished.

## 10. Destructive or high-impact changes

Deletion is allowed when a live dependency audit shows the object is gauge, duplicated, generated output, or superseded provenance. Preserve historical source through Git history/provenance where required.

Do not:
- delete or rewrite negative developmental branches;
- rewrite historical ancestry to make a cleaner story;
- promote a receipt into a runtime;
- promote a runtime into independent return;
- promote a successful build into scientific truth;
- direct-push a new developmental authority merely because external-agent tests passed.
