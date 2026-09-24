from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

class EpistemicStatus(str, Enum):
    LICENSE="LICENSE"; LICENSE_NOT="LICENSE_NOT"; UNDETERMINED="UNDETERMINED"
class GovernanceDisposition(str, Enum):
    ADMIT="ADMIT"; WITHHOLD="WITHHOLD"; REJECT_CUT="REJECT_CUT"
class RelationStatus(str, Enum):
    PRESERVES="PRESERVES"; FAILS="FAILS_TO_PRESERVE"; UNDETERMINED="RELATION_UNDETERMINED"

@dataclass(frozen=True)
class Boundary:
    scope: tuple[str,...]=()
    jurisdiction: tuple[str,...]=()
    admissible_interactions: tuple[str,...]=()
    conditions: tuple[str,...]=()

@dataclass(frozen=True)
class Provenance:
    sources: tuple[str,...]=()
    parents: tuple[str,...]=()
    exposure: tuple[str,...]=()
    route: tuple[str,...]=()
    authoring: tuple[str,...]=()

@dataclass(frozen=True)
class SemanticContext:
    referent: str
    frame: str
    register: str
    index: str
    boundary: Boundary=Boundary()
    provenance: Provenance=Provenance()

@dataclass(frozen=True)
class Relation:
    id: str
    kind: str
    terms: tuple[str,...]
    context_id: str
    provenance: Provenance=Provenance()
    status: RelationStatus=RelationStatus.UNDETERMINED
    future_family: tuple[str,...]=()

@dataclass(frozen=True)
class Residual:
    id: str
    reason: str
    affected_ids: tuple[str,...]
    discriminator: str|None=None
    reopen_when: str|None=None
    provenance: Provenance=Provenance()

@dataclass(frozen=True)
class Projection:
    id: str
    source_ids: tuple[str,...]
    future_family: tuple[str,...]
    signature: tuple[Any,...]
    lost_distinctions: tuple[str,...]=()
    reconstruction_handle: str|None=None

@dataclass(frozen=True)
class Warrant:
    claim_id: str
    status: EpistemicStatus
    evidence_ids: tuple[str,...]=()
    scope: str=""
    reason: str=""

@dataclass(frozen=True)
class Proposal:
    id: str
    action: str
    context_id: str
    capability: str
    effect_scope: str
    target_claim_id: str|None=None
    expected_interface: str|None=None

@dataclass(frozen=True)
class GovernanceRecord:
    id: str
    proposal_id: str
    disposition: GovernanceDisposition
    reason: str
    reopen_when: str|None=None

@dataclass(frozen=True)
class Authorization:
    id: str
    proposal_id: str
    governance_id: str
    capability: str
    effect_scope: str
    valid: bool

@dataclass(frozen=True)
class ExecutionReceipt:
    id: str
    proposal_id: str
    authorization_id: str
    effect_scope: str
    success: bool
    result: Any

@dataclass(frozen=True)
class ReturnedConsequence:
    id: str
    receipt_id: str
    interface: str
    source: str
    value: Any
    provenance: Provenance=Provenance()

@dataclass(frozen=True)
class Verification:
    id: str
    receipt_id: str
    consequence_id: str
    passed: bool
    checked_scope: str
    reasons: tuple[str,...]=()

@dataclass(frozen=True)
class LateralComparison:
    shared: tuple[str,...]
    left_only: tuple[str,...]
    right_only: tuple[str,...]
    unresolved: tuple[str,...]
    merged: bool=False
