# LessWrong / BetterWrong preprint guide

Current LessWrong references checked for this release:

- Editor guide: https://www.lesswrong.com/w/guide-to-the-lesswrong-editor
- Readable posts: https://www.lesswrong.com/posts/bK8iEj25uhboJoCCP/how-to-write-readable-posts
- Rationalist Taboo: https://www.lesswrong.com/w/rationalist-taboo
- LessWrong jargon: https://www.lesswrong.com/w/lesswrong-jargon

LessWrong currently supports LaTeX and both WYSIWYG and Markdown editing; its own guide warns that conversion between editor modes can be lossy. Keep a source copy outside the editor.


## 2026 editor and LLM-use note

The older LessWrong editor wiki page is explicitly marked out of date. LessWrong announced a new Lexical-based editor in March 2026, while older drafts/posts may still use previous editor behavior. Treat Markdown conversion as a portability aid, not a guaranteed lossless round trip.

LessWrong's March 2026 LLM policy also matters for these preprints. Substantially LLM-written or substantially LLM-revised prose is treated as **LLM output** and must be placed in the site's LLM-content blocks (or a fully LLM-output collapsible section); first-time users face a stricter quality bar. Human-written text may use LLM-assisted research/idea development without thereby becoming LLM output, but borrowed/generated wording crosses that boundary. Before posting, the human author should therefore independently understand, verify, and deliberately rewrite/endorse the public prose rather than dumping generated manuscript text into the forum. Code is treated separately by the policy.

Current LessWrong source: `https://www.lesswrong.com/posts/nQWavk9mnwcv6ScMR/new-lesswrong-editor-also-an-update-to-our-llm-policy`.

## House projection

A forum preprint should normally begin with:

1. **TL;DR** - one paragraph.
2. **Epistemic status** - what is result, hypothesis, formalism, interpretation, or OPEN.
3. **Problem before vocabulary** - ordinary language and concrete example.
4. **Claim** - the smallest thing actually asserted.
5. **Strongest comparator / prior art.**
6. **Cruxes** - observations or arguments that would materially change the conclusion.
7. **What would change my mind.**
8. **Project vocabulary bridge** - only after the object is visible.
9. **Technical appendix / paper link.**

Use simple, literal prose when possible. Define terms, taboo high-load words, and own inferences as inferences. Do not use the vocabulary center to perform jargon substitution while preserving the same inferential distance.

## BetterWrong status

BetterWrong-specific indexed documentation was not independently retrievable during this audit. The provided Markdown exports therefore target the conservative feature subset shared by LessWrong-style readers: headings, paragraphs, lists, links, code fences, and MathJax/LaTeX math. Review on the actual target site before publication.
