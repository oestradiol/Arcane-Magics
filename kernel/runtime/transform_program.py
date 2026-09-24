from __future__ import annotations

"""Minimal generic executor for writable Venus TransformPrograms.

The program is data. This module knows only how to:
- load and hash a program;
- validate a requested transition against that program;
- emit a deterministic transition receipt.

It does not choose targets, queries, dispositions, sources, or next actions.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .vmk2 import digest


class TransformProgramError(ValueError):
    pass


@dataclass(frozen=True)
class TransformReceipt:
    receipt_id: str
    program_digest: str
    program_id: str
    prior_state: str
    action: str
    next_state: str
    payload_digest: str
    actor_id: str


def load_program(path: str | Path) -> dict[str, Any]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("schema") != "Venus.TransformProgram.v0.1":
        raise TransformProgramError("unsupported TransformProgram schema")
    if not obj.get("program_id") or not obj.get("initial_state"):
        raise TransformProgramError("program_id and initial_state required")
    if not isinstance(obj.get("transitions"), list) or not obj["transitions"]:
        raise TransformProgramError("transitions required")
    return obj


def program_digest(program: Mapping[str, Any]) -> str:
    return digest(program)


def allowed_actions(program: Mapping[str, Any], state: str) -> tuple[str, ...]:
    return tuple(
        row["action"]
        for row in program["transitions"]
        if row.get("from") == state
    )


def step(
    program: Mapping[str, Any],
    *,
    state: str,
    action: str,
    payload: Mapping[str, Any],
    actor_id: str,
) -> TransformReceipt:
    if not actor_id:
        raise TransformProgramError("actor_id required")

    matches = [
        row
        for row in program["transitions"]
        if row.get("from") == state and row.get("action") == action
    ]
    if len(matches) != 1:
        allowed = allowed_actions(program, state)
        raise TransformProgramError(
            f"transition not admitted: state={state} action={action}; allowed={allowed}"
        )
    transition = matches[0]
    missing = tuple(
        field for field in transition.get("require", ())
        if field not in payload
    )
    if missing:
        raise TransformProgramError(f"transition payload missing fields: {missing}")

    pd = program_digest(program)
    body = {
        "program_digest": pd,
        "program_id": program["program_id"],
        "prior_state": state,
        "action": action,
        "next_state": transition["to"],
        "payload_digest": digest(dict(payload)),
        "actor_id": actor_id,
    }
    return TransformReceipt(receipt_id=digest(body), **body)
