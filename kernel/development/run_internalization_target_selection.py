from __future__ import annotations

import json
from pathlib import Path

from kernel.development.ownership_audit import (
    CausalReturn,
    FunctionOwnership,
    select_internalization_target,
)

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "kernel/development/INTERNALIZATION_OWNERSHIP_INVENTORY.json"
RETURNS = ROOT / "kernel/development/INTERNALIZATION_CAUSAL_RETURNS.json"


def run() -> dict:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    returned = json.loads(RETURNS.read_text(encoding="utf-8"))
    functions = tuple(FunctionOwnership(**row) for row in inventory["rows"])
    causal = tuple(
        CausalReturn(
            function_id=row["function_id"],
            ablation_changes_behavior=bool(row["ablation_changes_behavior"]),
            returned_gain_if_internalized=row["returned_gain_if_internalized"],
            provenance_id=row["provenance_id"],
        )
        for row in returned["returns"]
    )
    outcome = select_internalization_target(functions, causal_returns=causal)
    return {
        "schema": "Venus.InternalizationTargetSelectionResult.v0.1",
        "status": outcome.status,
        "candidate_ids": list(outcome.candidate_ids),
        "selected_target_id": outcome.selected_target_id,
        "selection_basis": outcome.selection_basis,
        "promotion_authority": outcome.promotion_authority,
        "world_execution_owner": "EXTERNAL_WORLD_INTERFACE",
        "evaluation_owner": "INDEPENDENT_EVALUATOR",
    }


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
