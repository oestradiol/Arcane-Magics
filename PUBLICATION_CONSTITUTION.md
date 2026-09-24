# Publication Constitution

The bundle is one research family and four independently warranted projections. Shared vocabulary, provenance, didactics, or genealogy never transfers truth status across registers.

## 1. Non-transfer law

`shared governance != shared truth status`

`formal theorem != physical evidence != theological warrant != engineering return`

A result may be cited across monographs only with its original register, scope, evidence type, and unresolved bridges intact.

## 2. Claim registers

Every nontrivial claim should be typed with at least:

- **register:** FORM, SCI/PHYS, ENG, HIST, PHEN, THEOPHEN/MYTHOS, GOVERNANCE, META;
- **modality/status:** definition, observation, result, supported-local, hypothesis, conjecture, OPEN, WITHHOLD, negative, superseded/provenance-only;
- **index/scope:** which Perspective, task family, source family, scale, time, jurisdiction, or carrier;
- **warrant:** proof, source, experiment, returned consequence, historical reconstruction, phenomenological report, or declared symbolic interpretation;
- **falsifier/reopening route:** what future event would change the disposition.

## 3. Claim-strength law

Symbolic language is allowed. It must be bounded by explicit operational, structural, phenomenological, historical, metaphorical, or evidential status. Symbolic intensity does not raise warrant. Formal consistency does not establish empirical truth. Build success does not establish semantic truth. Retrieval does not establish evidence. Evidence does not establish authority or jurisdiction.

## 4. Devil's Audit

Before release, a hostile-but-fair reviewer asks:

1. What is the strongest ordinary comparator, historical predecessor, or mature substitute, and which relation is actually being claimed: genealogy, precedence, recurrence, technical inheritance, or consequential reduction?
2. Which attractive noun can be deleted without losing the operation?
3. Is a local success being promoted to a universal claim?
4. Is correlation, recurrence, or analogy being promoted to causation or identity?
5. Did any proposal see its evaluator or hidden target before commitment?
6. Can a negative result actually block publication/promotion?
7. Does a later correction rewrite history or merely supersede authority?
8. Is any theological, phenomenological, formal, or physical claim borrowing warrant from an adjacent register?
9. Does a build/test/hash merely prove what it actually checks?
10. Would a skeptical reader know exactly what would change the conclusion?

## 5. Didactic / founder-independence law

The intended trajectory is:

`encounter -> distinguish -> reconstruct -> attack -> author`

A strong paper progressively removes author dependence. Tests include vocabulary-free reconstruction, source-wording removal, counterexample generation, novel transfer, terminology replacement, OPEN/WITHHOLD localization, founder-rescue requests, and the ability to reject or mutate the framework while preserving useful distinctions.

Founder independence means functional succession, not erasure of provenance or credit.

Historical priority and project causal genealogy are separate. A mature comparator may narrow or reduce a mechanism claim at a declared index without becoming the retroactive cause of the project's documented developmental trajectory. Reduction is consequential and indexed: it applies only where substitution preserves the declared action, prediction, warrant, reconstruction, transport, later admissibility, correction route, and failure localization. See `docs/CREDITS_AND_REDUCTIONS.md`.

## 6. Reader-interface law

First occurrence should normally expose:

`referent -> relation -> scope/index -> sign -> project term`

Do not require readers to memorize a project name before they can see the object it denotes. Each major section should provide at least one of: a concrete example, a reconstruction prompt, a falsifier/crux, a comparator, or a register boundary.

## 7. Inhabitable-reader law

When abstraction outruns ordinary reconstruction, public-facing material should periodically expose at least one human-scale path:

`receive -> locate -> move -> return -> redistribute`

or ask explicitly about world-incidence, carrier exchange, self-incidence, maintenance cost, preserved difference, or a concrete reopening route.

This is a didactic requirement, not warrant. A humane example cannot substitute for proof or evidence, and a formal result cannot excuse a reader interface that hides who receives consequence, who bears cost, who may refuse, or what can still return independently.

See `docs/INHABITABLE_READER_PATH.md`.

## 8. Researcher / reviewer separation

Research artifacts distinguish proposal, source acquisition, evaluation, and adjudication. A researcher may generate a model or query; an independent or prefrozen evaluator owns hidden scoring where the claim requires non-preauthored return. Reviewer repairs may fix verifier defects only if they do not alter the proposal, threshold, target, or returned evidence.

## 9. Positive-claim / milestone law

Public-facing material should state the strongest earned positive contribution before its nearest claim fence.

The authoritative public achievement surface is `docs/EARNED_MILESTONES.md`. A claim may be advertised strongly when that ledger records:
- the exact milestone or result;
- register and scope;
- warrant;
- nearest stronger unearned promotion.

Claim fences prevent unsupported promotion; they do not require burying the positive result.

SOTA comparison is maintained separately in `docs/SOTA_WATCH.md`, and evaluation rules live in `docs/EVALUATION_CONSTITUTION.md`. A moving comparator may reopen an evaluation burden without rewriting project genealogy.

## 10. Forum and arXiv projections

The arXiv version optimizes self-contained scholarly communication and source portability. The LessWrong/BetterWrong preprint projection optimizes inferential distance: TL;DR, epistemic status, ordinary-language problem, neutral model, strongest comparator, cruxes, what-would-change-my-mind, then optional project vocabulary. These are different presentations of the same typed claim, not different truth standards.


## 11. Carrier-specific release rules

Publication carriers change presentation and packaging, not truth status.

### arXiv

For TeX-origin papers:

- submit source rather than only a generated PDF;
- include required local `.sty` and bibliography products;
- exclude caches, backups, hidden files, and unused build debris;
- freeze dates rather than relying on `\today`;
- build and visually inspect the exact upload candidate;
- keep each paper self-contained rather than borrowing missing premises from companion papers;
- choose the article license deliberately and consistently with controlled rights.

The packaging implementation is `scripts/package_arxiv.py`; arXiv suitability/category/endorsement remains an external submission decision.

### Forum / LessWrong-style projection

A forum projection should minimize inferential distance:

```text
TL;DR
-> epistemic status
-> ordinary problem
-> smallest claim
-> concrete example
-> strongest comparator / prior art
-> model
-> cruxes / what would change the conclusion
-> optional vocabulary bridge
-> technical source / reproducibility
```

Generated Markdown is an editing substrate, not automatically a publishable essay. Conversion must not leave broken cross-references, raw Pandoc theorem wrappers, unsupported renderer macros, or paper-native exposition that hides the argument behind notation.

A suggested public sequence is OFE -> Eclipsis -> Arcane Magics -> Venus -> cross-paper cruxes. Each post should bind itself to an exact manuscript snapshot and must not import warrant from later posts.

Platform/editor and LLM-disclosure requirements change over time and must be checked against the target platform at publication time; they are not frozen as repository theory.

### Generated artifacts

Generated PDFs, forum Markdown, arXiv ZIPs, TeX bundles, manifests, and checksums are CI/release outputs. They are not source authority merely because they were generated once.
