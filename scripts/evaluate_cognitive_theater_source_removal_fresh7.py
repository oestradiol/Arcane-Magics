from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    if spec is None or spec.loader is None:
        raise RuntimeError(rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


theater = load_module("fresh7_theater_eval", "kernel/development/cognitive_theater_state.py")


def resolve(value, binding):
    if isinstance(value, str) and value in binding:
        return binding[value]
    if isinstance(value, list):
        return [resolve(x, binding) for x in value]
    if isinstance(value, dict):
        return {k: resolve(v, binding) for k, v in value.items()}
    return value


def evaluator_materialize(state, task_id: str, binding):
    task = state["tasks"][task_id]
    program = task["state_program"]
    participants = [
        binding[role] for role in program.get("participant_roles", [])
    ] + [str(x) for x in program.get("static_participants", [])]

    local = {}
    for key, values in (program.get("initial_kfs") or {}).items():
        participant = binding[key] if key in binding else str(key)
        local[participant] = {str(k): str(v) for k, v in values.items()}

    events = []
    for event in program.get("events", []):
        event_id = (
            binding[str(event["event_id_role"])]
            if "event_id_role" in event
            else str(event["event_id"])
        )
        actor_role = event.get("actor_role")
        actor = binding[actor_role] if actor_role in binding else actor_role
        visible = [
            binding[x] if x in binding else str(x)
            for x in event.get("visible_to", [])
        ]
        effects = []
        for effect in event.get("effects", []):
            key = str(effect["participant"])
            effects.append({
                "participant": binding[key] if key in binding else key,
                "proposition": str(effect["proposition"]),
                "status": str(effect["status"]),
            })
        events.append({
            "event_id": event_id,
            "actor": actor,
            "relation": event.get("relation"),
            "objects": [resolve(x, binding) for x in event.get("objects", [])],
            "visible_to": visible,
            "effects": effects,
        })

    return {
        "schema": state["output_state_schema"],
        "participants": participants,
        "local_kfs": local,
        "events": events,
        "residuals": list(program.get("residuals", [])),
    }


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def run_isolated(state, public_rows):
    runtime_src = (ROOT / "kernel/runtime/structured_template_machine.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="fresh7-source-removal-") as td:
        root = Path(td)
        (root / "structured_template_machine.py").write_text(runtime_src, encoding="utf-8")
        (root / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        (root / "rows.json").write_text(json.dumps(public_rows, ensure_ascii=False), encoding="utf-8")
        driver = """from __future__ import annotations
import json
from pathlib import Path
import structured_template_machine as machine

state=json.loads(Path("state.json").read_text(encoding="utf-8"))
rows=json.loads(Path("rows.json").read_text(encoding="utf-8"))
out=[]
for row in rows:
    pred=machine.predict(state,context=row["context"],surface=row["surface"])
    out.append({"id":row["id"],"prediction":pred})
print(json.dumps(out,ensure_ascii=False,sort_keys=True))
"""
        (root / "driver.py").write_text(driver, encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
        }
        proc = subprocess.run(
            [sys.executable, "-I", "driver.py"],
            cwd=root,
            env=env,
            check=True,
            text=True,
            capture_output=True,
        )
        files = sorted(p.name for p in root.iterdir())
        return json.loads(proc.stdout), files


def evaluate():
    pre = load("kernel/development/COGNITIVE_THEATER_SOURCE_REMOVAL_FRESH7_PREFREEZE.json")
    state = load("kernel/development/COGNITIVE_THEATER_STATE_OWNERSHIP_CANDIDATE.json")

    public_rows = [
        {"id": row["id"], "context": row["context"], "surface": row["surface"]}
        for row in pre["rows"]
    ]
    returned, bundle_files = run_isolated(state, public_rows)
    by_id = {row["id"]: row["prediction"] for row in returned}

    total = len(pre["rows"])
    task_binding_correct = 0
    state_correct = 0
    withholds = 0
    per_context = {}
    per_task = {}
    gauge = {}
    rows = []

    for row in pre["rows"]:
        pred = by_id[row["id"]]
        expected = evaluator_materialize(state, row["task_id"], row["gold"])
        theater.validate(expected)
        if pred["state"] is not None:
            theater.validate(pred["state"])

        task_ok = pred["task_id"] == row["task_id"] and pred["binding"] == row["gold"]
        state_ok = pred["state"] is not None and canon(pred["state"]) == canon(expected)
        task_binding_correct += int(task_ok)
        state_correct += int(state_ok)
        withholds += int(pred["state"] is None)

        per_context.setdefault(row["context"], {"correct": 0, "total": 0, "withholds": 0})
        per_context[row["context"]]["correct"] += int(state_ok)
        per_context[row["context"]]["total"] += 1
        per_context[row["context"]]["withholds"] += int(pred["state"] is None)

        per_task.setdefault(row["task_id"], {"correct": 0, "total": 0, "withholds": 0})
        per_task[row["task_id"]]["correct"] += int(state_ok)
        per_task[row["task_id"]]["total"] += 1
        per_task[row["task_id"]]["withholds"] += int(pred["state"] is None)

        gauge.setdefault(row["gauge_pair"], []).append(
            canon(pred["state"]) if pred["state"] is not None else None
        )
        rows.append({
            "id": row["id"],
            "context": row["context"],
            "task_id": row["task_id"],
            "predicted_task_id": pred["task_id"],
            "task_binding_correct": task_ok,
            "state_correct": state_ok,
            "withhold": pred["state"] is None,
            "margin": pred["assignment_margin"],
        })

    for bucket in (per_context, per_task):
        for stats in bucket.values():
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] else 0.0

    gauge_same = sum(
        1
        for vals in gauge.values()
        if len(vals) >= 2 and vals[0] is not None and all(v == vals[0] for v in vals[1:])
    )

    runtime_src = (ROOT / "kernel/runtime/structured_template_machine.py").read_text(encoding="utf-8").casefold()
    forbidden_runtime_markers = [
        "english",
        "japanese",
        "brazilian_portuguese",
        "mathematics",
        "theater",
        "#206",
        "cognitive_theater_state_composer",
        "foundational_cognitive_theater",
        "kernel.development",
    ]
    runtime_marker_hits = [x for x in forbidden_runtime_markers if x in runtime_src]

    forbidden_bundle = {
        Path(x).name for x in pre["forbidden_execution_bundle"]
    }
    bundle_forbidden_hits = sorted(forbidden_bundle & set(bundle_files))

    return {
        "schema": "Venus.CognitiveTheaterSourceRemovalFresh7Result.v0.1",
        "status": "RETURNED_FRESH7_ISOLATED_SOURCE_REMOVAL_COMPARISON",
        "issue_ref": 206,
        "rows": rows,
        "total": total,
        "task_binding_correct": task_binding_correct,
        "task_binding_accuracy": task_binding_correct / total if total else 0.0,
        "state_correct": state_correct,
        "state_accuracy": state_correct / total if total else 0.0,
        "withholds": withholds,
        "gauge_pairs_total": len(gauge),
        "gauge_pairs_identical_state": gauge_same,
        "per_context": per_context,
        "per_task": per_task,
        "isolated_bundle_files": bundle_files,
        "forbidden_bundle_hits": bundle_forbidden_hits,
        "runtime_forbidden_marker_hits": runtime_marker_hits,
        "capability_specific_source_in_isolated_execution": bool(bundle_forbidden_hits or runtime_marker_hits),
        "source_removal_pass": (
            task_binding_correct == total
            and state_correct == total
            and gauge_same == len(gauge)
            and not bundle_forbidden_hits
            and not runtime_marker_hits
        ),
        "fresh_world_return_external": False,
        "independent_external_evaluation": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2, sort_keys=True))
