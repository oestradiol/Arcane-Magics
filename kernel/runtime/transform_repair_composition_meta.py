from __future__ import annotations

"""Target-blind meta-search over repair-composition depth."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .transform_program_multi_repair import search_composed_repairs
from .transform_program_repair_search import BehavioralTrace


@dataclass(frozen=True)
class CompositionDepthOutcome:
    status: str
    parent_max_patch_count: int
    selected_max_patch_count: int | None
    selected_patches: tuple[Mapping[str, Any], ...]
    promotion_authority: bool


def search_composition_depth(
    meta_program: Mapping[str, Any],
    transform_parent: Mapping[str, Any],
    traces: Iterable[BehavioralTrace],
) -> CompositionDepthOutcome:
    enabled_ops = tuple(meta_program.get("enabled_patch_ops", ()))
    parent_max = int(meta_program.get("max_patch_count", 1))
    available = tuple(
        sorted(set(int(x) for x in meta_program.get("available_patch_counts", (parent_max,))))
    )

    parent = search_composed_repairs(
        transform_parent,
        traces,
        allowed_patch_ops=enabled_ops,
        max_patch_count=parent_max,
    )
    if parent.status == "UNIQUE_COMPOSED_REPAIR_CANDIDATE":
        return CompositionDepthOutcome(
            "NO_COMPOSITION_EXPANSION_NEEDED",
            parent_max,
            None,
            parent.selected_patches,
            False,
        )

    viable = []
    for candidate_max in available:
        if candidate_max <= parent_max:
            continue
        result = search_composed_repairs(
            transform_parent,
            traces,
            allowed_patch_ops=enabled_ops,
            max_patch_count=candidate_max,
        )
        if result.status == "UNIQUE_COMPOSED_REPAIR_CANDIDATE":
            viable.append((candidate_max, result))

    if len(viable) == 1:
        depth, result = viable[0]
        return CompositionDepthOutcome(
            "UNIQUE_COMPOSITION_DEPTH_IMPROVEMENT",
            parent_max,
            depth,
            result.selected_patches,
            False,
        )
    if not viable:
        return CompositionDepthOutcome(
            "WITHHOLD_NO_VIABLE_COMPOSITION_DEPTH",
            parent_max,
            None,
            (),
            False,
        )
    return CompositionDepthOutcome(
        "WITHHOLD_AMBIGUOUS_COMPOSITION_DEPTH",
        parent_max,
        None,
        (),
        False,
    )
