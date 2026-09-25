from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_recurrence import (
    load_catalog,
    make_live_candidate,
)


def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--problem", required=True)
    p.add_argument("--history-prs")
    p.add_argument("--history-issues")
    p.add_argument(
        "--catalog",
        default=str(ROOT / "kernel/development/AUTONOMOUS_RECURRENCE_CATALOG.json"),
    )
    p.add_argument("--output", required=True)
    args = p.parse_args()

    carriers = []
    for path in (args.history_prs, args.history_issues):
        if path:
            carriers.extend(load(path))

    envelope = make_live_candidate(
        problem=load(args.problem),
        carriers=carriers,
        catalog=load_catalog(args.catalog),
        repository_root=ROOT,
    )
    Path(args.output).write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(envelope, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
