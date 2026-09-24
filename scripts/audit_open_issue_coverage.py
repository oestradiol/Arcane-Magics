#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "docs" / "TEST_COVERAGE_MATRIX.md"
ROADMAP = ROOT / "docs" / "ISSUE_ROADMAP.md"
CYCLE_CARRIER_TITLE = re.compile(r"^venus: autonomous cycle (?:issue|pr)-\d+$", re.I)

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_open_issue_coverage.py OPEN_ISSUES.json")
        return 2
    if not COVERAGE.exists():
        print("OPEN ISSUE COVERAGE FAIL: missing docs/TEST_COVERAGE_MATRIX.md")
        return 1
    if not ROADMAP.exists():
        print("OPEN ISSUE COVERAGE FAIL: missing docs/ISSUE_ROADMAP.md")
        return 1

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    carrier_numbers = {
        int(row["number"])
        for row in payload
        if CYCLE_CARRIER_TITLE.match(str(row.get("title") or ""))
    }
    open_numbers = {
        int(row["number"])
        for row in payload
        if int(row["number"]) not in carrier_numbers
    }

    coverage_text = COVERAGE.read_text(encoding="utf-8", errors="replace")
    covered = {int(n) for n in re.findall(r"\|\s*#(\d+)(?=\s|\|)", coverage_text)}

    roadmap_text = ROADMAP.read_text(encoding="utf-8", errors="replace")
    roadmap_numbers = {int(n) for n in re.findall(r"#(\d+)", roadmap_text)}

    missing_coverage = sorted(open_numbers - covered)
    missing_roadmap = sorted(open_numbers - roadmap_numbers)
    stale = sorted(covered - open_numbers)
    stale_roadmap = sorted(roadmap_numbers - open_numbers)

    if missing_coverage or missing_roadmap:
        print("OPEN ISSUE COVERAGE FAIL")
        if missing_coverage:
            print("unmapped open issues in TEST_COVERAGE_MATRIX:",
                  ", ".join(f"#{n}" for n in missing_coverage))
        if missing_roadmap:
            print("unmapped open issues in ISSUE_ROADMAP:",
                  ", ".join(f"#{n}" for n in missing_roadmap))
        return 1

    print(
        "OPEN ISSUE COVERAGE PASS "
        f"({len(open_numbers)} project issues; cycle_carriers={len(carrier_numbers)}; coverage_stale={len(stale)}; "
        f"roadmap_stale={len(stale_roadmap)})"
    )
    if stale:
        print("stale coverage rows (non-blocking):", ", ".join(f"#{n}" for n in stale))
    if stale_roadmap:
        print("closed issues still mentioned for history (non-blocking):",
              ", ".join(f"#{n}" for n in stale_roadmap))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
