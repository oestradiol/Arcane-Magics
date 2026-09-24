from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from typing import Any

from kernel.development.edu17r1_repair_contract import (
    canonical_sha256,
    load_parent,
    validate_candidate,
)

ROOT = Path(__file__).resolve().parents[2]
RESIDUAL = ROOT / "kernel/development/EDU17R1_TYPED_RESIDUAL.json"

CONTROLLER_ID = "EDU16-RC1::RECURSIVE_PROPOSAL_V0.1"
VERSION = "EDU16_RC1_RECURSIVE_PROPOSAL_v0.1"


class RecursiveProposalError(ValueError):
    pass


@dataclass(frozen=True)
class RepairFamily:
    id: str
    mismatch: str
    machinery_kind: str


FAMILIES = (
    RepairFamily("RELATION_BINDING", "surface_without_target_relation", "typed_relation_admission_gate"),
    RepairFamily("PROVENANCE_BINDING", "source_unbound", "claim_local_provenance_gate"),
    RepairFamily("TEMPORAL_BINDING", "temporal_unbound", "event_order_gate"),
    RepairFamily("AUTHORITY_BINDING", "authority_unbound", "authority_jurisdiction_gate"),
    RepairFamily("DEPENDENCY_BINDING", "dependency_unbound", "dependency_closure_gate"),
)


def source_sha256(path: Path = Path(__file__)) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_typed_residual(path: Path = RESIDUAL) -> dict[str, Any]:
    residual = json.loads(path.read_text(encoding="utf-8"))
    if residual.get("schema") != "Venus.TypedDevelopmentalResidual.v0.1":
        raise RecursiveProposalError("unexpected typed residual schema")
    if residual.get("hidden_evaluation_exposed") is not False:
        raise RecursiveProposalError("hidden evaluation must remain unexposed")
    return residual


def derive_mismatches(residual: dict[str, Any]) -> tuple[str, ...]:
    o = residual["observations"]
    out: list[str] = []
    if o.get("surface_signal_present") and not o.get("required_target_relation_present"):
        out.append("surface_without_target_relation")
    if not o.get("source_binding_present"):
        out.append("source_unbound")
    if not o.get("temporal_binding_present"):
        out.append("temporal_unbound")
    if not o.get("authority_binding_present"):
        out.append("authority_unbound")
    if not o.get("dependency_binding_present"):
        out.append("dependency_unbound")
    return tuple(out)


def select_family(residual: dict[str, Any]) -> RepairFamily:
    mismatches = derive_mismatches(residual)
    if not mismatches:
        raise RecursiveProposalError("STOP_NO_LIVE_REPAIR_MISMATCH")
    matching = tuple(f for f in FAMILIES if f.mismatch in mismatches)
    if len(mismatches) != 1 or len(matching) != 1:
        raise RecursiveProposalError("WITHHOLD_MULTI_AXIS_REPAIR_AMBIGUITY")
    return matching[0]


def _relation_candidate(parent: dict[str, Any], parent_sha: str, residual: dict[str, Any]) -> dict[str, Any]:
    machinery_change = {
        "kind": "typed_relation_admission_gate",
        "rule": "surface observation is insufficient; admit the target classification only from an explicit typed target relation",
        "required_evidence": ["required_target_relation_present"],
        "insufficient_evidence": ["surface_signal_present"],
        "on_missing_relation": "WITHHOLD",
        "preserve_axes": ["source_binding", "temporal_binding", "authority_binding", "dependency_binding"],
        "label_gauge": "renaming the surface marker must not change classification when typed relations are unchanged",
    }
    discriminator = (
        "Hold the surface signal fixed while varying only the typed target relation: "
        "classification must follow the relation. Then rename the surface signal while "
        "preserving the typed relation: classification must remain invariant."
    )
    seed = {
        "parent": parent_sha,
        "residual": residual["id"],
        "family": "RELATION_BINDING",
        "machinery_change": machinery_change,
        "discriminator": discriminator,
    }
    return {
        "schema": "Venus.EDU17R1RepairCandidate.v0.1",
        "candidate_id": "RC-" + canonical_sha256(seed)[:20],
        "parent_carrier_id": parent["carrier_id"],
        "parent_state_sha256": parent_sha,
        "residual": "MENTION != INCIDENCE",
        "problem_statement": (
            "A surface signal was admitted as evidence for a target relation even though "
            "the returned trace showed the target relation itself was absent."
        ),
        "discriminator": discriminator,
        "machinery_change": machinery_change,
        "expected_changed_admissibility": (
            "surface-only cases WITHHOLD; relation-grounded cases remain admissible; "
            "surface renaming alone cannot change the decision"
        ),
        "non_goals": [
            "hidden benchmark optimization",
            "general semantic understanding",
            "developmental promotion",
            "AGI or consciousness inference",
        ],
        "stop_conditions": [
            "WITHHOLD if more than one independent repair axis is implicated",
            "STOP if no live mismatch remains",
            "do not expose hidden issue #31 labels before candidate freeze",
        ],
        "implementation_identity": {
            "artifact": "kernel/development/recursive_proposal.py",
            "sha256": source_sha256(),
            "version": VERSION,
        },
        "author_controller_id": CONTROLLER_ID,
        "author_controller_state_sha256": parent_sha,
        "hidden_evaluation_exposed": False,
        "external_model_supplied_substantive_repair": False,
        "promotion_authority": False,
    }


def generate_candidate(*, residual_path: Path = RESIDUAL) -> dict[str, Any]:
    parent, parent_sha = load_parent()
    owned = set(parent.get("owned", ()))
    required_owned = {
        "curriculum target selection",
        "curriculum gate proposal",
        "open-domain problem selection",
        "research-question formation",
    }
    if not required_owned.issubset(owned):
        raise RecursiveProposalError("parent lacks admitted proposal-formation ownership")

    residual = load_typed_residual(residual_path)
    family = select_family(residual)
    if family.id != "RELATION_BINDING":
        raise RecursiveProposalError(f"WITHHOLD_UNIMPLEMENTED_REPAIR_FAMILY:{family.id}")

    candidate = _relation_candidate(parent, parent_sha, residual)
    errors = validate_candidate(candidate)
    if errors:
        raise RecursiveProposalError("; ".join(errors))
    return candidate


def main() -> int:
    candidate = generate_candidate()
    print(json.dumps(candidate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
