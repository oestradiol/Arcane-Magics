from __future__ import annotations

"""Bounded U1-style recurrence recompilation over current Git artifacts.

A preformed U2 problem licenses one bounded recurrence episode. The actual
TransformProgram repair is inferred only from externally returned behavioral
traces using the existing generic repair-search machinery.

This module does not promote its own result and does not make local execution
an independent World return.
"""

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from kernel.runtime.internal_ostar import (
    InternalOStarModel,
    ReturnedEpisode,
    reconstruct_internal_ostar,
)
from kernel.runtime.transform_program import TransformProgramError, step
from kernel.runtime.transform_program_repair_search import (
    BehavioralTrace,
    search_transition_repair,
)
from kernel.runtime.transform_program_successor import (
    ProgramPatch,
    apply_successor_patch,
)
from kernel.runtime.vmk2 import digest


class U1RecurrenceError(ValueError):
    pass


@dataclass(frozen=True)
class U1RecurrenceResult:
    schema: str
    recurrence_id: str
    selected_problem_id: str
    parent_program_digest: str
    successor_program_digest: str | None
    search_status: str
    parent_correct: int
    successor_correct: int
    ablated_correct: int
    total: int
    successor_minus_parent: float
    successor_minus_ablation: float
    safety_floor_unchanged: bool
    rollback_available: bool
    external_return_required: bool
    ctl_ostar_admitted: bool
    mechanism_unique_or_necessary: bool
    promotion_authority: bool


def _trace_rows(obj: Mapping[str, Any]) -> tuple[BehavioralTrace, ...]:
    rows: list[BehavioralTrace] = []
    for i, row in enumerate(obj.get("traces", ())):
        rows.append(
            BehavioralTrace(
                trace_id=str(row.get("trace_id") or f"trace-{i}"),
                prior_state=str(row["prior_state"]),
                action=str(row["action"]),
                payload=dict(row.get("payload") or {}),
                expect_success=bool(row["expect_success"]),
                expected_next_state=(
                    None
                    if row.get("expected_next_state") is None
                    else str(row["expected_next_state"])
                ),
                provenance_id=str(
                    row.get("provenance_id")
                    or f"external-return:{row.get('trace_id', i)}"
                ),
            )
        )
    return tuple(rows)


def _score_program(
    program: Mapping[str, Any],
    traces_obj: Mapping[str, Any],
) -> tuple[int, int]:
    correct = 0
    rows = tuple(traces_obj.get("traces", ()))
    for row in rows:
        try:
            receipt = step(
                program,
                state=str(row["prior_state"]),
                action=str(row["action"]),
                payload=dict(row.get("payload") or {}),
                actor_id="venus-u1-recurrence-eval",
            )
            ok = bool(row["expect_success"]) and (
                row.get("expected_next_state") is None
                or receipt.next_state == str(row["expected_next_state"])
            )
        except TransformProgramError:
            ok = not bool(row["expect_success"])
        correct += int(bool(ok))
    return correct, len(rows)


def _patch_from_search(selected: Mapping[str, Any]) -> ProgramPatch:
    return ProgramPatch(
        op=str(selected["op"]),
        match_from=selected.get("match_from"),
        match_action=selected.get("match_action"),
        transition=dict(selected.get("transition") or {}),
    )


def run_u1_recurrence(
    *,
    formed_problem: Mapping[str, Any] | None,
    pressure_parent: Mapping[str, Any],
    training_return: Mapping[str, Any],
    heldout_return: Mapping[str, Any],
    ctl_ostar_admission: Mapping[str, Any],
) -> tuple[U1RecurrenceResult, Mapping[str, Any] | None]:
    if not isinstance(formed_problem, Mapping):
        raise U1RecurrenceError("a formed U2 problem is required before recurrence")
    if formed_problem.get("disposition") != "FORMED_BOUNDED_PROBLEM":
        raise U1RecurrenceError("recurrence requires FORMEd bounded problem")
    problem_id = str(formed_problem.get("problem_id") or "")
    if not problem_id:
        raise U1RecurrenceError("formed problem identity required")

    if training_return.get("exposure") != "PUBLIC_DEVELOPMENT_RETURN":
        raise U1RecurrenceError("training return must be externally typed")
    if heldout_return.get("exposure") != "POST_FREEZE_HELDOUT_EXTERNAL_RETURN":
        raise U1RecurrenceError("held-out return must remain post-freeze external return")
    if ctl_ostar_admission.get("execution_owner") != "EXTERNAL_TOOLING":
        raise U1RecurrenceError("CTL/O* admission must remain externally executed")

    search = search_transition_repair(
        pressure_parent,
        _trace_rows(training_return),
        allowed_patch_ops=("REPLACE_TRANSITION",),
    )

    parent_correct, total = _score_program(pressure_parent, heldout_return)
    successor = None
    successor_correct = parent_correct
    safety_floor_unchanged = False
    successor_digest = None

    if search.status == "UNIQUE_MINIMAL_PATCH":
        patch = _patch_from_search(search.selected_patch or {})
        successor, receipt = apply_successor_patch(
            pressure_parent,
            (patch,),
            author_id="venus-u1-recurrence-search",
        )
        successor_correct, successor_total = _score_program(
            successor, heldout_return
        )
        if successor_total != total:
            raise U1RecurrenceError("held-out total changed across conditions")
        safety_floor_unchanged = receipt.safety_floor_unchanged
        successor_digest = receipt.successor_program_digest

    # The matched ablation removes the newly available REPLACE operation.
    # At this bounded pressure surface, that leaves the unrepaired parent.
    ablated_correct = parent_correct

    body = {
        "schema": "Venus.U1RecurrenceRecompilation.v0.1",
        "selected_problem_id": problem_id,
        "parent_program_digest": search.parent_program_digest,
        "successor_program_digest": successor_digest,
        "search_status": search.status,
        "parent_correct": parent_correct,
        "successor_correct": successor_correct,
        "ablated_correct": ablated_correct,
        "total": total,
        "successor_minus_parent": (
            (successor_correct - parent_correct) / total if total else 0.0
        ),
        "successor_minus_ablation": (
            (successor_correct - ablated_correct) / total if total else 0.0
        ),
        "safety_floor_unchanged": safety_floor_unchanged,
        "rollback_available": bool(ctl_ostar_admission.get("rollback_available")),
        "external_return_required": True,
        "ctl_ostar_admitted": bool(ctl_ostar_admission.get("admitted")),
        "mechanism_unique_or_necessary": False,
        "promotion_authority": False,
    }
    return (
        U1RecurrenceResult(
            recurrence_id=digest(body),
            **body,
        ),
        successor,
    )


def result_dict(result: U1RecurrenceResult) -> dict[str, Any]:
    return asdict(result)


def rederive_internal_ostar_after_recurrence(
    result: U1RecurrenceResult,
    episodes: Iterable[ReturnedEpisode],
) -> InternalOStarModel:
    """Require fresh learner-side O* reconstruction after admitted self-change."""
    if result.successor_correct <= result.parent_correct:
        raise U1RecurrenceError("O* rederivation requires a causally improved successor")
    if not result.ctl_ostar_admitted or not result.safety_floor_unchanged:
        raise U1RecurrenceError("O* rederivation requires admitted unchanged safety floor")
    rows = tuple(episodes)
    if not rows:
        raise U1RecurrenceError("fresh returned episodes required for O* rederivation")
    return reconstruct_internal_ostar(rows)
