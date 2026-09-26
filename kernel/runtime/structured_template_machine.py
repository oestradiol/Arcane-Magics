from __future__ import annotations

"""Generic executor for state-owned structured-template programs.

All domain semantics, tokenization patterns, context labels, opaque task/role
programs, thresholds, and output-state schema names arrive as data. The module
does not import any capability teacher, donor, curriculum, or project-specific
developmental scaffold.
"""

from difflib import SequenceMatcher
from itertools import permutations
import re
from typing import Any, Mapping


class StructuredTemplateError(ValueError):
    pass


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def _compiled(state: Mapping[str, Any]):
    contract = state.get("executor_contract") or {}
    token_pattern = str(contract.get("token_pattern") or "")
    unit_split_pattern = str(contract.get("unit_split_pattern") or "")
    if not token_pattern or not unit_split_pattern:
        raise StructuredTemplateError("state-owned token and unit patterns required")
    try:
        return re.compile(token_pattern), re.compile(unit_split_pattern)
    except re.error as exc:
        raise StructuredTemplateError("invalid state-owned regex pattern") from exc


def _tokens(state: Mapping[str, Any], text: str) -> tuple[str, ...]:
    token_re, _ = _compiled(state)
    out: list[str] = []
    for token in token_re.findall(str(text)):
        if token not in out:
            out.append(token)
    return tuple(out)


def _units(state: Mapping[str, Any], text: str) -> tuple[str, ...]:
    _, split_re = _compiled(state)
    return tuple(_norm(x) for x in split_re.split(str(text)) if _norm(x))


def _signature(
    state: Mapping[str, Any],
    text: str,
    *,
    roles: tuple[str, ...],
    binding: Mapping[str, str],
) -> tuple[str, ...]:
    token_re, _ = _compiled(state)
    markers = {binding[role]: f"<R{i}>" for i, role in enumerate(roles)}
    units = tuple(
        _norm(token_re.sub(lambda m: markers.get(m.group(0), "<OTHER>"), unit))
        for unit in _units(state, text)
    )
    if bool((state.get("executor_contract") or {}).get("presentation_order_semantic")):
        return units
    return tuple(sorted(units))


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


def materialize(
    state: Mapping[str, Any],
    program: Mapping[str, Any],
    binding: Mapping[str, str],
) -> dict[str, Any]:
    output_schema = str(state.get("output_state_schema") or "")
    if not output_schema:
        raise StructuredTemplateError("output_state_schema required")

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
            "objects": [_resolve(x, binding) for x in event.get("objects", [])],
            "visible_to": visible,
            "effects": effects,
        })

    return {
        "schema": output_schema,
        "participants": participants,
        "local_kfs": local,
        "events": events,
        "residuals": list(program.get("residuals", [])),
    }


def predict(
    state: Mapping[str, Any],
    *,
    context: str,
    surface: str,
) -> dict[str, Any]:
    if state.get("schema") != "Venus.StateOwnedStructuredTemplateProgram.v0.1":
        raise StructuredTemplateError("unsupported state-owned template schema")
    tasks = state.get("tasks") or {}
    if not tasks:
        raise StructuredTemplateError("state-owned tasks required")

    centers = _tokens(state, surface)
    ranked = []
    for task_id, task in tasks.items():
        roles = tuple(str(x) for x in task.get("roles", []))
        if len(centers) != len(roles):
            continue
        templates = (task.get("contexts") or {}).get(context)
        if not templates:
            continue
        for perm in permutations(centers):
            binding = {role: token for role, token in zip(roles, perm)}
            sig = _signature(state, surface, roles=roles, binding=binding)
            score = max(
                (_align(sig, tuple(template)) for template in templates),
                default=0.0,
            )
            ranked.append((
                score,
                str(task_id),
                tuple(perm),
                binding,
                sig,
                task["state_program"],
            ))

    if not ranked:
        return {
            "status": "WITHHOLD_NO_ADMISSIBLE_PROGRAM",
            "task_id": None,
            "binding": None,
            "state": None,
            "assignment_margin": 0.0,
        }

    ranked.sort(key=lambda x: (-x[0], x[1], x[2]))
    best = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = best[0] - second
    threshold = float((state.get("executor_contract") or {}).get("min_margin", 0.0))

    if best[0] <= 0.0 or margin < threshold:
        return {
            "status": "WITHHOLD_STRUCTURED_TEMPLATE_AMBIGUOUS",
            "task_id": None,
            "binding": None,
            "state": None,
            "assignment_margin": margin,
        }

    return {
        "status": "PREDICTED_STATE_FROM_STATE_OWNED_PROGRAM",
        "task_id": best[1],
        "binding": best[3],
        "state": materialize(state, best[5], best[3]),
        "operator_signature": best[4],
        "assignment_margin": margin,
    }
