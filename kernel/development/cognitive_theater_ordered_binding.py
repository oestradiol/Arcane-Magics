from __future__ import annotations

"""Generic ordered opaque-center binding scaffold for #206 Fresh2.

The learner receives opaque-token teacher episodes as data. It uses sequence
alignment on centered surfaces, preserving order and multiplicity that the
earlier set-Jaccard scaffold discarded. No face grammar or task semantics are
hard-coded here.
"""

from difflib import SequenceMatcher
from itertools import permutations
import re
from typing import Any, Mapping

TOKEN_RE=re.compile(r"[@#][A-Za-z]+")


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def opaque_tokens(text: str) -> tuple[str,...]:
    out=[]
    for tok in TOKEN_RE.findall(str(text)):
        if tok not in out:
            out.append(tok)
    return tuple(out)


def centered_surface(text: str, focus: str) -> str:
    def repl(match):
        return "<SELF>" if match.group(0)==focus else "<OTHER>"
    return _norm(TOKEN_RE.sub(repl,str(text)))


def _sequence_similarity(a: str,b: str) -> float:
    return SequenceMatcher(None,a,b,autojunk=False).ratio()


def learn_state(prefreeze: Mapping[str,Any]) -> dict[str,Any]:
    tasks={}
    for task in prefreeze["tasks"]:
        tid=str(task["id"])
        roles=tuple(str(k) for k in task["output_schema"].keys())
        faces={}
        for face,rows in task["train_examples"].items():
            protos={role:[] for role in roles}
            for row in rows:
                surface=str(row["surface"])
                gold={str(k):str(v) for k,v in row["gold"].items()}
                tokens=opaque_tokens(surface)
                if set(gold.values())!=set(tokens):
                    raise ValueError(f"gold/token mismatch for {tid}/{face}")
                for role,token in gold.items():
                    protos[role].append(centered_surface(surface,token))
            faces[str(face)]={role:tuple(vals) for role,vals in protos.items()}
        tasks[tid]={"roles":roles,"faces":faces}
    return {"schema":"Venus.OrderedOpaqueCenterBindingState.v0.1","tasks":tasks}


def predict(state: Mapping[str,Any], *, task_id: str, face: str, surface: str, min_margin: float=0.001)->dict[str,Any]:
    if state.get("schema")!="Venus.OrderedOpaqueCenterBindingState.v0.1":
        raise ValueError("unsupported ordered binding state")
    task=state["tasks"][task_id]
    roles=tuple(task["roles"])
    tokens=opaque_tokens(surface)
    if len(tokens)!=len(roles):
        return {"status":"WITHHOLD_TOKEN_CARDINALITY","binding":None,"assignment_margin":0.0}
    matrix={}
    for token in tokens:
        centered=centered_surface(surface,token)
        matrix[token]={}
        for role in roles:
            matrix[token][role]=max(
                (_sequence_similarity(centered,p) for p in task["faces"][face][role]),
                default=0.0,
            )
    ranked=[]
    for perm in permutations(tokens):
        binding={role:token for role,token in zip(roles,perm)}
        score=sum(matrix[token][role] for role,token in binding.items())
        ranked.append((score,tuple(perm),binding))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    best=ranked[0]
    second=ranked[1][0] if len(ranked)>1 else 0.0
    margin=best[0]-second
    if best[0]<=0.0 or margin<min_margin:
        return {"status":"WITHHOLD_ORDERED_BINDING_AMBIGUOUS","binding":None,"assignment_margin":margin}
    return {"status":"PREDICTED_ORDERED_OPAQUE_BINDING","binding":best[2],"assignment_margin":margin}
