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
from kernel.development.autonomous_problem_formation import (
    bind_problem_to_carriers,
    form_problem,
    problem_dict,
    snapshot_to_incidence,
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
    parser.add_argument("--learning-output", required=True)
    parser.add_argument("--developmental-parent-state", default=str(ROOT / "kernel/development/EDU16_RECONSTRUCTED_STATE.json"))
    parser.add_argument("--current-state-receipt", default=str(ROOT / "kernel/custody/R226_CURRENT_STATE_RECEIPT.json"))
    parser.add_argument("--problem-output")
    parser.add_argument(
        "--standing-obligation",
        default=str(ROOT / "kernel/development/CANONICAL_TELIC_RECOVERY_BOOTSTRAP.json"),
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    issues = load_work_items(args.issues, "ISSUE")
    prs = load_work_items(args.prs, "PR")
    roadmap_text = Path(args.roadmap).read_text(encoding="utf-8")
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    developmental_parent = json.loads(Path(args.developmental_parent_state).read_text(encoding="utf-8"))
    current_state_receipt = json.loads(Path(args.current_state_receipt).read_text(encoding="utf-8"))

    history_prs = json.loads(Path(args.history_prs).read_text(encoding="utf-8"))
    history_issues = (
        json.loads(Path(args.history_issues).read_text(encoding="utf-8"))
        if args.history_issues else []
    )
    history_carriers = tuple(history_prs) + tuple(history_issues)
    learning_state = from_json(
        json.loads(Path(args.learning_state).read_text(encoding="utf-8"))
    )
    updated_learning = update_from_cycle_prs(learning_state, history_carriers)
    Path(args.learning_output).write_text(
        json.dumps(to_json(updated_learning), indent=2, sort_keys=True) + "\n",
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
    barriers = target_barriers(history_carriers)
    active_cycle = active_autonomous_cycle(history_carriers)

    all_items = tuple(issues) + tuple(prs)
    standing_carrier_key = None
    standing_orientation_active = False
    standing_path = Path(args.standing_obligation)
    if standing_path.exists():
        standing = json.loads(standing_path.read_text(encoding="utf-8"))
        carrier = standing.get("carrier") or {}
        standing_status = str(standing.get("status") or "")
        standing_orientation_active = (
            standing_status == "ACTIVE_STANDING_ORIENTATION"
        )
        if standing_status == "PREFROZEN_RECOVERY_OBLIGATION":
            kind = str(carrier.get("kind") or "").upper()
            number = int(carrier.get("number", 0) or 0)
            if kind in {"ISSUE", "PR"} and number > 0:
                standing_carrier_key = (kind, number)
    formed_problem = form_problem(
        snapshot_to_incidence(
            all_items,
            standing_carrier_key=standing_carrier_key,
        ),
        standing_orientation_active=standing_orientation_active,
    )
    allowed_target_keys = bind_problem_to_carriers(formed_problem, all_items)
    if args.problem_output:
        Path(args.problem_output).write_text(
            json.dumps(problem_dict(formed_problem), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    cycle = make_cycle(
        issues=issues,
        prs=prs,
        roadmap_text=roadmap_text,
        internal_policy=policy,
        target_barriers=barriers,
        active_cycle=active_cycle,
        kind_utility=utility,
        method_utility=method_utility,
        developmental_parent=developmental_parent,
        current_state_receipt=current_state_receipt,
        formed_problem=problem_dict(formed_problem),
        allowed_target_keys=allowed_target_keys,
    )
    Path(args.output).write_text(
        json.dumps(asdict(cycle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(cycle), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
