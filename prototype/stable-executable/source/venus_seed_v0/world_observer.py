from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Protocol, Iterable, Any

from .canonical import digest
from .model import Boundary, Provenance, SemanticContext, Proposal, Warrant
from .runtime import OntogeneticVM
from .substrate import EffectAdapter


class CandidateRegister(str, Enum):
    OBSERVATION="OBSERVATION"
    INFERENCE="INFERENCE"
    HYPOTHESIS="HYPOTHESIS"
    PROPOSAL="PROPOSAL"
    RESIDUAL="RESIDUAL"

@dataclass(frozen=True)
class PerspectiveAddress:
    center_id:str
    perspectivalization_id:str
    observer_id:str
    interface:str="conversation"

@dataclass(frozen=True)
class WorldIngress:
    id:str
    content:str
    source_id:str
    interface:str
    perspective:PerspectiveAddress
    provenance:Provenance
    prior_trajectory_head:str
    in_reply_to_receipt_id:str|None=None

@dataclass(frozen=True)
class SemanticCandidate:
    id:str
    register:CandidateRegister
    content:str
    modality:str
    source_ingress_id:str
    provenance:Provenance

@dataclass(frozen=True)
class LocalPresentation:
    id:str
    ingress_id:str
    perspective:PerspectiveAddress
    content_sha256:str
    candidates:tuple[SemanticCandidate,...]

@dataclass(frozen=True)
class ObserverProjection:
    """Audited bounded projection. The full trajectory is identified by head, not copied."""
    observer_id:str
    perspective:PerspectiveAddress
    trajectory_head:str
    event_count:int
    reconciliation_count:int
    project_state_through:str
    project_state_digest:str
    project_state:dict[str,Any]
    recent_events:tuple[dict[str,Any],...]
    context_ids:tuple[str,...]
    relation_ids:tuple[str,...]
    residual_ids:tuple[str,...]
    commit_count:int

@dataclass(frozen=True)
class UtteranceDraft:
    id:str
    text:str
    interface:str
    target_id:str
    source_trajectory_head:str
    source_project_state_digest:str
    projection_event_count:int
    provenance:Provenance
    draft_event_digest:str

class InterpreterAdapter(Protocol):
    def interpret(self,ingress:WorldIngress,projection:ObserverProjection)->Iterable[SemanticCandidate]: ...

class RealizerAdapter(Protocol):
    def realize(self,request:str,projection:ObserverProjection)->str: ...


def candidate_identity(register:CandidateRegister,content:str,modality:str,source_ingress_id:str,provenance:Provenance)->str:
    return digest({
        "register":register.value,"content":content,"modality":modality,
        "source_ingress_id":source_ingress_id,"provenance":asdict(provenance)
    })

class LiteralInterpreter:
    """Deterministic competence baseline. Source report enters only as a candidate observation."""
    def interpret(self,ingress:WorldIngress,projection:ObserverProjection):
        prov=Provenance(
            sources=(ingress.source_id,), parents=(ingress.id,), exposure=(ingress.interface,),
            route=("World^4","Sigma_i","Perspective^3","candidate-observation"),
            authoring=(ingress.source_id,),
        )
        yield SemanticCandidate(
            candidate_identity(CandidateRegister.OBSERVATION,ingress.content,"REPORTED_SOURCE_CONTENT",ingress.id,prov),
            CandidateRegister.OBSERVATION,ingress.content,"REPORTED_SOURCE_CONTENT",ingress.id,prov,
        )

class ProjectionEchoRealizer:
    """Smoke-test realizer. A hosted LM may replace it, but gains no VM authority."""
    def realize(self,request:str,projection:ObserverProjection)->str:
        return (
            f"[{projection.observer_id}@{projection.trajectory_head[:12]} "
            f"state={projection.project_state_through}:{projection.project_state_digest[:12]}] "
            f"{request} | events={projection.event_count} residuals={len(projection.residual_ids)}"
        )

