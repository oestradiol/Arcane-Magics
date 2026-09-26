#!/usr/bin/env python3
"""Fail if a result-bearing developmental revision has no distinction-test row.

Repair object 6 from the 2026-09-26 forensic provenance bundle. The defect it
guards against, in that bundle's own words:

    roadmap/DAG/result provenance exists
    but
    historical executable distinction-row coverage is absent

which lets "a high-level distinction remain live after the mechanism that would
test historical noncollapse is absent from the matrix layer". R206 was the
worked example: the only BOUNDED_RSI node in the graph, still named active
improver at R215, surviving live as one prose line with no executable check.

A revision passes if it has EITHER
  - a row in HISTORICAL_DISTINCTION_TEST_MATRIX.json, or
  - an explicit NO_TEST_ROW_REQUIRED disposition carrying a rationale.

A declared gap is neither. It is an acknowledged absence with a reopening
condition, printed on every run so it cannot fade, and it fails closed if it
stops reproducing — a gap that silently disappears was closed by compression,
not by evidence.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAG = ROOT / "provenance/FULL_DEVELOPMENTAL_DAG_POST_R226_RECOMPILE.json"
MATRIX = ROOT / "provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json"
DISPOSITIONS = ROOT / "provenance/DAG_TEST_COVERAGE_DISPOSITIONS.json"

REVISION = re.compile(r"R\d{1,3}")


def result_bearing_revisions(dag: dict) -> dict[str, dict]:
    """Every node with an id like R206 that carries a status or verdict.

    The DAG scatters revisions across overlays rather than holding one flat
    list, so this walks generically. A node without status or verdict is a
    reference, not a result, and carries no test obligation.
    """
    found: dict[str, dict] = {}

    def walk(obj):
        if isinstance(obj, dict):
            ident = str(obj.get("id") or "")
            if REVISION.fullmatch(ident) and (obj.get("status") or obj.get("verdict")):
                found.setdefault(ident, obj)
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(dag)
    return found


def revisions_cited_by(matrix: dict) -> set[str]:
    cited: set[str] = set()
    for row in matrix.get("rows", []):
        blob = " ".join(
            str(row.get(field, ""))
            for field in ("source_revision_or_branch", "source_artifact", "id")
        )
        cited.update(REVISION.findall(blob))
    return cited


def main() -> int:
    for path in (DAG, MATRIX):
        if not path.exists():
            print(f"WITHHOLD: {path.relative_to(ROOT)} is absent")
            return 2
    try:
        dag = json.loads(DAG.read_text(encoding="utf-8"))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WITHHOLD: cannot parse inputs: {exc}")
        return 2

    dispositions = {}
    declared_gaps = {}
    if DISPOSITIONS.exists():
        try:
            data = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"WITHHOLD: dispositions do not parse: {exc}")
            return 2
        dispositions = {
            row["revision"]: row
            for row in data.get("no_test_row_required", [])
            if "revision" in row
        }
        declared_gaps = {
            row["revision"]: row
            for row in data.get("declared_gaps", [])
            if "revision" in row
        }

    bearing = result_bearing_revisions(dag)
    cited = revisions_cited_by(matrix)

    uncovered = []
    for rev in sorted(bearing, key=lambda r: int(r[1:])):
        if rev in cited or rev in dispositions or rev in declared_gaps:
            continue
        node = bearing[rev]
        uncovered.append(
            f"{rev}  class={node.get('class', '-')}  "
            f"status={str(node.get('status') or node.get('verdict'))[:48]}"
        )

    # A disposition must carry its reasoning, or it is a silent exemption.
    malformed = [
        rev for rev, row in dispositions.items()
        if not str(row.get("rationale", "")).strip()
    ] + [
        rev for rev, row in declared_gaps.items()
        if not str(row.get("reopening_condition", "")).strip()
    ]

    # A declared gap that no longer reproduces was closed by compression, not
    # by evidence. Same rule as the self-sealing auditor's stale residuals.
    stale = sorted(
        rev for rev in declared_gaps
        if rev not in bearing or rev in cited
    )

    if malformed:
        print(f"DAG TEST COVERAGE: {len(malformed)} disposition(s) without reasoning")
        for rev in sorted(malformed):
            print(f"  {rev}")
        return 1

    if stale:
        print(f"DAG TEST COVERAGE: {len(stale)} declared gap(s) no longer reproduce")
        for rev in stale:
            print(f"  {rev}")
        print()
        print("A gap that stops reproducing was either closed by a row or removed")
        print("from the DAG. Record which, with the row that closed it. Do not let")
        print("it lapse silently.")
        return 1

    if uncovered:
        print(f"DAG TEST COVERAGE FINDINGS ({len(uncovered)})")
        for item in uncovered:
            print(f"  {item}")
        print()
        print("Each result-bearing revision needs either a row in")
        print("HISTORICAL_DISTINCTION_TEST_MATRIX.json, or a NO_TEST_ROW_REQUIRED")
        print("disposition with a rationale, or a declared gap with a reopening")
        print("condition. A live distinction whose historical test is absent from")
        print("the matrix layer is the defect this check exists to prevent.")
        return 1

    if declared_gaps:
        print(f"DECLARED COVERAGE GAPS ({len(declared_gaps)}) — acknowledged, unclosed")
        for rev in sorted(declared_gaps, key=lambda r: int(r[1:])):
            print(f"  {rev}: {declared_gaps[rev].get('reopening_condition')}")
        print()

    print(
        f"DAG TEST COVERAGE PASS ({len(bearing)} result-bearing revisions; "
        f"{len(cited & set(bearing))} with matrix rows; "
        f"{len(dispositions)} dispositioned; {len(declared_gaps)} declared gaps)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
