# ADR 0003: Nix plus .venv

## Decision

Use Nix for the base toolchain and a repo-local `.venv` for the package environment.

## Reason

This keeps the environment reproducible on NixOS while preserving a familiar local Python workflow.

## Consequence

The documented setup uses `nix develop` first, then a local `.venv` created with
`--system-site-packages`, followed by editable install with `--no-build-isolation`.