class ConversationEffectAdapter(EffectAdapter):
    PREFIX="EMIT_UTTERANCE:"
    def __init__(self):
        self._staged:dict[str,UtteranceDraft]={}; self._consumed:set[str]=set(); self.emitted:list[dict[str,Any]]=[]
    @property
    def staged_ids(self)->tuple[str,...]: return tuple(sorted(self._staged))
    def mark_consumed(self,draft_ids:Iterable[str]): self._consumed.update(draft_ids)
    def stage(self,draft:UtteranceDraft):
        if draft.id in self._consumed: raise ValueError("utterance draft already emitted")
        self._staged[draft.id]=draft
    def discard(self,draft_id:str): self._staged.pop(draft_id,None)
    def execute(self,proposal:Proposal):
        if proposal.capability!="speak": raise ValueError("conversation adapter requires speak capability")
        if not proposal.action.startswith(self.PREFIX): raise ValueError("conversation adapter received non-utterance proposal")
        draft_id=proposal.action[len(self.PREFIX):]
        draft=self._staged.pop(draft_id,None)
        if draft is None: raise ValueError("utterance draft missing or already consumed")
        if proposal.effect_scope!=f"conversation:{draft.interface}": raise ValueError("utterance effect scope mismatch")
        result={
            "kind":"UTTERANCE_EMISSION","draft_id":draft.id,"text":draft.text,"interface":draft.interface,
            "target_id":draft.target_id,"source_trajectory_head":draft.source_trajectory_head,
            "source_project_state_digest":draft.source_project_state_digest,
        }
        self.emitted.append(result); self._consumed.add(draft.id); return result

