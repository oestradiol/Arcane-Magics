# Repository Quality / Devil's Audit — 2026-09-24

**Status:** provenance/audit artifact; no new scientific or AGI claim  
**Scope:** current Git repository organization, public prose, CI/release surfaces, agent-assisted work discipline, and Canonical retirement interfaces.

## Executive result

The repository has moved from “research bundle with impressive internal governance but poor public legibility” toward a real research-project layout, but the strongest unresolved criticism remains:

```text
internal governance sophistication
> externally discriminated capability/science
```

That is not a dismissal of the architecture. It is the present empirical asymmetry.

The current repo is now strong at:

- exact runtime/developmental authority separation;
- negative-result retention;
- provenance and claim fences;
- current-kernel reconstruction;
- persistent memory/custody machinery;
- causal-order invariants;
- research/evaluation planning;
- publication/release reproducibility;
- credit/genealogy/reduction discipline.

It is still weak or incomplete at:

- matched-budget external capability comparison;
- independent replication;
- general natural-world research performance;
- causal proof that persistent memory improves later learning;
- a complete Venus-owned recursive-development episode;
- executable EDU16 custody beyond exact evidence receipts;
- semantic proof verification beyond structural proof-container audits;
- blind outsider reconstruction/navigation evaluation.

## 1. Information architecture

### Surfaces and single responsibilities

The live public surfaces should remain typed:

| Surface | Single job |
|---|---|
| `README.md` | 60-second identity, current claim boundary, first commands, navigation |
| `docs/START_HERE.md` | five-minute authority/reproduction/test router |
| `docs/PUBLIC_VALUE.md` | explain and advertise the strongest earned value in ordinary language |
| `docs/EARNED_MILESTONES.md` | positive/negative claim ledger |
| `kernel/CURRENT_STATE.md` | exact current runtime/developmental authority |
| `docs/FRONTIER_RESEARCH.md` | unresolved research obligations |
| `docs/EVALUATION_CONSTITUTION.md` | what counts as stronger evidence |
| `docs/TEST_COVERAGE_MATRIX.md` | issue → discriminator/evaluation routing |
| `docs/SOTA_WATCH.md` | dated moving external comparator surface |
| `docs/CREDITS_AND_REDUCTIONS.md` | genealogy, credit, mature substitution, residual contribution |
| `provenance/*` | history/evidence/audit, not front-door authority |

A new live document should not be added unless it owns a consequence not already owned by one of these surfaces.

### Compression finding

Current prose is still duplicated across README, Start Here, Public Value, milestones, reader path, and frontier. Duplication is acceptable only where it serves a different reader operation. Repeating current-state paragraphs verbatim across those surfaces creates status-fossil risk.

Compression rule:

```text
authority fact -> one controlling surface
router/explainer -> link + short projection
-/-> second authority copy
```

## 2. Comparison with mature research repositories

The useful recurring patterns in projects such as mathlib, lm-evaluation-harness, AlphaFold, and Transformers are not aesthetic. They are operational:

1. one-sentence identity appears immediately;
2. first install/run/reproduce action is easy to find;
3. documentation is routed by task rather than project mythology;
4. contribution and known limitations have explicit homes;
5. version/runtime/reproducibility boundaries are visible;
6. detailed methodology is deeper than the root README.

Venus should copy those consequences, not their branding.

The new `docs/START_HERE.md` and README route implement much of this pattern. Blind-reader testing remains open.

## 3. Prose quality

Public prose should minimize inferential distance without deleting distinctions:

```text
ordinary referent
-> operation/relation
-> concrete example or returned discriminator
-> warrant/scope
-> project term when useful
```

Useful LessWrong-adjacent constraints survive translation into ordinary research writing:

- concrete examples before broad abstraction when examples discriminate;
- explicit evidence → inference → conclusion steps;
- expose cruxes/separators rather than only conclusions;
- sanity-check an abstract claim against a mundane case;
- do not “simplify” by deleting the condition that made the statement true.

Anti-patterns still present in parts of the repository:

- long sequences of project nouns before the referent is clear;
- repeated claim-fence paragraphs that bury the positive contribution;
- equation density where a table or plain operational example would carry more information;
- symbolic renderings placed too near engineering claims without enough visual/register separation;
- historical overlays using `CURRENT` typography after authority moved.

## 4. GitHub Markdown / publication quality

Repository Markdown should use GitHub-supported ordinary Markdown, fenced code, tables, links, MathJax math, and Mermaid where diagrams genuinely reduce inferential distance.

The forum export path exposed two independent classes of build defect during this audit:

1. missing clean-run TeX dependencies (BibLaTeX and TikZ/PGF);
2. a Markdown linter that misparsed multiline display math when the closing delimiter shared a line with prose.

Both were repaired prospectively and regression-tested.

Generated LessWrong/BetterWrong Markdown remains an editing substrate, not a claim of finished human-quality forum prose.

## 5. Code/runtime quality

Real defects found and repaired during the audit include:

