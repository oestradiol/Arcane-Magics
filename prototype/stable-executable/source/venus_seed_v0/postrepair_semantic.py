from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import combinations
from typing import Iterable, Sequence
import hashlib, json
import numpy as np

OPS=("RAW","XOR","EQ","AND","OR")

@dataclass(frozen=True)
class FeatureExpr:
    op:str
    i:int
    j:int=-1
    def payload(self): return {"op":self.op,"i":int(self.i),"j":int(self.j)}

@dataclass
class LearnedCrossing:
    width:int
    action_bits:int
    expressions:list[FeatureExpr]
    state_digest:str

@dataclass
class PatchClause:
    literals:tuple[tuple[int,int],...]
    xor_mask:int

@dataclass
class LearnedPatch:
    clauses:list[PatchClause]
    provenance_token:str
    state_digest:str


def _digest(x)->str:
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def candidate_features(width:int)->list[FeatureExpr]:
    out=[FeatureExpr("RAW",i) for i in range(width)]
    for i,j in combinations(range(width),2):
        for op in ("XOR","EQ","AND","OR"):
            out.append(FeatureExpr(op,i,j))
    return out

def eval_feature(X:np.ndarray,e:FeatureExpr)->np.ndarray:
    a=X[:,e.i].astype(np.int8)
    if e.op=="RAW": return a
    b=X[:,e.j].astype(np.int8)
    if e.op=="XOR": return a^b
    if e.op=="EQ": return (a==b).astype(np.int8)
    if e.op=="AND": return a&b
    if e.op=="OR": return a|b
    raise ValueError(e.op)

def actions_to_bits(y:Sequence[int], bits:int)->np.ndarray:
    a=np.asarray(y,dtype=np.int64)
    return np.column_stack([((a>>k)&1).astype(np.int8) for k in range(bits)])

def bits_to_actions(B:np.ndarray)->np.ndarray:
    y=np.zeros(len(B),dtype=np.int64)
    for k in range(B.shape[1]): y |= (B[:,k].astype(np.int64)<<k)
    return y

def fit_crossing(X:np.ndarray,y:Sequence[int],action_bits:int=3)->LearnedCrossing:
    X=np.asarray(X,dtype=np.int8); Y=actions_to_bits(y,action_bits); cands=candidate_features(X.shape[1])
    ex=[]
    for k in range(action_bits):
        exact=[]
        for e in cands:
            if np.array_equal(eval_feature(X,e),Y[:,k]): exact.append(e)
        if not exact:
            # Select best only for explicit WITHHOLD diagnostics; do not silently claim success.
            scores=[float(np.mean(eval_feature(X,e)==Y[:,k])) for e in cands]
            best=max(scores)
            raise RuntimeError(f"WITHHOLD_NO_EXACT_FEATURE bit={k} best={best}")
        exact.sort(key=lambda e:(1 if e.op=="RAW" else 2,e.op,e.i,e.j))
        ex.append(exact[0])
    payload={"width":X.shape[1],"action_bits":action_bits,"expressions":[e.payload() for e in ex]}
    return LearnedCrossing(X.shape[1],action_bits,ex,_digest(payload))

def predict_crossing(model:LearnedCrossing,X:np.ndarray)->np.ndarray:
    X=np.asarray(X,dtype=np.int8); B=np.column_stack([eval_feature(X,e) for e in model.expressions]); return bits_to_actions(B)

def rederive_after_transform(Xt:np.ndarray,y:Sequence[int],action_bits:int=3)->LearnedCrossing:
    return fit_crossing(Xt,y,action_bits)

def _mask_for_literals(X:np.ndarray,lits:tuple[tuple[int,int],...])->np.ndarray:
    m=np.ones(len(X),dtype=bool)
    for i,v in lits: m &= (X[:,i]==v)
    return m

