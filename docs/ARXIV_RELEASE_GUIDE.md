# arXiv release guide (checked 2026-09-24)

Official arXiv guidance used for this release:

- Submission guidelines: https://info.arxiv.org/help/submit/index.html
- TeX/LaTeX submissions: https://info.arxiv.org/help/submit_tex.html
- TeX Live versions: https://info.arxiv.org/help/faq/texlive.html
- Licenses: https://info.arxiv.org/help/license/index.html

Release rules encoded by `scripts/package_arxiv.py`:

1. Prefer TeX source over a PDF produced from TeX.
2. Use arXiv-safe filenames (`A-Z a-z 0-9 _ + - . , =`).
3. Include custom `.sty` files and any required `.bbl`.
4. Do not include backups, build junk, referee letters, hidden dotfiles, or unused assets.
5. Avoid `\today`; freeze dates explicitly.
6. Build and visually inspect the generated PDF before submission.
7. arXiv currently supports TeX Live 2023 and 2025 (2025 default).
8. arXiv explicitly offers CC BY-NC-SA 4.0. Each posted version's selected license is irrevocable, so the submitter must deliberately confirm it.
9. A paper must remain topical/refereeable and self-contained; companion papers cannot supply missing premises by implication.

10. TeX Live 2025 is the default, but arXiv documents a `cleveref` compatibility problem under TL2025. OFE uses `cleveref`; inspect its generated Section/Proposition labels on arXiv Preview. If labels are wrong, select TeX Live 2023 or migrate to a supported alternative such as `zref-clever` before release.
11. A generated source ZIP is a technical upload candidate, not evidence that the manuscript is suitable for a particular arXiv category. Category scope/moderation and endorsement remain separate submission questions.


The repository license and arXiv selected license should be deliberately aligned per released version.
