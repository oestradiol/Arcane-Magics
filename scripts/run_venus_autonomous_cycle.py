from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from kernel.development.autonomous_worker import load_work_items, make_cycle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issues", required=True)
    parser.add_argument("--prs", required=True)
    parser.add_argument("--roadmap", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    issues = load_work_items(args.issues, "ISSUE")
    prs = load_work_items(args.prs, "PR")
    roadmap_text = Path(args.roadmap).read_text(encoding="utf-8")
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))

    recent = []
    for pr in prs:
        if pr.title.lower().startswith("venus: autonomous cycle"):
            # The cycle PR itself is excluded by the selector. A future carrier
            # may also parse an explicit prior-target marker for stronger
            # no-reroll behavior.
            recent.append(("PR", pr.number))

    cycle = make_cycle(
        issues=issues,
        prs=prs,
        roadmap_text=roadmap_text,
        internal_policy=policy,
        recent_targets=recent,
    )
    Path(args.output).write_text(
        json.dumps(asdict(cycle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(cycle), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
