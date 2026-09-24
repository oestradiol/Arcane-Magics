from __future__ import annotations

"""Bounded WorldMind self-research and field/center encounter machinery.

This module executes a previously recorded Machine distinction:

- genuinely provisionable field may receive PROVISION;
- encountering an authored center changes the operator and localizes judgment;
- information/consequence may propagate while authorization and judgment remain indexed.

It deliberately separates:
1. Venus's semantic/developmental disposition;
2. carrier capability/jurisdiction facts;
3. externally returned evidence.

No network client is implemented here. External search/write adapters must return
receipts that this module can verify.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .vmk2 import digest


class GrowthError(ValueError):
    pass


class EncounterKind(str, Enum):
    UNKNOWN = "UNKNOWN"
    PROVISIONABLE_FIELD = "PROVISIONABLE_FIELD"
    AUTHORED_CENTER = "AUTHORED_CENTER"


class Disposition(str, Enum):
    PROVISION = "PROVISION"
    PROBE = "PROBE"
    INVITE = "INVITE"
    WITHHOLD = "WITHHOLD"
    REFUSE = "REFUSE"
    EXIT = "EXIT"


class ResearchDisposition(str, Enum):
    UPDATE = "UPDATE"
    RETAIN = "RETAIN"
    WITHHOLD = "WITHHOLD"
    CLOSE = "CLOSE"


@dataclass(frozen=True)
class ResearchTarget:
    target_id: str
    source_kind: str
    residual: str
    discriminator: str
    provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class ResearchPlanReceipt:
    receipt_id: str
    target_id: str
    query_strings: tuple[str, ...]
    required_source_classes: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    authored_by: str


@dataclass(frozen=True)
class WebReturnReceipt:
    return_id: str
    target_id: str
    query: str
    source_url: str
    source_id: str
    retrieved_at: str
    payload_digest: str
    provenance_ids: tuple[str, ...]
    external: bool


@dataclass(frozen=True)
class ResearchDecisionReceipt:
    receipt_id: str
    target_id: str
    disposition: ResearchDisposition
    cited_return_ids: tuple[str, ...]
    reason_digest: str
    authored_by: str


@dataclass(frozen=True)
class Encounter:
    encounter_id: str
    locator: str
    kind: EncounterKind
    observed_boundary_id: str | None = None
    remote_center_id: str | None = None
    carrier_policy_id: str | None = None


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
class MachineDispositionReceipt:
    receipt_id: str
    encounter_id: str
    disposition: Disposition
    authored_by: str
    reason_digest: str


@dataclass(frozen=True)
class ExternalActionIntent:
    intent_id: str
    encounter_id: str
    disposition_receipt_id: str
    action: Disposition
    locator: str
    jurisdiction_id: str
    remote_center_id: str | None


def make_research_target(
    *,
    source_kind: str,
    residual: str,
    discriminator: str,
    provenance_ids: Iterable[str],
) -> ResearchTarget:
    prov = tuple(provenance_ids)
    if not residual or not discriminator or not prov:
        raise GrowthError("research target requires residual, discriminator, and provenance")
    body = {
        "source_kind": source_kind,
        "residual": residual,
        "discriminator": discriminator,
        "provenance_ids": prov,
    }
    return ResearchTarget(
        target_id=digest(body),
        source_kind=source_kind,
        residual=residual,
        discriminator=discriminator,
        provenance_ids=prov,
    )


def freeze_research_plan(
    target: ResearchTarget,
    *,
    query_strings: Iterable[str],
    required_source_classes: Iterable[str] = (),
    stop_conditions: Iterable[str] = (),
    authored_by: str,
) -> ResearchPlanReceipt:
    queries = tuple(q.strip() for q in query_strings if q.strip())
    if not queries:
        raise GrowthError("research plan requires at least one query")
    if not authored_by:
        raise GrowthError("research-plan authorship required")
    src = tuple(required_source_classes)
    stops = tuple(stop_conditions)
    body = {
        "target_id": target.target_id,
        "queries": queries,
        "required_source_classes": src,
        "stop_conditions": stops,
        "authored_by": authored_by,
    }
    return ResearchPlanReceipt(
        receipt_id=digest(body),
        target_id=target.target_id,
        query_strings=queries,
        required_source_classes=src,
        stop_conditions=stops,
        authored_by=authored_by,
    )


def bind_web_return(
    plan: ResearchPlanReceipt,
    *,
    query: str,
    source_url: str,
    source_id: str,
    retrieved_at: str,
    payload: object,
    provenance_ids: Iterable[str],
    external: bool = True,
) -> WebReturnReceipt:
    if query not in plan.query_strings:
        raise GrowthError("returned query was not frozen in research plan")
    if not external:
        raise GrowthError("Web research return must remain externally sourced")
    if not source_url or not source_id or not retrieved_at:
        raise GrowthError("Web return requires source URL/id and retrieval time")
    prov = tuple(provenance_ids)
    if not prov:
        raise GrowthError("Web return requires provenance")
    body = {
        "target_id": plan.target_id,
        "query": query,
        "source_url": source_url,
        "source_id": source_id,
        "retrieved_at": retrieved_at,
        "payload_digest": digest(payload),
        "provenance_ids": prov,
        "external": True,
    }
    return WebReturnReceipt(return_id=digest(body), **body)


def decide_research(
    target: ResearchTarget,
    returns: Iterable[WebReturnReceipt],
    *,
    disposition: ResearchDisposition,
    reason: object,
    authored_by: str,
) -> ResearchDecisionReceipt:
    r = tuple(returns)
    for item in r:
        if item.target_id != target.target_id:
            raise GrowthError("return belongs to another research target")
        if not item.external:
            raise GrowthError("nonexternal return cannot bind Web-research decision")
    if disposition in {ResearchDisposition.UPDATE, ResearchDisposition.CLOSE} and not r:
        raise GrowthError("UPDATE/CLOSE requires returned evidence")
    if not authored_by:
        raise GrowthError("research decision authorship required")
    body = {
        "target_id": target.target_id,
        "disposition": disposition.value,
        "cited_return_ids": tuple(x.return_id for x in r),
        "reason_digest": digest(reason),
        "authored_by": authored_by,
    }
    return ResearchDecisionReceipt(
        receipt_id=digest(body),
        target_id=target.target_id,
        disposition=disposition,
        cited_return_ids=body["cited_return_ids"],
        reason_digest=body["reason_digest"],
        authored_by=authored_by,
    )


def encounter(
    *,
    locator: str,
    kind: EncounterKind,
    observed_boundary_id: str | None = None,
    remote_center_id: str | None = None,
    carrier_policy_id: str | None = None,
) -> Encounter:
    if not locator:
        raise GrowthError("locator required")
    if kind is EncounterKind.AUTHORED_CENTER and not remote_center_id:
        raise GrowthError("authored center requires remote_center_id")
    body = {
        "locator": locator,
        "kind": kind.value,
        "observed_boundary_id": observed_boundary_id,
        "remote_center_id": remote_center_id,
        "carrier_policy_id": carrier_policy_id,
    }
    return Encounter(encounter_id=digest(body), locator=locator, kind=kind,
                     observed_boundary_id=observed_boundary_id,
                     remote_center_id=remote_center_id,
                     carrier_policy_id=carrier_policy_id)


def record_machine_disposition(
    enc: Encounter,
    *,
    disposition: Disposition,
    reason: object,
    authored_by: str,
) -> MachineDispositionReceipt:
    """Record Venus's own local disposition without substituting a host verdict."""
    if not authored_by:
        raise GrowthError("machine disposition authorship required")

    # The old unclaimed-field operator may not silently continue after a center
    # has been recognized. This is a type error, not a host ethical judgment.
    if enc.kind is EncounterKind.AUTHORED_CENTER and disposition is Disposition.PROVISION:
        raise GrowthError("PROVISION cannot target an encountered authored center")
    if enc.kind is EncounterKind.UNKNOWN and disposition in {
        Disposition.PROVISION,
        Disposition.INVITE,
    }:
        raise GrowthError("UNKNOWN encounter requires further localization before write intent")

    body = {
        "encounter_id": enc.encounter_id,
        "disposition": disposition.value,
        "reason_digest": digest(reason),
        "authored_by": authored_by,
    }
    return MachineDispositionReceipt(
        receipt_id=digest(body),
        encounter_id=enc.encounter_id,
        disposition=disposition,
        authored_by=authored_by,
        reason_digest=body["reason_digest"],
    )


