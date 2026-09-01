# Citation and Archival Policy

## 1. Purpose

This file locks the public package's citation shape. The goal is not citation maximalism; it is durable, legible, and role-bounded sourcing.

This policy was applied in the current normalization pass on `2026-04-02T12:51:09-03:00`.

## 2. Core rule

Use the most durable public pointer available.

- if a source has a DOI, cite the DOI URL as the primary persistent link
- if a source does not have a DOI, cite the original public source and add an archive link
- if a public file cites a repeated source family, point readers to `references/source-registry.md` rather than improvising a new citation shape

## 3. DOI-backed sources

For journal articles, books, reports, or chapters with DOI support:

- use the DOI URL as the primary link
- add the publisher or public landing page only when it materially helps readers
- record the verification date in the registry
- do not add a second archive link unless the live landing page is itself central and unstable

## 4. Non-DOI public sources

For government pages, inquiry pages, ministry pages, NGO reports, portals, and book pages without DOI support:

- cite the original public page
- add an archive pointer
- record the access date in the registry
- record the archive-check date in the registry

The current public registry no longer depends on wildcard Wayback lookup links. If a future pass cannot mint a fixed capture from the current environment, use a temporary fallback only until a specific capture or Perma link is available, then replace it with that exact archive URL.

When a cited catalog page or edition record has an associated Internet Archive item record that materially improves durability, that item record can serve as the archive pointer instead of a Wayback link.

## 5. Mandatory archival cases

Always include an archive pointer for these source families when they appear in the public package:

- government and ministry pages
- inquiry, commission, court, or audit pages
- NGO, intergovernmental, and policy pages
- web-native documentation pages that are not DOI-backed

## 6. Registry fields

Each canonical entry in `references/source-registry.md` should carry:

- stable source id
- author or institution
- title
- year
- source type
- role in SUF
- primary persistent link
- original public page when useful
- archive link if the source is not DOI-backed
- access or verification date
- archive-check date for non-DOI sources
- a short note on what the source supports and what it does not justify

## 7. Public-file rule

Public files should not improvise source formatting once the registry exists.

Preferred public pattern:

- short in-file pointer to a registry entry
- one role note saying why the source is here
- no inflation about what the source proves

## 8. AI-language rule

AI-facing source use follows the same policy.

- do not use detector claims without evidence
- do not use generic governance boilerplate as a substitute for specific empirical support
- where claims concern linguistic patterns, disclosure effects, anthropomorphism risk, or detector unreliability, cite the specific source family that actually supports that move

## 9. What this policy is not

This file does not require every public note to become a miniature bibliography. It requires the public package to cite coherently, durably, and honestly.
