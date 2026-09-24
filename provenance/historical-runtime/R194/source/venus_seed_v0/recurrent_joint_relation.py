from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class RecurrentEpisodeWitness:
    rederive_seq: int
    return_revision_seq: int
    later_acquisition_seq: int
    transformed_without_mapping: bool
    nonpreauthored_return: bool
    provenance_guarded: bool
    later_acquisition_changed: bool


def _events(vm):
    return [e for e in vm.journal.events if e.get("kind") not in {"RECONCILIATION", "PROJECT_STATE"}]


def _changed_acquisition(payload: dict[str, Any]) -> bool:
    return (
        payload.get("treatment_model") != payload.get("stale_model")
        or payload.get("treatment_selected_input") != payload.get("stale_selected_input")
    )


def extract_r142_style_recurrent_witnesses(vm) -> list[RecurrentEpisodeWitness]:
    """Extract only complete rederive -> returned local revision -> later acquisition chains.

    Earlier P9/machinery Residuals are intentionally excluded. They are developmental
    ancestry, but they are not evidence that one joint self/world predictive relation was
    repeatedly reconstructed under the Strong-N2 burden.
    """
    evs = _events(vm)
    out: list[RecurrentEpisodeWitness] = []
    for i, e in enumerate(evs):
        if e.get("kind") != "OPAQUE_TRANSFORM_REDERIVATION":
            continue
        rev = None
        acq = None
        for e2 in evs[i + 1 :]:
            if e2.get("kind") == "OPAQUE_TRANSFORM_REDERIVATION":
                break
            if rev is None and e2.get("kind") == "RETURN_BOUND_LOCAL_REVISION":
                rev = e2
                continue
            if rev is not None and e2.get("kind") == "LATER_ACQUISITION_STATE":
                acq = e2
                break
        if rev is None or acq is None:
            continue
        ep = e.get("payload", {})
        rp = rev.get("payload", {})
        ap = acq.get("payload", {})
        out.append(
            RecurrentEpisodeWitness(
                rederive_seq=int(e.get("seq")),
                return_revision_seq=int(rev.get("seq")),
                later_acquisition_seq=int(acq.get("seq")),
                transformed_without_mapping=ep.get("coordinate_mapping_given") is False and bool(ep.get("expressions")),
                nonpreauthored_return=bool(rp.get("bound_token")) and rp.get("self_validation") is False,
                provenance_guarded=int(rp.get("misbound_records_rejected", 0) or 0) > 0,
                later_acquisition_changed=_changed_acquisition(ap),
            )
        )
    return out


def audit_current_recurrence_evidence(vm) -> dict[str, Any]:
    witnesses = extract_r142_style_recurrent_witnesses(vm)
    p9_residuals = sum(1 for e in _events(vm) if e.get("kind") == "P9_DIAGNOSTIC_RESIDUAL")
    machinery_residuals = sum(
        1 for e in _events(vm)
        if e.get("kind") in {"MACHINERY_RESIDUAL", "MULTI_MACHINERY_RESIDUAL"}
    )
    complete = [
        w for w in witnesses
        if w.transformed_without_mapping
        and w.nonpreauthored_return
        and w.provenance_guarded
        and w.later_acquisition_changed
    ]
    return {
        "r142_style_complete_cycles": len(complete),
        "witnesses": [asdict(w) for w in complete],
        "p9_residual_count": p9_residuals,
        "machinery_residual_count": machinery_residuals,
        "p9_or_machinery_residuals_credited_as_strong_n2_recurrence": False,
        "minimum_cycles_for_r150_prospective_spec": 4,
        "strong_n2_recurrence_scientific_status": (
            "OPEN / INSUFFICIENT REPEATED PROSPECTIVE EPISODES"
            if len(complete) < 4
            else "EVIDENCE_PRESENT_BUT_NOT_PROSPECTIVELY_FROZEN"
        ),
    }


def validate_joint_relation_model(root: Path) -> dict[str, Any]:
    model = json.loads((root / "r150" / "R150_RECURRENT_JOINT_RELATION_MODEL_v0.1.json").read_text())
    freeze = json.loads((root / "r150" / "R150_STRONG_N2_PROSPECTIVE_FREEZE_SPEC_v0.1.json").read_text())
    checks = {
        "joint_components_complete": model["joint_object"]["components"] == [
            "Structure_t", "Semantics_t", "Residual_t", "Provenance_<=t", "PredictionUpdate_t"
        ],
        "static_fixed_point_rejected": model["fixed_point"]["rejected"] == "J_(t+1) == J_t",
        "recurrent_update_is_candidate": "nonpreauthored_return_t" in model["fixed_point"]["candidate"],
        "corrigibility_required": model["fixed_point"]["corrigibility_required"] is True,
        "self_sealing_invalid": model["fixed_point"]["self_sealing_invalid"] is True,
        "reciprocal_chart_burden_present": "reconstructibility" in model["charts"]["burden"],
        "multi_episode_floor": int(freeze["minimum_fresh_episodes"]) >= 4,
        "self_only_control": "SELF_ONLY" in freeze["controls"],
        "world_only_control": "WORLD_ONLY" in freeze["controls"],
        "residual_erased_control": "RESIDUAL_ERASED" in freeze["controls"],
        "direct_host_control": "DIRECT_HOST" in freeze["controls"],
        "hard_copy_control": "HARD_COPY_EFFECTIVE_STATE" in freeze["controls"],
        "no_science_in_spec": freeze["status"] == "DESIGN_READY_NOT_FROZEN_NOT_EXECUTED",
    }
    return {"checks": checks, "pass": all(checks.values()), "model": model, "freeze_spec": freeze}


def run_r150_design_audit(vm, root: Path) -> dict[str, Any]:
    ev = audit_current_recurrence_evidence(vm)
    val = validate_joint_relation_model(root)
    checks = {
        "parent_r149": vm.project_state.get("through") == "R149",
        "scientific_head_r142_preserved": str(vm.project_state.get("science", {}).get("N2_FULL_PARENT_R133", "")).startswith("CLOSED"),
        "model_validation": bool(val["pass"]),
        "existing_complete_cycle_count_exactly_one": ev["r142_style_complete_cycles"] == 1,
        "existing_evidence_insufficient_for_recurrence_claim": ev["r142_style_complete_cycles"] < val["freeze_spec"]["minimum_fresh_episodes"],
        "p9_not_laundered": ev["p9_or_machinery_residuals_credited_as_strong_n2_recurrence"] is False,
    }
    return {
        "schema": "Venus.R150.RecurrentJointRelationDesignAudit.v0.1",
        "date": "2026-09-14",
        "transaction": "DESIGN_FORMAL_DEVELOPMENTAL_RECONCILIATION",
        "scientific_effect": "NONE",
        "scientific_head": "R142",
        "parent": "R149",
        "status": "PASS / DESIGN-ADMITTED / SCIENCE-OPEN" if all(checks.values()) else "FAIL",
        "checks": checks,
        "current_recurrence_evidence": ev,
        "fixed_point_retype": {
            "from": "stable self-model/world-model object or static state equality",
            "to": "recurrent rediscovery/update law over one joint self-world relational predictive object",
            "self_chart": "World-as-related-to-this adaptive trajectory",
            "world_chart": "this adaptive trajectory-as-situated-in-World",
            "joint_relation": "Structure x Semantics + Residual + provenance + predictive update relation",
            "mature_project_name": "Intelligent Love",
            "whole_object_science": "OPEN",
        },
        "next_result_bearing_edge": "fresh prospective multi-episode Strong-N2 recurrence freeze; one result seed; no reroll; separately written reconstruction",
    }
