from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.development.lateral_episode import (
    relation_expanded_tokens,
    path_tokens,
    scale_tokens,
)

def sim(a,b):
    a=frozenset(a); b=frozenset(b)
    u=a|b
    return len(a&b)/len(u) if u else 0.0

def token_fn(face_set):
    faces=tuple(face_set)
    def fn(row):
        out=set()
        if "relation_expanded" in faces:
            out.update(relation_expanded_tokens(row))
        if "path_topology" in faces:
            out.update(path_tokens(row))
        if "change_scale" in faces:
            out.update(scale_tokens(row))
        return frozenset(out)
    return fn

def predict(train,row,fn,k,exclude=None):
    pool=[x for x in train if int(x["pr_number"])!=exclude]
    ranked=sorted(
        (-sim(fn(x),fn(row)),int(x["pr_number"]),bool(x["label"]))
        for x in pool
    )[:k]
    yes=sum(1 for _,_,lab in ranked if lab)
    no=len(ranked)-yes
    if yes==no:
        all_yes=sum(1 for x in pool if bool(x["label"]))
        all_no=len(pool)-all_yes
        if all_yes==all_no:
            return False
        return all_yes>all_no
    return yes>no

def loo(train,fn,k):
    correct=0
    for row in train:
        pred=predict(train,row,fn,k,exclude=int(row["pr_number"]))
        correct+=int(pred==bool(row["label"]))
    return correct/len(train)

def merge_training(ep1,reveal1,transfer,reveal_t):
    labels1={int(k):bool(v) for k,v in reveal1["holdout_labels"].items()}
    labelst={int(k):bool(v) for k,v in reveal_t["holdout_labels"].items()}
    rows=[]
    for row in ep1["train"]:
        rows.append({**row,"label":bool(row["train_label"])})
    for row in ep1["holdout"]:
        n=int(row["pr_number"])
        rows.append({**row,"label":labels1[n]})
    for row in transfer["rows"]:
        n=int(row["pr_number"])
        rows.append({**row,"label":labelst[n]})
    seen=set()
    dedup=[]
    for row in rows:
        n=int(row["pr_number"])
        if n in seen:
            raise SystemExit(f"duplicate accumulated training PR {n}")
        seen.add(n); dedup.append(row)
    return dedup

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--episode1-visible",required=True)
    p.add_argument("--episode1-reveal",required=True)
    p.add_argument("--transfer-visible",required=True)
    p.add_argument("--transfer-reveal",required=True)
    p.add_argument("--holdout-visible",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=json.loads((ROOT/args.prefreeze).read_text())
    ep1=json.loads((ROOT/args.episode1_visible).read_text())
    rev1=json.loads((ROOT/args.episode1_reveal).read_text())
    tr=json.loads((ROOT/args.transfer_visible).read_text())
    revt=json.loads((ROOT/args.transfer_reveal).read_text())
    hold=json.loads((ROOT/args.holdout_visible).read_text())

    expected=[int(x) for x in pre["fresh_holdout_universe"]["selected_pr_numbers"]]
    got=[int(x["pr_number"]) for x in hold["rows"]]
    if got!=expected:
        raise SystemExit("episode2 holdout differs from prefreeze")
    if hold.get("labels_present") is not False or hold.get("merged_state_present") is not False:
        raise SystemExit("episode2 labels leaked before prediction")

    train=merge_training(ep1,rev1,tr,revt)
    candidates=[]
    for faces in pre["revision_space"]["face_sets"]:
        fn=token_fn(faces)
        for k in pre["revision_space"]["k_values"]:
            if len(train)<int(k)+1:
                continue
            score=loo(train,fn,int(k))
            policy_id="+".join(faces)+f"|k={k}"
            candidates.append({
                "policy_id":policy_id,
                "faces":list(faces),
                "k":int(k),
                "loo_accuracy":score,
                "added_face_count":max(0,len(faces)-1),
            })
    selected=sorted(
        candidates,
        key=lambda x:(-x["loo_accuracy"],x["added_face_count"],x["k"],x["policy_id"])
    )[0]
    fn=token_fn(selected["faces"])
    preds={
        str(int(row["pr_number"])):bool(predict(train,row,fn,selected["k"]))
        for row in hold["rows"]
    }
    result={
        "schema":"Venus.LateralEpisode2Proposal.v0.1",
        "episode":2,
        "training_count":len(train),
        "candidate_scores":candidates,
        "selected_policy":selected,
        "holdout_predictions":preds,
        "holdout_labels_accessed":False,
        "fresh_holdout_count":len(preds),
        "internalization_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
        "claim_fence":"Proposal is a self-revised bounded policy selected from the prefrozen family using prior returned labels only. Fresh holdout labels remain hidden."
    }
    (ROOT/args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
