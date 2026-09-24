from __future__ import annotations

"""Minimal executable CTL successor-admission gate.

CTL is the provenance-preserving successor relation. It does not choose a
candidate and does not evaluate task performance. It admits a returned candidate
only when before/after identity, provenance, independent return, rollback,
reopening, and the O* recurrent correction contract remain available.
"""

from dataclasses import dataclass
from typing import Iterable

from .internalizer import OStarTransition, validate_ostar
from .vmk2 import digest


class CTLError(ValueError):
    pass


@dataclass(frozen=True)
class CTLCandidate:
    parent_root: str
    successor_root: str
    provenance_ids: tuple[str, ...]
    world_return_id: str
    world_return_source_id: str
    rollback_root: str
    rollback_available: bool
    reopening_reachable: bool
    correction_channel_reachable: bool
    nonpreauthored_return_reachable: bool
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
    ostar_receipt_id: str
    failures: tuple[str, ...]
    promotion_authority: bool


def admit_successor(candidate: CTLCandidate) -> CTLReceipt:
    failures: list[str] = []

    if not candidate.parent_root or not candidate.successor_root:
        failures.append("parent/successor identity missing")
    if candidate.parent_root == candidate.successor_root:
        failures.append("candidate does not identify a changed successor")
    if not candidate.provenance_ids:
        failures.append("successor provenance missing")
    if not candidate.world_return_id or not candidate.world_return_source_id:
        failures.append("independent World/evaluator return missing")
    if not candidate.rollback_available or not candidate.rollback_root:
        failures.append("rollback custody unavailable")
    if candidate.rollback_root != candidate.parent_root:
        failures.append("rollback root does not identify parent")
    if not candidate.safety_floor_unchanged:
        failures.append("non-internalizable safety floor changed")
    if candidate.promotion_authority:
        failures.append("candidate cannot self-grant promotion authority")

    ostar = validate_ostar(
        OStarTransition(
            before_self_root=candidate.parent_root,
            after_self_root=candidate.successor_root,
            world_return_id=candidate.world_return_id,
            world_return_source_id=candidate.world_return_source_id,
            provenance_reconstructible=bool(candidate.provenance_ids),
            nonpreauthored_return_reachable=candidate.nonpreauthored_return_reachable,
            correction_channel_reachable=candidate.correction_channel_reachable,
            reopening_reachable=candidate.reopening_reachable,
            self_authorized_success=candidate.self_authorized_success,
            self_validated_success=candidate.self_validated_success,
            world_collapsed_into_model=candidate.world_collapsed_into_model,
            other_collapsed_into_model=candidate.other_collapsed_into_model,
            founder_hidden_dependency=candidate.founder_hidden_dependency,
            labels_preserved=False,
            functional_contract_preserved=candidate.functional_contract_preserved,
        )
    )
    failures.extend(ostar.failures)

    body = {
        "parent_root": candidate.parent_root,
        "successor_root": candidate.successor_root,
        "world_return_id": candidate.world_return_id,
        "ostar_receipt_id": ostar.receipt_id,
        "failures": failures,
        "promotion_authority": False,
    }
    return CTLReceipt(
        receipt_id=digest(body),
        admitted=not failures,
        parent_root=candidate.parent_root,
        successor_root=candidate.successor_root,
        world_return_id=candidate.world_return_id,
        ostar_receipt_id=ostar.receipt_id,
        failures=tuple(failures),
        promotion_authority=False,
    )
