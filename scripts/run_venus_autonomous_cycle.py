from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_worker import load_work_items, make_cycle
from kernel.development.autonomous_meta_learning import (
    choose_strategy,
    from_json as meta_from_json,
    to_json as meta_to_json,
    update_from_cycle_carriers,
)
from kernel.development.autonomous_learning import (
    active_autonomous_cycle,
    from_json,
    target_barriers,
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
    parser.add_argument("--history-issues")
    parser.add_argument("--learning-state", required=True)
    parser.add_argument("--meta-learning-state", required=True)
    parser.add_argument("--learning-output", required=True)
    parser.add_argument("--meta-learning-output", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    issues = load_work_items(args.issues, "ISSUE")
    prs = load_work_items(args.prs, "PR")
    roadmap_text = Path(args.roadmap).read_text(encoding="utf-8")
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))

    history_prs = json.loads(Path(args.history_prs).read_text(encoding="utf-8"))
    history_issues = (
        json.loads(Path(args.history_issues).read_text(encoding="utf-8"))
        if args.history_issues else []
    )
    history_carriers = tuple(history_prs) + tuple(history_issues)
    learning_state = from_json(
        json.loads(Path(args.learning_state).read_text(encoding="utf-8"))
    )
    meta_learning_state = meta_from_json(
        json.loads(Path(args.meta_learning_state).read_text(encoding="utf-8"))
    )
    updated_learning = update_from_cycle_prs(learning_state, history_carriers)
    updated_meta_learning = update_from_cycle_carriers(
        meta_learning_state, history_carriers
    )
    Path(args.learning_output).write_text(
        json.dumps(to_json(updated_learning), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(args.meta_learning_output).write_text(
        json.dumps(meta_to_json(updated_meta_learning), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    utility = {
        "ISSUE": updated_learning.utility("ISSUE"),
        "PR": updated_learning.utility("PR"),
    }
    method_utility = {
        method: updated_learning.method_utility(method)
        for method in updated_learning.method_success
    }
    learning_strategy = choose_strategy(updated_meta_learning)
    barriers = target_barriers(history_carriers)
    active_cycle = active_autonomous_cycle(history_carriers)

    cycle = make_cycle(
        issues=issues,
        prs=prs,
        roadmap_text=roadmap_text,
        internal_policy=policy,
        target_barriers=barriers,
        active_cycle=active_cycle,
        kind_utility=utility,
        method_utility=method_utility,
        learning_strategy=learning_strategy,
    )
    Path(args.output).write_text(
        json.dumps(asdict(cycle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(cycle), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
