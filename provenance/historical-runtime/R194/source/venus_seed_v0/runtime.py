from __future__ import annotations
from pathlib import Path
from .canonical import digest
from .trajectory import TrajectoryJournal
from .model import *
from .dependency import DependencyGraph
from .governance import GovernancePolicy,authorize,verify
from .substrate import PolicyBridge,InMemoryAdapter,CapabilityRouterAdapter,EffectAdapter
from .lateral import compare

class OntogeneticVM:
    """IS0 semantic/ontogenetic VM prototype. It owns typed semantic state; effects cross PolicyBridge."""
    def __init__(self,journal_path=None,adapter=None):
        self.journal=TrajectoryJournal(journal_path); self.contexts={};self.relations={};self.residuals={};self.dependencies=DependencyGraph()
        self.policy=GovernancePolicy()
        if isinstance(adapter,CapabilityRouterAdapter): self.effect_router=adapter
        else: self.effect_router=CapabilityRouterAdapter(default=adapter or InMemoryAdapter())
        self.bridge=PolicyBridge(self.effect_router);self.commits=[]
        self.reconciliations=[]; self.project_state={}
        self._replay()
    def _replay(self):
        for e in self.journal.events:self._reduce(e["kind"],e["payload"])
    def _record(self,kind,payload,route=(),source=None):
        e=self.journal.append(kind,payload,route=route,source=source);self._reduce(kind,payload);return e
    def _reduce(self,kind,p):
        if kind=="CONTEXT": self.contexts[p["id"]]=p
        elif kind=="RELATION": self.relations[p["id"]]=p
        elif kind=="RESIDUAL": self.residuals[p["id"]]=p
        elif kind=="COMMIT": self.commits.append(p)
        elif kind=="RECONCILIATION": self.reconciliations.append(p)
        elif kind=="PROJECT_STATE": self.project_state=p

    _INTERFACE_RESERVED_KINDS=frozenset({
        "CONTEXT","RELATION","RESIDUAL","COMMIT","RECONCILIATION","PROJECT_STATE",
        "GOVERNANCE","AUTHORIZATION","EXECUTION","RETURN","VERIFICATION"
    })
    def install_effect_adapter(self,capability:str,adapter:EffectAdapter,*,effect_scope_prefix:str|None=None,replace:bool=False):
        return self.effect_router.register(capability,adapter,effect_scope_prefix=effect_scope_prefix,replace=replace)
    def record_interface_event(self,kind:str,payload:dict,*,route=("perspective-interface",),source=None):
        if kind in self._INTERFACE_RESERVED_KINDS: raise ValueError(f"interface event kind is reserved: {kind}")
        if not isinstance(payload,dict): raise TypeError("interface payload must be a dict")
        return self._record(kind,payload,route=route,source=source)

    def register_context(self,c:SemanticContext):
        cid=digest(c); self._record("CONTEXT",{"id":cid,"value":repr(c)},route=("semantic",)); return cid
    def register_relation(self,r:Relation):
        if r.context_id not in self.contexts: raise ValueError("unknown context")
        self._record("RELATION",{"id":r.id,"kind":r.kind,"terms":list(r.terms),"context_id":r.context_id},route=("relation",));return r.id
    def retain_residual(self,r:Residual): self._record("RESIDUAL",{"id":r.id,"reason":r.reason,"affected":list(r.affected_ids),"reopen_when":r.reopen_when},route=("residual",));return r.id
    def lateral(self,left,right,unresolved=()): return compare(left,right,unresolved=unresolved)
    def enact(self,proposal:Proposal,warrant:Warrant|None,*,capability_allowed=True,boundary_ok=True,return_source="world",return_interface="effect"):
        g=self.policy.decide(proposal,warrant,capability_allowed=capability_allowed,boundary_ok=boundary_ok)
        self._record("GOVERNANCE",{"id":g.id,"proposal":proposal.id,"disposition":g.disposition.value},route=("governance",))
        a=authorize(proposal,g);self._record("AUTHORIZATION",{"id":a.id,"proposal":proposal.id,"valid":a.valid},route=("authorization",))
        if not a.valid:return {"governance":g,"authorization":a,"receipt":None,"consequence":None,"verification":None,"committed":False}
        receipt=self.bridge.execute(proposal,a);self._record("EXECUTION",{"id":receipt.id,"proposal":proposal.id,"success":receipt.success,"capability":proposal.capability,"effect_scope":proposal.effect_scope},route=("vm-os-bridge","execution"),source="os")
        consequence=ReturnedConsequence(digest({"r":receipt.id,"v":receipt.result,"s":return_source}),receipt.id,return_interface,return_source,receipt.result)
        self._record("RETURN",{"id":consequence.id,"receipt":receipt.id,"source":return_source},route=("io-return",),source=return_source)
        v=verify(receipt,consequence,scope_ok=True);self._record("VERIFICATION",{"id":v.id,"receipt":receipt.id,"passed":v.passed},route=("verification",))
        committed=False
        if v.passed:
            self._record("COMMIT",{"proposal":proposal.id,"receipt":receipt.id,"verification":v.id},route=("writeback",));committed=True
        return {"governance":g,"authorization":a,"receipt":receipt,"consequence":consequence,"verification":v,"committed":committed}
