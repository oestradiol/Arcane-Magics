#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "provenance" / "HISTORICAL_DISTINCTION_TEST_MATRIX.json"
COVERAGE = ROOT / "docs" / "TEST_COVERAGE_MATRIX.md"
FOREIGN_POINTERS = ROOT / "provenance" / "CROSS_REGISTER_SOURCE_POINTERS.json"

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
    "HISTORICAL_EVIDENCE_NO_CURRENT_REGRESSION",
    "HISTORICAL_EVIDENCE_MATURE_REDUCED",
    "HISTORICAL_REGRESSION_ORACLE_NEEDS_MINIMAL_REEXECUTION_ROUTE",
    "HISTORICAL_PROMOTED_KERNEL",
    "PRESERVED_NEGATIVE_CARRIER_GAP",
    "HISTORICAL_MATURE_REDUCTION",
    "HISTORICAL_RESULT_MECHANISM_REDUCED",
    "CLOSED_NEGATIVE_DO_NOT_REROLL",
    "REFERENCE_PASS_CURRENT_INVARIANT_COVERED",
    "REFERENCE_PASS_PROSPECTIVE_TRANSFER_TEST_OPEN",
    "READY_ONLY_EXTERNAL_RETURN_OPEN",
    "RECONSTRUCTED_CLAIM_STATE_EVENT_REPLAY_OPEN",
    "EXTERNAL_HEAVY_CUSTODY_HASH_BOUND",
    "OPEN_EXTRACTION_FROM_CANONICAL_CUSTODY",
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
    "exact historical event replay != reconstructed claim-bearing developmental carrier",
    "failure of realization/proxy != parent/global rejection",
    "malformed question != immortal OPEN research object",
    "structural bridge/analogy != target-domain theorem",
)


def source_paths(raw: str) -> list[str]:
    # A row may cite multiple source paths separated by semicolon.
    return [p.strip() for p in raw.split(";") if p.strip()]


def main() -> int:
    errors: list[str] = []

    foreign_sources: dict[tuple[str, str], dict] = {}
    if not FOREIGN_POINTERS.exists():
        errors.append("missing provenance/CROSS_REGISTER_SOURCE_POINTERS.json")
    else:
        pobj = json.loads(FOREIGN_POINTERS.read_text(encoding="utf-8"))
        if pobj.get("schema") != "ArcaneMagics.CrossRegisterSourcePointers.v1":
            errors.append("cross-register source pointer file has wrong schema")
        for row in pobj.get("sources", ()):
            branch = str(row.get("branch") or "")
            path = str(row.get("path") or "")
            commit = str(row.get("commit") or "")
            blob_sha = str(row.get("blob_sha") or "")
            if not branch.startswith("split/") or not path:
                errors.append(f"invalid cross-register source pointer: {row}")
                continue
            if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
                errors.append(f"{branch}:{path}: invalid commit identity")
            if re.fullmatch(r"[0-9a-f]{40}", blob_sha) is None:
                errors.append(f"{branch}:{path}: invalid blob identity")
            foreign_sources[(branch, path)] = row

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
            # The archaeology matrix may cite retired Canonical-only objects or
            # named historical packets that are intentionally not live Git paths.
            # Their absence from Git is part of the custody/disposition fact, not
            # a malformed matrix row.
            if rel.startswith("Canonical") or rel.startswith("R191_"):
                continue
            if rel.startswith("split/") and ":" in rel:
                owner_branch, owner_path = rel.split(":", 1)
                if (owner_branch, owner_path) not in foreign_sources:
                    errors.append(
                        f"{rid}: foreign source lacks exact branch/blob custody: {rel}"
                    )
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

    if len(rows) < 30:
        errors.append(
            f"historical archaeology unexpectedly shrank to {len(rows)} rows; expected >=30"
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
