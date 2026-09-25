#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
rel="monographs/01_OFE/main.tex"
text=(ROOT/rel).read_text(encoding="utf-8",errors="replace")

FORMAL_ENV=re.compile(r"\\begin\{(lemma|theorem|proposition|corollary)\}(?:\[[^\]]*\])?")
PROOF=re.compile(r"\\begin\{proof\}")
NEXT_BLOCK=re.compile(r"\\begin\{(?:lemma|theorem|proposition|corollary|conjecture|definition|remark|example)\}")

errors=[]
for m in FORMAL_ENV.finditer(text):
    start=m.end()
    nxt=NEXT_BLOCK.search(text,start)
    end=nxt.start() if nxt else len(text)
    if not PROOF.search(text[start:end]):
        line=text.count("\n",0,m.start())+1
        errors.append(f"{rel}:{line}: {m.group(1)} lacks an explicit proof before the next formal block")

for m in re.finditer(r"\\begin\{conjecture\}(?:\[[^\]]*\])?",text):
    start=m.end()
    nxt=NEXT_BLOCK.search(text,start)
    end=nxt.start() if nxt else len(text)
    if PROOF.search(text[start:end]):
        line=text.count("\n",0,m.start())+1
        errors.append(f"{rel}:{line}: conjecture unexpectedly contains a proof environment")

if errors:
    print("OFE PROOF-CONTAINER AUDIT FAIL")
    for e in errors: print("- "+e)
    sys.exit(1)

print(f"OFE PROOF-CONTAINER AUDIT PASS ({len(list(FORMAL_ENV.finditer(text)))} proof-bearing containers)")