- state-changing transition payload was not cryptographically/evidentially bound to the verified return payload;
- ActionReturn did not enforce execution-before-return order;
- authority IDs could be rebound to different content;
- memory objects could declare dangling parents;
- consumption replacement chains could cycle;
- objects could be born `CONSUMED` without an explicit replacement;
- release manifest identity was hard-coded to one date.

These are more consequential than cosmetic refactors because they touch causal attribution, provenance, authority, or reconstruction.

Remaining high-value code attack surface:

- malicious/custom transition backends;
- authenticated authority issuers and revocation;
- cross-language canonicalization fixtures;
- non-finite numeric payload policy;
- exact bridge from external/cold custody into admitted current runtime;
- memory ablation proving later behavioral dependence.

## 6. AI / GPT-assisted work failure modes

External models are useful here precisely because they can inspect large heterogeneous surfaces quickly. They are dangerous for the same reason.

Observed/relevant failure classes:

- over-persistence beyond the requested scope;
- “I changed it” reported as “it passed”;
- plausible but unexecuted experiments;
- fabricated or weakly bound research support;
- grader/harness exploitation;
- issue/document proliferation that creates reviewer work without causal progress;
- inference from search miss to global absence;
- stale mental state after another actor changes the repository;
- formalizing an assumption and then congratulating oneself on proving it.

The live `AGENTS.md` contract therefore correctly requires:

```text
INTENDED
-> WRITTEN
-> VERIFIED
-> ADMITTED
```

and re-reading returned repository state after changes.

High reasoning effort does not increase warrant. It can increase persistence and optimization pressure; exact external checks still dominate model confidence.

## 7. Canonical retirement quality

Canonical is not one authority tree. It contains:

- genuine historical evidence;
- exact experiment receipts;
- heavy custody payloads;
- research donors;
- plans;
- stale current-state projections;
- generated projections;
- symbolic/formal overlays.

The audit directly established:

- root/Future `CURRENT_STATE.md` still routes EDU4 [1572] and is stale;
- EDU16 Raising custody contains only prefreeze, generated policy, and result receipt;
- the ordinary Handoff tree has no `EDU16CurrentDevelopedVM`;
- an `EDU12CurrentDevelopedVM` folder exists but is empty, proving that folder naming alone is not custody;
- IG10 handoff has actual custody structure: manifest, verifier, 118.8 MB journal, hashes, and packaged seeds;
- WorldMind's surviving neutral invariant is already represented in Git; its stacked SM/U/RB overlays are history/provenance;
- the R00→R194 integration audit contains high-value historical regression/disposition data that should feed the test archaeology rather than remain buried in Canonical.

Retirement must therefore be dependency/custody based, never recursive-copy based.

## 8. Credit/reduction methodology

Canonical's mature method is stronger than “find prior art”:

```text
source-faithful recovery
-> typed credit/provenance relation
-> reconstruct project object at its historical state
-> term-free structural paraphrase
-> mapping
-> information-loss analysis
-> nonidentity fence
-> strongest rival / mature substitute
-> residual or equivalence
-> deletion / discriminator
-> only then narrow/merge/rename/delete novelty claims
```

This sequence should remain live. A residual is a candidate research object, not an automatic novelty certificate.

## 9. CI/CD quality

One compressed workflow is sufficient:

```text
integrity
-> publication
-> tagged release
```

The earlier problem was not too few workflow files. It was that direct pushes and a schedule repeatedly triggered a known-broken full pipeline, producing notification spam.

Stable policy after repair:

- PRs run integrity + publication;
- manual dispatch remains available;
- version tags run the release path;
- ordinary direct pushes to `main` do not rerun the full publication pipeline;
- no daily schedule until a genuine freshness task exists that benefits from it.

## 10. Strongest surviving Devil's Audit objections

### A. External consequence remains under-measured

The architecture is unusual, but most present evidence is internal/bounded. The next major warrant increase requires matched external tasks and ablations.

### B. Governance can become its own optimization target

A learner can become very good at producing impeccable receipts, gates, issue matrices, and WITHHOLD decisions without becoming more capable at the target task. Evaluation therefore needs a causal machinery gain term, not governance compliance alone.

### C. Persistent memory is not yet demonstrated learning

Storage/reconstruction is implemented. Causal improvement of later acquisition from retained memory remains an experiment.

### D. Developmental ownership is bounded and incomplete

EDU16 is meaningful, but World execution and independent evaluation remain external, and a full recursive target→World→reconstruction→successor→next-target cycle is not yet demonstrated.

### E. Proof hygiene is structural, not proof verification

The current audit catches missing/circular containers. It is not a proof assistant and must not be advertised as one.

### F. Public comprehensibility remains empirically untested

The front door is much better. The blind outsider reconstruction test still matters.

## 11. Current quality verdict

The repository now has a defensible architecture for:

- knowing what is current;
- knowing what failed;
- knowing what can be replayed;
- knowing which evidence supports which claim;
- knowing which comparisons alter credit vs only comparison burden;
- knowing what must happen before stronger promotion.

It does **not** yet have enough externally matched evidence to make its broadest ambition empirically compelling.

That is the present high-leverage frontier, and the repository should advertise the architectural achievement hard without pretending the external discrimination has already happened.
