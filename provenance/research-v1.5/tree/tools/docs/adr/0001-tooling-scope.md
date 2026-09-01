# ADR 0001: Tooling Scope

## Decision

Create one shared tooling package at `Research/tools/`.

## Reason

The tooling should support SUF now and remain reusable for Knowledge later without mixing code into the public framework package.

## Consequence

Tooling versioning and research-doc versioning remain separate inside the same repository tree.
