from __future__ import annotations

"""Governed semantic state-transition kernel for the WorldMirror engineering body.

Architectural role:
- this is the constitutional execution core, not the whole WorldMirror system;
- it owns typed evidence/return/state-transition mechanics and content roots;
- it does not choose developmental goals, browse the Web, or self-authorize policy;
- persistent hydration is handled by ``kernel.runtime.current``;
- long-lived semantic/network memory is handled by ``kernel.runtime.memory``;
- learner-owned developmental semantics live primarily under ``kernel/development``.

See ``docs/WORLDMIRROR_VM.md`` and ``kernel/runtime/README.md``.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
from copy import deepcopy
import json
import math
from typing import Any, Callable, Dict, FrozenSet, Iterable, Optional, Tuple


class VMK2Error(ValueError):
    pass


def _canonical_value(value: Any) -> Any:
    """Normalize authority-bearing values to a deterministic JSON subset."""
    if hasattr(value, '__dataclass_fields__'):
        return _canonical_value(asdict(value))
    if isinstance(value, Enum):
        return _canonical_value(value.value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise VMK2Error('non-finite number forbidden in canonical state')
        return value
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise VMK2Error('canonical mappings require string keys')
        return {k: _canonical_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(v) for v in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_canonical_value(v) for v in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(
                item, sort_keys=True, separators=(',', ':'), allow_nan=False
            ),
        )
    return value


def canonical(value: Any) -> bytes:
    normalized = _canonical_value(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(',', ':'),
        allow_nan=False,
    ).encode()


def digest(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()


class ReturnRole(str, Enum):
    ENCOUNTER = 'EncounterReturn'
    ACTION = 'ActionReturn'


class PolicyMode(str, Enum):
    WORD = 'WORD_RECONSTRUCT_ONLY'
    PORTAL = 'PORTAL_TRANSITION'


class ReceiptStatus(str, Enum):
    PASS = 'PASS'
    WITHHOLD = 'WITHHOLD'
    FAIL = 'FAIL'


@dataclass(frozen=True)
class EvidenceReceipt:
    evidence_id: str
    source_id: str
    assessor_id: str
    payload_digest: str
    exposure_epoch: int
    provenance_ids: Tuple[str, ...] = ()
    immutable: bool = True


@dataclass(frozen=True)
class ExecutionReceipt:
    receipt_id: str
    action_id: str
    target_id: str
    effect_digest: str
    epoch: int


@dataclass(frozen=True)
class IngressEvent:
    event_id: str
    evidence_id: str
    source_id: str
    target_id: str
    role: ReturnRole
    epoch: int
    nonce: str
    receipt_id: Optional[str] = None
    interface_id: str = 'default'
    jurisdiction_id: str = 'default'


@dataclass(frozen=True)
class VerifiedReturn:
    return_id: str
    ingress_event_id: str
    evidence_id: str
    source_id: str
    target_id: str
    role: ReturnRole
    epoch: int
    nonce: str
    receipt_id: Optional[str]
    jurisdiction_id: str


@dataclass(frozen=True)
class JurisdictionReceipt:
    receipt_id: str
    jurisdiction_id: str
    actor_id: str
    target_ids: FrozenSet[str]
    allowed_modes: FrozenSet[PolicyMode]
    valid_from_epoch: int
    valid_until_epoch: int
    status: ReceiptStatus = ReceiptStatus.PASS


@dataclass(frozen=True)
class LegitimacyReceipt:
    receipt_id: str
    actor_id: str
    target_id: str
    check_name: str
    status: ReceiptStatus
    valid_from_epoch: int
    valid_until_epoch: int
    withdrawn: bool = False


@dataclass(frozen=True)
class TurnLease:
    lease_id: str
    owner_id: str
    start_epoch: int
    end_epoch: int
    contamination_epoch: Optional[int] = None


@dataclass(frozen=True)
class TransitionPolicy:
    policy_id: str
    actor_id: str
    target_id: str
    mode: PolicyMode
    jurisdiction_receipt_id: str
    legitimacy_receipt_ids: Tuple[str, ...] = ()
    required_turn_owner: Optional[str] = None


@dataclass(frozen=True)
class StateObject:
    object_id: str
    value: Any
    root: str
    dependencies: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class StateTransitionReceipt:
    transition_id: str
    verified_return_id: str
    policy_id: str
    target_id: str
    before_root: str
    after_root: str
    dependency_closure: FrozenSet[str]
    sibling_roots_before: Dict[str, str]
    sibling_roots_after: Dict[str, str]
    epoch: int


@dataclass(frozen=True)
class ProjectionReceipt:
    projection_id: str
    future_family: FrozenSet[str]
    evidence_ids: Tuple[str, ...]
    payload_digest: str


@dataclass(frozen=True)
class ReopeningReceipt:
    reopening_id: str
    projection_id: str
    prior_future_family: FrozenSet[str]
    expanded_future_family: FrozenSet[str]
    separator_evidence_id: str
    separator_digest: str
    epoch: int


class Backend:
    def decode(self, payload: Any) -> Any:
        raise NotImplementedError

    def update(self, old_value: Any, decoded: Any) -> Any:
        raise NotImplementedError


class AdditiveBackend(Backend):
    def decode(self, payload: Any) -> Any:
        return payload

    def update(self, old_value: Any, decoded: Any) -> Any:
        return old_value + decoded


class JsonRoundtripAdditiveBackend(Backend):
    def decode(self, payload: Any) -> Any:
        return json.loads(json.dumps(payload))

    def update(self, old_value: Any, decoded: Any) -> Any:
        return old_value + decoded


class VMK2Reference:
    """Reference successor kernel for VMK-2 obligations.

    Deliberately generic and post-differentiation. It is a bounded engineering
    carrier, not a consciousness/AGI/ontology claim and not a promoted replacement
    for historical VMK-1 until integration/externality gates are separately met.
    """

    KERNEL_VERSION = 'VMK2_REFERENCE_v0.1'

    def __init__(self):
        self.evidence: Dict[str, EvidenceReceipt] = {}
        self.execution_receipts: Dict[str, ExecutionReceipt] = {}
        self.ingress: Dict[str, IngressEvent] = {}
        self.returns: Dict[str, VerifiedReturn] = {}
        self.jurisdictions: Dict[str, JurisdictionReceipt] = {}
        self.legitimacy: Dict[str, LegitimacyReceipt] = {}
        self.turn_leases: Dict[str, TurnLease] = {}
        self.policies: Dict[str, TransitionPolicy] = {}
        self.state: Dict[str, StateObject] = {}
        self.transitions: Dict[str, StateTransitionReceipt] = {}
        self.projections: Dict[str, ProjectionReceipt] = {}
        self.reopenings: Dict[str, ReopeningReceipt] = {}
        self.consumed_nonces: set[str] = set()
        self.exposure_log: list[tuple[int, str, str]] = []

    # D1/D2/D4: real evidence + canonical ingress + exposure order
    def register_evidence(
        self, *, source_id: str, assessor_id: str, payload: Any,
        exposure_epoch: int, provenance_ids: Iterable[str] = (), immutable: bool = True
    ) -> EvidenceReceipt:
        if not source_id or not assessor_id:
            raise VMK2Error('source and assessor required')
        body = {
            'source_id': source_id,
            'assessor_id': assessor_id,
            'payload_digest': digest(payload),
            'exposure_epoch': exposure_epoch,
            'provenance_ids': tuple(provenance_ids),
            'immutable': immutable,
        }
        eid = digest(body)
        rec = EvidenceReceipt(eid, source_id, assessor_id, body['payload_digest'], exposure_epoch, tuple(provenance_ids), immutable)
        self.evidence[eid] = rec
        self.exposure_log.append((exposure_epoch, 'EVIDENCE_REGISTERED', eid))
        return rec

    def register_execution_receipt(self, *, action_id: str, target_id: str, effect: Any, epoch: int) -> ExecutionReceipt:
        rid = digest({'action': action_id, 'target': target_id, 'effect': digest(effect), 'epoch': epoch})
        rec = ExecutionReceipt(rid, action_id, target_id, digest(effect), epoch)
        self.execution_receipts[rid] = rec
        return rec

    def ingest_return(
        self, *, evidence_id: str, source_id: str, target_id: str, role: ReturnRole,
        epoch: int, nonce: str, receipt_id: Optional[str] = None,
        interface_id: str = 'default', jurisdiction_id: str = 'default'
    ) -> VerifiedReturn:
        ev = self.evidence.get(evidence_id)
        if ev is None or not ev.immutable:
            raise VMK2Error('return requires resolvable immutable evidence')
        if ev.source_id != source_id:
            raise VMK2Error('source/evidence mismatch')
        if epoch < ev.exposure_epoch:
            raise VMK2Error('return predates evidence exposure')
        if role is ReturnRole.ACTION:
            if not receipt_id or receipt_id not in self.execution_receipts:
                raise VMK2Error('ActionReturn requires execution receipt')
            action_receipt = self.execution_receipts[receipt_id]
            if action_receipt.target_id != target_id:
                raise VMK2Error('action receipt target mismatch')
            if action_receipt.epoch > epoch:
                raise VMK2Error('ActionReturn predates execution receipt')
        event_body = {
            'evidence': evidence_id, 'source': source_id, 'target': target_id,
            'role': role.value, 'epoch': epoch, 'nonce': nonce, 'receipt': receipt_id,
            'interface': interface_id, 'jurisdiction': jurisdiction_id,
        }
        event_id = digest(event_body)
        self.ingress[event_id] = IngressEvent(event_id, evidence_id, source_id, target_id, role, epoch, nonce, receipt_id, interface_id, jurisdiction_id)
        ret_id = digest({'ingress': event_id, 'verified': True})
        ret = VerifiedReturn(ret_id, event_id, evidence_id, source_id, target_id, role, epoch, nonce, receipt_id, jurisdiction_id)
        self.returns[ret_id] = ret
        self.exposure_log.append((epoch, 'RETURN_INGESTED', ret_id))
        return ret

    # D5-D8: typed governance, jurisdiction, pacing/turn, legitimacy
    @staticmethod
    def _register_immutable(registry: Dict[str, Any], key: str, value: Any, kind: str) -> None:
        existing = registry.get(key)
        if existing is not None and existing != value:
            raise VMK2Error(f'{kind} id already bound to different content')
        registry[key] = value

    def register_jurisdiction(self, receipt: JurisdictionReceipt) -> None:
        self._register_immutable(
            self.jurisdictions, receipt.receipt_id, receipt, 'jurisdiction receipt'
        )

    def register_legitimacy(self, receipt: LegitimacyReceipt) -> None:
        self._register_immutable(
            self.legitimacy, receipt.receipt_id, receipt, 'legitimacy receipt'
        )

    def register_turn_lease(self, lease: TurnLease) -> None:
        self._register_immutable(self.turn_leases, lease.lease_id, lease, 'turn lease')

    def register_policy(self, policy: TransitionPolicy) -> None:
        self._register_immutable(
            self.policies, policy.policy_id, policy, 'transition policy'
        )

    def _verify_policy(self, policy_id: str, *, actor_id: str, target_id: str, epoch: int, lease_id: Optional[str]) -> TransitionPolicy:
        p = self.policies.get(policy_id)
        if p is None:
            raise VMK2Error('unknown transition policy')
        if p.actor_id != actor_id or p.target_id != target_id:
            raise VMK2Error('policy binding mismatch')
        j = self.jurisdictions.get(p.jurisdiction_receipt_id)
        if j is None or j.status is not ReceiptStatus.PASS:
            raise VMK2Error('jurisdiction unavailable')
        if j.actor_id != actor_id or target_id not in j.target_ids or p.mode not in j.allowed_modes:
            raise VMK2Error('jurisdiction denies transition')
        if not (j.valid_from_epoch <= epoch <= j.valid_until_epoch):
            raise VMK2Error('jurisdiction expired/not yet valid')
        for lid in p.legitimacy_receipt_ids:
            lr = self.legitimacy.get(lid)
            if lr is None or lr.status is not ReceiptStatus.PASS or lr.withdrawn:
                raise VMK2Error('legitimacy check failed/withdrawn')
            if lr.actor_id != actor_id or lr.target_id != target_id:
                raise VMK2Error('legitimacy binding mismatch')
            if not (lr.valid_from_epoch <= epoch <= lr.valid_until_epoch):
                raise VMK2Error('legitimacy receipt expired/not yet valid')
        if p.required_turn_owner:
            if not lease_id or lease_id not in self.turn_leases:
                raise VMK2Error('turn lease required')
            lease = self.turn_leases[lease_id]
            if lease.owner_id != p.required_turn_owner:
                raise VMK2Error('wrong turn owner')
            if not (lease.start_epoch <= epoch <= lease.end_epoch):
                raise VMK2Error('outside turn window')
            if lease.contamination_epoch is not None and lease.contamination_epoch <= epoch:
                raise VMK2Error('turn contaminated')
        return p

    # D9/D10 + word/portal separation
    def register_state(self, object_id: str, value: Any, dependencies: Iterable[str] = ()) -> StateObject:
        # State custody must not depend on a caller retaining and mutating an alias.
        owned_value = deepcopy(value)
        obj = StateObject(
            object_id,
            owned_value,
            digest({'id': object_id, 'value': owned_value}),
            frozenset(dependencies),
        )
        self.state[object_id] = obj
        return obj

    def _verify_state_integrity(self) -> None:
        """Fail closed if any stored value drifted beneath its recorded root."""
        for object_id, obj in self.state.items():
            actual = digest({'id': object_id, 'value': obj.value})
            if actual != obj.root:
                raise VMK2Error(f'state root drift detected: {object_id}')

    def dependency_closure(self, target_id: str) -> FrozenSet[str]:
        if target_id not in self.state:
            raise VMK2Error('unknown state target')
        seen: set[str] = set()
        stack = [target_id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            obj = self.state.get(cur)
            if obj:
                stack.extend(obj.dependencies)
        return frozenset(seen)

    def reconstruct(self, payload: Any, backend: Backend) -> Any:
        return backend.decode(payload)

    def transition(
        self, *, verified_return_id: str, actor_id: str, target_id: str,
        payload: Any, backend: Backend, policy_id: str, epoch: int,
        lease_id: Optional[str] = None
    ) -> Optional[StateTransitionReceipt]:
        ret = self.returns.get(verified_return_id)
        if ret is None:
            raise VMK2Error('unknown verified return')
        if ret.target_id != target_id:
            raise VMK2Error('return/target mismatch')
        if ret.nonce in self.consumed_nonces:
            raise VMK2Error('replayed return nonce')
        ev = self.evidence.get(ret.evidence_id)
        if ev is None or not ev.immutable:
            raise VMK2Error('verified return lost immutable evidence binding')
        if digest(payload) != ev.payload_digest:
            raise VMK2Error('transition payload is not bound to verified return evidence')
        decoded = backend.decode(payload)
        p = self._verify_policy(policy_id, actor_id=actor_id, target_id=target_id, epoch=epoch, lease_id=lease_id)
        # Word = reconstruct only. It never spends the nonce because no transition occurred.
        if p.mode is PolicyMode.WORD:
            return None
        obj = self.state.get(target_id)
        if obj is None:
            raise VMK2Error('unknown state target')
        self._verify_state_integrity()
        before = obj.root
        siblings_before = {k: v.root for k, v in self.state.items() if k != target_id}
        # Backends receive an owned copy. A backend may return a new value but may
        # not mutate the prior state's referent in place.
        new_value = backend.update(deepcopy(obj.value), decoded)
        new_obj = StateObject(target_id, new_value, digest({'id': target_id, 'value': new_value}), obj.dependencies)
        self.state[target_id] = new_obj
        self._verify_state_integrity()
        siblings_after = {k: v.root for k, v in self.state.items() if k != target_id}
        closure = self.dependency_closure(target_id)
        # No sibling outside affected target may mutate in this reference transition.
        if siblings_before != siblings_after:
            self.state[target_id] = obj
            raise VMK2Error('unaffected sibling mutation detected')
        tr_body = {
            'return': verified_return_id, 'policy': policy_id, 'target': target_id,
            'before': before, 'after': new_obj.root, 'closure': sorted(closure), 'epoch': epoch,
        }
        tid = digest(tr_body)
        tr = StateTransitionReceipt(tid, verified_return_id, policy_id, target_id, before, new_obj.root, closure, siblings_before, siblings_after, epoch)
        self.transitions[tid] = tr
        self.consumed_nonces.add(ret.nonce)
        return tr

    # D12/D13: evidence-backed compression and reopening
    def register_projection(self, *, future_family: Iterable[str], evidence_ids: Iterable[str], payload: Any) -> ProjectionReceipt:
        ff = frozenset(future_family)
        eids = tuple(evidence_ids)
        if not ff:
            raise VMK2Error('projection requires future family')
        for eid in eids:
            if eid not in self.evidence:
                raise VMK2Error('projection evidence handle unresolved')
        pid = digest({'F': sorted(ff), 'evidence': eids, 'payload': digest(payload)})
        pr = ProjectionReceipt(pid, ff, eids, digest(payload))
        self.projections[pid] = pr
        return pr

    def reopen_projection(self, *, projection_id: str, expanded_future_family: Iterable[str], separator_evidence_id: str, separator: Any, epoch: int) -> ReopeningReceipt:
        p = self.projections.get(projection_id)
        if p is None:
            raise VMK2Error('unknown projection')
        newf = frozenset(expanded_future_family)
        if not p.future_family < newf:
            raise VMK2Error('reopening requires strict future-family expansion')
        ev = self.evidence.get(separator_evidence_id)
        if ev is None or not ev.immutable:
            raise VMK2Error('reopening separator must bind immutable evidence')
        if ev.payload_digest != digest(separator):
            raise VMK2Error('separator/evidence mismatch')
        rid = digest({'projection': projection_id, 'F': sorted(newf), 'separator': separator_evidence_id, 'epoch': epoch})
        rr = ReopeningReceipt(rid, projection_id, p.future_family, newf, separator_evidence_id, digest(separator), epoch)
        self.reopenings[rid] = rr
        return rr


def consequence_equivalent_backends(old_value: float, payload: float, backends: Iterable[Backend]) -> bool:
    vals = []
    for b in backends:
        vals.append(b.update(old_value, b.decode(payload)))
    return all(abs(vals[0] - x) < 1e-12 for x in vals[1:])
