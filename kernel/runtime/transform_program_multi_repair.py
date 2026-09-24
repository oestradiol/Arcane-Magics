from __future__ import annotations

"""Generic bounded composition of independently returned TransformProgram repairs.

This layer does not invent patch semantics. It groups returned behavioral traces
by unresolved state/action pair, delegates each pair to the generic repair
search, and composes only uniquely identified patches up to a state-owned
max_patch_count.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .transform_program import program_digest
from .transform_program_repair_search import (
    BehavioralTrace,
    search_transition_repair,
)
from .transform_program_successor import ProgramPatch, apply_successor_patch


@dataclass(frozen=True)
class MultiRepairOutcome:
    status: str
    unresolved_pair_count: int
    max_patch_count: int
    selected_patches: tuple[Mapping[str, Any], ...]
    successor_program_digest: str | None
    promotion_authority: bool


def search_composed_repairs(
    parent: Mapping[str, Any],
    traces: Iterable[BehavioralTrace],
    *,
    allowed_patch_ops: Iterable[str],
    max_patch_count: int,
) -> MultiRepairOutcome:
    rows = tuple(traces)
    groups: dict[tuple[str, str], list[BehavioralTrace]] = {}
    for trace in rows:
        groups.setdefault((trace.prior_state, trace.action), []).append(trace)

    pair_count = len(groups)
    if pair_count == 0:
        return MultiRepairOutcome(
            "WITHHOLD_NO_RETURNED_PRESSURE", 0, max_patch_count, (), None, False
        )
    if pair_count > max_patch_count:
        return MultiRepairOutcome(
            "WITHHOLD_COMPOSITION_DEPTH_INSUFFICIENT",
            pair_count,
            max_patch_count,
            (),
            None,
            False,
        )

    patches: list[ProgramPatch] = []
    serialized: list[Mapping[str, Any]] = []
    for key in sorted(groups):
        result = search_transition_repair(
            parent,
            groups[key],
            allowed_patch_ops=allowed_patch_ops,
        )
        if result.status != "UNIQUE_MINIMAL_PATCH" or result.selected_patch is None:
            return MultiRepairOutcome(
                "WITHHOLD_COMPONENT_REPAIR_NOT_UNIQUE",
                pair_count,
                max_patch_count,
                (),
                None,
                False,
            )
        item = result.selected_patch
        patch = ProgramPatch(
            op=str(item["op"]),
            match_from=item.get("match_from"),
            match_action=item.get("match_action"),
            transition=item.get("transition") or None,
        )
        patches.append(patch)
        serialized.append(dict(item))

    successor, _ = apply_successor_patch(
        parent,
        tuple(patches),
        author_id="venus-generic-composed-repair-search",
    )

    # Re-check all returned traces against the composed successor through the
    # same pair search semantics by requiring each component to have been unique.
    return MultiRepairOutcome(
        "UNIQUE_COMPOSED_REPAIR_CANDIDATE",
        pair_count,
        max_patch_count,
        tuple(serialized),
        program_digest(successor),
        False,
    )
