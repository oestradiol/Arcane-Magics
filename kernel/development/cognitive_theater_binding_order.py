from __future__ import annotations

"""Data-driven opaque-center binding scaffold for #206 G2/G3.

The code is given only the benchmark's opaque token syntax (@participant, #event).
It contains no English/Japanese/PT-BR/Math grammar and no task-specific semantic
words. Roles are learned from token-centered teacher contexts.
"""

from itertools import permutations
import re
from typing import Any, Mapping

TOKEN_RE=re.compile(r"[@#][A-Za-z]+")


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def _features(text: str, n: int = 3) -> frozenset[str]:
    value=_norm(text)
    if not value:
        return frozenset()
    if len(value)<n:
        return frozenset((value,))
    return frozenset(value[i:i+n] for i in range(len(value)-n+1))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    u=a|b
    return 0.0 if not u else len(a&b)/len(u)


def opaque_tokens(text: str) -> tuple[str,...]:
    seen=[]
    for tok in TOKEN_RE.findall(str(text)):
        if tok not in seen:
            seen.append(tok)
    return tuple(seen)


def centered_surface(text: str, focus: str) -> str:
    """Replace all occurrences of focus by SELF and other opaque tokens by OTHER."""
    def repl(match):
        return "<SELF>" if match.group(0)==focus else "<OTHER>"
    return TOKEN_RE.sub(repl,str(text))


def learn_binding_state(prefreeze: Mapping[str,Any], *, n: int = 3) -> dict[str,Any]:
    tasks={}
    for task in prefreeze["tasks"]:
        task_id=str(task["id"])
        roles=tuple(str(x) for x in task["output_schema"].keys())
        faces={}
        for face,rows in task["train_examples"].items():
            protos={role:[] for role in roles}
            for row in rows:
                surface=str(row["surface"])
                gold={str(k):str(v) for k,v in row["gold"].items()}
                tokens=opaque_tokens(surface)
                if set(gold.values())!=set(tokens):
                    raise ValueError(f"gold/token mismatch for {task_id}/{face}")
                for role,token in gold.items():
                    protos[role].append(tuple(sorted(_features(centered_surface(surface,token),n))))
            faces[str(face)]={role:tuple(vals) for role,vals in protos.items()}
        tasks[task_id]={"roles":roles,"faces":faces}
    return {
        "schema":"Venus.OpaqueCenterBindingState.v0.1",
        "n":int(n),
        "tasks":tasks,
    }


def _role_score(state: Mapping[str,Any], task_id: str, face: str, role: str, surface: str, token: str) -> float:
    target=_features(centered_surface(surface,token),int(state["n"]))
    protos=state["tasks"][task_id]["faces"][face][role]
    return max((_jaccard(target,frozenset(x)) for x in protos),default=0.0)


def predict_binding(
    state: Mapping[str,Any],
    *,
    task_id: str,
    face: str,
    surface: str,
    min_assignment_margin: float = 0.002,
) -> dict[str,Any]:
    if state.get("schema")!="Venus.OpaqueCenterBindingState.v0.1":
        raise ValueError("unsupported binding state")
    task=state["tasks"][task_id]
    roles=tuple(task["roles"])
    tokens=opaque_tokens(surface)
    if len(tokens)!=len(roles):
        return {"status":"WITHHOLD_TOKEN_CARDINALITY","binding":None,"scores":{}}

    matrix={
        token:{role:_role_score(state,task_id,face,role,surface,token) for role in roles}
        for token in tokens
    }
    ranked=[]
    for perm in permutations(tokens):
        binding={role:token for role,token in zip(roles,perm)}
        score=sum(matrix[token][role] for role,token in binding.items())
        ranked.append((score,tuple(perm),binding))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    best=ranked[0]
    second=ranked[1][0] if len(ranked)>1 else 0.0
    margin=best[0]-second
    if best[0]<=0.0 or margin<min_assignment_margin:
        return {"status":"WITHHOLD_BINDING_AMBIGUOUS","binding":None,"scores":matrix,"assignment_margin":margin}
    return {
        "status":"PREDICTED_OPAQUE_CENTER_BINDING",
        "binding":best[2],
        "scores":matrix,
        "assignment_margin":margin,
    }
