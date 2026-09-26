from __future__ import annotations

import importlib.util
import json
import re
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mod(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    if spec is None or spec.loader is None:
        raise RuntimeError(rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


unary = mod("fresh5_unary", "kernel/development/cognitive_theater_ordered_binding.py")
pair = mod("fresh5_pair", "kernel/development/cognitive_theater_relational_graph.py")
joint = mod("fresh5_joint", "kernel/development/cognitive_theater_joint_scene.py")
local = mod("fresh5_local", "kernel/development/cognitive_theater_local_operator_graph.py")

TOKEN_RE = re.compile(r"[@#][A-Za-z]+")


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def unique_tokens(text: str) -> tuple[str, ...]:
    out = []
    for token in TOKEN_RE.findall(str(text)):
        if token not in out:
            out.append(token)
    return tuple(out)


def count_state(pre):
    out = {}
    for task in pre["tasks"]:
        tid = task["id"]
        roles = tuple(task["output_schema"])
        faces = {}
        for face, rows in task["train_examples"].items():
            by_role = {role: [] for role in roles}
            for row in rows:
                seq = TOKEN_RE.findall(row["surface"])
                for role, token in row["gold"].items():
                    by_role[role].append(seq.count(token))
            faces[face] = {
                role: sum(vals) / len(vals)
                for role, vals in by_role.items()
            }
        out[tid] = {"roles": roles, "faces": faces}
    return out


def count_predict(state, task_id: str, face: str, surface: str):
    roles = tuple(state[task_id]["roles"])
    centers = unique_tokens(surface)
    seq = TOKEN_RE.findall(surface)
    ranked = []
    for perm in permutations(centers):
        binding = {role: token for role, token in zip(roles, perm)}
        cost = sum(
            abs(seq.count(token) - state[task_id]["faces"][face][role])
            for role, token in binding.items()
        )
        ranked.append((cost, tuple(perm), binding))
    ranked.sort(key=lambda x: (x[0], x[1]))
    if len(ranked) > 1 and abs(ranked[0][0] - ranked[1][0]) < 1e-12:
        return None
    return ranked[0][2]


def evaluate_kind(pre, kind: str):
    count = count_state(pre) if kind == "count" else None
    state = (
        unary.learn_state(pre)
        if kind == "unary"
        else pair.learn_state(pre)
        if kind == "pair"
        else joint.learn_state(pre)
        if kind == "joint"
        else local.learn_state(pre)
        if kind == "local"
        else None
    )

    correct = total = withholds = 0
    per_task = {}
    per_face = {}
    for task in pre["tasks"]:
        tid = task["id"]
        per_task[tid] = {"correct": 0, "total": 0, "withholds": 0}
        for face, rows in task["heldout_examples"].items():
            per_face.setdefault(face, {"correct": 0, "total": 0, "withholds": 0})
            for row in rows:
                if kind == "count":
                    pred = count_predict(count, tid, face, row["surface"])
                elif kind == "unary":
                    pred = unary.predict(state, task_id=tid, face=face, surface=row["surface"])["binding"]
                elif kind == "pair":
                    pred = pair.predict(state, task_id=tid, face=face, surface=row["surface"])["binding"]
                elif kind == "joint":
                    pred = joint.predict(state, task_id=tid, face=face, surface=row["surface"])["binding"]
                else:
                    pred = local.predict(state, task_id=tid, face=face, surface=row["surface"])["binding"]

                ok = pred == row["gold"]
                total += 1
                correct += int(ok)
                withholds += int(pred is None)
                per_task[tid]["total"] += 1
                per_task[tid]["correct"] += int(ok)
                per_task[tid]["withholds"] += int(pred is None)
                per_face[face]["total"] += 1
                per_face[face]["correct"] += int(ok)
                per_face[face]["withholds"] += int(pred is None)

    for bucket in (per_task, per_face):
        for stats in bucket.values():
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] else 0.0

    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "withholds": withholds,
        "per_task": per_task,
        "per_face": per_face,
    }


def evaluate():
    pre = load("kernel/development/COGNITIVE_THEATER_LOCAL_OPERATOR_FRESH5_PREFREEZE.json")
    count = evaluate_kind(pre, "count")
    unary_result = evaluate_kind(pre, "unary")
    pair_result = evaluate_kind(pre, "pair")
    joint_result = evaluate_kind(pre, "joint")
    local_result = evaluate_kind(pre, "local")
    return {
        "schema": "Venus.CognitiveTheaterLocalOperatorFresh5Result.v0.1",
        "status": "RETURNED_FRESH5_LOCAL_DEVELOPMENTAL_COMPARISON",
        "issue_ref": 206,
        "count_only": count,
        "unary_ordered": unary_result,
        "pairwise_relational": pair_result,
        "joint_scene": joint_result,
        "local_operator_graph": local_result,
        "local_minus_count": local_result["accuracy"] - count["accuracy"],
        "local_minus_unary": local_result["accuracy"] - unary_result["accuracy"],
        "local_minus_pairwise": local_result["accuracy"] - pair_result["accuracy"],
        "local_minus_joint": local_result["accuracy"] - joint_result["accuracy"],
        "independent_external_evaluation": False,
        "general_theater_claim": False,
        "general_music_claim": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2, sort_keys=True))
