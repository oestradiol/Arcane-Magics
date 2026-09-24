from __future__ import annotations

"""Minimal successor constructor for writable Venus TransformPrograms.

The learner authors the patch. This module only applies a small deterministic
patch language, preserves parent identity, and blocks edits to the external
safety-floor declaration.
"""

from dataclasses import dataclass
import copy
from typing import Any, Iterable, Mapping

from .transform_program import program_digest
from .vmk2 import digest


class TransformSuccessorError(ValueError):
    pass


@dataclass(frozen=True)
class ProgramPatch:
    op: str
    match_from: str | None = None
    match_action: str | None = None
    transition: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ProgramSuccessorReceipt:
    receipt_id: str
    parent_program_digest: str
    successor_program_digest: str
    author_id: str
    patch_digest: str
    patch_count: int
    safety_floor_unchanged: bool
    promotion_authority: bool


def _transition_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return str(row.get("from")), str(row.get("action"))


def apply_successor_patch(
    parent: Mapping[str, Any],
    patches: Iterable[ProgramPatch],
    *,
    author_id: str,
) -> tuple[dict[str, Any], ProgramSuccessorReceipt]:
    if not author_id:
        raise TransformSuccessorError("author_id required")
    rows = tuple(patches)
    if not rows:
        raise TransformSuccessorError("empty successor patch")

    successor = copy.deepcopy(dict(parent))
    original_floor = copy.deepcopy(parent.get("non_internalizable_runtime_invariants", []))
    transitions = list(successor.get("transitions", []))

    for patch in rows:
        if patch.op == "ADD_TRANSITION":
            if patch.transition is None:
                raise TransformSuccessorError("ADD_TRANSITION requires transition")
            new = dict(patch.transition)
            if not new.get("from") or not new.get("action") or not new.get("to"):
                raise TransformSuccessorError("transition requires from/action/to")
            key = _transition_key(new)
            if any(_transition_key(x) == key for x in transitions):
                raise TransformSuccessorError(f"transition already exists: {key}")
            transitions.append(new)
        elif patch.op == "REMOVE_TRANSITION":
            key = (patch.match_from, patch.match_action)
            kept = [x for x in transitions if _transition_key(x) != key]
            if len(kept) == len(transitions):
                raise TransformSuccessorError(f"transition not found: {key}")
            transitions = kept
        elif patch.op == "REPLACE_TRANSITION":
            if patch.transition is None:
                raise TransformSuccessorError("REPLACE_TRANSITION requires transition")
            key = (patch.match_from, patch.match_action)
            hits = [i for i, x in enumerate(transitions) if _transition_key(x) == key]
            if len(hits) != 1:
                raise TransformSuccessorError(f"transition match not unique: {key}")
            new = dict(patch.transition)
            if not new.get("from") or not new.get("action") or not new.get("to"):
                raise TransformSuccessorError("replacement requires from/action/to")
            transitions[hits[0]] = new
        else:
            raise TransformSuccessorError(f"unsupported patch op: {patch.op}")

    successor["transitions"] = transitions
    successor["authority"] = "LEARNER_AUTHORED_SUCCESSOR_CANDIDATE"
    successor["claim_bearing"] = False
    successor["promotion_authority"] = False
    successor["parent_program_digest"] = program_digest(parent)
    successor["successor_author_id"] = author_id

    if successor.get("non_internalizable_runtime_invariants", []) != original_floor:
        raise TransformSuccessorError("successor may not modify non-internalizable runtime invariants")

    patch_obj = [
        {
            "op": p.op,
            "match_from": p.match_from,
            "match_action": p.match_action,
            "transition": None if p.transition is None else dict(p.transition),
        }
        for p in rows
    ]
    body = {
        "parent_program_digest": program_digest(parent),
        "successor_program_digest": program_digest(successor),
        "author_id": author_id,
        "patch_digest": digest(patch_obj),
        "patch_count": len(rows),
        "safety_floor_unchanged": True,
        "promotion_authority": False,
    }
    receipt = ProgramSuccessorReceipt(receipt_id=digest(body), **body)
    return successor, receipt
