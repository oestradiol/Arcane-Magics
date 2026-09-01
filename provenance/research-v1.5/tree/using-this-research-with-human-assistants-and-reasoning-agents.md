# Using This Research with Human Assistants and Reasoning Agents

## Purpose

This note explains how the `Research/` repository can be used by:

- individual human readers
- human assistants helping another reader navigate the material
- reasoning agents working as structured support tools

The goal is not to pretend that assistants or agents replace careful scholarship. The goal is to make the research easier to navigate, interpret, and discuss without losing source discipline or claim discipline.

## Core stance

This repository is intentionally documentation-first and structure-heavy. That makes it compatible with:

- close human reading
- collaborative note-taking
- route-based guided study
- reasoning-agent support for navigation, summarization, cross-referencing, and traceability

That compatibility is a feature of the project, not an accident.

## What assistants and agents can help with

- locating the right entry point for a given question
- tracing dependencies between framework layers, methods, routes, and references
- summarizing bounded sections without pretending to replace the source text
- comparing notes across files while preserving file-level context
- helping readers move between SUF and Knowledge without collapsing the two packages into one

## What assistants and agents should not do

- invent claims not grounded in the files
- blur open questions into settled conclusions
- treat one route as proof of the whole framework
- hide uncertainty, disagreement, or deferred work
- replace domain-native expertise where the package itself says local methods matter more

## Accessibility and supported navigation

Readers with accessibility needs may benefit from working with a human assistant who can help with:

- paced reading
- oral explanation or paraphrase
- route selection
- glossary support
- cross-file navigation
- turning dense sections into stepwise reading sequences

That kind of support is encouraged here. It fits the structure of the repository well, especially because the files are organized around navigation surfaces, bounded roles, and explicit reading paths.

## Suggested support workflow

1. Start with the package README that best fits the reader's goal.
2. Use the relevant navigation index before going deep.
3. Keep citations and source links visible during explanation.
4. Distinguish clearly between summary, interpretation, and open questions.
5. Return to the original note whenever a claim carries real argumentative weight.

## Agent cold-start workflow

Reasoning agents using the public repository should usually:

1. read `README.md` and `START_HERE.md`
2. read `governance/AUTHORITATIVE_INDEX_v0_2.md`
3. read the package-local current-state surfaces relevant to the task
4. capture the current repo commit and working-tree state before editing or summarizing current status
5. keep local working memory small and rely on file references rather than long restatements

This repository is easier to use well when the agent treats the files as the canonical memory and the prompt as only a temporary working register.

## Externalization and handoff discipline

Agents should prefer:

- short summaries anchored to file paths
- explicit repo-state references when currentness matters
- durable write-back into the right note or doc over repeated conversational restatement
- concise handoff packets that state what changed, how it was checked, and where the next operator should start

Agents should avoid:

- carrying large unreferenced paraphrases in context
- treating local memory as more authoritative than the files
- blurring generated synthesis into accepted package truth without updating the appropriate surfaces

## SUF-specific note

SUF is especially usable in assistant-supported settings because it already emphasizes:

- layer discipline
- explicit boundaries
- claim typing
- route logic
- separation between what is modeled, what is argued, and what is still open

That makes it a good support scaffold for both human assistants and reasoning agents, as long as they stay honest about uncertainty and do not overread the framework.

## Where to start

- [Structured Unity Framework](structured-unity-framework/README.md)
- [Knowledge](knowledge/README.md)
- [Studying and Teaching with SUF](knowledge/studying-and-teaching-with-suf.md)

## Edit-scope discipline

Reasoning agents should stay inside current surfaces, designated work surfaces, or an explicitly declared change scope. Editing unrelated existing files should count as a control failure even when the text still sounds plausible.

## Validation note

When the task depends on current repository state, use the governed validation tooling before treating the repo as clean current state. In Nix-based environments, the intended path is the `tools` flake; in other environments, use the equivalent supported Python setup documented in `tools/README.md`.
