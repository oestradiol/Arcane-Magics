from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Sequence

FAMILIES=("POLY_PLUS_ONE","PARITY_AFFINE","THRESHOLD_AFFINE","ABS_AFFINE")
OFFSETS=(-2,-1,0,1,2)
AMPS=(-2,-1,1,2)
PHASES=(0,1)
THRESHOLDS=(-2,-1,0,1,2)
CENTERS=(-2,-1,0,1,2)
POLY_MAX_DEGREE=6
POLY_COEFF_VALUES=(-3,-2,-1,0,1,2,3)

@dataclass(frozen=True)
class ConstructorFit:
    family:str
    exact:bool
    params:tuple[int,...]
    searched:int
    exact_count:int
    degree_witness:int|None=None

def _parity(x:int,p:int)->int: return 1 if ((x+p)&1)==0 else -1
def _threshold(x:int,t:int)->int: return 1 if x>=t else -1

def evaluate(family:str, params:Sequence[int], x:int)->int:
    if family=="PARITY_AFFINE":
        a,b,p=params; return a+b*_parity(int(x),int(p))
    if family=="THRESHOLD_AFFINE":
        a,b,t=params; return a+b*_threshold(int(x),int(t))
    if family=="ABS_AFFINE":
        a,b,c=params; return a+b*abs(int(x)-int(c))
    if family=="POLY_PLUS_ONE":
        return sum(int(c)*(int(x)**i) for i,c in enumerate(params))
    raise KeyError(family)

def finite_difference_degree(obs:Sequence[tuple[int,int]])->int:
    xs=[int(x) for x,_ in obs]
    if any(xs[i+1]-xs[i]!=1 for i in range(len(xs)-1)): raise ValueError("unit grid required")
    vals=[int(y) for _,y in obs]; d=0
    for i in range(len(vals)):
        if any(v!=0 for v in vals): d=i
        vals=[vals[j+1]-vals[j] for j in range(len(vals)-1)]
        if not vals: break
    return d

def _small_family_params(family:str):
    if family=="PARITY_AFFINE": return product(OFFSETS,AMPS,PHASES)
    if family=="THRESHOLD_AFFINE": return product(OFFSETS,AMPS,THRESHOLDS)
    if family=="ABS_AFFINE": return product(OFFSETS,AMPS,CENTERS)
    raise KeyError(family)

def fit_constructor(family:str, obs:Sequence[tuple[int,int]])->ConstructorFit:
    obs=tuple((int(x),int(y)) for x,y in obs)
    if family=="POLY_PLUS_ONE":
        d=finite_difference_degree(obs)
        if d>POLY_MAX_DEGREE: return ConstructorFit(family,False,(),0,0,d)
        exact=[]; searched=0
        for cs in product(POLY_COEFF_VALUES,repeat=POLY_MAX_DEGREE+1):
            searched+=1
            if all(evaluate(family,cs,x)==y for x,y in obs): exact.append(tuple(int(z) for z in cs))
        return ConstructorFit(family,bool(exact),min(exact) if exact else (),searched,len(exact),d)
    exact=[]; searched=0
    for p in _small_family_params(family):
        searched+=1
        if all(evaluate(family,p,x)==y for x,y in obs): exact.append(tuple(int(z) for z in p))
    return ConstructorFit(family,bool(exact),min(exact) if exact else (),searched,len(exact),None)

def fit_meta_grammar(obs): return {f:fit_constructor(f,obs) for f in FAMILIES}

def revise_constructor(current_family:str, obs:Sequence[tuple[int,int]]):
    fits=fit_meta_grammar(obs); exact=tuple(f for f in FAMILIES if fits[f].exact)
    if not exact: raise ValueError("no exact successor in supplied meta-grammar")
    chosen=fits[exact[0]]
    return {"current":fits[current_family],"selected":chosen,"exact_families":exact,"changed":chosen.family!=current_family,"fits":fits}

def predict(fit:ConstructorFit,xs:Sequence[int]):
    if not fit.exact: raise ValueError("inexact constructor fit")
    return tuple(evaluate(fit.family,fit.params,int(x)) for x in xs)
