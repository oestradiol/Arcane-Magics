#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "provenance" / "HISTORICAL_DISTINCTION_TEST_MATRIX.json"
TEST_DIR = ROOT / "tests"
SCRIPT_DIR = ROOT / "scripts"

ALLOWED_STATUS = {
    "IMPLEMENTED",
    "IMPLEMENTED_PARTIAL",
    "IMPLEMENTED_PROVENANCE_ONLY",
    "IMPLEMENTED_PROSE_ONLY",
    "PLANNED",
    "OPEN_EXTRACTION",
    "HISTORICAL_ONLY",
}

errors: list[str] = []

if not MATRIX.exists():
    errors.append("missing provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json")
else:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    rows = data.get("distinctions", [])
    if not rows:
        errors.append("historical distinction matrix has no rows")
    seen: set[str] = set()
    required = {
        "id",
        "source_revision_or_branch",
        "source_artifact",
        "distinction",
        "triggering_experiment_or_failure",
        "causal_consequence",
        "later_dependents",
        "current_owner",
        "test_layer",
        "status",
        "credit_genealogy_note",
        "reopening_condition",
    }
    for i, row in enumerate(rows, 1):
        missing = sorted(required - set(row))
        if missing:
            errors.append(f"row {i}: missing fields {missing}")
            continue
        rid = row["id"]
        if rid in seen:
            errors.append(f"duplicate distinction id: {rid}")
        seen.add(rid)
        if row["status"] not in ALLOWED_STATUS:
            errors.append(f"{rid}: invalid status {row['status']}")
        src = ROOT / row["source_artifact"]
        if not src.exists():
            errors.append(f"{rid}: source artifact missing: {row['source_artifact']}")
        test_path = row.get("test_path")
        if row["status"].startswith("IMPLEMENTED") and test_path:
            p = ROOT / test_path
            if not p.exists():
                errors.append(f"{rid}: mapped test/audit missing: {test_path}")
        if row["status"] == "IMPLEMENTED" and not test_path:
            errors.append(f"{rid}: IMPLEMENTED requires test_path")

    # These are constitutional/historical separators already relied upon by live docs.
    required_ids = {
        "RECEIPT_NOT_RETURN",
        "WORD_NOT_PORTAL",
        "LOCAL_FAILURE_NOT_GLOBAL",
        "CURRENT_LABEL_NOT_AUTHORITY",
        "MATURE_SUBSTITUTION_NOT_GENEALOGY_ERASURE",
        "MEMORY_NOT_LEARNING",
        "MAP_NOT_TRAVERSAL",
        "UNKNOWN_NOT_PERMISSION",
        "FOUNDER_LABEL_NOT_SEMANTICS",
        "HANDOFF_NOT_REPLICATION",
        "NEGATIVE_BRANCH_PRESERVED",
        "CERTIFIED_INSUFFICIENCY_BEFORE_EXPANSION",
        "FUTURE_FAMILY_REOPENING",
        "SELECTED_EVIDENCE_NOT_RETURN_BUNDLE",
        "MENTION_NOT_INCIDENCE",
        "NO_GLOBAL_AGENT_LIFT",
        "STOP_REENTRY_NOT_FAKE_REVISION",
        "STATUS_FOSSIL",
        "NEGATIVE_GLOBALIZE",
        "MALFORMED_OPEN",
        "BRIDGE_THEOREM_LAUNDER",
    }
    absent = sorted(required_ids - seen)
    if absent:
        errors.append("matrix missing required historical distinctions: " + ", ".join(absent))

# Every issue in the roadmap range should be named by the test-architecture issue.
roadmap_issue = ROOT / "docs" / "TEST_COVERAGE_MATRIX.md"
if roadmap_issue.exists():
    text = roadmap_issue.read_text(encoding="utf-8", errors="replace")
    numbers = {int(n) for n in re.findall(r"#(\d+)", text)}
    # Coverage is allowed to omit closed issues later, but v0.1 explicitly covers the current planning range.
    for n in range(4, 38):
        if n not in numbers:
            errors.append(f"TEST_COVERAGE_MATRIX.md missing issue #{n}")

if errors:
    print("CAUSAL DISTINCTION / COVERAGE AUDIT FAIL")
    for error in errors:
        print("- " + error)
    sys.exit(1)

print("CAUSAL DISTINCTION / COVERAGE AUDIT PASS")