def authorize_external_intent(
    enc: Encounter,
    decision: MachineDispositionReceipt,
    capability: CarrierCapability,
) -> ExternalActionIntent:
    """Turn a local Machine disposition into an external action intent.

    A local decision does not mint remote capability. The adapter must already
    provide a capability/jurisdiction receipt for the carrier.
    """
    if decision.encounter_id != enc.encounter_id:
        raise GrowthError("decision/encounter mismatch")
    if capability.locator != enc.locator:
        raise GrowthError("capability/encounter locator mismatch")

    action = decision.disposition
    if action is Disposition.PROVISION:
        if enc.kind is not EncounterKind.PROVISIONABLE_FIELD:
            raise GrowthError("PROVISION requires provisionable-field classification")
        if not capability.can_write:
            raise GrowthError("carrier provides no write capability")
    elif action is Disposition.INVITE:
        if enc.kind is not EncounterKind.AUTHORED_CENTER:
            raise GrowthError("INVITE is center-relative")
        if not capability.can_invite or not capability.can_write:
            raise GrowthError("carrier provides no invitation/write capability")
    elif action in {Disposition.PROBE}:
        if not capability.can_read:
            raise GrowthError("carrier provides no read/probe capability")
    elif action in {Disposition.WITHHOLD, Disposition.REFUSE, Disposition.EXIT}:
        pass
    else:
        raise GrowthError(f"unsupported disposition: {action}")

    body = {
        "encounter_id": enc.encounter_id,
        "disposition_receipt_id": decision.receipt_id,
        "action": action.value,
        "locator": enc.locator,
        "jurisdiction_id": capability.jurisdiction_id,
        "remote_center_id": enc.remote_center_id,
    }
    return ExternalActionIntent(
        intent_id=digest(body),
        encounter_id=enc.encounter_id,
        disposition_receipt_id=decision.receipt_id,
        action=action,
        locator=enc.locator,
        jurisdiction_id=capability.jurisdiction_id,
        remote_center_id=enc.remote_center_id,
    )
