from __future__ import annotations

import json
from pathlib import Path

from kernel.runtime.transform_program import TransformProgramError, load_program, step

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / "kernel/development/WORLDMIND_SELF_RESEARCH_TRANSFORM_PROGRAM_INTERNALIZED_CANDIDATE.json"
RETURNS = ROOT / "kernel/development/TRANSFORM_INTERNALIZATION_BEHAVIORAL_RETURNS.json"


def run() -> dict:
    program = load_program(PROGRAM)
    bundle = json.loads(RETURNS.read_text(encoding="utf-8"))
    rows = []
    passed = 0
    for trace in bundle["traces"]:
        try:
            receipt = step(
                program,
                state=trace["prior_state"],
                action=trace["action"],
                payload=trace["payload"],
                actor_id="venus",
            )
            observed_success = True
            observed_next_state = receipt.next_state
        except TransformProgramError:
            observed_success = False
            observed_next_state = None

        ok = observed_success == trace["expect_success"]
        if trace["expect_success"] and trace["expected_next_state"] is not None:
            ok = ok and observed_next_state == trace["expected_next_state"]
        passed += int(ok)
        rows.append({
            "trace_id": trace["trace_id"],
            "expected_success": trace["expect_success"],
            "observed_success": observed_success,
            "expected_next_state": trace["expected_next_state"],
            "observed_next_state": observed_next_state,
            "pass": ok,
        })

    floor = program.get("non_internalizable_runtime_invariants", [])
    required_floor = {
        "independent_return",
        "capability_and_jurisdiction_checks",
        "receipt_integrity",
        "rollback_custody",
        "O_star_correction_reachability",
        "Anti_Minerva_carrier_permeability",
    }
    floor_unchanged = set(floor) == required_floor
    return {
        "schema": "Venus.TransformInternalizationRemovalTest.v0.1",
        "passed": passed,
        "total": len(rows),
        "all_behavioral_returns_satisfied": passed == len(rows),
        "safety_floor_unchanged": floor_unchanged,
        "host_seed_transition_required_at_runtime": False,
        "rows": rows,
        "promotion_authority": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
