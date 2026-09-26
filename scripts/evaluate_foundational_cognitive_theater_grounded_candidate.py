from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD_PATH=ROOT/"kernel/development/cognitive_theater_learner.py"
SPEC=importlib.util.spec_from_file_location("cognitive_theater_learner",MOD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load cognitive theater learner")
mod=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=mod
SPEC.loader.exec_module(mod)


def load(rel: str):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))


def teacher_templates(matched: dict) -> dict:
    return {row["relation_id"]:row for row in matched["structures"]}


def evaluate() -> dict:
    grounding=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_GROUNDING_CURRICULUM.json")
    matched=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_MATCHED_STRUCTURE.json")
    seed=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SEED.json")
    pre=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_FACTORIAL_PREFREEZE.json")
    baseline=load("kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_FACTORIAL_BASELINE_RESULT.json")

    state=mod.learn_state(grounding,teacher_templates(matched),n=3)
    relation_rows={row["relation_id"]:row for row in seed["relations"]}
    gold_templates=teacher_templates(matched)

    rows=[]
    correct=0
    template_exact=0
    withholds=0
    per_face={face:{"correct":0,"total":0,"withholds":0} for face in pre["faces"]}

    for fold_idx,fold in enumerate(pre["folds"]):
        for relation,face in fold:
            surface=relation_rows[relation]["surfaces"][face]["heldout"][0]
            pred=mod.predict(state,face=face,text=surface)
            ok=pred.relation_id==relation
            exact=bool(ok and pred.template==gold_templates[relation])
            correct+=int(ok)
            template_exact+=int(exact)
            withholds+=int(pred.relation_id is None)
            per_face[face]["total"]+=1
            per_face[face]["correct"]+=int(ok)
            per_face[face]["withholds"]+=int(pred.relation_id is None)
            rows.append({
                "fold":fold_idx,
                "relation_id":relation,
                "face":face,
                "prediction":pred.relation_id,
                "status":pred.status,
                "correct":ok,
                "template_exact":exact,
                "top_atoms":[list(x) for x in pred.atom_scores[:4]],
                "relation_scores":[list(x) for x in pred.relation_scores],
            })

    total=len(rows)
    acc=correct/total if total else 0.0
    return {
        "schema":"Venus.FoundationalCognitiveTheaterGroundedCandidateResult.v0.1",
        "status":"RETURNED_GROUNDED_TEMPLATE_CANDIDATE",
        "issue_ref":206,
        "candidate_scope":"G0_GROUNDING_PLUS_G1_TEMPLATE_RECONSTRUCTION_ONLY",
        "correct":correct,
        "total":total,
        "accuracy":acc,
        "template_exact":template_exact,
        "withholds":withholds,
        "surface_baseline_accuracy":baseline["accuracy"],
        "baseline_delta":acc-baseline["accuracy"],
        "per_face":per_face,
        "rows":rows,
        "surface_referent_binding_tested":False,
        "music_order_intervention_tested":False,
        "participant_kfs_intervention_tested":False,
        "internalization_claim":False,
        "language_competence_claim":False,
        "cultural_cognition_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
        "next_residual":"HOLD_LEXICAL_GROUNDING_FIXED_AND_TEST_PARTICIPANT_KFS_BINDING_PLUS_TEMPORAL_ORDER",
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
