from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "kernel/development/EDU16_RECONSTRUCTED_STATE.json"

class DevelopmentalOwnershipError(ValueError):
    pass


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class RepairCandidate:
    schema: str
    candidate_id: str
    parent_carrier_id: str
    parent_state_sha256: str
    residual: str
    problem_statement: str
    discriminator: str
    machinery_change: dict[str, Any]
    expected_changed_admissibility: str
    non_goals: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    implementation_identity: dict[str, str]
    author_controller_id: str
    author_controller_state_sha256: str
    hidden_evaluation_exposed: bool
    external_model_supplied_substantive_repair: bool
    promotion_authority: bool = False


def load_parent(path: Path = PARENT) -> tuple[dict[str, Any], str]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("carrier_id") != "EDU16-RC1":
        raise DevelopmentalOwnershipError("repair parent must be EDU16-RC1")
    return state, canonical_sha256(state)


def validate_candidate(candidate: dict[str, Any], *, parent_path: Path = PARENT) -> list[str]:
    errors: list[str] = []
    parent, parent_sha = load_parent(parent_path)

    required = {
        "schema", "candidate_id", "parent_carrier_id", "parent_state_sha256",
        "residual", "problem_statement", "discriminator", "machinery_change",
        "expected_changed_admissibility", "non_goals", "stop_conditions",
        "implementation_identity", "author_controller_id",
        "author_controller_state_sha256", "hidden_evaluation_exposed",
        "external_model_supplied_substantive_repair", "promotion_authority",
    }
    missing = sorted(required - set(candidate))
    if missing:
        return [f"missing fields: {missing}"]

    if candidate["schema"] != "Venus.EDU17R1RepairCandidate.v0.1":
        errors.append("wrong candidate schema")
    if candidate["parent_carrier_id"] != parent["carrier_id"]:
        errors.append("candidate parent is not EDU16-RC1")
    if candidate["parent_state_sha256"] != parent_sha:
        errors.append("candidate parent-state hash mismatch")
    if candidate["residual"] != "MENTION != INCIDENCE":
        errors.append("candidate does not consume the frozen EDU17R1 residual")
    if candidate["hidden_evaluation_exposed"] is not False:
        errors.append("candidate must be authored before hidden #31 exposure")
    if candidate["external_model_supplied_substantive_repair"] is not False:
        errors.append("externally supplied substantive repair cannot be labeled Venus-owned")
    if candidate["promotion_authority"] is not False:
        errors.append("candidate authorship receipt cannot grant promotion authority")

    controller = candidate.get("author_controller_id")
    if not isinstance(controller, str) or not controller:
        errors.append("missing admitted developmental controller identity")
    controller_sha = candidate.get("author_controller_state_sha256")
    if not isinstance(controller_sha, str) or len(controller_sha) != 64:
        errors.append("invalid controller-state SHA-256")

    for field in ("problem_statement", "discriminator", "expected_changed_admissibility"):
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            errors.append(f"{field} must be non-empty")
    if not isinstance(candidate.get("machinery_change"), dict) or not candidate["machinery_change"]:
        errors.append("machinery_change must be a non-empty structured object")

    impl = candidate.get("implementation_identity")
    if not isinstance(impl, dict):
        errors.append("implementation_identity must be an object")
    else:
        for key in ("artifact", "sha256", "version"):
            if not impl.get(key):
                errors.append(f"implementation_identity.{key} required")

    return errors


def bind_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    errors = validate_candidate(candidate)
    if errors:
        raise DevelopmentalOwnershipError("; ".join(errors))
    receipt = {
        "schema": "Venus.EDU17R1RepairOwnershipReceipt.v0.1",
        "candidate_sha256": canonical_sha256(candidate),
        "candidate_id": candidate["candidate_id"],
        "parent_carrier_id": candidate["parent_carrier_id"],
        "parent_state_sha256": candidate["parent_state_sha256"],
        "residual": candidate["residual"],
        "author_controller_id": candidate["author_controller_id"],
        "author_controller_state_sha256": candidate["author_controller_state_sha256"],
        "hidden_evaluation_exposed": False,
        "external_model_supplied_substantive_repair": False,
        "promotion_authority": False,
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    return receipt
