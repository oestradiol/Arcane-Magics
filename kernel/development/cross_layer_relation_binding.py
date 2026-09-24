from __future__ import annotations

"""Generic cross-layer relation binding substrate.

This module exposes only a typed constructor and return-binding boundary.
It does not choose endpoints, relation semantics, or acceptance. Those choices
belong to the learner and independently returned evidence.

Dependency order:
raw/source occurrence
-> learner-authored proposal
-> external return
-> admitted/rejected typed relation instance
"""

from dataclasses import dataclass
from typing import Iterable

from kernel.runtime.vmk2 import digest


class RelationBindingError(ValueError):
    pass


ALLOWED_SORTS = frozenset({
    "BYTE","TOKEN","SPAN","NODE","EDGE","EVENT","SOURCE","CHANNEL",
    "VALUE","TIME","STATE","ACTION","RETURN"
})


@dataclass(frozen=True)
class CarrierOccurrence:
    occurrence_id: str
    carrier_object_id: str
    source_id: str
    source_start: int
    source_end: int
    provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class RelationEndpoint:
    object_id: str
    object_sort: str


@dataclass(frozen=True)
class RelationBindingProposal:
    proposal_id: str
    occurrence_id: str
    left_endpoint: RelationEndpoint
    right_endpoint: RelationEndpoint
    relation_symbol: str
    discriminator_id: str
    author_id: str
    provenance_ids: tuple[str, ...]
    hidden_evaluation_exposed: bool = False
    promotion_authority: bool = False


@dataclass(frozen=True)
class ReturnedBindingJudgment:
    return_id: str
    proposal_id: str
    source_id: str
    accepted: bool
    provenance_ids: tuple[str, ...]
    external: bool = True


@dataclass(frozen=True)
class BindingOutcome:
    outcome_id: str
    proposal_id: str
    return_id: str
    disposition: str
    typed_relation_id: str | None
    hidden_evaluation_exposed: bool
    promotion_authority: bool


def make_occurrence(
    *,
    carrier_object_id: str,
    source_id: str,
    source_start: int,
    source_end: int,
    provenance_ids: Iterable[str],
) -> CarrierOccurrence:
    prov = tuple(provenance_ids)
    if not carrier_object_id or not source_id or not prov:
        raise RelationBindingError("occurrence requires carrier, source, provenance")
    if source_start < 0 or source_end < source_start:
        raise RelationBindingError("invalid source coordinates")
    body = {
        "carrier_object_id": carrier_object_id,
        "source_id": source_id,
        "source_start": source_start,
        "source_end": source_end,
        "provenance_ids": prov,
    }
    return CarrierOccurrence(occurrence_id=digest(body), **body)


def make_binding_proposal(
    occurrence: CarrierOccurrence,
    *,
    left_endpoint: RelationEndpoint,
    right_endpoint: RelationEndpoint,
    relation_symbol: str,
    discriminator_id: str,
    author_id: str,
    provenance_ids: Iterable[str] = (),
    hidden_evaluation_exposed: bool = False,
) -> RelationBindingProposal:
    if hidden_evaluation_exposed:
        raise RelationBindingError("hidden evaluation may not author proposal")
    if left_endpoint.object_sort not in ALLOWED_SORTS:
        raise RelationBindingError("invalid left endpoint sort")
    if right_endpoint.object_sort not in ALLOWED_SORTS:
        raise RelationBindingError("invalid right endpoint sort")
    if not left_endpoint.object_id or not right_endpoint.object_id:
        raise RelationBindingError("endpoint ids required")
    if not relation_symbol or not discriminator_id or not author_id:
        raise RelationBindingError("relation, discriminator, and author required")

    prov = tuple(dict.fromkeys((*occurrence.provenance_ids, *tuple(provenance_ids))))
    body = {
        "occurrence_id": occurrence.occurrence_id,
        "left_endpoint": left_endpoint.__dict__,
        "right_endpoint": right_endpoint.__dict__,
        "relation_symbol": relation_symbol,
        "discriminator_id": discriminator_id,
        "author_id": author_id,
        "provenance_ids": prov,
    }
    return RelationBindingProposal(
        proposal_id=digest(body),
        occurrence_id=occurrence.occurrence_id,
        left_endpoint=left_endpoint,
        right_endpoint=right_endpoint,
        relation_symbol=relation_symbol,
        discriminator_id=discriminator_id,
        author_id=author_id,
        provenance_ids=prov,
    )


def bind_return(
    proposal: RelationBindingProposal,
    judgment: ReturnedBindingJudgment,
) -> BindingOutcome:
    if not judgment.external:
        raise RelationBindingError("binding judgment must be externally returned")
    if judgment.proposal_id != proposal.proposal_id:
        raise RelationBindingError("return/proposal mismatch")
    if not judgment.return_id or not judgment.source_id or not judgment.provenance_ids:
        raise RelationBindingError("returned judgment requires identity and provenance")

    disposition = "ACCEPTED_RETURNED_BINDING" if judgment.accepted else "REJECTED_RETURNED_BINDING"
    typed_relation_id = None
    if judgment.accepted:
        typed_relation_id = digest({
            "proposal_id": proposal.proposal_id,
            "return_id": judgment.return_id,
            "left_endpoint": proposal.left_endpoint.__dict__,
            "right_endpoint": proposal.right_endpoint.__dict__,
            "relation_symbol": proposal.relation_symbol,
            "source_provenance": proposal.provenance_ids,
            "return_provenance": judgment.provenance_ids,
        })

    body = {
        "proposal_id": proposal.proposal_id,
        "return_id": judgment.return_id,
        "disposition": disposition,
        "typed_relation_id": typed_relation_id,
    }
    return BindingOutcome(
        outcome_id=digest(body),
        proposal_id=proposal.proposal_id,
        return_id=judgment.return_id,
        disposition=disposition,
        typed_relation_id=typed_relation_id,
        hidden_evaluation_exposed=False,
        promotion_authority=False,
    )
