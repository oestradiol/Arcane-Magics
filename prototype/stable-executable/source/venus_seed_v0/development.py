from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence
from .canonical import digest


@dataclass(frozen=True)
class ProbeRequest:
    id: str
    x: Any
    revision: int
    allowed: tuple[Any, ...]


@dataclass(frozen=True)
class ReturnedProbe:
    request_id: str
    x: Any
    revision: int
    value: Any


class CandidateBoundary:
    """A scoped alternative boundary.

    Consensus is licensed only when at least one live candidate remains and all live
    candidates agree. A request is bound to the current revision and can be consumed once.
    Returned evidence, not the request itself, advances revision.
    """
    def __init__(self, candidate_ids: Iterable[Any], evaluator: Callable[[Any, Any], Any]):
        self.candidate_ids=list(candidate_ids)
        self.evaluator=evaluator
        self.revision=0
        self._pending: dict[str, ProbeRequest] = {}
        self._used_x: set[Any] = set()
        self.history: list[ReturnedProbe] = []

    def forecast(self, x: Any):
        if not self.candidate_ids:
            return None
        values={self.evaluator(cid,x) for cid in self.candidate_ids}
        return next(iter(values)) if len(values)==1 else None

    def request(self, x: Any, allowed: Sequence[Any]) -> ProbeRequest:
        allowed_tuple=tuple(allowed)
        if x not in allowed_tuple:
            raise ValueError('probe outside declared interface')
        if x in self._used_x or any(r.x==x for r in self._pending.values()):
            raise ValueError('duplicate probe')
        rid=digest({'x':x,'revision':self.revision,'allowed':allowed_tuple,'serial':len(self.history)+len(self._pending)})
        req=ProbeRequest(rid,x,self.revision,allowed_tuple)
        self._pending[rid]=req
        return req

    def returned(self, request: ProbeRequest, value: Any) -> ReturnedProbe:
        current=self._pending.get(request.id)
        if current != request:
            raise ValueError('unmatched or already-consumed request')
        if request.revision != self.revision:
            raise ValueError('stale request revision')
        del self._pending[request.id]
        self._used_x.add(request.x)
        self.candidate_ids=[cid for cid in self.candidate_ids if self.evaluator(cid,request.x)==value]
        rec=ReturnedProbe(request.id,request.x,request.revision,value)
        self.history.append(rec)
        self.revision += 1
        return rec

    def choose_disagreement(self, allowed: Sequence[Any]):
        options=[x for x in allowed if x not in self._used_x and not any(r.x==x for r in self._pending.values())]
        if not options:
            return None
        if not self.candidate_ids:
            return options[0]
        if len(self.candidate_ids)==1:
            return options[0]
        def score(x):
            values=[self.evaluator(cid,x) for cid in self.candidate_ids]
            counts={v:values.count(v) for v in set(values)}
            return (max(counts.values()),repr(x))
        return min(options,key=score)


@dataclass
class RetainedOrdering:
    """Search priority is retained separately from epistemic warrant."""
    priorities: list[Any] = field(default_factory=list)

    def ordered(self, candidates: Iterable[Any]) -> list[Any]:
        c=list(candidates); rank={v:i for i,v in enumerate(self.priorities)}
        return sorted(c,key=lambda v:(rank.get(v,len(rank)),repr(v)))

    def retain_after_verified(self, candidate: Any, *, verified: bool):
        if not verified:
            return False
        if candidate not in self.priorities:
            self.priorities.append(candidate)
        return True


@dataclass(frozen=True)
class LayoutResult:
    semantic_state: Any
    history_digest: str
    cost: float


def compare_layouts(results: Mapping[str,LayoutResult], *, favored: str, baseline: str, minimum_margin: float=0.0):
    a=results[favored]; b=results[baseline]
    if a.semantic_state != b.semantic_state or a.history_digest != b.history_digest:
        raise ValueError('layout comparison is not capacity/semantics matched')
    margin=0.0 if b.cost==0 else (b.cost-a.cost)/b.cost
    return {'lossless':True,'margin':margin,'passes_cost_gate':margin>=minimum_margin}


