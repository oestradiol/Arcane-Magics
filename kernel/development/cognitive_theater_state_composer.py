from __future__ import annotations

"""Capability-specific scaffold for Fresh6 explicit cognitive-Theater state composition.

The learner receives opaque task/role identifiers, training surfaces, and
teacher-authored state programs as data. Evaluation supplies only face_id and
raw surface. The scaffold chooses an opaque learned microtheater, binds opaque
centers, then instantiates Venus.CognitiveTheaterState.v0.1.

This is not runtime authority and not an Internalizer result. Source removal is
a later burden.
"""

from difflib import SequenceMatcher
from itertools import permutations
import re
from typing import Any, Mapping

TOKEN_RE = re.compile(r"[@#][A-Za-z]+")
UNIT_SPLIT_RE = re.compile(r"(?:[.;。]+|\s*∧\s*)")


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def _tokens(text: str) -> tuple[str, ...]:
    out: list[str] = []
    for token in TOKEN_RE.findall(str(text)):
        if token not in out:
            out.append(token)
    return tuple(out)


def _units(text: str) -> tuple[str, ...]:
    return tuple(_norm(x) for x in UNIT_SPLIT_RE.split(str(text)) if _norm(x))


def _signature(
    text: str,
    *,
    roles: tuple[str, ...],
    binding: Mapping[str, str],
) -> tuple[str, ...]:
    markers = {binding[role]: f"<R{i}>" for i, role in enumerate(roles)}
    # The sequence inside a local relation remains visible, but unit
    # presentation order is quotiented for this bounded family.
    return tuple(
        sorted(
            _norm(TOKEN_RE.sub(lambda m: markers.get(m.group(0), "<OTHER>"), unit))
            for unit in _units(text)
        )
    )


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def _align(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        return _align(b, a)
    best = 0.0
    for perm in permutations(b, len(a)):
        score = sum(_sim(x, y) for x, y in zip(a, perm)) / max(len(a), len(b))
        best = max(best, score)
    return best


def _resolve(value: Any, binding: Mapping[str, str]) -> Any:
    if isinstance(value, str) and value in binding:
        return binding[value]
    if isinstance(value, list):
        return [_resolve(x, binding) for x in value]
    if isinstance(value, dict):
        return {k: _resolve(v, binding) for k, v in value.items()}
    return value


def materialize_state(
    program: Mapping[str, Any],
    binding: Mapping[str, str],
) -> dict[str, Any]:
    participants = [
        binding[role] for role in program.get("participant_roles", [])
    ] + [str(x) for x in program.get("static_participants", [])]

    local_kfs: dict[str, dict[str, str]] = {}
    for key, kfs in program.get("initial_kfs", {}).items():
        participant = binding[key] if key in binding else str(key)
        local_kfs[participant] = {str(p): str(s) for p, s in kfs.items()}

    events = []
    for event in program.get("events", []):
        if "event_id_role" in event:
            event_id = binding[str(event["event_id_role"])]
        else:
            event_id = str(event["event_id"])

        actor_role = event.get("actor_role")
        actor = binding[actor_role] if actor_role in binding else actor_role

        visible_to = [
            binding[x] if x in binding else str(x)
            for x in event.get("visible_to", [])
        ]
        effects = []
        for effect in event.get("effects", []):
            key = str(effect["participant"])
            effects.append(
                {
                    "participant": binding[key] if key in binding else key,
                    "proposition": str(effect["proposition"]),
                    "status": str(effect["status"]),
                }
            )
        events.append(
            {
                "event_id": event_id,
                "actor": actor,
                "relation": event.get("relation"),
                "objects": [_resolve(x, binding) for x in event.get("objects", [])],
                "visible_to": visible_to,
                "effects": effects,
            }
        )

    return {
        "schema": "Venus.CognitiveTheaterState.v0.1",
        "participants": participants,
        "local_kfs": local_kfs,
        "events": events,
        "residuals": list(program.get("residuals", [])),
    }


def learn_state(prefreeze: Mapping[str, Any]) -> dict[str, Any]:
    tasks: dict[str, Any] = {}
    for task in prefreeze["tasks"]:
        task_id = str(task["task_id"])
        roles = tuple(str(x) for x in task["output_schema"].keys())
        faces: dict[str, tuple[tuple[str, ...], ...]] = {}
        # Deliberately consume training examples only.
        for face, rows in task["train_examples"].items():
            faces[str(face)] = tuple(
                _signature(
                    str(row["surface"]),
                    roles=roles,
                    binding={str(k): str(v) for k, v in row["gold"].items()},
                )
                for row in rows
            )
        tasks[task_id] = {
            "roles": roles,
            "faces": faces,
            "state_program": dict(task["state_program"]),
        }

    return {
        "schema": "Venus.ExplicitCognitiveTheaterComposerState.v0.1",
        "tasks": tasks,
        "presentation_order_semantic": False,
        "state_programs_are_teacher_scaffold": True,
    }


def predict(
    state: Mapping[str, Any],
    *,
    face: str,
    surface: str,
    min_margin: float = 0.005,
) -> dict[str, Any]:
    if state.get("schema") != "Venus.ExplicitCognitiveTheaterComposerState.v0.1":
        raise ValueError("unsupported explicit-Theater composer state")

    centers = _tokens(surface)
    ranked = []
    for task_id, task in state["tasks"].items():
        roles = tuple(task["roles"])
        if len(centers) != len(roles):
            continue
        face_templates = task["faces"].get(face)
        if not face_templates:
            continue
        for perm in permutations(centers):
            binding = {role: token for role, token in zip(roles, perm)}
            signature = _signature(surface, roles=roles, binding=binding)
            score = max(
                (_align(signature, template) for template in face_templates),
                default=0.0,
            )
            ranked.append(
                (
                    score,
                    str(task_id),
                    tuple(perm),
                    binding,
                    signature,
                    task["state_program"],
                )
            )

    if not ranked:
        return {
            "status": "WITHHOLD_NO_ADMISSIBLE_THEATER",
            "task_id": None,
            "binding": None,
            "state": None,
            "assignment_margin": 0.0,
        }

    ranked.sort(key=lambda x: (-x[0], x[1], x[2]))
    best = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = best[0] - second

    if best[0] <= 0.0 or margin < min_margin:
        return {
            "status": "WITHHOLD_EXPLICIT_THEATER_AMBIGUOUS",
            "task_id": None,
            "binding": None,
            "state": None,
            "assignment_margin": margin,
        }

    theater_state = materialize_state(best[5], best[3])
    return {
        "status": "PREDICTED_EXPLICIT_COGNITIVE_THEATER_STATE",
        "task_id": best[1],
        "binding": best[3],
        "state": theater_state,
        "operator_signature": best[4],
        "assignment_margin": margin,
    }
