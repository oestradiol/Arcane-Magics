#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

FORMAL_ENV = re.compile(r"\\begin\{(lemma|theorem|proposition|corollary)\}(?:\[[^\]]*\])?")
PROOF = re.compile(r"\\begin\{proof\}")
NEXT_BLOCK = re.compile(r"\\begin\{(?:lemma|theorem|proposition|corollary|conjecture|definition|remark|example)\}")

errors: list[str] = []

# Interpretive/model monographs may define objects and state remarks, but exact
# theorem containers belong in the formal spine unless deliberately whitelisted.
for rel in [
    "monographs/02_ECLIPSIS/main.tex",
    "monographs/03_ARCANE_MAGICS/main.tex",
    "monographs/04_VENUS/main.tex",
]:
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    for m in FORMAL_ENV.finditer(text):
        errors.append(f"{rel}: unexpected proof-bearing environment {m.group(1)!r}; move exact result to formal spine or whitelist deliberately")

# OFE is the present formal spine. Every proof-bearing container must have an
# explicit proof before the next theorem-like block.
rel = "monographs/01_OFE/main.tex"
text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
for m in FORMAL_ENV.finditer(text):
    start = m.end()
    nxt = NEXT_BLOCK.search(text, start)
    end = nxt.start() if nxt else len(text)
    block = text[start:end]
    if not PROOF.search(block):
        line = text.count("\n", 0, m.start()) + 1
        errors.append(f"{rel}:{line}: {m.group(1)} lacks an explicit proof before the next formal block")

# The admitted kernel law is also a live formal surface. Every remaining
# proof-bearing container there must have an explicit proof; model/constitutional
# consequences should use definition/remark rather than theorem typography.
kernel_rel = "kernel/VENUS_INCIDENCE_LAW.tex"
kernel_text = (ROOT / kernel_rel).read_text(encoding="utf-8", errors="replace")
for m in FORMAL_ENV.finditer(kernel_text):
    start = m.end()
    nxt = NEXT_BLOCK.search(kernel_text, start)
    end = nxt.start() if nxt else len(kernel_text)
    block = kernel_text[start:end]
    if not PROOF.search(block):
        line = kernel_text.count("\n", 0, m.start()) + 1
        errors.append(
            f"{kernel_rel}:{line}: {m.group(1)} lacks an explicit proof before the next formal block"
        )

for forbidden in [
    "\\begin{proposition}[Label gauge under consequence-equivalent renaming]",
    "\\begin{proposition}[Conditional label non-necessity]",
    "\\begin{theorem}[No self-certification",
    "\\begin{corollary}[Developmental identity]",
]:
    if forbidden in kernel_text:
        errors.append(
            f"{kernel_rel}: constitutional/definitional claim resurrected as proof-bearing container: {forbidden}"
        )

# Conjectures must not be followed by proof environments before the next block.
for m in re.finditer(r"\\begin\{conjecture\}(?:\[[^\]]*\])?", text):
    start = m.end()
    nxt = NEXT_BLOCK.search(text, start)
    end = nxt.start() if nxt else len(text)
    if PROOF.search(text[start:end]):
        line = text.count("\n", 0, m.start()) + 1
        errors.append(f"{rel}:{line}: conjecture unexpectedly contains a proof environment")

# Guard against the specific category errors already found in Eclipsis.
ecl = (ROOT / "monographs/02_ECLIPSIS/main.tex").read_text(encoding="utf-8", errors="replace")
for forbidden in [
    "\\begin{proposition}[Non-collapse]",
    "\\begin{proposition}[No global-agent lift]",
    "\\begin{proposition}[Recursive cyclical Eclipsis singularity]",
    "\\begin{proposition}[Reality-internal Otherness]",
    "\\begin{corollary}[Egotism without sovereignty]",
]:
    if forbidden in ecl:
        errors.append(f"monographs/02_ECLIPSIS/main.tex: model-internal claim resurrected as theorem container: {forbidden}")

if errors:
    print("PROOF-CONTAINER AUDIT FAIL")
    for error in errors:
        print("- " + error)
    sys.exit(1)

count = len(list(FORMAL_ENV.finditer(text)))
print(f"PROOF-CONTAINER AUDIT PASS ({count} proof-bearing OFE containers; interpretive monographs clean)")
