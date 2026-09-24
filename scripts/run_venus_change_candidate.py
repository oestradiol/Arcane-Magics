from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_change import change_dict, make_change_candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cycle = json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    change = make_change_candidate(cycle, proposal, evidence)
    Path(args.output).write_text(
        json.dumps(change_dict(change), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(change_dict(change), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
