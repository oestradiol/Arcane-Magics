from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import shutil, tempfile
from typing import Any

from .canonical import digest
from .current_seed_r154 import CurrentScientificSeed
from .kernel_vmk1 import (
    VenusKernelVMK1, GovernanceEnvelope, ReturnSourceKind, NonPreauthorshipWarrant,
    CompensationDisposition,
)
from .model import EpistemicStatus, Provenance, Proposal, Warrant
from .vmk2_reference import (
    VMK2Reference, ReturnRole, PolicyMode, ReceiptStatus,
    JurisdictionReceipt, LegitimacyReceipt, TurnLease, TransitionPolicy, Backend,
)
from .causal_obligations import CausalObligationRegistry

@dataclass(frozen=True)
class SuccessorConservationReceipt:
    schema:str
    parent_through:str
    parent_head:str
    successor_head:str
    parent_event_count:int
    successor_event_count:int
    project_state_digest:str
    obligation_count:int
    obligation_span:tuple[str,str]
    coverage_counts:dict[str,int]
    open_gate_count:int
    r154_conservation_gate_pass:bool

class CanonicalTransformationKernelR194:
    """Immediate Python prototype successor over the conserved R154 organism.

    This is the integration carrier, not a production/Linux/UEFI design.  It keeps
    the historical organism intact, overlays VMK-1 execution/return law, binds the
    VMK-2 hardening reference, and requires lossless R1..R194 causal custody.
    """
    VERSION='PYTHON_CANONICAL_TRANSFORMATION_KERNEL_R194_v0.1'

    def __init__(self, root:Path, vm:VenusKernelVMK1, vmk2:VMK2Reference, obligations:CausalObligationRegistry, parent_seed, successor_journal:Path):
        self.root=Path(root); self.vm=vm; self.vmk2=vmk2; self.obligations=obligations; self.parent_seed=parent_seed; self.successor_journal=Path(successor_journal)

    @classmethod
    def boot(cls, root:Path|str, *, successor_journal:Path|str|None=None):
        root=Path(root)
        parent=CurrentScientificSeed.boot_current(root)
        obligations=CausalObligationRegistry(root)
        obligations.assert_complete()
        parent_journal=root/'state'/'CURRENT_R154_N1_ANTI_ORIENTED_TRAJECTORY_v0.1.jsonl'
        if successor_journal is None:
            fd,name=tempfile.mkstemp(prefix='canonical_r194_',suffix='.jsonl')
            import os; os.close(fd)
            successor_journal=Path(name)
        else:
            successor_journal=Path(successor_journal)
        shutil.copyfile(parent_journal,successor_journal)
        successor=VenusKernelVMK1(successor_journal)
        # R179 was additive. Replaying old bytes through the stricter successor may
        # not change inherited state merely by loading it.
        if successor.journal.head != parent.vm.journal.head:
            raise RuntimeError('successor replay changed historical trajectory head')
        if digest(successor.project_state) != digest(parent.vm.project_state):
            raise RuntimeError('successor replay changed historical ProjectState')
        if len(successor.reconciliations) != len(parent.vm.reconciliations):
            raise RuntimeError('successor replay changed reconciliation count')
        return cls(root,successor,VMK2Reference(),obligations,parent,Path(successor_journal))

    def conservation_receipt(self)->SuccessorConservationReceipt:
        self.obligations.assert_complete()
        return SuccessorConservationReceipt(
            schema='Canonical.PythonPrototype.R194.ConservationReceipt.v1',
            parent_through=str(self.parent_seed.vm.project_state.get('through','UNKNOWN')),
            parent_head=self.parent_seed.vm.journal.head,
            successor_head=self.vm.journal.head,
            parent_event_count=len(self.parent_seed.vm.journal.events),
            successor_event_count=len(self.vm.journal.events),
            project_state_digest=digest(self.vm.project_state),
            obligation_count=len(self.obligations.entries),
            obligation_span=('R1','R194'),
            coverage_counts=self.obligations.counts(),
            open_gate_count=len(self.obligations.open_gates()),
            r154_conservation_gate_pass=bool(self.parent_seed.gate.get('current_vm_eligible',False)),
        )

    # ---- VMK-1: proposal -> governance -> authorization -> effect receipt only ----
    def enact(self, proposal:Proposal, warrant:Warrant|None, *, governance:GovernanceEnvelope|None=None):
        result=self.vm.enact(proposal,warrant,governance=governance)
        if result.get('consequence') is not None:
            raise RuntimeError('receipt/return collapse detected')
        return result

    # ---- VMK-2 + VMK-1 authoritative ingress bridge ----
    def ingest_world_return(
        self, *, value:Any, source_id:str, assessor_id:str, target_id:str,
        epoch:int, nonce:str, role:ReturnRole=ReturnRole.ENCOUNTER,
        receipt_id:str|None=None, interface:str='world', jurisdiction_id:str='default',
        future_family:tuple[str,...]=(), evidence_provenance:tuple[str,...]=(),
    ):
        ev=self.vmk2.register_evidence(
            source_id=source_id, assessor_id=assessor_id, payload=value,
            exposure_epoch=epoch, provenance_ids=evidence_provenance, immutable=True)
        if receipt_id is not None:
            # bind the actual VMK-1 execution receipt into VMK-2's causal role table
            p=self.vm.pending_executions.get(receipt_id)
            if p is None: raise ValueError('unknown VMK-1 execution receipt')
            self.vmk2.register_execution_receipt(
                action_id=p.get('proposal_id') or p.get('proposal',{}).get('id','unknown'),
                target_id=target_id,effect=p.get('result'),epoch=max(0,epoch-1))
            # VMK2 generated receipt IDs are content-derived and need not equal VMK1 IDs;
            # role binding is independently checked by VMK-1 below. For ActionReturn use
            # a locally registered receipt matching the target.
            v2rid=next(reversed(self.vmk2.execution_receipts))
        else:
            v2rid=None
        v2=self.vmk2.ingest_return(
            evidence_id=ev.evidence_id,source_id=source_id,target_id=target_id,role=role,
            epoch=epoch,nonce=nonce,receipt_id=v2rid,interface_id=interface,jurisdiction_id=jurisdiction_id)
        prov=Provenance(
            sources=(ev.evidence_id,*evidence_provenance),
            parents=((receipt_id,) if receipt_id else ()),
            exposure=(f'epoch:{epoch}',interface),
            route=('VMK2_TRUSTED_INGRESS','VMK1_EXTERNAL_RETURN'),
            authoring=(source_id,),
        )
        npr=NonPreauthorshipWarrant(assessor_id,EpistemicStatus.LICENSE,(ev.evidence_id,),reason='VMK2 immutable ingress receipt')
        v1=self.vm.register_external_return(
            value=value,source_id=source_id,
            source_kind=ReturnSourceKind.WORLD if role is ReturnRole.ENCOUNTER else ReturnSourceKind.INDEPENDENT_EVALUATOR,
            interface=interface,provenance=prov,npr_warrant=npr,receipt_id=receipt_id,
            jurisdiction=jurisdiction_id,future_family=future_family)
        verification=self.vm.verify_external_return(v1.id)
        if not verification.passed:
            raise RuntimeError(f'VMK-1 rejected VMK-2 ingress: {verification.reasons}')
        return {'evidence':ev,'vmk2_return':v2,'vmk1_return':v1,'verification':verification}

    # ---- VMK-2 state/policy surface, used by successor/self-maintenance experiments ----
    def register_mutable_state(self, object_id:str, value:Any, dependencies=()):
        return self.vmk2.register_state(object_id,value,dependencies)

    def register_transition_policy(
        self, *, policy_id:str, actor_id:str, target_id:str, mode:PolicyMode,
        epoch_from:int=0, epoch_to:int=10**9, legitimacy_checks:tuple[str,...]=('self-maintenance',),
        required_turn_owner:str|None=None,
    ):
        jid=f'jur:{policy_id}'
        self.vmk2.register_jurisdiction(JurisdictionReceipt(jid,jid,actor_id,frozenset({target_id}),frozenset({mode}),epoch_from,epoch_to,ReceiptStatus.PASS))
        lids=[]
        for check in legitimacy_checks:
            lid=f'leg:{policy_id}:{check}'
            self.vmk2.register_legitimacy(LegitimacyReceipt(lid,actor_id,target_id,check,ReceiptStatus.PASS,epoch_from,epoch_to,False)); lids.append(lid)
        if required_turn_owner:
            lease_id=f'lease:{policy_id}'
            self.vmk2.register_turn_lease(TurnLease(lease_id,required_turn_owner,epoch_from,epoch_to,None))
        else: lease_id=None
        self.vmk2.register_policy(TransitionPolicy(policy_id,actor_id,target_id,mode,jid,tuple(lids),required_turn_owner))
        return policy_id,lease_id

    def transition(self, *, verified_return_id:str, actor_id:str, target_id:str, payload:Any, backend:Backend, policy_id:str, epoch:int, lease_id:str|None=None):
        return self.vmk2.transition(verified_return_id=verified_return_id,actor_id=actor_id,target_id=target_id,payload=payload,backend=backend,policy_id=policy_id,epoch=epoch,lease_id=lease_id)

    def canonical_curriculum(self):
        """One-teach packet. It contains burdens, not privileged project vocabulary.

        The later teaching experiment decides what the learner reconstructs; this
        method merely exposes the lossless causal curriculum with scope/status.
        """
        self.obligations.assert_complete()
        return tuple({
            'id':o.r_id,'status':o.status,'burden':o.burden,
            'implementation_mode':o.implementation_mode,'source_class':o.source_class,
        } for o in sorted(self.obligations.entries.values(),key=lambda x:int(x.r_id[1:])))
