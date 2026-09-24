from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_patch import (
    load_write_policy,
    make_patch_plan,
    patch_plan_dict,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--write-policy", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cycle = json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    policy = load_write_policy(args.write_policy)
    plan = make_patch_plan(cycle, policy)
    payload = patch_plan_dict(plan)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
