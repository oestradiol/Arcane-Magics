# Publication research notes

This bundle reconciles internal Library governance with current external publication practice.

Internal controls used: prose-coherence validator; Devil's Audit epistemic-boundary policy; reader-autonomy/source-removal audit; Version-0-to-Version-1 bottom-up/top-down/lateral audit; founder-independence criteria; current EDU preregistration/evaluator-separation lineage.

External controls checked 2026-09-24: current arXiv submission/TeX/license documentation and current LessWrong editor/readability/jargon/taboo materials. BetterWrong-specific indexed documentation was not independently available, so no BetterWrong-only behavior is asserted.


Current external checks were normalized into build rules rather than copied as prose ornament: arXiv source packages are minimal and top-level; style/.bbl dependencies are included where required; file names stay in the portable character set; forum exports target Markdown + MathJax and preserve a warning that editor-mode conversion can be lossy. Rationalist-facing prose uses ordinary referents, cruxes/discriminators, taboo-able project terms, strongest comparators, and explicit inference ownership.

## 2026-09-24 external audit deltas

- arXiv currently supports TeX Live 2023 and 2025, with 2025 default; its TeX guidance explicitly documents a `cleveref` issue under TL2025 and recommends TL2023 or `zref-clever` as alternatives.
- arXiv requires source packages to omit build junk/backups/unused assets and asks submitters to inspect the generated PDF before completing submission.
- arXiv offers CC BY-NC-SA 4.0 and states that the license chosen for a posted version is irrevocable; journal/funder compatibility must therefore be checked before submission.
- LessWrong's March 2026 editor announcement replaced the main editor with Lexical and introduced/clarified LLM-content blocks. Substantially LLM-generated or substantially LLM-revised prose must be marked as such under current LessWrong policy.
- BetterWrong-specific current documentation was not independently recoverable, so the release does not assert BetterWrong-only editor, licensing, or LLM-policy behavior.
