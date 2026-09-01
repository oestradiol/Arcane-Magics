# Knowledge Package Spec

Canonical filename: `knowledge-package-spec.md`

## 1. Purpose

This document is the control spec for `Research/knowledge/`.

It defines a public, Obsidian-first knowledge atlas founded on SUF and structured for navigation, study, and later growth.

## 2. Core contract

`Research/knowledge/` must be:

- public and package-ready
- Obsidian-friendly and graph-friendly
- study-first rather than publication-formalized
- broader than SUF where that improves the atlas
- typed in its cross-links
- scaffolded by SUF without becoming captive to SUF

## 3. SUF role

SUF should act here as:

- a layered scaffold for broad cluster order
- one route-building and comparison lens
- one source of optional study hooks between nodes

Preferred explicit `suf_role` values are:

- `primary_scaffold`
- `supporting_scaffold`
- `domain_native_lead`

Public prose may translate these as:

- primary scaffold
- supporting scaffold
- domain-native lead

SUF should **not** be treated as the mandatory voice inside every node. Each note should be able to guide its own study, combine other frameworks, or move beyond SUF entirely.

## 4. Required note behavior

Cluster, domain, and subdomain notes should normally include:

- frontmatter with at least `tags`, `kind`, and `status`
- study purpose
- key questions
- canonical or starter anchors
- typed links
- typed relation opportunities
- an optional `SUF hook / route note`
- current status
- route links where route travel is genuinely useful

Deepened hub nodes that foreground SUF should include:

- `suf_role`
- selective `aliases`
- `related_routes`
- expanded anchor families
- fuller outbound links and route pointers

## 5. Handoff rule

If SUF is not carrying most of the explanatory work in a note, the note should either:

- mark SUF as `supporting_scaffold`, or
- mark the note as `domain_native_lead`

and then hand off to the better local framework instead of keeping SUF in the foreground by inertia.

## 6. Anti-rules

Do not let this package:

- collapse into the SUF applications atlas
- become a dump of disconnected notes
- overlink so aggressively that the graph becomes noise
- treat SUF as the only legitimate framework
- mistake scaffold order for proof of metaphysical or disciplinary hierarchy
