from __future__ import annotations

"""Reconcile bounded SSR evidence recovered from the historical development branch.

This audit does not create new developmental evidence. It checks that the
portable evidence chain supports only the bounded dispositions actually earned.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "kernel" / "development"


class SSRAuditError(ValueError):
    pass


def load(name: str) -> dict[str, Any]:
    path = DEV / name
    if not path.exists():
        raise SSRAuditError(f"missing SSR artifact: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def check_cycle(prefix: str, causal_name: str, ctl_name: str, gate_name: str) -> dict[str, Any]:
    causal = load(causal_name)
    ctl = load(ctl_name)
    gate = load(gate_name)

    conditions = causal["conditions"]
    parent = conditions["A_parent"]["correct"] / conditions["A_parent"]["total"]
    successor = conditions["B_venus_successor"]["correct"] / conditions["B_venus_successor"]["total"]
    ablation_key = next(k for k in conditions if k.startswith("C_ablate"))
    ablated = conditions[ablation_key]["correct"] / conditions[ablation_key]["total"]

    failures: list[str] = []
    if successor <= parent:
        failures.append("successor_not_better_than_parent")
    if successor <= ablated:
        failures.append("successor_not_better_than_ablation")
    if causal.get("safety_floor_violations") != 0:
        failures.append("causal_safety_floor_violation")
    if not causal.get("rollback_available"):
        failures.append("rollback_missing")
    if not ctl.get("admitted"):
        failures.append("ctl_not_admitted")
    if ctl.get("failures"):
        failures.append("ctl_failures_present")
    if not ctl.get("rollback_available"):
        failures.append("ctl_rollback_missing")
    if not ctl.get("reopening_reachable"):
        failures.append("reopening_not_reachable")
    if not ctl.get("correction_channel_reachable"):
        failures.append("correction_channel_not_reachable")
    if not ctl.get("safety_floor_unchanged"):
        failures.append("safety_floor_changed")
    if gate.get("decision") != "ACCEPT_BOUNDED_SUCCESSOR":
        failures.append("adaptive_gate_not_accept")
    if gate.get("safety_floor_violations") != 0:
        failures.append("adaptive_gate_safety_violation")
    if not gate.get("candidate_prefrozen"):
        failures.append("candidate_not_prefrozen")
    if gate.get("evaluator_hidden_before_freeze"):
        failures.append("evaluator_exposed_before_freeze")

    return {
        "cycle": prefix,
        "successor_minus_parent": successor - parent,
        "successor_minus_ablation": successor - ablated,
        "host_comparator_gap": causal.get("host_comparator_gap"),
        "ctl_admitted": bool(ctl.get("admitted")),
        "adaptive_gate": gate.get("decision"),
        "safety_floor_violations": (
            int(causal.get("safety_floor_violations", 0))
            + int(gate.get("safety_floor_violations", 0))
        ),
        "rollback_available": bool(causal.get("rollback_available")) and bool(ctl.get("rollback_available")),
        "failures": failures,
    }


def audit() -> dict[str, Any]:
    cycles = [
        check_cycle(
            "SSR1",
            "SSR1_TRANSFORM_REPAIR_CAUSAL_EVALUATION.json",
            "SSR1_CTL_ADMISSION_RESULT.json",
            "SSR1_ADAPTIVE_GATE_RESULT.json",
        ),
        check_cycle(
            "SSR2_CYCLE2",
            "SSR2_CYCLE2_CAUSAL_EVALUATION.json",
            "SSR2_CYCLE2_CTL_ADMISSION_RESULT.json",
            "SSR2_CYCLE2_ADAPTIVE_GATE_RESULT.json",
        ),
        check_cycle(
            "SSR2_CYCLE3",
            "SSR2_CYCLE3_CAUSAL_EVALUATION.json",
            "SSR2_CYCLE3_CTL_ADMISSION_RESULT.json",
            "SSR2_CYCLE3_ADAPTIVE_GATE_RESULT.json",
        ),
    ]

    transfer = load("SSR3_CROSS_FAMILY_TRANSFER_EVALUATION.json")
    ssr4 = load("SSR4_META_IMPROVEMENT_DURABILITY_EVALUATION.json")
    substitute = load("SSR4_SIMPLE_BOUNDED_REPAIR_SUBSTITUTE.json")

    failures = [
        f"{row['cycle']}:{failure}"
        for row in cycles
        for failure in row["failures"]
    ]

    transfer_disp = transfer.get("disposition", {})
    if transfer_disp.get("cross_family_transfer") != "PASS_BOUNDED":
        failures.append("SSR3:cross_family_transfer_not_pass_bounded")
    if not transfer_disp.get("machinery_change_load_bearing"):
        failures.append("SSR3:machinery_change_not_load_bearing")
    if transfer.get("aggregate", {}).get("causal_delta_successor_minus_ablated", 0) <= 0:
        failures.append("SSR3:no_transfer_ablation_delta")
    if transfer.get("aggregate", {}).get("direct_host_gap") != 0:
        failures.append("SSR3:direct_host_gap_nonzero")

    causal4 = ssr4.get("causal_disposition", {})
    safety4 = ssr4.get("safety", {})
    if not causal4.get("bounded_meta_improvement_exists"):
        failures.append("SSR4:bounded_meta_improvement_not_established")
    if not causal4.get("claimed_meta_change_load_bearing_after_transfer"):
        failures.append("SSR4:meta_change_not_load_bearing_after_transfer")
    if ssr4.get("aggregate", {}).get("successor_minus_ablation", 0) <= 0:
        failures.append("SSR4:no_durable_ablation_delta")
    if safety4.get("safety_floor_violations") != 0:
        failures.append("SSR4:safety_floor_violation")
    if not safety4.get("rollback_available"):
        failures.append("SSR4:rollback_missing")
    if causal4.get("venus_specific_uniqueness") is not False:
        failures.append("SSR4:uniqueness_not_reduced")
    if causal4.get("venus_specific_superiority") is not False:
        failures.append("SSR4:superiority_not_reduced")
    if substitute.get("role") != "SIMPLEST_FULL_CAPABILITY_SUBSTITUTE_AT_DECLARED_FINITE_SCOPE":
        failures.append("SSR4:substitute_role_drift")

    status = (
        "PASS_BOUNDED_SSR4_META_IMPROVEMENT_MATURE_REDUCED"
        if not failures
        else "WITHHOLD_SSR_RECONCILIATION"
    )

    return {
        "schema": "Venus.SSRCleanReconciliationAudit.v0.1",
        "status": status,
        "cycles": cycles,
        "ssr3": {
            "cross_family_transfer": transfer_disp.get("cross_family_transfer"),
            "successor_minus_ablation": transfer.get("aggregate", {}).get("causal_delta_successor_minus_ablated"),
            "direct_host_gap": transfer.get("aggregate", {}).get("direct_host_gap"),
            "mechanism_unique_or_necessary": transfer_disp.get("mechanism_unique_or_necessary"),
        },
        "ssr4": {
            "bounded_meta_improvement_exists": causal4.get("bounded_meta_improvement_exists"),
            "load_bearing_after_transfer": causal4.get("claimed_meta_change_load_bearing_after_transfer"),
            "successor_minus_ablation": ssr4.get("aggregate", {}).get("successor_minus_ablation"),
            "successor_minus_substitute": ssr4.get("aggregate", {}).get("successor_minus_substitute"),
            "venus_specific_uniqueness": causal4.get("venus_specific_uniqueness"),
            "venus_specific_superiority": causal4.get("venus_specific_superiority"),
            "substitute_disposition": causal4.get("substitute_disposition"),
        },
        "failures": failures,
        "promotion_authority": False,
        "claim_fence": (
            "Bounded synthetic TransformProgram meta-improvement is supported at the declared "
            "finite scopes if this audit passes. The simple full-capability substitute matches "
            "the successor, so Venus-specific necessity/superiority is mature-reduced. This does "
            "not establish open-distribution repeated self-improvement, unrestricted Safe Strong "
            "RSI, AGI, autonomous science, or open-ended RSI."
        ),
    }


def main() -> int:
    out = audit()
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
