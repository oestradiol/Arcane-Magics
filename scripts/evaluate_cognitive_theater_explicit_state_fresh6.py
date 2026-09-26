from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mod(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    if spec is None or spec.loader is None:
        raise RuntimeError(rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


composer = mod("fresh6_composer", "kernel/development/cognitive_theater_state_composer.py")
theater = mod("fresh6_theater", "kernel/development/cognitive_theater_state.py")
joint = mod("fresh6_joint", "kernel/development/cognitive_theater_joint_scene.py")


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def expected_state(task, binding):
    return composer.materialize_state(task["state_program"], binding)


def canonical_state(state):
    return json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def global_joint_state(prefreeze):
    """Build a comparator that knows all opaque task IDs but receives no task ID at eval."""
    tasks = {}
    for task in prefreeze["tasks"]:
        tid = task["task_id"]
        shim = {
            "tasks": [{
                "id": tid,
                "output_schema": task["output_schema"],
                "train_examples": task["train_examples"],
                "heldout_examples": {},
            }]
        }
        tasks[tid] = joint.learn_state(shim)["tasks"][tid]
    return {"schema": "Fresh6.GlobalJointComparator.v0.1", "tasks": tasks}


def global_joint_predict(state, *, face: str, surface: str, min_margin: float = 0.005):
    # Use the current joint-scene normalizer, but task identity is hidden.
    ranked = []
    for tid, task in state["tasks"].items():
        shim = {
            "schema": "Venus.JointRoleNormalizedSceneState.v0.1",
            "tasks": {tid: task},
        }
        pred = joint.predict(
            shim,
            task_id=tid,
            face=face,
            surface=surface,
            min_margin=0.0,
        )
        if pred["binding"] is None:
            continue

        # Reconstruct the candidate's score directly from its normalized scene.
        roles = tuple(task["roles"])
        normalized = joint.normalize_scene(surface, roles=roles, binding=pred["binding"])
        score = max(
            (joint.sim(normalized, proto) for proto in task["faces"][face]),
            default=0.0,
        )
        ranked.append((score, tid, pred["binding"]))

    if not ranked:
        return {"task_id": None, "binding": None, "margin": 0.0}

    ranked.sort(key=lambda x: (-x[0], x[1], tuple(sorted(x[2].items()))))
    best = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = best[0] - second
    if margin < min_margin:
        return {"task_id": None, "binding": None, "margin": margin}
    return {"task_id": best[1], "binding": best[2], "margin": margin}


def evaluate():
    pre = load("kernel/development/COGNITIVE_THEATER_EXPLICIT_STATE_FRESH6_PREFREEZE.json")
    learned = composer.learn_state(pre)
    joint_state = global_joint_state(pre)

    rows = []
    explicit_correct = 0
    task_binding_correct = 0
    joint_task_binding_correct = 0
    total = 0
    withholds = 0
    gauge = {}
    per_face = {}
    per_task = {}

    task_index = {task["task_id"]: task for task in pre["tasks"]}

    for task in pre["tasks"]:
        tid = task["task_id"]
        per_task[tid] = {"correct_state": 0, "correct_task_binding": 0, "total": 0, "withholds": 0}
        for face, heldout in task["heldout_examples"].items():
            per_face.setdefault(face, {"correct_state": 0, "correct_task_binding": 0, "total": 0, "withholds": 0})
            for row in heldout:
                pred = composer.predict(learned, face=face, surface=row["surface"])
                joint_pred = global_joint_predict(joint_state, face=face, surface=row["surface"])

                expected = expected_state(task, row["gold"])
                state_ok = pred["state"] is not None and canonical_state(pred["state"]) == canonical_state(expected)
                task_binding_ok = pred["task_id"] == tid and pred["binding"] == row["gold"]
                joint_ok = joint_pred["task_id"] == tid and joint_pred["binding"] == row["gold"]
                total += 1
                explicit_correct += int(state_ok)
                task_binding_correct += int(task_binding_ok)
                joint_task_binding_correct += int(joint_ok)
                withholds += int(pred["state"] is None)

                per_task[tid]["correct_state"] += int(state_ok)
                per_task[tid]["correct_task_binding"] += int(task_binding_ok)
                per_task[tid]["total"] += 1
                per_task[tid]["withholds"] += int(pred["state"] is None)

                per_face[face]["correct_state"] += int(state_ok)
                per_face[face]["correct_task_binding"] += int(task_binding_ok)
                per_face[face]["total"] += 1
                per_face[face]["withholds"] += int(pred["state"] is None)

                if pred["state"] is not None:
                    theater.validate(pred["state"])

                gauge.setdefault(row["gauge_pair_id"], []).append(
                    canonical_state(pred["state"]) if pred["state"] is not None else None
                )

                rows.append({
                    "task_id": tid,
                    "face": face,
                    "surface": row["surface"],
                    "predicted_task_id": pred["task_id"],
                    "task_binding_correct": task_binding_ok,
                    "explicit_state_correct": state_ok,
                    "joint_task_binding_correct": joint_ok,
                    "withhold": pred["state"] is None,
                    "margin": pred["assignment_margin"],
                })

    for bucket in (per_task, per_face):
        for stats in bucket.values():
            denom = stats["total"]
            stats["state_accuracy"] = stats["correct_state"] / denom if denom else 0.0
            stats["task_binding_accuracy"] = stats["correct_task_binding"] / denom if denom else 0.0

    gauge_pairs_total = len(gauge)
    gauge_pairs_same = sum(
        1 for vals in gauge.values()
        if len(vals) >= 2 and vals[0] is not None and all(v == vals[0] for v in vals[1:])
    )

    # KFS intervention: change one returned effect and require endpoint change.
    kfs_interventions = []
    for tid in ("T0", "T1"):
        task = task_index[tid]
        first_face = next(iter(task["heldout_examples"]))
        row = task["heldout_examples"][first_face][0]
        base = expected_state(task, row["gold"])
        mutated = copy.deepcopy(base)

        # Intervene on the last effective write so the prefrozen endpoint
        # discriminator measures a causally live KFS consequence rather than an
        # earlier write that is legitimately overwritten by later history.
        target = None
        for event in reversed(mutated["events"]):
            effects = event.get("effects") or []
            if effects:
                target = effects[-1]
                break
        if target is None:
            raise RuntimeError(f"{tid} has no KFS effect for intervention")
        old = target["status"]
        target["status"] = "KNOWN_FALSE" if old != "KNOWN_FALSE" else "KNOWN_TRUE"

        theater.validate(base)
        theater.validate(mutated)
        kfs_interventions.append({
            "task_id": tid,
            "endpoint_changed": not theater.same_endpoint(base, mutated),
        })

    # Event-history intervention: reverse events for T2. Endpoint is intentionally
    # invariant because T2 carries temporal structure in event history, not KFS effects.
    task = task_index["T2"]
    first_face = next(iter(task["heldout_examples"]))
    row = task["heldout_examples"][first_face][0]
    base = expected_state(task, row["gold"])
    reversed_state = copy.deepcopy(base)
    reversed_state["events"] = list(reversed(reversed_state["events"]))
    theater.validate(base)
    theater.validate(reversed_state)
    history_intervention = {
        "same_endpoint": theater.same_endpoint(base, reversed_state),
        "history_changed": not theater.same_history(base, reversed_state),
    }

    explicit_acc = explicit_correct / total if total else 0.0
    task_binding_acc = task_binding_correct / total if total else 0.0
    joint_acc = joint_task_binding_correct / total if total else 0.0
    return {
        "schema": "Venus.CognitiveTheaterExplicitStateFresh6Result.v0.1",
        "status": "RETURNED_FRESH6_EXPLICIT_STATE_COMPARISON",
        "issue_ref": 206,
        "rows": rows,
        "total": total,
        "explicit_state_correct": explicit_correct,
        "explicit_state_accuracy": explicit_acc,
        "task_binding_correct": task_binding_correct,
        "task_binding_accuracy": task_binding_acc,
        "joint_task_binding_correct": joint_task_binding_correct,
        "joint_task_binding_accuracy": joint_acc,
        "withholds": withholds,
        "gauge_pairs_total": gauge_pairs_total,
        "gauge_pairs_identical_state": gauge_pairs_same,
        "kfs_interventions": kfs_interventions,
        "history_intervention": history_intervention,
        "per_task": per_task,
        "per_face": per_face,
        "task_id_visible_at_evaluation": False,
        "relation_id_visible_at_evaluation": False,
        "teacher_state_target_visible_at_evaluation": False,
        "independent_external_evaluation": False,
        "source_removal_pass": False,
        "general_theater_claim": False,
        "general_music_claim": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2, sort_keys=True))
