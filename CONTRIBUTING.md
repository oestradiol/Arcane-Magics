# Contributing to Venus-Minerva

Contributions are welcome from people who want to improve the mathematics, engineering, reproducibility, provenance, criticism, or public accessibility of the project.

You do **not** need to accept the project's terminology or larger interpretations to contribute.

## High-value contributions

Especially useful:

- reproduce an experiment;
- find a bug;
- formalize a small theorem;
- supply a counterexample;
- show that a project construct reduces to a mature existing formalism;
- improve a comparator or null model;
- trace a provenance error;
- improve documentation for an outsider;
- challenge a claimed dependency;
- propose a tighter discriminator;
- independently reimplement a bounded result.

A successful deletion or narrowing is progress.

## Before opening a large PR

Prefer an issue for:

- new research lanes;
- cross-register promotions;
- new physical interpretations;
- new AGI/consciousness claims;
- large terminology changes;
- changes that affect current developmental authority.

Small corrections, tests, formalizations, and documentation fixes can go directly to a PR.

## Research contribution format

For a new bounded result, include:

1. **Parent** — exact commit / receipt / state.
2. **Question** — frozen before the result.
3. **Scope** — what register and target are actually being tested.
4. **Comparator** — null, baseline, rival, or mature substitute.
5. **Evidence budget** — what evidence is admitted.
6. **Result** — PASS / FAIL / WITHHOLD / mature reduction / other typed outcome.
7. **Dependency-local update** — exactly what changes.
8. **Claim fence** — what the result does not establish.
9. **Reproduction** — commands, fixtures, or proof checker.

## Commit style

Prefer one causal change per commit.

Good:

```text
formal: add section existence counterexample
test: preserve EDU17 provenance failure
docs: expose current developmental boundary
research: freeze residual-incidence discriminator
```

Avoid commits that simultaneously rewrite terminology, alter tests, reinterpret results, and promote conclusions.

## Criticism protocol

Please be direct and specific.

Useful criticism identifies one or more of:

- hidden premise;
- invalid inference;
- missing comparator;
- unearned register crossing;
- circular definition;
- inadequate lower-bound argument;
- provenance break;
- unreproducible result;
- mature prior art that substitutes the project construct;
- stronger ordinary explanation.

The project explicitly prefers a correct negative result to a dramatic incorrect positive result.

## Truth-status discipline

A result in one register does not automatically propagate to another.

Examples:

- FORM theorem does not establish PHYS identity.
- ENG PASS does not establish AGI.
- historical recurrence does not establish metaphysics.
- symbolic usefulness does not establish mechanism.
- analogy to P versus NP does not establish a complexity lower bound.

See `PUBLICATION_CONSTITUTION.md` and `docs/FRONTIER_RESEARCH.md`.

## Humane interface check

For reader-facing work, include at least one ordinary-language reconstruction of what the machinery means for an indexed participant or affected system.

Useful prompts:

- what is being received?
- where does it land?
- what action or continuation changes?
- what can return independently?
- who pays the maintenance cost?
- can another center disagree, refuse, fork, or exit?
- what remains stable, and what is allowed to reopen?

Do not invent personal stories merely to make a theory feel warm. The point is operational legibility, not sentimentality.

See `docs/INHABITABLE_READER_PATH.md`.

## Reproducibility

Start with:

```bash
make audit
make papers
```

The current developmental lineage lives under `prototype/`; historical R194 runtime code is preserved under `provenance/historical-runtime/R194/`.

If your result depends on a generated artifact, include enough source and commands for another person to regenerate it.

## Funding

If you want to support compute, publication, or maintenance without contributing code, GitHub Sponsors is enabled for this repository.

Funding does not buy claim authority, acceptance, or favorable review.
