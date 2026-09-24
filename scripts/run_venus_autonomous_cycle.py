from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from kernel.development.autonomous_worker import load_work_items, make_cycle
from kernel.development.autonomous_learning import (
    active_autonomous_cycle,
    from_json,
    to_json,
    update_from_cycle_prs,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--issues", required=True)
    p.add_argument("--prs", required=True)
    p.add_argument("--roadmap", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--history-prs", required=True)
    p.add_argument("--learning-state", required=True)
    p.add_argument("--learning-output", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    issues = load_work_items(args.issues, "ISSUE")
    prs = load_work_items(args.prs, "PR")
    roadmap_text = Path(args.roadmap).read_text(encoding="utf-8")
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    history = json.loads(Path(args.history_prs).read_text(encoding="utf-8"))

    state = from_json(json.loads(Path(args.learning_state).read_text(encoding="utf-8")))
    learned = update_from_cycle_prs(state, history)
    serialized = to_json(learned)
    Path(args.learning_output).write_text(
        json.dumps(serialized, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    cycle = make_cycle(
        issues=issues,
        prs=prs,
        roadmap_text=roadmap_text,
        internal_policy=policy,
        learner_state_id=json.dumps(serialized, sort_keys=True),
        feature_weights=learned.weights,
        active_autonomous_cycle=active_autonomous_cycle(history),
    )
    Path(args.output).write_text(
        json.dumps(asdict(cycle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(cycle), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