def _find_exact_clause(X:np.ndarray,target:np.ndarray,max_literals:int=4)->tuple[tuple[int,int],...]|None:
    # Search conjunctions over raw coordinates. Exact means mask == target over supplied calibration set.
    width=X.shape[1]
    for r in range(1,max_literals+1):
        for idxs in combinations(range(width),r):
            # Only values that occur on target rows are worth testing.
            vals=set(tuple(int(X[t,i]) for i in idxs) for t in np.where(target)[0])
            for vv in sorted(vals):
                lits=tuple(zip(idxs,vv)); m=_mask_for_literals(X,lits)
                if np.array_equal(m,target): return lits
    return None

def fit_local_patch(X:np.ndarray,old_y:Sequence[int],new_y:Sequence[int],provenance_token:str,max_clauses:int=4,max_literals:int=4)->LearnedPatch:
    X=np.asarray(X,dtype=np.int8); old=np.asarray(old_y,dtype=np.int64); new=np.asarray(new_y,dtype=np.int64)
    delta=old^new; clauses=[]
    for d in sorted(int(x) for x in set(delta.tolist()) if int(x)!=0):
        target=(delta==d)
        # Peel exact conjunctions; this can express finite unions without preauthoring support identities.
        rem=target.copy(); count=0
        while rem.any() and count<max_clauses:
            # Find a conjunction that is subset of rem and covers most remaining positives while no negatives.
            best=None; bestcov=-1
            width=X.shape[1]
            for r in range(1,max_literals+1):
                for idxs in combinations(range(width),r):
                    vals=set(tuple(int(X[t,i]) for i in idxs) for t in np.where(rem)[0])
                    for vv in vals:
                        lits=tuple(zip(idxs,vv)); m=_mask_for_literals(X,lits)
                        if np.any(m & ~target): continue
                        cov=int(np.sum(m & rem))
                        if cov>bestcov or (cov==bestcov and best is not None and lits<best): best=lits;bestcov=cov
            if best is None or bestcov<=0: break
            m=_mask_for_literals(X,best); rem &= ~m; clauses.append(PatchClause(best,d)); count+=1
        if rem.any(): raise RuntimeError(f"WITHHOLD_PATCH_LANGUAGE_INSUFFICIENT delta={d} remaining={int(rem.sum())}")
    payload={"token":provenance_token,"clauses":[{"literals":c.literals,"xor_mask":c.xor_mask} for c in clauses]}
    return LearnedPatch(clauses,provenance_token,_digest(payload))

def apply_patch(patch:LearnedPatch,X:np.ndarray,old_y:Sequence[int],provenance_token:str)->np.ndarray:
    if provenance_token!=patch.provenance_token: raise RuntimeError("REJECT_MISBOUND")
    X=np.asarray(X,dtype=np.int8); y=np.asarray(old_y,dtype=np.int64).copy()
    for c in patch.clauses: y[_mask_for_literals(X,c.literals)] ^= int(c.xor_mask)
    return y

def fit_acquisition(raw_bit:np.ndarray, action_bit:np.ndarray, target:np.ndarray):
    raw=np.asarray(raw_bit,dtype=np.int8); act=np.asarray(action_bit,dtype=np.int8); t=np.asarray(target,dtype=np.int8)
    candidates={
      "RAW":raw,"ACTION":act,"XOR":raw^act,"EQ":(raw==act).astype(np.int8),"AND":raw&act,"OR":raw|act,
      "NOT_RAW":1-raw,"NOT_ACTION":1-act,
    }
    exact=[k for k,v in candidates.items() if np.array_equal(v,t)]
    if exact:return {"form":sorted(exact)[0],"exact":True}
    k=max(candidates,key=lambda q:float(np.mean(candidates[q]==t)))
    return {"form":k,"exact":False,"accuracy":float(np.mean(candidates[k]==t))}

def predict_acquisition(model,raw_bit,action_bit):
    raw=np.asarray(raw_bit,dtype=np.int8); act=np.asarray(action_bit,dtype=np.int8); k=model["form"]
    return {"RAW":raw,"ACTION":act,"XOR":raw^act,"EQ":(raw==act).astype(np.int8),"AND":raw&act,"OR":raw|act,"NOT_RAW":1-raw,"NOT_ACTION":1-act}[k]
