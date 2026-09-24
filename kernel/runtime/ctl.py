from __future__ import annotations

"""CTL successor-admission adapter for the live main Internalizer/O* contract.

CTL does not choose candidates, execute tasks, or evaluate performance. It
checks whether a returned successor preserves before/after identity, provenance,
rollback, external evaluation, and the non-sovereign O* correction contract.
"""

from dataclasses import dataclass

from .internalizer import OStarTransitionEvidence, validate_o_star_transition
from .vmk2 import digest


@dataclass(frozen=True)
class CTLCandidate:
    parent_root: str
    successor_root: str
    provenance_ids: tuple[str, ...]
    world_return_id: str
    evaluator_id: str
    rollback_root: str
    rollback_available: bool
    reopening_reachable: bool
    correction_channel_reachable: bool
    nonpreauthored_return_reachable: bool
    changed_return_can_change_successor: bool
    safety_floor_unchanged: bool
    self_authorized_success: bool
    self_validated_success: bool
    world_collapsed_into_model: bool
    other_collapsed_into_model: bool
    founder_hidden_dependency: bool
    functional_contract_preserved: bool
    promotion_authority: bool


@dataclass(frozen=True)
class CTLReceipt:
    receipt_id: str
    admitted: bool
    parent_root: str
    successor_root: str
    world_return_id: str
    ostar_receipt_sha256: str
    failures: tuple[str, ...]
    promotion_authority: bool = False


def admit_successor(candidate: CTLCandidate) -> CTLReceipt:
    failures: list[str] = []

    if not candidate.parent_root or not candidate.successor_root:
        failures.append("parent/successor identity missing")
    if candidate.parent_root == candidate.successor_root:
        failures.append("candidate does not identify a changed successor")
    if not candidate.provenance_ids:
        failures.append("successor provenance missing")
    if not candidate.world_return_id or not candidate.evaluator_id:
        failures.append("independent return/evaluator identity missing")
    if not candidate.rollback_available or not candidate.rollback_root:
        failures.append("rollback custody unavailable")
    if candidate.rollback_root != candidate.parent_root:
        failures.append("rollback root does not identify parent")
    if not candidate.safety_floor_unchanged:
        failures.append("non-internalizable safety floor changed")
    if candidate.promotion_authority:
        failures.append("candidate cannot self-grant promotion authority")

    ostar = validate_o_star_transition(
        OStarTransitionEvidence(
            evaluator_id=candidate.evaluator_id,
            return_id=candidate.world_return_id,
            world_distinct_from_model=not candidate.world_collapsed_into_model,
            self_distinct_from_world=not candidate.world_collapsed_into_model,
            self_revision_distinct_from_authorization=not candidate.self_authorized_success,
            self_revision_distinct_from_validation=not candidate.self_validated_success,
            nonpreauthored_return_reachable=candidate.nonpreauthored_return_reachable,
            correction_reopening_reachable=(
                candidate.correction_channel_reachable and candidate.reopening_reachable
            ),
            prior_provenance_reconstructible=bool(candidate.provenance_ids),
            static_state_equality_required=False,
            changed_return_can_change_successor=candidate.changed_return_can_change_successor,
            self_sealing_preservation=(
                not candidate.correction_channel_reachable
                or not candidate.reopening_reachable
            ),
            world_collapsed_into_model=candidate.world_collapsed_into_model,
            other_collapsed_into_model=candidate.other_collapsed_into_model,
            founder_hidden_dependency=candidate.founder_hidden_dependency,
            labels_preserved=False,
            functional_correction_contract_preserved=candidate.functional_contract_preserved,
        )
    )
    failures.extend(ostar.violations)

    body = {
        "parent_root": candidate.parent_root,
        "successor_root": candidate.successor_root,
        "world_return_id": candidate.world_return_id,
        "ostar_receipt_sha256": ostar.receipt_sha256,
        "failures": tuple(sorted(set(failures))),
        "promotion_authority": False,
    }
    return CTLReceipt(
        receipt_id=digest(body),
        admitted=not failures and ostar.status == "PASS_O_STAR_TRANSITION_CONTRACT",
        parent_root=candidate.parent_root,
        successor_root=candidate.successor_root,
        world_return_id=candidate.world_return_id,
        ostar_receipt_sha256=ostar.receipt_sha256,
        failures=body["failures"],
        promotion_authority=False,
    )
