#!/usr/bin/env python3
from pathlib import Path
import re, sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
errors=[]

required=["README.md","BRANCH_TREE.md","REPOSITORY_AUTHORITY_BOUNDARY.md","monographs/01_OFE/main.tex","formal/lean/lakefile.toml","docs/LAYER_IDENTITY.md","docs/SCIENTIFIC_FUTURE.md"]
must=[["README.md","Operational Future Equivalence"],["REPOSITORY_AUTHORITY_BOUNDARY.md","formal consistency != empirical truth"],["docs/LAYER_IDENTITY.md","split/ofe"]]
forbidden=[["README.md","split/venus-minerva"],["REPOSITORY_AUTHORITY_BOUNDARY.md","Venus-Minerva"]]

for rel in required:
    if not (ROOT/rel).exists():
        errors.append(f"missing required branch-local surface: {rel}")

for rel, token in must:
    p=ROOT/rel
    if not p.exists() or token not in p.read_text(encoding="utf-8",errors="replace"):
        errors.append(f"{rel}: missing required token {token!r}")

for rel, token in forbidden:
    p=ROOT/rel
    if p.exists() and token in p.read_text(encoding="utf-8",errors="replace"):
        errors.append(f"{rel}: forbidden stale token {token!r}")

live_markdown = [
    ROOT/"README.md",
    ROOT/"BRANCH_TREE.md",
    ROOT/"REPOSITORY_AUTHORITY_BOUNDARY.md",
    ROOT/"CONTRIBUTING.md",
]
live_markdown += sorted((ROOT/"docs").glob("*.md")) if (ROOT/"docs").exists() else []
live_markdown += sorted((ROOT/"monographs").glob("*/README.md")) if (ROOT/"monographs").exists() else []

for md in live_markdown:
    if not md.exists():
        continue
    text=md.read_text(encoding="utf-8",errors="replace")
    if len(re.findall(r"^\s*\x60\x60\x60",text,flags=re.M)) % 2:
        errors.append(f"{md.relative_to(ROOT)}: unclosed fenced block")

if errors:
    print("LAYER SURFACE AUDIT FAIL")
    for e in errors: print("- "+e)
    sys.exit(1)
print("LAYER SURFACE AUDIT PASS")
