#!/usr/bin/env python3
from pathlib import Path
import re, sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
errors=[]

required=["README.md","BRANCH_TREE.md","REPOSITORY_AUTHORITY_BOUNDARY.md","monographs/04_MINERVA/main.tex","kernel/CURRENT_STATE.md","kernel/README.md","kernel/TRUST_BOUNDARY.md","kernel/runtime/current.py","docs/SELF_MODEL.md","docs/GLOBAL_REPOSITORY_OPERATION.md"]
must=[["README.md","engineering · body"],["docs/SELF_MODEL.md","fixed relation != frozen self-model"],["docs/GLOBAL_REPOSITORY_OPERATION.md","can inspect != can claim"],["kernel/CURRENT_STATE.md","# Minerva current state"]]
forbidden=[["kernel/README.md","VENUS_INCIDENCE_LAW.tex"],["BRANCH_TREE.md","WORLDMIND.md"],["README.md","split/venus-minerva"]]

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

link_re=re.compile(r"\[[^\]]+\]\(([^)]+)\)")
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
    for raw in link_re.findall(text):
        raw=unquote(raw.strip().strip("<>"))
        if not raw or raw.startswith(("http://","https://","mailto:","#")):
            continue
        target=raw.split("#",1)[0].split("?",1)[0]
        if not target:
            continue
        p=(md.parent/target).resolve() if not target.startswith("/") else ROOT/target.lstrip("/")
        try:
            p.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if not p.exists():
            errors.append(f"{md.relative_to(ROOT)}: broken relative link {raw!r}")

if errors:
    print("LAYER SURFACE AUDIT FAIL")
    for e in errors: print("- "+e)
    sys.exit(1)
print("LAYER SURFACE AUDIT PASS")
