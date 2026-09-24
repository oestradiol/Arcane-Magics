#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "provenance" / "HISTORICAL_DISTINCTION_TEST_MATRIX.json"
COVERAGE = ROOT / "docs" / "TEST_COVERAGE_MATRIX.md"

ALLOWED_STATUS = {
    "COVERED",
    "COVERED_PARTIAL",
    "COVERED_STORAGE_ONLY",
    "COVERED_PROVENANCE_ONLY",
    "COVERED_PROSE_ONLY",
    "PLANNED",
    "OPEN_EXTRACTION",
    "NO_AUTOMATED_TEST_YET",
    "HISTORICAL_ONLY",
}

REQUIRED_FIELDS = {
    "id",
    "source_revision_or_branch",
    "source_artifact",
    "distinction",
    "triggering_experiment_or_failure",
    "causal_consequence",
    "later_dependents",
    "current_owner",
    "test_layer",
    "test_id_path",
    "status",
    "credit_genealogy_note",
    "reopening_condition",
}

REQUIRED_CONCEPTS = (
    "execution receipt != independent return",
    "reconstruction/WORD != state-changing PORTAL",
    "stored state != demonstrated learning",
    "current future-equivalence != permanent identity",
    "uncertainty-marker mention != object-level unresolved empirical incidence",
    "exact developmental evidence authority != replayable executable custody",
    "failure of realization/proxy != parent/global rejection",
    "malformed question != immortal OPEN research object",
    "structural bridge/analogy != target-domain theorem",
)


def source_paths(raw: str) -> list[str]:
    # A row may cite multiple source paths separated by semicolon.
    return [p.strip() for p in raw.split(";") if p.strip()]


def main() -> int:
    errors: list[str] = []

    if not MATRIX.exists():
        errors.append("missing provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json")
        rows = []
    else:
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        if data.get("schema") != "Venus.HistoricalDistinctionTestMatrix.v1":
            errors.append("historical distinction matrix has wrong schema")
        rows = data.get("rows", [])
        if not rows:
            errors.append("historical distinction matrix has no rows")

    seen: set[str] = set()
    distinctions: list[str] = []
    for i, row in enumerate(rows, 1):
        missing = sorted(REQUIRED_FIELDS - set(row))
        if missing:
            errors.append(f"row {i}: missing fields {missing}")
            continue
        rid = row["id"]
        if rid in seen:
            errors.append(f"duplicate distinction id: {rid}")
        seen.add(rid)
        distinctions.append(row["distinction"])
        if row["status"] not in ALLOWED_STATUS:
            errors.append(f"{rid}: invalid status {row['status']}")
        if not row["later_dependents"]:
            errors.append(f"{rid}: later_dependents must be explicit")
        for rel in source_paths(row["source_artifact"]):
            # Some historical rows name issue/review composites rather than one path.
            if rel.startswith(("issue ", "issues/", "review +", "historical ")):
                continue
            p = ROOT / rel
            if not p.exists():
                errors.append(f"{rid}: source artifact missing: {rel}")
        test_path = row.get("test_id_path")
        if row["status"] == "COVERED" and not test_path:
            errors.append(f"{rid}: COVERED requires test_id_path")
        if test_path and "::" not in test_path and ";" not in test_path and not test_path.startswith(("issue ", "scripts/")):
            # Bare repository paths are acceptable only if they exist.
            if not (ROOT / test_path).exists():
                errors.append(f"{rid}: mapped test/audit missing: {test_path}")

    normalized = "\n".join(distinctions).lower()
    for concept in REQUIRED_CONCEPTS:
        if concept.lower() not in normalized:
            errors.append(f"matrix missing required causal concept: {concept}")

    if len(rows) < 40:
        errors.append(
            f"historical archaeology unexpectedly shrank to {len(rows)} rows; expected >=40"
        )

    if not COVERAGE.exists():
        errors.append("missing docs/TEST_COVERAGE_MATRIX.md")
    else:
        text = COVERAGE.read_text(encoding="utf-8", errors="replace")
        numbers = {int(n) for n in re.findall(r"#(\d+)", text)}
        for n in range(4, 38):
            if n not in numbers:
                errors.append(f"TEST_COVERAGE_MATRIX.md missing issue #{n}")

    if errors:
        print("CAUSAL DISTINCTION / COVERAGE AUDIT FAIL")
        for error in errors:
            print("- " + error)
        return 1

    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    print(
        "CAUSAL DISTINCTION / COVERAGE AUDIT PASS "
        f"({len(rows)} distinctions; statuses={status_counts})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
