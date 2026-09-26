from __future__ import annotations

import argparse
import json
from pathlib import Path

from kernel.development.network_inquiry import form_network_query


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--problem", required=True)
    p.add_argument("--output", required=True)
    args=p.parse_args()

    problem=json.loads(Path(args.problem).read_text(encoding="utf-8"))
    query=form_network_query(problem)
    Path(args.output).write_text(
        json.dumps(query.__dict__, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
