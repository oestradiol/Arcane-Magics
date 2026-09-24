#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "docs" / "TEST_COVERAGE_MATRIX.md"

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_open_issue_coverage.py OPEN_ISSUES.json")
        return 2
    if not COVERAGE.exists():
        print("OPEN ISSUE COVERAGE FAIL: missing docs/TEST_COVERAGE_MATRIX.md")
        return 1

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    open_numbers = {int(row["number"]) for row in payload}
    text = COVERAGE.read_text(encoding="utf-8", errors="replace")
    covered = {int(n) for n in re.findall(r"\|\s*#(\d+)\s*\|", text)}

    missing = sorted(open_numbers - covered)
    stale = sorted(covered - open_numbers)

    if missing:
        print("OPEN ISSUE COVERAGE FAIL")
        print("unmapped open issues:", ", ".join(f"#{n}" for n in missing))
        return 1

    print(
        "OPEN ISSUE COVERAGE PASS "
        f"({len(open_numbers)} open issues; {len(stale)} mapped rows now closed/stale)"
    )
    if stale:
        print("stale mapped rows (non-blocking):", ", ".join(f"#{n}" for n in stale))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
