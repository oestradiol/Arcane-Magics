from __future__ import annotations
from dataclasses import dataclass
from . import m7_improver_v10 as m7

@dataclass(frozen=True)
class RSIScope:
    status:str='CLOSED / SUPPORTED-LIMITED / MATURE-REDUCED [R127]'
    open_ended:bool=False
    claim:str='bounded governed revision-selection state can improve later independently validated revision selection at frozen scope'
    reduction_fence:str='DIRECT_PATCHED exact state reproduces treatment; exact enumerator remains ceiling; mechanism novelty/necessity not established'

class RecoveredBoundedM7:
    """Exact bounded M7 improver logic recovered as a successor capability.

    It intentionally carries the R127 reduction fence. It is not an open-ended
    self-authorizing RSI primitive and cannot edit Canonical authority.
    """
    scope=RSIScope()
    @staticmethod
    def fit(rows): return m7.fit_policy(rows)
    @staticmethod
    def govern(proposal,public,truth,target_world_id): return m7.govern(proposal,public,truth,target_world_id)
    @staticmethod
    def choose(pool,state=None): return m7.choose_public(pool,state)
    @staticmethod
    def evaluate(public,truth,state=None): return m7.evaluate_returned(public,truth,state)
    @staticmethod
    def shuffled(rows,world_id): return m7.shuffled(rows,world_id)
