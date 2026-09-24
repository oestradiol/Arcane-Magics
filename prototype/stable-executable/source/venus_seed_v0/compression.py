from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

@dataclass(frozen=True)
class CompressionWitness:
    left: Any
    right: Any
    old_signature: Any
    new_left: Any
    new_right: Any
    discriminator: str

@dataclass(frozen=True)
class ReductionResult:
    equivalent: bool
    tested: int
    mismatches: tuple[Any, ...] = ()


def quotient_by_signature(states: Iterable[Any], signature: Callable[[Any], Hashable]):
    groups=defaultdict(list)
    for s in states: groups[signature(s)].append(s)
    return tuple(tuple(v) for _,v in sorted(groups.items(),key=lambda kv:repr(kv[0])))


def reduction_equivalent(states: Iterable[Any], left: Callable[[Any],Any], right: Callable[[Any],Any]) -> ReductionResult:
    mism=[]; n=0
    for s in states:
        n+=1
        a,b=left(s),right(s)
        if a!=b: mism.append((s,a,b))
    return ReductionResult(not mism,n,tuple(mism))


def separating_witness(states: Iterable[Any], old_signature: Callable[[Any],Hashable], new_consequence: Callable[[Any],Any], *, discriminator='expanded-future-family'):
    groups=defaultdict(list)
    for s in states: groups[old_signature(s)].append(s)
    for sig,group in groups.items():
        for i,a in enumerate(group):
            for b in group[i+1:]:
                na,nb=new_consequence(a),new_consequence(b)
                if na!=nb:
                    return CompressionWitness(a,b,sig,na,nb,discriminator)
    return None


def refinement_needed(states, old_signature, new_consequence) -> bool:
    return separating_witness(states,old_signature,new_consequence) is not None


def effective_quotient(states: Iterable[Any], consequence: Callable[[Any],Hashable]):
    return quotient_by_signature(states,consequence)


def representation_is_gauge(states: Iterable[Any], encoding_a: Callable[[Any],Any], encoding_b: Callable[[Any],Any], consequence: Callable[[Any],Any]) -> bool:
    """Different encodings are gauge when they never alter declared consequence partition."""
    states=list(states)
    qa=quotient_by_signature(states,lambda s:(consequence(s),))
    qb=quotient_by_signature(states,lambda s:(consequence(s),))
    # Encodings may differ arbitrarily; only their induced consequence matters here.
    return qa==qb and any(encoding_a(s)!=encoding_b(s) for s in states)


def minimal_binary_refinement(states: Iterable[Any], old_signature: Callable[[Any],Hashable], new_consequence: Callable[[Any],Hashable]):
    """Return one bit per state iff every old class splits into at most two new consequence classes.

    This is a generic finite witness, not a claim that the bit has a privileged coordinate meaning.
    """
    states=list(states); bit={}
    groups=defaultdict(list)
    for s in states: groups[old_signature(s)].append(s)
    for _,group in groups.items():
        vals=[]
        for s in group:
            v=new_consequence(s)
            if v not in vals: vals.append(v)
        if len(vals)>2: return None
        for s in group: bit[s]=vals.index(new_consequence(s))
    return bit


def refine_signature(old_signature: Callable[[Any],Hashable], added_bit: Mapping[Any,int]):
    return lambda s:(old_signature(s),added_bit[s])


def reachable(start: Hashable, goals: set[Hashable], edges: Mapping[Hashable,Iterable[Hashable]]) -> bool:
    q=deque([start]); seen={start}
    while q:
        x=q.popleft()
        if x in goals:return True
        for y in edges.get(x,()):
            if y not in seen: seen.add(y); q.append(y)
    return False


def strongly_connected_components(nodes: Iterable[Hashable], edges: Mapping[Hashable,Iterable[Hashable]]):
    nodes=list(nodes); index=0; stack=[]; on=set(); idx={}; low={}; out=[]
    def visit(v):
        nonlocal index
        idx[v]=low[v]=index;index+=1;stack.append(v);on.add(v)
        for w in edges.get(v,()):
            if w not in idx: visit(w); low[v]=min(low[v],low[w])
            elif w in on: low[v]=min(low[v],idx[w])
        if low[v]==idx[v]:
            comp=[]
            while True:
                w=stack.pop();on.remove(w);comp.append(w)
                if w==v:break
            out.append(frozenset(comp))
    for n in nodes:
        if n not in idx: visit(n)
    return tuple(out)


def self_sealing_component(start: Hashable, repair_goals: set[Hashable], edges: Mapping[Hashable,Iterable[Hashable]]) -> bool:
    """Strong obstruction = repair unreachable and start lies in a closed SCC."""
    if reachable(start,repair_goals,edges): return False
    nodes=set(edges)|{y for ys in edges.values() for y in ys}|{start}
    for comp in strongly_connected_components(nodes,edges):
        if start in comp:
            exits={y for x in comp for y in edges.get(x,()) if y not in comp}
            return len(comp)>1 and not exits
    return False


def mature_substitution_allowed(states: Iterable[Any], project: Callable[[Any],Any], mature: Callable[[Any],Any]) -> bool:
    return reduction_equivalent(states,project,mature).equivalent
