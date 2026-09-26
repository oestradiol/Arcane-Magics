from __future__ import annotations

"""Generic pairwise relational Theater scaffold for #206 Fresh3.

No language, role, or task semantics are hard-coded. Teacher episodes provide
opaque centers and role assignments. The learner represents each ordered center
pair inside its full scene and learns role-pair prototypes.
"""

from difflib import SequenceMatcher
from itertools import permutations
import re
from typing import Any, Mapping

TOKEN_RE=re.compile(r"[@#][A-Za-z]+")

def _norm(text: str)->str:
    return " ".join(str(text).casefold().split())

def tokens(text: str)->tuple[str,...]:
    out=[]
    for tok in TOKEN_RE.findall(str(text)):
        if tok not in out:
            out.append(tok)
    return tuple(out)

def centered_pair(text: str, src: str, dst: str)->str:
    def repl(match):
        tok=match.group(0)
        if tok==src: return "<SRC>"
        if tok==dst: return "<DST>"
        return "<OTHER>"
    return _norm(TOKEN_RE.sub(repl,str(text)))

def similarity(a: str,b: str)->float:
    return SequenceMatcher(None,a,b,autojunk=False).ratio()

def learn_state(prefreeze: Mapping[str,Any])->dict[str,Any]:
    tasks={}
    for task in prefreeze["tasks"]:
        tid=str(task["id"])
        roles=tuple(str(k) for k in task["output_schema"].keys())
        faces={}
        for face,rows in task["train_examples"].items():
            protos={(ra,rb):[] for ra in roles for rb in roles if ra!=rb}
            for row in rows:
                surface=str(row["surface"])
                gold={str(k):str(v) for k,v in row["gold"].items()}
                for ra in roles:
                    for rb in roles:
                        if ra==rb: continue
                        protos[(ra,rb)].append(centered_pair(surface,gold[ra],gold[rb]))
            faces[str(face)]={f"{a}||{b}":tuple(v) for (a,b),v in protos.items()}
        tasks[tid]={"roles":roles,"faces":faces}
    return {"schema":"Venus.PairwiseRelationalTheaterGraphState.v0.1","tasks":tasks}

def predict(state: Mapping[str,Any], *, task_id: str, face: str, surface: str, min_margin: float=0.001)->dict[str,Any]:
    if state.get("schema")!="Venus.PairwiseRelationalTheaterGraphState.v0.1":
        raise ValueError("unsupported relational Theater state")
    task=state["tasks"][task_id]
    roles=tuple(task["roles"])
    centers=tokens(surface)
    if len(centers)!=len(roles):
        return {"status":"WITHHOLD_TOKEN_CARDINALITY","binding":None,"assignment_margin":0.0}
    ranked=[]
    for perm in permutations(centers):
        binding={role:center for role,center in zip(roles,perm)}
        scores=[]
        for ra in roles:
            for rb in roles:
                if ra==rb: continue
                observed=centered_pair(surface,binding[ra],binding[rb])
                key=f"{ra}||{rb}"
                score=max((similarity(observed,p) for p in task["faces"][face][key]),default=0.0)
                scores.append(score)
        ranked.append((sum(scores)/len(scores),tuple(perm),binding))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    best=ranked[0]
    second=ranked[1][0] if len(ranked)>1 else 0.0
    margin=best[0]-second
    if best[0]<=0.0 or margin<min_margin:
        return {"status":"WITHHOLD_RELATIONAL_GRAPH_AMBIGUOUS","binding":None,"assignment_margin":margin}
    return {"status":"PREDICTED_PAIRWISE_RELATIONAL_THEATER_GRAPH","binding":best[2],"assignment_margin":margin}
