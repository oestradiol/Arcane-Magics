from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_study import StudyTarget, run_bounded_reproduction


def _target(rows, number: int):
    for row in rows:
        if int(row["number"]) == number:
            return row
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--issues", required=True)
    parser.add_argument("--prs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    cycle = json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    if cycle.get("study_method") != "REPRODUCTION":
        raise SystemExit("selected study method is not REPRODUCTION")

    kind = str(cycle["target_kind"]).upper()
    number = int(cycle["target_number"])
    rows = json.loads(
        Path(args.issues if kind == "ISSUE" else args.prs).read_text(encoding="utf-8")
    )
    row = _target(rows, number)
    if row is None:
        raise SystemExit(f"selected target missing from frozen snapshot: {kind} #{number}")

    target = StudyTarget(
        kind=kind,
        number=number,
        title=str(row.get("title") or ""),
        body=str(row.get("body") or ""),
    )
    receipt = run_bounded_reproduction(
        ROOT,
        cycle_id=str(cycle["cycle_id"]),
        target=target,
        timeout_seconds=args.timeout,
    )
    Path(args.output).write_text(
        json.dumps(asdict(receipt), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(receipt), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
