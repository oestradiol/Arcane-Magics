from __future__ import annotations

"""Generic joint role-normalized scene binder for #206 Fresh4.

The code contains no face, task, or role semantics. Teacher data supplies an
ordered role schema and gold variable bindings. Candidate assignments are
evaluated by normalizing the entire scene under one joint assignment.
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
    for x in TOKEN_RE.findall(str(text)):
        if x not in out: out.append(x)
    return tuple(out)

def normalize_scene(text: str, *, roles: tuple[str,...], binding: Mapping[str,str])->str:
    marker={binding[role]:f"<R{i}>" for i,role in enumerate(roles)}
    return _norm(TOKEN_RE.sub(lambda m:marker.get(m.group(0),"<OTHER>"),str(text)))

def sim(a: str,b: str)->float:
    return SequenceMatcher(None,a,b,autojunk=False).ratio()

def learn_state(prefreeze: Mapping[str,Any])->dict[str,Any]:
    tasks={}
    for task in prefreeze["tasks"]:
        tid=str(task["id"]); roles=tuple(str(k) for k in task["output_schema"].keys()); faces={}
        for face,rows in task["train_examples"].items():
            templates=[]
            for row in rows:
                gold={str(k):str(v) for k,v in row["gold"].items()}
                templates.append(normalize_scene(row["surface"],roles=roles,binding=gold))
            faces[str(face)]=tuple(templates)
        tasks[tid]={"roles":roles,"faces":faces}
    return {"schema":"Venus.JointRoleNormalizedSceneState.v0.1","tasks":tasks}

def predict(state: Mapping[str,Any], *, task_id: str, face: str, surface: str, min_margin: float=0.001)->dict[str,Any]:
    if state.get("schema")!="Venus.JointRoleNormalizedSceneState.v0.1":
        raise ValueError("unsupported joint scene state")
    task=state["tasks"][task_id]; roles=tuple(task["roles"]); centers=tokens(surface)
    if len(centers)!=len(roles):
        return {"status":"WITHHOLD_TOKEN_CARDINALITY","binding":None,"assignment_margin":0.0}
    ranked=[]
    for perm in permutations(centers):
        binding={role:center for role,center in zip(roles,perm)}
        normalized=normalize_scene(surface,roles=roles,binding=binding)
        score=max((sim(normalized,p) for p in task["faces"][face]),default=0.0)
        ranked.append((score,tuple(perm),binding))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    best=ranked[0]; second=ranked[1][0] if len(ranked)>1 else 0.0; margin=best[0]-second
    if best[0]<=0.0 or margin<min_margin:
        return {"status":"WITHHOLD_JOINT_SCENE_AMBIGUOUS","binding":None,"assignment_margin":margin}
    return {"status":"PREDICTED_JOINT_ROLE_NORMALIZED_SCENE","binding":best[2],"assignment_margin":margin}
