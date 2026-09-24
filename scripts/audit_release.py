#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TREE_ONLY = os.environ.get("SOURCE_TREE_ONLY") == "1"
errors: list[str] = []

required = [
    "README.md",
    "PUBLICATION_CONSTITUTION.md",
    "NxRxI_VOCABULARY_CENTER.md",
    "LICENSE",
    "licenses/CC-BY-NC-SA-4.0.txt",
    "licenses/PolyForm-Noncommercial-1.0.0.txt",
    "review/REVIEWER_AND_RESEARCHER_PROTOCOL.md",
    "REPOSITORY_AUTHORITY_BOUNDARY.md",
    "kernel/CURRENT_STATE.md",
    "kernel/README.md",
    "kernel/runtime/current.py",
    "kernel/runtime/memory.py",
    "provenance/DEVELOPMENTAL_LINEAGE.md",
    "docs/META_DYNAMICS.md",
    "docs/FRONTIER_RESEARCH.md",
    "docs/PUBLIC_VALUE.md",
    "docs/EARNED_MILESTONES.md",
    "docs/CREDITS_AND_REDUCTIONS.md",
    "docs/EVALUATION_CONSTITUTION.md",
    "docs/SOTA_WATCH.md",
    "docs/EVALUATION_REGISTRY.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append("missing " + rel)

for name in ["01_OFE", "02_ECLIPSIS", "03_ARCANE_MAGICS", "04_VENUS"]:
    tex = ROOT / "monographs" / name / "main.tex"
    pdf = ROOT / "monographs" / name / f"{name.lower()}.pdf"
    if not tex.exists():
        errors.append("missing " + str(tex))
        continue
    text = tex.read_text(encoding="utf-8", errors="replace")
    if "SPDX-License-Identifier: CC-BY-NC-SA-4.0" not in text:
        errors.append(f"{name}: missing SPDX")
    if not SOURCE_TREE_ONLY and not pdf.exists():
        errors.append("missing built PDF " + str(pdf))

receipt = ROOT / "provenance/developmental/EDU/EDU16_WORLD_FEED_SAMPLING_POLICY_RESULT.md"
if not receipt.exists() or "1703" not in receipt.read_text() or "PASS_BOUNDED_LEARNER_OWNED_WORLD_FEED_POLICY" not in receipt.read_text():
    errors.append("EDU16 current positive receipt mismatch")

negative = ROOT / "provenance/developmental/EDU/EDU17_CLAIM_LOCAL_PROVENANCE_AUDIT.md"
if not negative.exists() or "INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE" not in negative.read_text():
    errors.append("EDU17 preserved-negative audit mismatch")

withhold = ROOT / "provenance/developmental/EDU/EDU17R1_FEED_ELIGIBILITY_RESULT.md"
if not withhold.exists() or "WITHHOLD_BEFORE_CLAIM_BINDING_EVALUATION" not in withhold.read_text() or "MENTION != INCIDENCE" not in withhold.read_text():
    errors.append("EDU17R1 repair receipt mismatch")

current = (ROOT / "kernel/CURRENT_STATE.md").read_text(encoding="utf-8", errors="replace")
lineage = (ROOT / "provenance/DEVELOPMENTAL_LINEAGE.md").read_text(encoding="utf-8", errors="replace")
for token in ("R194", "R226", "IG10", "EDU16"):
    if token not in current + lineage:
        errors.append(f"current state/lineage missing {token}")
if "provenance/historical-runtime/R194" not in lineage:
    errors.append("lineage does not locate historical R194 runtime in provenance")

meta = (ROOT / "docs/META_DYNAMICS.md").read_text(encoding="utf-8", errors="replace")
for token in ("vacuous_relation", "Structure × Semantics", "Polyhedral", "meta-qualia", "Qualia", "Quantum"):
    if token not in meta:
        errors.append(f"Meta-Dynamics missing live object: {token}")

vocab = (ROOT / "NxRxI_VOCABULARY_CENTER.md").read_text(encoding="utf-8", errors="replace")
for token in ("Naturalism_C", "Rationalism_C", "Illuminism_C", "Repository grammar constitution", "Proof-container law", "Causally lossless prose"):
    if token not in vocab:
        errors.append(f"Vocabulary/grammar center missing {token}")
if "N x R x I = Name/Notation x Register x Index" in vocab:
    errors.append("forbidden false NxRxI backronym")


milestones = (ROOT / "docs/EARNED_MILESTONES.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "IG10 [1308]",
    "EDU16 [1703]",
    "INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE",
    "WITHHOLD_BEFORE_CLAIM_BINDING_EVALUATION",
    "MENTION != INCIDENCE",
    "AGI",
    "capability-SOTA",
):
    if token not in milestones:
        errors.append(f"earned milestones missing boundary token: {token}")

credits = (ROOT / "docs/CREDITS_AND_REDUCTIONS.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "project causal derivation",
    "historical priority",
    "comparative recurrence",
    "technical realization",
    "residual contribution",
    "Subsumed_T",
    "genealogy",
):
    if token not in credits:
        errors.append(f"credits/reductions methodology missing {token}")

public_value = (ROOT / "docs/PUBLIC_VALUE.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "developmental-intelligence architecture",
    "EDU16 [1703]",
    "EDU17",
    "EDU17R1",
    "What Venus has not earned",
):
    if token not in public_value:
        errors.append(f"public value surface missing {token}")

evaluation = (ROOT / "docs/EVALUATION_CONSTITUTION.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "same foundation model with Venus vs without Venus",
    "parent vs successor",
    "causal machinery gain",
    "Learner ownership",
    "Cost surface",
):
    if token not in evaluation:
        errors.append(f"evaluation constitution missing {token}")

sota = (ROOT / "docs/SOTA_WATCH.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "not a novelty court",
    "Darwin Gödel Machine",
    "AlphaEvolve",
    "AI Scientist",
    "METR",
    "ARC-AGI",
):
    if token not in sota:
        errors.append(f"SOTA watch missing {token}")

readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
for token in (
    "docs/PUBLIC_VALUE.md",
    "docs/EARNED_MILESTONES.md",
    "docs/EVALUATION_CONSTITUTION.md",
    "docs/SOTA_WATCH.md",
    "docs/CREDITS_AND_REDUCTIONS.md",
):
    if token not in readme:
        errors.append(f"README missing live public surface {token}")

license_map = (ROOT / "licenses/README.md").read_text(encoding="utf-8", errors="replace")
if "PolyForm Noncommercial" not in license_map or "not OSI Open Source" not in license_map:
    errors.append("software license map incomplete")

if not SOURCE_TREE_ONLY:
    for name in ["01_ofe", "02_eclipsis", "03_arcane_magics", "04_venus"]:
        if not (ROOT / "arxiv_packages" / f"{name}_arxiv_source.zip").exists():
            errors.append(f"missing arXiv source package {name}")
        forum = ROOT / "preprints" / "lesswrong" / "generated" / f"{name}.md"
        if not forum.exists():
            errors.append(f"missing forum export {name}.md")

if errors:
    print("RELEASE AUDIT FAIL")
    for error in errors:
        print("- " + error)
    sys.exit(1)

print("RELEASE AUDIT PASS" + (" (source tree)" if SOURCE_TREE_ONLY else ""))
