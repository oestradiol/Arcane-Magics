from __future__ import annotations

"""Generic meta-search over the state-owned TransformProgram repair grammar.

A parent repair grammar may enable only a subset of already available primitive
patch operations. If returned behavioral evidence is not repairable under the
enabled subset, this search tests one-operation grammar expansions.

It contains no task-specific action/state names.
"""

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping

from .transform_program_repair_search import (
    BehavioralTrace,
    search_transition_repair,
)
from .vmk2 import digest


@dataclass(frozen=True)
class RepairGrammarExpansionOutcome:
    schema: str
    parent_meta_digest: str
    parent_status: str
    status: str
    selected_operation: str | None
    selected_patch: Mapping[str, Any] | None
    viable_operations: tuple[str, ...]
    promotion_authority: bool


def search_repair_grammar_expansion(
    meta_program: Mapping[str, Any],
    transform_parent: Mapping[str, Any],
    traces: Iterable[BehavioralTrace],
) -> RepairGrammarExpansionOutcome:
    rows = tuple(traces)
    enabled = tuple(str(x) for x in meta_program.get("enabled_patch_ops", ()))
    available = tuple(str(x) for x in meta_program.get("available_patch_ops", ()))
    parent_result = search_transition_repair(
        transform_parent, rows, allowed_patch_ops=enabled
    )

    if parent_result.status == "UNIQUE_MINIMAL_PATCH":
        return RepairGrammarExpansionOutcome(
            schema="Venus.RepairGrammarExpansionOutcome.v0.1",
            parent_meta_digest=digest(meta_program),
            parent_status=parent_result.status,
            status="NO_META_EXPANSION_NEEDED",
            selected_operation=None,
            selected_patch=parent_result.selected_patch,
            viable_operations=(),
            promotion_authority=False,
        )

    viable: list[tuple[str, Mapping[str, Any]]] = []
    for op in sorted(set(available) - set(enabled)):
        result = search_transition_repair(
            transform_parent,
            rows,
            allowed_patch_ops=tuple(enabled) + (op,),
        )
        if result.status == "UNIQUE_MINIMAL_PATCH" and result.selected_patch is not None:
            viable.append((op, result.selected_patch))

    if not viable:
        status = "WITHHOLD_NO_VIABLE_GRAMMAR_EXPANSION"
        selected_op = None
        selected_patch = None
    elif len(viable) > 1:
        status = "WITHHOLD_AMBIGUOUS_GRAMMAR_EXPANSION"
        selected_op = None
        selected_patch = None
    else:
        status = "UNIQUE_META_IMPROVEMENT_CANDIDATE"
        selected_op, selected_patch = viable[0]

    return RepairGrammarExpansionOutcome(
        schema="Venus.RepairGrammarExpansionOutcome.v0.1",
        parent_meta_digest=digest(meta_program),
        parent_status=parent_result.status,
        status=status,
        selected_operation=selected_op,
        selected_patch=selected_patch,
        viable_operations=tuple(x[0] for x in viable),
        promotion_authority=False,
    )


def outcome_dict(outcome: RepairGrammarExpansionOutcome) -> dict[str, Any]:
    return asdict(outcome)
