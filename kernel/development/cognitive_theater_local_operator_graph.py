from __future__ import annotations

"""Generic local-operator graph binder for cognitive Theater Fresh5.

This scaffold deliberately separates:
- discourse presentation order, treated as non-semantic for this task family;
- local relation/operator structure inside each clause/unit;
- participant/event role binding across the composed scene.

No face, language word, task name, role name, or answer key is hard-coded.
Teacher data supplies opaque role schemas and examples. A later Internalizer
claim requires compiling any earned semantics into learner-owned state and
removing this capability-specific scaffold.
"""

from difflib import SequenceMatcher
from itertools import permutations
import re
from typing import Any, Mapping

TOKEN_RE = re.compile(r"[@#][A-Za-z]+")
UNIT_SPLIT_RE = re.compile(r"(?:[.;。]+|\s*∧\s*)")


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def opaque_tokens(text: str) -> tuple[str, ...]:
    out: list[str] = []
    for token in TOKEN_RE.findall(str(text)):
        if token not in out:
            out.append(token)
    return tuple(out)


def split_local_units(text: str) -> tuple[str, ...]:
    return tuple(_norm(x) for x in UNIT_SPLIT_RE.split(str(text)) if _norm(x))


def normalize_local_unit(
    unit: str,
    *,
    roles: tuple[str, ...],
    binding: Mapping[str, str],
) -> str:
    markers = {binding[role]: f"<R{i}>" for i, role in enumerate(roles)}
    return _norm(TOKEN_RE.sub(lambda m: markers.get(m.group(0), "<OTHER>"), unit))


def local_operator_signature(
    text: str,
    *,
    roles: tuple[str, ...],
    binding: Mapping[str, str],
) -> tuple[str, ...]:
    # Presentation order among discourse units is intentionally quotiented out.
    # Order *inside* a local operator remains available, so role direction and
    # nested/local relations are not reduced to a bag of tokens.
    return tuple(
        sorted(
            normalize_local_unit(unit, roles=roles, binding=binding)
            for unit in split_local_units(text)
        )
    )


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def _multiset_alignment(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    # Fresh5 scenes are intentionally tiny. Exact bounded matching keeps the
    # comparator transparent and avoids importing an opaque optimizer.
    if len(a) > len(b):
        return _multiset_alignment(b, a)

    best = 0.0
    for perm in permutations(b, len(a)):
        score = sum(_similarity(x, y) for x, y in zip(a, perm)) / max(len(a), len(b))
        if score > best:
            best = score
    return best


def learn_state(prefreeze: Mapping[str, Any]) -> dict[str, Any]:
    tasks: dict[str, Any] = {}
    for task in prefreeze["tasks"]:
        task_id = str(task["id"])
        roles = tuple(str(k) for k in task["output_schema"].keys())
        faces: dict[str, Any] = {}
        for face, rows in task["train_examples"].items():
            templates = []
            for row in rows:
                gold = {str(k): str(v) for k, v in row["gold"].items()}
                templates.append(
                    local_operator_signature(
                        str(row["surface"]),
                        roles=roles,
                        binding=gold,
                    )
                )
            faces[str(face)] = tuple(templates)
        tasks[task_id] = {"roles": roles, "faces": faces}
    return {
        "schema": "Venus.LocalOperatorTheaterGraphState.v0.1",
        "tasks": tasks,
        "presentation_order_semantic": False,
        "local_operator_internal_order_preserved": True,
    }


def predict(
    state: Mapping[str, Any],
    *,
    task_id: str,
    face: str,
    surface: str,
    min_margin: float = 0.001,
) -> dict[str, Any]:
    if state.get("schema") != "Venus.LocalOperatorTheaterGraphState.v0.1":
        raise ValueError("unsupported local-operator Theater state")

    task = state["tasks"][task_id]
    roles = tuple(task["roles"])
    centers = opaque_tokens(surface)
    if len(centers) != len(roles):
        return {
            "status": "WITHHOLD_TOKEN_CARDINALITY",
            "binding": None,
            "assignment_margin": 0.0,
            "operator_signature": None,
        }

    ranked = []
    for perm in permutations(centers):
        binding = {role: token for role, token in zip(roles, perm)}
        signature = local_operator_signature(surface, roles=roles, binding=binding)
        score = max(
            (_multiset_alignment(signature, template) for template in task["faces"][face]),
            default=0.0,
        )
        ranked.append((score, tuple(perm), binding, signature))

    ranked.sort(key=lambda x: (-x[0], x[1]))
    best = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = best[0] - second

    if best[0] <= 0.0 or margin < min_margin:
        return {
            "status": "WITHHOLD_LOCAL_OPERATOR_GRAPH_AMBIGUOUS",
            "binding": None,
            "assignment_margin": margin,
            "operator_signature": None,
        }

    return {
        "status": "PREDICTED_LOCAL_OPERATOR_THEATER_GRAPH",
        "binding": best[2],
        "assignment_margin": margin,
        "operator_signature": best[3],
    }
