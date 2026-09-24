<div align="center">

# Venus-Minerva

**A research family for operational equivalence, relational reconstruction, developmental intelligence, and bounded open-ended inquiry.**

[Meta-Dynamics](docs/META_DYNAMICS.md) · [Inhabitable path](docs/INHABITABLE_READER_PATH.md) · [Research frontier](docs/FRONTIER_RESEARCH.md) · [Current Venus state](prototype/CURRENT_STATE.md) · [Publication constitution](PUBLICATION_CONSTITUTION.md) · [Contribute](CONTRIBUTING.md) · [Sponsor](https://github.com/sponsors/oestradiol)

</div>

<p align="center">
  <a href="https://github.com/oestradiol/Venus-Minerva/actions/workflows/venus-steward.yml"><img alt="Venus steward" src="https://github.com/oestradiol/Venus-Minerva/actions/workflows/venus-steward.yml/badge.svg"></a>
  <a href="https://github.com/oestradiol/Venus-Minerva/issues"><img alt="Research issues" src="https://img.shields.io/github/issues/oestradiol/Venus-Minerva"></a>
  <a href="https://github.com/sponsors/oestradiol"><img alt="Sponsor" src="https://img.shields.io/badge/sponsor-GitHub%20Sponsors-EA4AAA?logo=githubsponsors"></a>
</p>
> [!IMPORTANT]
> This repository deliberately mixes several research registers, but it does **not** collapse their truth conditions. Formal results, engineering experiments, physical conjectures, historical comparisons, and symbolic interpretations remain separately typed.

> [!NOTE]
> Current Venus developmental head represented here: **EDU16 / 1703 records**. Later EDU17 is preserved as an invalid-for-promotion negative branch; EDU17R1 WITHHELD before claim-binding evaluation.

## Why this exists

The project is trying to make difficult cross-domain research more **reconstructible, falsifiable, and reusable**.

Rather than asking readers to accept one giant worldview, Venus-Minerva exposes separate formal, scientific, engineering, historical, and phenomenological projections, keeps negative results visible, and treats later counterevidence as something that should be able to reopen earlier closure.

The public goal is simple: make the useful parts easy for other people to inspect, criticize, reproduce, formalize, reuse, or delete.

## Quick start

```bash
git clone https://github.com/oestradiol/Venus-Minerva.git
cd Venus-Minerva

make audit      # repository/claim/source audit
make papers     # build all four monographs
make arxiv      # produce clean source packages
make release    # full build + audit + manifest + bundle
```

For the executable lineage, start at:

```text
prototype/stable-executable/README.md
prototype/stable-executable/source/PYTHON_R00_R194_PROTOTYPE_README.md
prototype/CURRENT_STATE.md
```

For open problems and bounded next experiments, start at:

```text
docs/FRONTIER_RESEARCH.md
```

## When not to use this repository

Do not use Venus-Minerva as:

- a substitute for domain-standard proofs, peer review, or experimental validation;
- evidence that a symbolic analogy establishes a physical mechanism;
- a source of medical, legal, financial, or other high-stakes decisions;
- a shortcut around current complexity-theory, PDE, or quantum-gravity literature;
- an autonomous authority that may certify its own research promotions.

Use it as a source of bounded formal objects, executable experiments, research questions, provenance, and falsifiable proposals.

For continuous automation constraints, see [`docs/AUTONOMOUS_RESEARCH.md`](docs/AUTONOMOUS_RESEARCH.md).

## What this is not

Venus-Minerva is not currently evidence of:

- solved P versus NP;
- a Navier-Stokes Millennium solution;
- established quantum gravity;
- AGI or consciousness;
- unrestricted autonomous science;
- open-ended recursive self-improvement;
- a theorem proving the symbolic or theological interpretations.

Those are separate burdens. Where the project touches them, the relevant lane states the exact remaining obligation.

---

## Research family

A four-monograph research family plus executable/provenance infrastructure. Start with the projection that matches your question; do **not** treat the bundle as one giant proof.

## Start here

| If you care about... | Read | Register |
|---|---|---|
| future-sufficient state, operational equivalence, quantum/control/QG tests | **I. Operational Future Equivalence** | SCI / FORM |
| local views, quotienting, gluing, residuals, return-conditioned reconstruction | **II. Eclipsis** | FORM + typed interpretation |
| comparative religion, philosophy, phenomenology, humanitarian Mythos | **III. Arcane Magics** | HIST / PHEN / THEOPHEN / MYTHOS |
| developmental intelligence, provenance, self-curriculum, preregistration, WorldMind | **IV. Venus** | ENG / GOVERNANCE |

PDFs are in each monograph directory after `make papers`. Source zips suitable for arXiv upload are generated with `make arxiv`.

## One law before everything else

**Shared governance does not imply shared truth status.** A theorem in Eclipsis does not prove a religious interpretation. A historical recurrence in Arcane does not validate a physical conjecture in OFE. A Venus engineering PASS does not establish AGI or consciousness.

Read `PUBLICATION_CONSTITUTION.md` and `NxRxI_VOCABULARY_CENTER.md` before cross-paper interpretation.

## Current Venus developmental boundary

Latest positive developmental head represented here:

`EDU16 -> PASS_BOUNDED_LEARNER_OWNED_WORLD_FEED_POLICY -> 1703 records`

The subsequent EDU17 branch is preserved but invalid for promotion after a claim-local provenance audit. EDU17R1 then WITHHELD before claim-binding evaluation because the fresh feed exposed the prior separator `MENTION != INCIDENCE`. World execution and independent evaluation remain external. AGI, consciousness, open-ended RSI, unrestricted semantics, natural-world generality, autonomous science, and independent external replication are **not established**.

`REPOSITORY_AUTHORITY_BOUNDARY.md` defines the new source-of-truth split: Venus-Minerva owns implementation/release-bearing developmental state; Canonical remains the external research-mapping, planning, and non-release provenance layer.

The repo also contains the latest self-contained stable executable Python package currently materialized for release (R00-R194) plus exact later developmental receipts. A receipt is not silently promoted into an executable checkpoint.

## Build

Requirements: Python 3, `latexmk`, pdfLaTeX/TeX Live, and optionally `pandoc` for forum exports.

```bash
make papers       # build all four PDFs
make arxiv        # create clean per-paper arXiv source zips
make texbundle    # create reusable TeX/source bundles
make forum        # create LessWrong/BetterWrong-oriented Markdown drafts
make audit        # claim/license/source/package checks
make bundle       # create the full repository ZIP beside the repo
make release      # build + package + audit + manifest + repository ZIP
```

## Public-preprint note

The generated LessWrong/BetterWrong Markdown files are editing substrates, not automatic ready-to-post copies. LessWrong currently requires substantial LLM-generated or substantially LLM-revised wording to be marked with its LLM-content feature; the human author should independently verify, understand, and deliberately own the posted prose. See `docs/LESSWRONG_BETTERWRONG_GUIDE.md`.

## Inhabitable reading cue

When the abstractions get dense, reduce the local problem to:

```text
receive -> locate -> move -> return -> redistribute
```

Then ask what reaches the indexed center, what it costs to maintain the carrier, what can return independently, and what must change without destroying continuity. See [`docs/INHABITABLE_READER_PATH.md`](docs/INHABITABLE_READER_PATH.md).

## Front-door norms

- first expose the referent, then the project term;
- state epistemic/register status before speculative bridges;
- strongest ordinary comparator first;
- negative results remain visible;
- OPEN and WITHHOLD are not shameful intermediate typography;
- source removal and founder independence are publication tests;
- readers should be able to disagree without first learning the project's private dialect.

## Licenses

Project-owned theory/docs/monographs/knowledge: **CC BY-NC-SA 4.0**. Project-owned software: **PolyForm Noncommercial 1.0.0**. Software is source-available/noncommercial, not OSI Open Source. See `licenses/README.md` and `LICENSE`.

## Preprint publication

`preprints/lesswrong/` contains a sequence map and forum template. Current LessWrong supports Markdown/WYSIWYG editing and LaTeX; conversion between editor modes can be lossy, so generated Markdown should be reviewed before posting. BetterWrong-specific indexed documentation was not independently available during this audit; the exports therefore target the conservative shared rationalist Markdown/MathJax vocabulary subset.

## Repository archaeology

`archaeology/S10_S11/` contains the transmission-adjusted comparative evidence artifacts that constrain Arcane. Archaeology is provenance and regression material, not present authority merely because it is older or more dramatic.