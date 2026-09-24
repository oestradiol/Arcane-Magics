from __future__ import annotations
from .canonical import digest
from .model import *

class GovernancePolicy:
    def decide(self,proposal:Proposal,warrant:Warrant|None,*,capability_allowed:bool,boundary_ok:bool=True):
        if not boundary_ok:
            return GovernanceRecord(digest({"p":proposal.id,"d":"WITHHOLD","r":"boundary"}),proposal.id,GovernanceDisposition.WITHHOLD,"boundary mismatch","matching boundary")
        if not capability_allowed:
            return GovernanceRecord(digest({"p":proposal.id,"d":"REJECT","r":"capability"}),proposal.id,GovernanceDisposition.REJECT_CUT,"capability unavailable")
        if warrant and warrant.status is EpistemicStatus.UNDETERMINED:
            return GovernanceRecord(digest({"p":proposal.id,"d":"WITHHOLD","r":"warrant"}),proposal.id,GovernanceDisposition.WITHHOLD,"warrant undetermined","new evidence")
        return GovernanceRecord(digest({"p":proposal.id,"d":"ADMIT"}),proposal.id,GovernanceDisposition.ADMIT,"admitted")

def authorize(proposal:Proposal,g:GovernanceRecord):
    ok=g.disposition is GovernanceDisposition.ADMIT and g.proposal_id==proposal.id
    return Authorization(digest({"p":proposal.id,"g":g.id,"ok":ok}),proposal.id,g.id,proposal.capability,proposal.effect_scope,ok)

def verify(receipt:ExecutionReceipt,consequence:ReturnedConsequence,*,scope_ok=True):
    ok=receipt.success and consequence.receipt_id==receipt.id and scope_ok
    return Verification(digest({"r":receipt.id,"c":consequence.id,"ok":ok}),receipt.id,consequence.id,ok,receipt.effect_scope,() if ok else ("lineage-or-scope-failure",))
