from __future__ import annotations

"""State-backed generic residual search.

The historical R194 grammar remains provenance/reference. Runtime behavior is
defined by a small state object plus this generic Boolean-expression interpreter.
No issue labels or target semantics enter this module.
"""

from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .recursive_proposal import ResidualObservation, SearchOutcome, RecursiveProposalError

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/"kernel/development/GENERIC_RESIDUAL_SEARCH_INTERNAL_STATE.json"
VERSION="INTERNALIZED_GENERIC_RESIDUAL_SEARCH_v0.1"


@dataclass(frozen=True)
class Expr:
    op:str
    args:tuple["Expr",...]=()
    index:int|None=None

    @staticmethod
    def atom(index:int)->"Expr":
        return Expr("ATOM",(),index)

    def eval(self,row:tuple[int,...])->int:
        if self.op=="ATOM":
            if self.index is None:
                raise RecursiveProposalError("ATOM missing index")
            return int(bool(row[self.index]))
        if len(self.args)!=2:
            raise RecursiveProposalError(f"{self.op} expects two arguments")
        a=self.args[0].eval(row)
        b=self.args[1].eval(row)
        if self.op=="AND": return a & b
        if self.op=="OR": return a | b
        if self.op=="XOR": return a ^ b
        raise RecursiveProposalError(f"unsupported state op {self.op}")

    @property
    def nodes(self)->int:
        return 1+sum(x.nodes for x in self.args)

    @property
    def depth(self)->int:
        return 0 if not self.args else 1+max(x.depth for x in self.args)

    def canonical(self)->str:
        if self.op=="ATOM":
            return f"x{self.index}"
        parts=sorted(x.canonical() for x in self.args)
        return f"{self.op}({parts[0]},{parts[1]})"


def load_state(path:Path=STATE)->dict:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema")!="Venus.InternalizedResidualSearchState.v0.1":
        raise RecursiveProposalError("unsupported internalized search state")
    if not obj.get("meta_ops"):
        raise RecursiveProposalError("internalized search state lacks meta_ops")
    return obj


def _domain(width:int)->tuple[tuple[int,...],...]:
    return tuple(tuple(int(v) for v in row) for row in product((0,1),repeat=width))


def _dedupe(exprs:Iterable[Expr],rows:Sequence[tuple[int,...]])->tuple[Expr,...]:
    best={}
    for e in exprs:
        sig=tuple(e.eval(r) for r in rows)
        old=best.get(sig)
        if old is None or (e.nodes,e.depth,e.canonical())<(old.nodes,old.depth,old.canonical()):
            best[sig]=e
    return tuple(sorted(best.values(),key=lambda e:(e.nodes,e.depth,e.canonical())))


def _pool(width:int,state:Mapping)->tuple[tuple[int,...],tuple[Expr,...]]:
    domain=_domain(width)
    atoms=tuple(Expr.atom(i) for i in range(width))
    raw=list(atoms)
    for left in atoms:
        for right in atoms:
            for op in state["meta_ops"]:
                raw.append(Expr(str(op),(left,right)))
                raw.append(Expr(str(op),(right,left)))
    by_syntax={e.canonical():e for e in raw}
    return domain,_dedupe(by_syntax.values(),domain)


def _normalize(observations:Iterable[ResidualObservation])->tuple[ResidualObservation,...]:
    rows=tuple(observations)
    if not rows:
        raise RecursiveProposalError("STOP_NO_RETURNED_RESIDUAL_OBSERVATIONS")
    width=len(rows[0].features)
    if width<2:
        raise RecursiveProposalError("generic search requires at least two feature coordinates")
    for row in rows:
        if len(row.features)!=width: raise RecursiveProposalError("feature-width mismatch")
        if any(x not in (0,1) for x in row.features): raise RecursiveProposalError("features must be binary")
        if row.desired_action not in (0,1): raise RecursiveProposalError("desired_action must be binary")
        if not row.provenance_id: raise RecursiveProposalError("returned observation requires provenance")
    return rows


def search_internalized(
    observations:Iterable[ResidualObservation],
    *,
    hidden_evaluation_exposed:bool=False,
    state_path:Path=STATE,
)->SearchOutcome:
    if hidden_evaluation_exposed:
        raise RecursiveProposalError("hidden evaluation may not enter proposal search")
    obs=_normalize(observations)
    state=load_state(state_path)
    width=len(obs[0].features)
    domain,pool=_pool(width,state)
    exact=tuple(
        e for e in pool
        if all(e.eval(r.features)==r.desired_action for r in obs)
    )
    exact=tuple(sorted(exact,key=lambda e:(e.nodes,e.depth,e.canonical())))
    if not exact:
        return SearchOutcome(
            schema="Venus.GenericResidualSearchOutcome.v0.2",
            version=VERSION,
            status="WITHHOLD_NO_EXPRESSIBLE_CANDIDATE",
            donor_git_blob_sha=state["source_donor"]["git_blob_sha"],
            observation_count=len(obs),feature_count=width,
            exact_semantic_candidates=(),minimal_complexity=None,
            next_discriminator=None,hidden_evaluation_exposed=False,promotion_authority=False,
        )
    minimum=min((e.nodes,e.depth) for e in exact)
    if len(exact)==1:
        return SearchOutcome(
            schema="Venus.GenericResidualSearchOutcome.v0.2",
            version=VERSION,status="UNIQUE_BOUNDED_PROGRAM_CANDIDATE",
            donor_git_blob_sha=state["source_donor"]["git_blob_sha"],
            observation_count=len(obs),feature_count=width,
            exact_semantic_candidates=(exact[0].canonical(),),minimal_complexity=minimum,
            next_discriminator=None,hidden_evaluation_exposed=False,promotion_authority=False,
        )
    observed={x.features for x in obs}
    best=None
    for row in domain:
        if row in observed: continue
        outputs=tuple(e.eval(row) for e in exact)
        z=outputs.count(0); o=outputs.count(1)
        if z==0 or o==0: continue
        score=(max(z,o),-min(z,o),tuple(row))
        if best is None or score<best[0]:
            best=(score,tuple(int(x) for x in row))
    discriminator=None if best is None else best[1]
    return SearchOutcome(
        schema="Venus.GenericResidualSearchOutcome.v0.2",
        version=VERSION,
        status=("WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR"
                if discriminator is not None
                else "WITHHOLD_OBSERVATIONALLY_EQUIVALENT_CANDIDATES"),
        donor_git_blob_sha=state["source_donor"]["git_blob_sha"],
        observation_count=len(obs),feature_count=width,
        exact_semantic_candidates=tuple(e.canonical() for e in exact),
        minimal_complexity=minimum,next_discriminator=discriminator,
        hidden_evaluation_exposed=False,promotion_authority=False,
    )
