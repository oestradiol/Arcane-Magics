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
    parser = argparse.ArgumentParser()
    parser.add_argument("--issues", required=True)
    parser.add_argument("--prs", required=True)
    parser.add_argument("--roadmap", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--history-prs", required=True)
    parser.add_argument("--learning-state", required=True)
    parser.add_argument("--learning-output", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    issues = load_work_items(args.issues, "ISSUE")
    prs = load_work_items(args.prs, "PR")
    roadmap_text = Path(args.roadmap).read_text(encoding="utf-8")
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))

    history_prs = json.loads(Path(args.history_prs).read_text(encoding="utf-8"))
    learning_state = from_json(
        json.loads(Path(args.learning_state).read_text(encoding="utf-8"))
    )
    updated_learning = update_from_cycle_prs(learning_state, history_prs)
    Path(args.learning_output).write_text(
        json.dumps(to_json(updated_learning), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    cycle = make_cycle(
        issues=issues,
        prs=prs,
        internal_policy=policy,
        learner_state_id=json.dumps(to_json(updated_learning), sort_keys=True),
        feature_weights=updated_learning.weights,
        active_autonomous_cycle=active_autonomous_cycle(history_prs),
        repo_root=Path(__file__).resolve().parents[1],
        roadmap_text=roadmap_text,
    )
    Path(args.output).write_text(
        json.dumps(asdict(cycle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(cycle), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