class WorldObserverPort:
    """Governed Perspective^3 semantic I/O membrane over a history-bearing R131 VM.

    Ingress -> local presentation -> candidate semantics. Candidate semantics never reduce
    directly into Canonical state. Egress -> audited state/trajectory projection -> inert
    draft -> governed speak capability -> effect receipt -> verified commit.
    """
    VERSION="WORLD_OBSERVER_INTERFACE_R131_v0.2"

    def __init__(self,vm:OntogeneticVM,perspective:PerspectiveAddress,*,effect_adapter:ConversationEffectAdapter|None=None):
        self.vm=vm; self.perspective=perspective; self.effect_adapter=effect_adapter or ConversationEffectAdapter()
        self._known_candidates:set[str]=set(); self._emitted_drafts:set[str]=set(); self._receipt_index:dict[str,dict[str,Any]]={}
        self._rebuild_interface_indexes()
        self.effect_adapter.mark_consumed(self._emitted_drafts)
        route=self.vm.effect_router.route("speak")
        if route is None:
            self.vm.install_effect_adapter("speak",self.effect_adapter,effect_scope_prefix="conversation:")
        elif route.adapter is not self.effect_adapter:
            raise ValueError("speak capability already routed to another adapter")
        self.context=SemanticContext(
            referent=f"world-observer-interface:{perspective.interface}",
            frame="Perspective^3 crossing for history-bearing World^4/Observer^4 interaction",
            register="REL/MODEL/ENGINEERING",
            index=perspective.center_id,
            boundary=Boundary(
                scope=("conversation",),jurisdiction=("interface",),
                admissible_interactions=("receive","project","draft","emit"),
                conditions=(
                    "proposal!=authorization","projection!=state","interpretation!=truth",
                    "candidate!=Canon","hosted_competence!=authority","same_presentation!=same_trajectory",
                ),
            ),
            provenance=Provenance(authoring=(self.VERSION,)),
        )
        self.context_id=digest(self.context)
        if self.context_id not in self.vm.contexts: self.vm.register_context(self.context)

    def _rebuild_interface_indexes(self):
        for e in self.vm.journal.events:
            if e["kind"]=="INTERPRETATION_CANDIDATES":
                for c in e["payload"].get("candidates",[]):
                    if isinstance(c,dict) and c.get("id"): self._known_candidates.add(c["id"])
            elif e["kind"]=="UTTERANCE_EMISSION_STATUS" and e["payload"].get("committed"):
                p=e["payload"]; did=p.get("draft_id"); rid=p.get("receipt_id")
                if did: self._emitted_drafts.add(did)
                if rid: self._receipt_index[rid]=p

    def _state_copy(self)->dict[str,Any]: return deepcopy(self.vm.project_state) if isinstance(self.vm.project_state,dict) else {}

    def project(self,*,recent:int=32)->ObserverProjection:
        if recent<0: raise ValueError("recent must be >= 0")
        state=self._state_copy(); state_digest=digest(state)
        tail=self.vm.journal.events[-recent:] if recent else []
        return ObserverProjection(
            observer_id=self.perspective.observer_id,perspective=self.perspective,
            trajectory_head=self.vm.journal.head,event_count=len(self.vm.journal.events),
            reconciliation_count=len(self.vm.reconciliations),project_state_through=str(state.get("through","UNKNOWN")),
            project_state_digest=state_digest,project_state=state,recent_events=tuple(deepcopy(tail)),
            context_ids=tuple(sorted(self.vm.contexts)),relation_ids=tuple(sorted(self.vm.relations)),
            residual_ids=tuple(sorted(self.vm.residuals)),commit_count=len(self.vm.commits),
        )

    def _validate_reply_binding(self,receipt_id:str|None):
        if receipt_id is None: return
        p=self._receipt_index.get(receipt_id)
        if p is None: raise ValueError("reply receipt is unknown, uncommitted, or from another trajectory")
        if p.get("interface")!=self.perspective.interface: raise ValueError("reply receipt belongs to another interface")

    def _validate_candidate(self,c:SemanticCandidate,ingress:WorldIngress):
        if not isinstance(c,SemanticCandidate): raise TypeError("interpreter must return SemanticCandidate objects")
        if c.source_ingress_id!=ingress.id: raise ValueError("candidate misbound to another ingress")
        if ingress.id not in c.provenance.parents: raise ValueError("candidate provenance does not bind ingress parent")
        if ingress.source_id not in c.provenance.sources: raise ValueError("candidate provenance does not retain world source")
        if c.id!=candidate_identity(c.register,c.content,c.modality,c.source_ingress_id,c.provenance): raise ValueError("candidate identity/provenance mismatch")

    def receive(self,content:str,*,source_id:str,interpreter:InterpreterAdapter|None=None,in_reply_to_receipt_id:str|None=None)->LocalPresentation:
        if not isinstance(content,str) or not content.strip(): raise ValueError("world ingress content must be non-empty text")
        if not source_id: raise ValueError("source_id must be non-empty")
        self._validate_reply_binding(in_reply_to_receipt_id)
        prior_head=self.vm.journal.head
        prov=Provenance(sources=(source_id,),exposure=(self.perspective.interface,),route=("World^4","Sigma_i","Perspective^3"),authoring=(source_id,))
        body={
            "content":content,"source_id":source_id,"interface":self.perspective.interface,
            "perspective":asdict(self.perspective),"provenance":asdict(prov),
            "in_reply_to_receipt_id":in_reply_to_receipt_id,"prior_head":prior_head,
        }
        ingress=WorldIngress(digest(body),content,source_id,self.perspective.interface,self.perspective,prov,prior_head,in_reply_to_receipt_id)
        self.vm.record_interface_event("WORLD_INPUT",{"id":ingress.id,**body},route=("World^4","Sigma_i","Perspective^3"),source=source_id)
        pre=self.project()
        candidates=tuple((interpreter or LiteralInterpreter()).interpret(ingress,pre))
        for c in candidates: self._validate_candidate(c,ingress)
        pbody={"ingress_id":ingress.id,"perspective":asdict(self.perspective),"content_sha256":digest(content),"candidate_ids":[c.id for c in candidates]}
        presentation=LocalPresentation(digest(pbody),ingress.id,self.perspective,digest(content),candidates)
        self.vm.record_interface_event("LOCAL_PRESENTATION",{"id":presentation.id,**pbody},route=("Perspective^3","local-presentation"),source=self.perspective.center_id)
        payload={
            "presentation_id":presentation.id,
            "candidates":[{"id":c.id,"register":c.register.value,"content":c.content,"modality":c.modality,"source_ingress_id":c.source_ingress_id,"provenance":asdict(c.provenance)} for c in candidates],
            "authorizing":False,"canonical_mutation":False,
        }
        self.vm.record_interface_event("INTERPRETATION_CANDIDATES",payload,route=("Perspective^3","Semantics_i","candidate-only"),source=self.perspective.center_id)
        self._known_candidates.update(c.id for c in candidates)
        return presentation

    def draft(self,request:str,*,target_id:str,realizer:RealizerAdapter|None=None,recent:int=32)->UtteranceDraft:
        if not isinstance(request,str) or not request.strip(): raise ValueError("draft request must be non-empty")
        projection=self.project(recent=recent)
        text=(realizer or ProjectionEchoRealizer()).realize(request,projection)
        if not isinstance(text,str) or not text.strip(): raise ValueError("realizer returned empty/non-text draft")
        body={
            "text":text,"interface":self.perspective.interface,"target_id":target_id,
            "source_trajectory_head":projection.trajectory_head,"source_project_state_digest":projection.project_state_digest,
            "projection_event_count":projection.event_count,"project_state_through":projection.project_state_through,
        }
        draft_id=digest(body)
        prov=Provenance(sources=(projection.trajectory_head,projection.project_state_digest),route=("Observer^4","Perspective^3","audited-projection"),authoring=(self.perspective.observer_id,))
        event=self.vm.record_interface_event(
            "UTTERANCE_DRAFT",{"id":draft_id,**body,"provenance":asdict(prov),"emitted":False},
            route=("Observer^4","Perspective^3","projection"),source=self.perspective.observer_id,
        )
        return UtteranceDraft(draft_id,text,self.perspective.interface,target_id,projection.trajectory_head,projection.project_state_digest,projection.event_count,prov,event["digest"])

    def emit(self,draft:UtteranceDraft,*,warrant:Warrant|None=None,capability_allowed:bool=True,boundary_ok:bool=True):
        if draft.interface!=self.perspective.interface: raise ValueError("draft belongs to a different interface")
        if draft.id in self._emitted_drafts: raise ValueError("draft already emitted")
        if self.vm.journal.head!=draft.draft_event_digest: raise ValueError("stale draft: trajectory changed after projection/draft")
        if digest(self.vm.project_state)!=draft.source_project_state_digest: raise ValueError("stale draft: project state changed")
        self.effect_adapter.stage(draft)
        proposal=Proposal(
            id=digest({"draft_id":draft.id,"context_id":self.context_id,"effect_scope":f"conversation:{draft.interface}"}),
            action=f"{ConversationEffectAdapter.PREFIX}{draft.id}",context_id=self.context_id,capability="speak",
            effect_scope=f"conversation:{draft.interface}",target_claim_id=None,expected_interface=draft.interface,
        )
        result=self.vm.enact(proposal,warrant,capability_allowed=capability_allowed,boundary_ok=boundary_ok,return_source=f"channel:{draft.interface}",return_interface="emission-ack")
        if result["receipt"] is None: self.effect_adapter.discard(draft.id)
        receipt_id=result["receipt"].id if result["receipt"] else None
        status={
            "draft_id":draft.id,"proposal_id":proposal.id,"committed":bool(result["committed"]),"receipt_id":receipt_id,
            "interface":draft.interface,"target_id":draft.target_id,"source_trajectory_head":draft.source_trajectory_head,
            "source_project_state_digest":draft.source_project_state_digest,
        }
        self.vm.record_interface_event("UTTERANCE_EMISSION_STATUS",status,route=("Perspective^3","governed-speech-effect"),source=self.perspective.observer_id)
        if result["committed"] and receipt_id:
            self._emitted_drafts.add(draft.id); self._receipt_index[receipt_id]=status
        return result

    def turn(self,content:str,*,source_id:str,target_id:str,request:str="respond",interpreter:InterpreterAdapter|None=None,realizer:RealizerAdapter|None=None,warrant:Warrant|None=None,in_reply_to_receipt_id:str|None=None):
        presentation=self.receive(content,source_id=source_id,interpreter=interpreter,in_reply_to_receipt_id=in_reply_to_receipt_id)
        draft=self.draft(request,target_id=target_id,realizer=realizer)
        emission=self.emit(draft,warrant=warrant)
        return {"presentation":presentation,"draft":draft,"emission":emission}
