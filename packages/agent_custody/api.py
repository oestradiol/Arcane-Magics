from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from kernel.runtime.vmk2 import (
    EvidenceReceipt,
    JurisdictionReceipt,
    PolicyMode,
    ReceiptStatus,
    ReturnRole,
    TransitionPolicy,
    VMK2Reference,
)


class AuthorityLevel(str, Enum):
    INTERNALLY_REGISTERED = 'INTERNALLY_REGISTERED'
    EXTERNALLY_AUTHENTICATED = 'EXTERNALLY_AUTHENTICATED'


@dataclass(frozen=True)
class ClaimBinding:
    claim_id: str
    returned_evidence_ids: frozenset[str]
    selected_evidence_ids: frozenset[str]
    required_evidence_ids: frozenset[str]

    def __post_init__(self) -> None:
        if not self.selected_evidence_ids <= self.returned_evidence_ids:
            raise ValueError('selected evidence must be a subset of returned evidence')

    @property
    def supported(self) -> bool:
        return self.required_evidence_ids <= self.selected_evidence_ids

    @property
    def missing_required_evidence(self) -> frozenset[str]:
        return self.required_evidence_ids - self.selected_evidence_ids


class AgentCustody:
    """Ordinary-language facade over the VMK2 reference custody kernel.

    This facade intentionally does not upgrade internally registered source/authority
    identifiers into cryptographically authenticated identities.
    """

    def __init__(self, vm: VMK2Reference | None = None):
        self.vm = vm or VMK2Reference()
        self.claims: dict[str, ClaimBinding] = {}

    @property
    def authority_level(self) -> AuthorityLevel:
        return AuthorityLevel.INTERNALLY_REGISTERED

    def record_evidence(self, *, source_id: str, assessor_id: str, payload, epoch: int, provenance_ids: Iterable[str] = ()) -> EvidenceReceipt:
        return self.vm.register_evidence(
            source_id=source_id, assessor_id=assessor_id, payload=payload,
            exposure_epoch=epoch, provenance_ids=provenance_ids,
        )

    def record_world_return(self, *, evidence_id: str, source_id: str, target_id: str, epoch: int, nonce: str):
        return self.vm.ingest_return(
            evidence_id=evidence_id, source_id=source_id, target_id=target_id,
            role=ReturnRole.ENCOUNTER, epoch=epoch, nonce=nonce,
        )

    def register_internal_authorization(
        self, *, receipt_id: str, jurisdiction_id: str, actor_id: str,
        target_ids: Iterable[str], allowed_modes: Iterable[PolicyMode],
        valid_from_epoch: int, valid_until_epoch: int,
    ) -> JurisdictionReceipt:
        receipt = JurisdictionReceipt(
            receipt_id=receipt_id, jurisdiction_id=jurisdiction_id, actor_id=actor_id,
            target_ids=frozenset(target_ids), allowed_modes=frozenset(allowed_modes),
            valid_from_epoch=valid_from_epoch, valid_until_epoch=valid_until_epoch,
            status=ReceiptStatus.PASS,
        )
        self.vm.register_jurisdiction(receipt)
        return receipt

    def register_transition_policy(self, *, policy_id: str, actor_id: str, target_id: str, mode: PolicyMode, jurisdiction_receipt_id: str) -> TransitionPolicy:
        policy = TransitionPolicy(
            policy_id=policy_id, actor_id=actor_id, target_id=target_id,
            mode=mode, jurisdiction_receipt_id=jurisdiction_receipt_id,
        )
        self.vm.register_policy(policy)
        return policy

    def bind_claim(
        self, *, claim_id: str, returned_evidence_ids: Iterable[str],
        selected_evidence_ids: Iterable[str], required_evidence_ids: Iterable[str],
    ) -> ClaimBinding:
        binding = ClaimBinding(
            claim_id=claim_id,
            returned_evidence_ids=frozenset(returned_evidence_ids),
            selected_evidence_ids=frozenset(selected_evidence_ids),
            required_evidence_ids=frozenset(required_evidence_ids),
        )
        for evidence_id in binding.returned_evidence_ids:
            if evidence_id not in self.vm.evidence:
                raise ValueError(f'unknown returned evidence id: {evidence_id}')
        self.claims[claim_id] = binding
        return binding

    def require_supported_claim(self, claim_id: str) -> ClaimBinding:
        binding = self.claims.get(claim_id)
        if binding is None:
            raise ValueError('unknown claim')
        if not binding.supported:
            missing = ','.join(sorted(binding.missing_required_evidence))
            raise ValueError(f'claim is not supported by selected evidence; missing={missing}')
        return binding
