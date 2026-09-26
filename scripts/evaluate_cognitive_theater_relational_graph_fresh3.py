from __future__ import annotations

import importlib.util, json, re, sys
from itertools import permutations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def mod(name,rel):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel)
    if spec is None or spec.loader is None: raise RuntimeError(rel)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m

unary=mod("ordered_unary","kernel/development/cognitive_theater_ordered_binding.py")
pair=mod("pairwise_graph","kernel/development/cognitive_theater_relational_graph.py")
TOKEN_RE=re.compile(r"[@#][A-Za-z]+")

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def unique_tokens(text):
    out=[]
    for x in TOKEN_RE.findall(str(text)):
        if x not in out: out.append(x)
    return tuple(out)

def learn_count(prefreeze):
    tasks={}
    for task in prefreeze["tasks"]:
        tid=task["id"]; roles=tuple(task["output_schema"]); faces={}
        for face,rows in task["train_examples"].items():
            vals={r:[] for r in roles}
            for row in rows:
                toks=TOKEN_RE.findall(row["surface"])
                for role,token in row["gold"].items(): vals[role].append(toks.count(token))
            faces[face]={r:sum(v)/len(v) for r,v in vals.items()}
        tasks[tid]={"roles":roles,"faces":faces}
    return tasks

def predict_count(state,tid,face,surface):
    roles=tuple(state[tid]["roles"]); toks=unique_tokens(surface); all_toks=TOKEN_RE.findall(surface)
    ranked=[]
    for perm in permutations(toks):
        binding={r:t for r,t in zip(roles,perm)}
        cost=sum(abs(all_toks.count(t)-state[tid]["faces"][face][r]) for r,t in binding.items())
        ranked.append((cost,tuple(perm),binding))
    ranked.sort(key=lambda x:(x[0],x[1]))
    if len(ranked)>1 and abs(ranked[0][0]-ranked[1][0])<1e-12:
        return None
    return ranked[0][2]

def evaluate_model(pre,kind):
    count_state=learn_count(pre) if kind=="count" else None
    state=unary.learn_state(pre) if kind=="unary" else pair.learn_state(pre) if kind=="pairwise" else None
    correct=0; total=0; withholds=0; per_task={}; per_face={}
    for task in pre["tasks"]:
        tid=task["id"]; per_task[tid]={"correct":0,"total":0,"withholds":0}
        for face,rows in task["heldout_examples"].items():
            per_face.setdefault(face,{"correct":0,"total":0,"withholds":0})
            for row in rows:
                if kind=="count":
                    pred=predict_count(count_state,tid,face,row["surface"]); status="COUNT_PREDICTED" if pred else "WITHHOLD_COUNT_TIE"
                elif kind=="unary":
                    out=unary.predict(state,task_id=tid,face=face,surface=row["surface"]); pred=out["binding"]; status=out["status"]
                else:
                    out=pair.predict(state,task_id=tid,face=face,surface=row["surface"]); pred=out["binding"]; status=out["status"]
                ok=pred==row["gold"]; total+=1; correct+=int(ok); withholds+=int(pred is None)
                per_task[tid]["total"]+=1; per_task[tid]["correct"]+=int(ok); per_task[tid]["withholds"]+=int(pred is None)
                per_face[face]["total"]+=1; per_face[face]["correct"]+=int(ok); per_face[face]["withholds"]+=int(pred is None)
    return {"correct":correct,"total":total,"accuracy":correct/total if total else 0.0,"withholds":withholds,"per_task":per_task,"per_face":per_face}

def evaluate():
    pre=load("kernel/development/COGNITIVE_THEATER_RELATIONAL_GRAPH_FRESH3_PREFREEZE.json")
    count=evaluate_model(pre,"count"); unary_result=evaluate_model(pre,"unary"); pairwise=evaluate_model(pre,"pairwise")
    return {
      "schema":"Venus.CognitiveTheaterRelationalGraphFresh3Result.v0.1",
      "status":"RETURNED_FRESH3_LOCAL_DEVELOPMENTAL_COMPARISON",
      "issue_ref":206,
      "count_only":count,
      "unary_ordered":unary_result,
      "pairwise_relational":pairwise,
      "pairwise_minus_count":pairwise["accuracy"]-count["accuracy"],
      "pairwise_minus_unary":pairwise["accuracy"]-unary_result["accuracy"],
      "independent_external_evaluation":False,
      "general_theater_claim":False,
      "internalization_claim":False,
      "promotion_authority":False,
      "truth_authority":False,
    }

if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
