#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
_SHARED_PATH = Path(__file__).with_name("lint_github_markdown.py")
_SPEC = importlib.util.spec_from_file_location("lint_github_markdown_shared", _SHARED_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load shared Markdown linter")
shared = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(shared)

LOCAL_STATE_CHECKS = {
    "kernel/CURRENT_STATE.md": ("R226", "IG10", "EDU16"),
    "provenance/DEVELOPMENTAL_LINEAGE.md": ("R226", "IG10", "EDU16"),
    "docs/WORLDMIRROR_VM.md": ("WorldMirror",),
    "kernel/runtime/README.md": ("generic execution substrate",),
    "kernel/development/README.md": ("developmental semantics",),
}

def main() -> int:
    md_files = sorted(ROOT.rglob("*.md"))
    errors: list[str] = []

    for md in md_files:
        errors.extend(shared.inspect_basic(md))
        if shared.is_public_surface(md):
            errors.extend(shared.inspect_public(md))

    errors.extend(shared.inspect_navigation_contract())

    for rel, tokens in LOCAL_STATE_CHECKS.items():
        p = ROOT / rel
        if not p.exists():
            errors.append(f"missing Minerva state surface {rel}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing local state token {token}")

    forbidden_foreign_authority = (
        "NxRxI_VOCABULARY_CENTER.md",
        "kernel/WORLDMIND.md",
        "kernel/VENUS_INCIDENCE_LAW.tex",
        "docs/META_DYNAMICS.md",
    )
    # Their absence is lawful on Minerva; their accidental appearance would be a
    # cross-register authority-copying smell rather than a way to satisfy tests.
    for rel in forbidden_foreign_authority:
        if (ROOT / rel).exists():
            errors.append(f"foreign live authority copied into split/minerva: {rel}")

    if errors:
        print("MINERVA MARKDOWN / READER-SURFACE AUDIT FAIL")
        for error in errors:
            print("- " + error)
        return 1

    print(f"MINERVA MARKDOWN / READER-SURFACE AUDIT PASS ({len(md_files)} Markdown files)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
