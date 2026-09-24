from __future__ import annotations
from dataclasses import dataclass
from .canonical import digest
from .model import Proposal,Authorization,ExecutionReceipt

class EffectAdapter:
    def execute(self,proposal:Proposal): raise NotImplementedError

class InMemoryAdapter(EffectAdapter):
    def __init__(self): self.effects=[]
    def execute(self,proposal):
        result={"action":proposal.action,"ordinal":len(self.effects)}; self.effects.append(result); return result

@dataclass(frozen=True)
class CapabilityRoute:
    capability: str
    adapter: EffectAdapter
    effect_scope_prefix: str | None = None

class CapabilityRouterAdapter(EffectAdapter):
    """Capability-indexed effect router with an optional compatibility default.

    Routing is execution plumbing only. It never grants authority; PolicyBridge still
    requires a valid Authorization before this adapter can be reached.
    """
    def __init__(self,default:EffectAdapter|None=None):
        self.default=default
        self._routes:dict[str,CapabilityRoute]={}

    @property
    def capabilities(self)->tuple[str,...]: return tuple(sorted(self._routes))

    def register(self,capability:str,adapter:EffectAdapter,*,effect_scope_prefix:str|None=None,replace:bool=False):
        if not capability: raise ValueError("capability must be non-empty")
        if capability in self._routes and not replace: raise ValueError(f"capability already routed: {capability}")
        self._routes[capability]=CapabilityRoute(capability,adapter,effect_scope_prefix)
        return adapter

    def unregister(self,capability:str):
        return self._routes.pop(capability,None)

    def route(self,capability:str)->CapabilityRoute|None:
        return self._routes.get(capability)

    def execute(self,proposal:Proposal):
        route=self._routes.get(proposal.capability)
        if route is None:
            if self.default is None: raise PermissionError(f"no effect adapter for capability: {proposal.capability}")
            return self.default.execute(proposal)
        if route.effect_scope_prefix is not None and not proposal.effect_scope.startswith(route.effect_scope_prefix):
            raise PermissionError("effect scope outside capability route")
        return route.adapter.execute(proposal)

class PolicyBridge:
    """VM -> OS/effect boundary. Capability possession is not authority."""
    def __init__(self,adapter:EffectAdapter): self.adapter=adapter
    def execute(self,proposal:Proposal,auth:Authorization):
        if not auth.valid or auth.proposal_id!=proposal.id or auth.effect_scope!=proposal.effect_scope:
            raise PermissionError("effect denied: missing/mismatched authorization")
        result=self.adapter.execute(proposal)
        return ExecutionReceipt(digest({"p":proposal.id,"a":auth.id,"result":result}),proposal.id,auth.id,proposal.effect_scope,True,result)