@dataclass(frozen=True)
class InformationBoundary:
    accessible_points: tuple[Any,...]

    def observationally_equivalent(self, left: Callable[[Any],Any], right: Callable[[Any],Any]) -> bool:
        return all(left(x)==right(x) for x in self.accessible_points)

    def lawful_disposition(self, left: Callable[[Any],Any], right: Callable[[Any],Any]) -> str:
        return 'WITHHOLD' if self.observationally_equivalent(left,right) else 'DISTINGUISHABLE'


def model_independent_challenge(allowed: Sequence[Any], used: Iterable[Any]=()):
    used=set(used)
    for x in allowed:
        if x not in used:
            return x
    return None

@dataclass(frozen=True)
class CoordinateWitness:
    left: Any
    right: Any
    old_basis: tuple[Any,...]
    future: Any
    left_value: Any
    right_value: Any


class ContinuationBasis:
    """A basis may grow only from a returned witness that the current quotient collides."""
    def __init__(self, basis=()):
        self.basis=list(basis) or [()]
        self.witnesses: list[CoordinateWitness] = []

    def extend_from_witness(self, left, right, future, observe: Callable[[Any],Any]):
        old=tuple(self.basis)
        # left/right must be indistinguishable under every existing continuation coordinate.
        for f in old:
            if observe(left+f) != observe(right+f):
                raise ValueError('pair already distinguished by current basis')
        lv,rv=observe(left+future),observe(right+future)
        if lv == rv:
            raise ValueError('proposed future is not distinguishing')
        if future in self.basis:
            raise ValueError('coordinate already present')
        w=CoordinateWitness(left,right,old,future,lv,rv)
        self.basis.append(future); self.witnesses.append(w)
        return w

    def record(self):
        return {'basis':self.basis,'witnesses':[w.__dict__ for w in self.witnesses]}

    @classmethod
    def from_record(cls, record):
        x=cls(record['basis']); x.witnesses=[CoordinateWitness(**w) for w in record.get('witnesses',[])]; return x


@dataclass(frozen=True)
class CausalEffectEvidence:
    treatment: Any
    control: Any
    deletion: Any
    effect_present: bool
    deletion_restores_control: bool


def causal_effect_evidence(treatment, control, deletion) -> CausalEffectEvidence:
    present=treatment != control
    restored=deletion == control
    return CausalEffectEvidence(treatment,control,deletion,present,restored)


def causal_effect_supported(treatment, control, deletion) -> bool:
    e=causal_effect_evidence(treatment,control,deletion)
    return e.effect_present and e.deletion_restores_control


class RepresentationBootstrap:
    """Current executable family first; generic constructor access only after returned insufficiency.

    The substrate never receives target truth. It receives executable candidates plus returned
    observations and separate verification returns. Candidate construction and evaluator truth
    remain outside this object.
    """
    def __init__(self, initial: Mapping[Any,Callable[[Any],Any]]):
        self.initial=dict(initial)
        self.live=dict(initial)
        self.constructor_open=False
        self.admitted_id=None
        self.admitted=None
        self.trigger_history=[]

    def update_current_family(self, observations: Sequence[tuple[Any,Any]]):
        self.live={k:f for k,f in self.live.items() if all(f(x)==y for x,y in observations)}
        if not self.live:
            self.constructor_open=True
            self.trigger_history.append({'kind':'EXPRESSIVE_INSUFFICIENCY','observations':len(observations)})
        return tuple(self.live)

    def propose_constructed(self, candidate_id: Any, executable: Callable[[Any],Any], observations: Sequence[tuple[Any,Any]]):
        if not self.constructor_open:
            raise ValueError('constructor family is not authorized')
        if not all(executable(x)==y for x,y in observations):
            raise ValueError('constructed candidate does not fit returned observations')
        return {'id':candidate_id,'executable':executable}

    def admit_constructed(self, proposal, verification: Sequence[tuple[Any,Any]]):
        f=proposal['executable']
        if not verification or not all(f(x)==y for x,y in verification):
            return False
        self.admitted_id=proposal['id']; self.admitted=f
        return True

    def predict(self, x):
        if self.admitted is not None:
            return self.admitted(x)
        if not self.live:
            return None
        vals={f(x) for f in self.live.values()}
        return next(iter(vals)) if len(vals)==1 else None

    def delete_constructed(self):
        self.admitted_id=None; self.admitted=None
