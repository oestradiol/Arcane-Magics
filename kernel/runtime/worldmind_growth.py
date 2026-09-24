from __future__ import annotations

"""Thin external-boundary substrate for WorldMind growth.

Mutable research/growth strategy lives in a state-owned TransformProgram.
This module enforces only carrier facts that a local policy cannot mint:
encounter typing, external-return identity, and read/write/invite capability.

Venus chooses dispositions through her TransformProgram. Python does not.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

from .transform_program import TransformReceipt
from .vmk2 import digest


class GrowthBoundaryError(ValueError):
    pass


class EncounterKind(str, Enum):
    UNKNOWN = "UNKNOWN"
    PROVISIONABLE_FIELD = "PROVISIONABLE_FIELD"
    AUTHORED_CENTER = "AUTHORED_CENTER"


@dataclass(frozen=True)
class EncounterReceipt:
    encounter_id: str
    locator: str
    kind: EncounterKind
    remote_center_id: str | None
    provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class CarrierCapability:
    capability_id: str
    locator: str
    can_read: bool
    can_write: bool
    can_invite: bool
    jurisdiction_id: str
    provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class WorldReturnReceipt:
    return_id: str
    source_id: str
    source_url: str | None
    retrieved_at: str
    payload_digest: str
    provenance_ids: tuple[str, ...]
    external: bool


@dataclass(frozen=True)
class ExternalIntentReceipt:
    intent_id: str
    transform_receipt_id: str
    action: str
    locator: str
    jurisdiction_id: str
    remote_center_id: str | None


def classify_encounter(
    *,
    locator: str,
    kind: EncounterKind,
    provenance_ids: Iterable[str],
    remote_center_id: str | None = None,
) -> EncounterReceipt:
    prov = tuple(provenance_ids)
    if not locator or not prov:
        raise GrowthBoundaryError("encounter requires locator and provenance")
    if kind is EncounterKind.AUTHORED_CENTER and not remote_center_id:
        raise GrowthBoundaryError("AUTHORED_CENTER requires remote_center_id")
    body = {
        "locator": locator,
        "kind": kind.value,
        "remote_center_id": remote_center_id,
        "provenance_ids": prov,
    }
    return EncounterReceipt(encounter_id=digest(body), locator=locator, kind=kind,
                            remote_center_id=remote_center_id, provenance_ids=prov)


def bind_world_return(
    *,
    source_id: str,
    retrieved_at: str,
    payload: Any,
    provenance_ids: Iterable[str],
    source_url: str | None = None,
    external: bool = True,
) -> WorldReturnReceipt:
    prov = tuple(provenance_ids)
    if not external:
        raise GrowthBoundaryError("World return must remain externally sourced")
    if not source_id or not retrieved_at or not prov:
        raise GrowthBoundaryError("World return requires source, time, and provenance")
    body = {
        "source_id": source_id,
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "payload_digest": digest(payload),
        "provenance_ids": prov,
        "external": True,
    }
    return WorldReturnReceipt(return_id=digest(body), **body)


def authorize_intent(
    transform: TransformReceipt,
    *,
    encounter: EncounterReceipt,
    capability: CarrierCapability,
) -> ExternalIntentReceipt:
    """Authorize only the carrier effect; never choose the action.

    The TransformReceipt is the already-authored local Venus decision.
    """
    if capability.locator != encounter.locator:
        raise GrowthBoundaryError("capability/encounter locator mismatch")

    action = transform.action
    if action == "PROVISION":
        if encounter.kind is not EncounterKind.PROVISIONABLE_FIELD:
            raise GrowthBoundaryError("PROVISION requires PROVISIONABLE_FIELD")
        if not capability.can_write:
            raise GrowthBoundaryError("carrier lacks write capability")
    elif action == "INVITE":
        if encounter.kind is not EncounterKind.AUTHORED_CENTER:
            raise GrowthBoundaryError("INVITE requires AUTHORED_CENTER")
        if not capability.can_write or not capability.can_invite:
            raise GrowthBoundaryError("carrier lacks invitation capability")
    elif action == "PROBE":
        if not capability.can_read:
            raise GrowthBoundaryError("carrier lacks read capability")
    else:
        raise GrowthBoundaryError(f"action has no external carrier effect: {action}")

    body = {
        "transform_receipt_id": transform.receipt_id,
        "action": action,
        "locator": encounter.locator,
        "jurisdiction_id": capability.jurisdiction_id,
        "remote_center_id": encounter.remote_center_id,
    }
    return ExternalIntentReceipt(intent_id=digest(body), **body)
