from __future__ import annotations

import importlib.util,json,re,sys
from itertools import permutations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def mod(name,rel):
    s=importlib.util.spec_from_file_location(name,ROOT/rel)
    if s is None or s.loader is None: raise RuntimeError(rel)
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

unary=mod("fresh4_unary","kernel/development/cognitive_theater_ordered_binding.py")
pair=mod("fresh4_pair","kernel/development/cognitive_theater_relational_graph.py")
joint=mod("fresh4_joint","kernel/development/cognitive_theater_joint_scene.py")
TOKEN_RE=re.compile(r"[@#][A-Za-z]+")

def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def utoks(text):
    out=[]
    for x in TOKEN_RE.findall(text):
        if x not in out: out.append(x)
    return tuple(out)

def count_state(pre):
    out={}
    for task in pre["tasks"]:
        tid=task["id"]; roles=tuple(task["output_schema"]); faces={}
        for face,rows in task["train_examples"].items():
            d={r:[] for r in roles}
            for row in rows:
                seq=TOKEN_RE.findall(row["surface"])
                for r,t in row["gold"].items(): d[r].append(seq.count(t))
            faces[face]={r:sum(v)/len(v) for r,v in d.items()}
        out[tid]={"roles":roles,"faces":faces}
    return out

def count_pred(st,tid,face,surface):
    roles=tuple(st[tid]["roles"]); centers=utoks(surface); seq=TOKEN_RE.findall(surface); ranked=[]
    for perm in permutations(centers):
        b={r:t for r,t in zip(roles,perm)}
        cost=sum(abs(seq.count(t)-st[tid]["faces"][face][r]) for r,t in b.items())
        ranked.append((cost,tuple(perm),b))
    ranked.sort(key=lambda x:(x[0],x[1]))
    if len(ranked)>1 and abs(ranked[0][0]-ranked[1][0])<1e-12: return None
    return ranked[0][2]

def evaluate_kind(pre,kind):
    cs=count_state(pre) if kind=="count" else None
    st=unary.learn_state(pre) if kind=="unary" else pair.learn_state(pre) if kind=="pair" else joint.learn_state(pre) if kind=="joint" else None
    correct=total=withholds=0; per_task={}; per_face={}
    for task in pre["tasks"]:
        tid=task["id"]; per_task[tid]={"correct":0,"total":0,"withholds":0}
        for face,rows in task["heldout_examples"].items():
            per_face.setdefault(face,{"correct":0,"total":0,"withholds":0})
            for row in rows:
                if kind=="count": pred=count_pred(cs,tid,face,row["surface"])
                elif kind=="unary": pred=unary.predict(st,task_id=tid,face=face,surface=row["surface"])["binding"]
                elif kind=="pair": pred=pair.predict(st,task_id=tid,face=face,surface=row["surface"])["binding"]
                else: pred=joint.predict(st,task_id=tid,face=face,surface=row["surface"])["binding"]
                ok=pred==row["gold"]; total+=1; correct+=int(ok); withholds+=int(pred is None)
                per_task[tid]["total"]+=1; per_task[tid]["correct"]+=int(ok); per_task[tid]["withholds"]+=int(pred is None)
                per_face[face]["total"]+=1; per_face[face]["correct"]+=int(ok); per_face[face]["withholds"]+=int(pred is None)
    return {"correct":correct,"total":total,"accuracy":correct/total if total else 0.0,"withholds":withholds,"per_task":per_task,"per_face":per_face}

def evaluate():
    pre=load("kernel/development/COGNITIVE_THEATER_JOINT_SCENE_FRESH4_PREFREEZE.json")
    count=evaluate_kind(pre,"count"); u=evaluate_kind(pre,"unary"); p=evaluate_kind(pre,"pair"); j=evaluate_kind(pre,"joint")
    return {
      "schema":"Venus.CognitiveTheaterJointSceneFresh4Result.v0.1","status":"RETURNED_FRESH4_LOCAL_DEVELOPMENTAL_COMPARISON","issue_ref":206,
      "count_only":count,"unary_ordered":u,"pairwise_relational":p,"joint_scene":j,
      "joint_minus_count":j["accuracy"]-count["accuracy"],"joint_minus_unary":j["accuracy"]-u["accuracy"],"joint_minus_pairwise":j["accuracy"]-p["accuracy"],
      "independent_external_evaluation":False,"general_theater_claim":False,"internalization_claim":False,"promotion_authority":False,"truth_authority":False
    }
if __name__=="__main__": print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
