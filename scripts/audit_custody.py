#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required = [
    "kernel/custody/R226_CURRENT_STATE_RECEIPT.json",
    "kernel/custody/verify_r226_developmental_seed.py",
    "kernel/custody/IG10_BUNDLE_MANIFEST.json",
    "kernel/custody/verify_ig10.py",
    "kernel/CURRENT_STATE.md",
    "provenance/DEVELOPMENTAL_LINEAGE.md",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append("missing " + rel)

for rel in [
    "kernel/custody/R226_CURRENT_STATE_RECEIPT.json",
    "kernel/custody/IG10_BUNDLE_MANIFEST.json",
]:
    p = ROOT / rel
    if not p.exists():
        continue
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{rel}: invalid JSON: {exc}")
        continue
    raw = json.dumps(data, sort_keys=True)
    if "sha256" not in raw.lower() and "hash" not in raw.lower():
        errors.append(f"{rel}: no hash-bearing custody field found")

for rel in [
    "kernel/custody/verify_r226_developmental_seed.py",
    "kernel/custody/verify_ig10.py",
]:
    p = ROOT / rel
    if not p.exists():
        continue
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as exc:
        errors.append(f"{rel}: verifier does not compile: {exc}")

current = (ROOT / "kernel/CURRENT_STATE.md").read_text(encoding="utf-8", errors="replace") if (ROOT / "kernel/CURRENT_STATE.md").exists() else ""
lineage = (ROOT / "provenance/DEVELOPMENTAL_LINEAGE.md").read_text(encoding="utf-8", errors="replace") if (ROOT / "provenance/DEVELOPMENTAL_LINEAGE.md").exists() else ""

for token in ["R226", "IG10", "EDU16", "EDU17", "EDU17R1"]:
    if token not in current:
        errors.append(f"kernel/CURRENT_STATE.md: missing {token}")
for token in ["R194", "R226", "IG10", "EDU16"]:
    if token not in lineage:
        errors.append(f"provenance/DEVELOPMENTAL_LINEAGE.md: missing {token}")

if "INVALID_FOR_PROMOTION" not in current:
    errors.append("kernel/CURRENT_STATE.md: EDU17 negative disposition missing")
if "MENTION != INCIDENCE" not in current:
    errors.append("kernel/CURRENT_STATE.md: EDU17R1 measured separator missing")
if "R194" in current and "historical" not in current.lower():
    errors.append("kernel/CURRENT_STATE.md: R194 appears without historical boundary")

for rel in [
    "kernel/state/IG10_HOT_CHECKPOINT.json",
    "kernel/runtime/current.py",
    "kernel/development/EDU_CURRENT.json",
]:
    if not (ROOT / rel).exists():
        errors.append("missing " + rel)
if "Git-reconstructible runtime checkpoint" not in current:
    errors.append("kernel/CURRENT_STATE.md: exact IG10 Git custody is not explicit")
if "EDU16" not in current or "1703" not in current:
    errors.append("kernel/CURRENT_STATE.md: later developmental authority is not explicit")

if errors:
    print("CUSTODY / STATE AUDIT FAIL")
    for error in errors:
        print("- " + error)
    sys.exit(1)

print("CUSTODY / STATE AUDIT PASS")
