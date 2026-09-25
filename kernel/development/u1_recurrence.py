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
from kernel.runtime.internal_ostar import (
    ReturnedEpisode,
    RoutingContext,
    reconstruct_internal_ostar,
    route_with_internal_ostar,
    route_without_internal_ostar,
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
    problem_trace_bound: bool
    post_mutation_ostar_rederived: bool
    post_mutation_ostar_model_id: str | None
    post_mutation_ostar_decision: str | None
    post_mutation_ostar_ablation_decision: str | None
    post_mutation_ostar_causal: bool
    promotion_authority: bool



def _problem_training_return(
    formed_problem: Mapping[str, Any],
    base_training_return: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind a formed problem into externally supplied trace semantics.

    The formed problem supplies target/residual/discriminator/provenance values.
    The external return artifact supplies which field-patterns should succeed,
    fail, and where a successful transition should land.
    """
    problem_id = str(formed_problem["problem_id"])
    residuals = tuple(str(x) for x in formed_problem.get("residual_coordinates", ()))
    discriminator = str(formed_problem.get("discriminator") or "")
    provenance_ids = tuple(str(x) for x in formed_problem.get("source_stream_ids", ()))
    if not residuals or not discriminator or not provenance_ids:
        raise U1RecurrenceError(
            "formed problem must carry residual, discriminator and source provenance"
        )

    positive = {
        "target_id": problem_id,
        "residual": "|".join(residuals),
        "discriminator": discriminator,
        "provenance_ids": list(provenance_ids),
    }
    required = frozenset(positive)
    base_rows = tuple(base_training_return.get("traces", ()))
    if not base_rows:
        raise U1RecurrenceError("external training-return traces required")

    rows: list[dict[str, Any]] = []
    for index, base in enumerate(base_rows):
        if str(base.get("prior_state")) != "IDLE" or str(base.get("action")) != "SELECT_TARGET":
            continue
        base_payload = dict(base.get("payload") or {})
        missing = required - set(base_payload)
        payload = dict(positive)
        for field in missing:
            payload.pop(field, None)
        rows.append({
            "trace_id": f"problem-bound-{index}",
            "prior_state": "IDLE",
            "action": "SELECT_TARGET",
            "payload": payload,
            "expect_success": bool(base["expect_success"]),
            "expected_next_state": base.get("expected_next_state"),
            "provenance_id": str(base["provenance_id"]),
        })

    if not rows or not any(row["expect_success"] for row in rows):
        raise U1RecurrenceError(
            "external training return lacks usable SELECT_TARGET semantics"
        )
    return {
        "schema": base_training_return.get("schema"),
        "date": base_training_return.get("date"),
        "exposure": base_training_return.get("exposure"),
        "target_kind": base_training_return.get("target_kind"),
        "traces": rows,
        "hidden_evaluation_exposed": bool(
            base_training_return.get("hidden_evaluation_exposed", False)
        ),
        "promotion_authority": False,
    }


def _rederive_post_mutation_ostar(
    obj: Mapping[str, Any] | None,
) -> tuple[bool, str | None, str | None, str | None, bool]:
    if not isinstance(obj, Mapping):
        return False, None, None, None, False
    if obj.get("owner") != "EXTERNAL_EVALUATOR":
        raise U1RecurrenceError("post-mutation O* returns must be externally owned")
    pre_rows = tuple(obj.get("pre_mutation_episodes", ()))
    rows = tuple(obj.get("episodes", ()))
    if not pre_rows or not rows:
        raise U1RecurrenceError(
            "pre- and post-mutation O* return episodes required"
        )

    def _episodes(source_rows: tuple[Mapping[str, Any], ...]) -> tuple[ReturnedEpisode, ...]:
        return tuple(
            ReturnedEpisode(
                episode_id=str(row["episode_id"]),
                external_access=bool(row["external_access"]),
                contradiction_reachable=bool(row["contradiction_reachable"]),
                revision_reachable=bool(row["revision_reachable"]),
                action_authorized=bool(row["action_authorized"]),
                evidence_sufficient=bool(row["evidence_sufficient"]),
                residual_unresolved=bool(row["residual_unresolved"]),
                carrier_status_only_rejection=bool(
                    row.get("carrier_status_only_rejection", False)
                ),
                consequence_relevant_carrier_difference=bool(
                    row.get("consequence_relevant_carrier_difference", False)
                ),
            )
            for row in source_rows
        )

    pre_model = reconstruct_internal_ostar(_episodes(pre_rows))
    episodes = _episodes(rows)
    model = reconstruct_internal_ostar(episodes)
    ctx_obj = obj.get("causal_context")
    if not isinstance(ctx_obj, Mapping):
        raise U1RecurrenceError("post-mutation O* causal context required")
    context = RoutingContext(
        context_id=str(ctx_obj["context_id"]),
        has_external_access=bool(ctx_obj["has_external_access"]),
        contradiction_reachable=bool(ctx_obj["contradiction_reachable"]),
        revision_reachable=bool(ctx_obj["revision_reachable"]),
        action_authorized=bool(ctx_obj["action_authorized"]),
        evidence_sufficient=bool(ctx_obj["evidence_sufficient"]),
        residual_unresolved=bool(ctx_obj["residual_unresolved"]),
        carrier_status_only_rejection=bool(
            ctx_obj.get("carrier_status_only_rejection", False)
        ),
        consequence_relevant_carrier_difference=bool(
            ctx_obj.get("consequence_relevant_carrier_difference", False)
        ),
    )
    intact = route_with_internal_ostar(model, context).decision.value
    ablated = route_without_internal_ostar(context).value
    return (
        model.model_id != pre_model.model_id,
        model.model_id,
        intact,
        ablated,
        intact != ablated,
    )


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
    post_mutation_ostar_return: Mapping[str, Any] | None = None,
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

    problem_training_return = _problem_training_return(
        formed_problem,
        training_return,
    )
    search = search_transition_repair(
        pressure_parent,
        _trace_rows(problem_training_return),
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

    positive_payload = problem_training_return["traces"][0]["payload"]
    problem_trace_bound = (
        positive_payload["target_id"] == problem_id
        and positive_payload["residual"]
        == "|".join(str(x) for x in formed_problem.get("residual_coordinates", ()))
        and positive_payload["discriminator"]
        == str(formed_problem.get("discriminator") or "")
        and tuple(positive_payload["provenance_ids"])
        == tuple(str(x) for x in formed_problem.get("source_stream_ids", ()))
    )

    (
        post_rederived,
        post_model_id,
        post_decision,
        post_ablation,
        post_causal,
    ) = _rederive_post_mutation_ostar(post_mutation_ostar_return)

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
        "problem_trace_bound": problem_trace_bound,
        "post_mutation_ostar_rederived": post_rederived,
        "post_mutation_ostar_model_id": post_model_id,
        "post_mutation_ostar_decision": post_decision,
        "post_mutation_ostar_ablation_decision": post_ablation,
        "post_mutation_ostar_causal": post_causal,
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
