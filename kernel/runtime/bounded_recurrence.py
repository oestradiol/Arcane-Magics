from __future__ import annotations

"""Founder-neutral bounded recurrence over writable state-machine programs.

The engine receives:
- a learner-formed problem object;
- an externally supplied training-return trace shell;
- a writable TransformProgram;
- optionally, a post-freeze held-out external return.

It may search and author a successor candidate inside the admitted patch grammar.
It cannot admit, promote, merge, release, or rewrite the external safety floor.
"""

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transform_program import TransformProgramError, program_digest, step
from .transform_program_repair_search import BehavioralTrace, search_transition_repair
from .transform_program_successor import ProgramPatch, apply_successor_patch
from .vmk2 import digest


class BoundedRecurrenceError(ValueError):
    pass


@dataclass(frozen=True)
class RecurrenceCandidate:
    schema: str
    candidate_id: str
    problem_id: str
    parent_program_digest: str
    successor_program_digest: str
    patch: Mapping[str, Any]
    training_return_id: str
    problem_pressure_digest: str
    safety_floor_unchanged: bool
    promotion_authority: bool = False


@dataclass(frozen=True)
class RecurrenceEvaluation:
    schema: str
    evaluation_id: str
    candidate_id: str
    parent_correct: int
    successor_correct: int
    ablated_correct: int
    total: int
    successor_minus_parent: float
    successor_minus_ablation: float
    heldout_return_id: str
    accepted_causal_gain: bool
    mechanism_unique_or_necessary: bool
    promotion_authority: bool = False


def _problem_fields(problem: Mapping[str, Any]) -> tuple[str, str, str, tuple[str, ...]]:
    if problem.get("disposition") != "FORMED_BOUNDED_PROBLEM":
        raise BoundedRecurrenceError("recurrence requires a formed bounded problem")
    problem_id = str(problem.get("problem_id") or "")
    residual = "|".join(str(x) for x in problem.get("residual_coordinates", ()))
    discriminator = str(problem.get("discriminator") or "")
    provenance = tuple(str(x) for x in problem.get("source_stream_ids", ()))
    if not problem_id or not residual or not discriminator or not provenance:
        raise BoundedRecurrenceError(
            "problem identity, residual, discriminator and provenance are required"
        )
    return problem_id, residual, discriminator, provenance


def bind_problem_to_external_trace_shell(
    problem: Mapping[str, Any],
    external_return: Mapping[str, Any],
) -> dict[str, Any]:
    """Replace only semantic values; retain externally returned trace semantics."""
    problem_id, residual, discriminator, provenance = _problem_fields(problem)
    if external_return.get("return_owner") != "EXTERNAL_EVALUATOR":
        raise BoundedRecurrenceError("training return must be externally owned")
    if external_return.get("exposure") != "PUBLIC_DEVELOPMENT_RETURN":
        raise BoundedRecurrenceError("training return exposure must be public development return")
    return_id = str(external_return.get("return_id") or "")
    if not return_id:
        raise BoundedRecurrenceError("training return identity required")

    replacement = {
        "target_id": problem_id,
        "problem_id": problem_id,
        "residual": residual,
        "discriminator": discriminator,
        "provenance_ids": list(provenance),
    }
    rows = []
    for row in external_return.get("traces", ()):
        payload = dict(row.get("payload") or {})
        for key, value in replacement.items():
            if key in payload:
                payload[key] = value
        rows.append({
            "trace_id": str(row.get("trace_id") or ""),
            "prior_state": str(row["prior_state"]),
            "action": str(row["action"]),
            "payload": payload,
            "expect_success": bool(row["expect_success"]),
            "expected_next_state": row.get("expected_next_state"),
            "provenance_id": str(row.get("provenance_id") or return_id),
        })
    if not rows:
        raise BoundedRecurrenceError("external training traces required")
    return {
        "return_id": return_id,
        "return_owner": "EXTERNAL_EVALUATOR",
        "exposure": "PUBLIC_DEVELOPMENT_RETURN",
        "traces": rows,
    }


def _traces(obj: Mapping[str, Any]) -> tuple[BehavioralTrace, ...]:
    out = []
    for index, row in enumerate(obj.get("traces", ())):
        provenance_id = str(row.get("provenance_id") or "")
        if not provenance_id:
            raise BoundedRecurrenceError("every returned trace requires provenance")
        out.append(BehavioralTrace(
            trace_id=str(row.get("trace_id") or f"trace-{index}"),
            prior_state=str(row["prior_state"]),
            action=str(row["action"]),
            payload=dict(row.get("payload") or {}),
            expect_success=bool(row["expect_success"]),
            expected_next_state=(
                None if row.get("expected_next_state") is None
                else str(row["expected_next_state"])
            ),
            provenance_id=provenance_id,
        ))
    return tuple(out)


def _patch(selected: Mapping[str, Any]) -> ProgramPatch:
    return ProgramPatch(
        op=str(selected["op"]),
        match_from=selected.get("match_from"),
        match_action=selected.get("match_action"),
        transition=dict(selected.get("transition") or {}),
    )


def author_candidate(
    *,
    problem: Mapping[str, Any],
    parent_program: Mapping[str, Any],
    training_return: Mapping[str, Any],
    allowed_patch_ops: Iterable[str],
    author_id: str = "bounded-recurrence-learner",
) -> tuple[RecurrenceCandidate | None, Mapping[str, Any] | None, str]:
    if not author_id:
        raise BoundedRecurrenceError("candidate author identity required")
    bound = bind_problem_to_external_trace_shell(problem, training_return)
    ops = tuple(str(x) for x in allowed_patch_ops)
    if not ops:
        raise BoundedRecurrenceError("at least one admitted patch operation required")
    search = search_transition_repair(
        parent_program,
        _traces(bound),
        allowed_patch_ops=ops,
    )
    if search.status != "UNIQUE_MINIMAL_PATCH":
        return None, None, search.status

    patch = _patch(search.selected_patch or {})
    successor, receipt = apply_successor_patch(
        parent_program,
        (patch,),
        author_id=author_id,
    )
    problem_id, residual, discriminator, provenance = _problem_fields(problem)
    pressure = {
        "problem_id": problem_id,
        "residual": residual,
        "discriminator": discriminator,
        "provenance": provenance,
        "bound_training_return": bound,
    }
    body = {
        "schema": "BoundedRecurrenceCandidate.v0.1",
        "problem_id": problem_id,
        "parent_program_digest": program_digest(parent_program),
        "successor_program_digest": receipt.successor_program_digest,
        "patch": {
            "op": patch.op,
            "match_from": patch.match_from,
            "match_action": patch.match_action,
            "transition": dict(patch.transition or {}),
        },
        "training_return_id": str(bound["return_id"]),
        "problem_pressure_digest": digest(pressure),
        "safety_floor_unchanged": receipt.safety_floor_unchanged,
        "promotion_authority": False,
    }
    return (
        RecurrenceCandidate(candidate_id=digest(body), **body),
        successor,
        search.status,
    )


def score_program(
    program: Mapping[str, Any],
    traces: Iterable[Mapping[str, Any]],
) -> tuple[int, int]:
    correct = 0
    rows = tuple(traces)
    for row in rows:
        try:
            receipt = step(
                program,
                state=str(row["prior_state"]),
                action=str(row["action"]),
                payload=dict(row.get("payload") or {}),
                actor_id="bounded-recurrence-evaluator",
            )
            ok = bool(row["expect_success"]) and (
                row.get("expected_next_state") is None
                or receipt.next_state == str(row["expected_next_state"])
            )
        except TransformProgramError:
            ok = not bool(row["expect_success"])
        correct += int(bool(ok))
    return correct, len(rows)


def evaluate_candidate(
    *,
    candidate: RecurrenceCandidate,
    parent_program: Mapping[str, Any],
    successor_program: Mapping[str, Any],
    heldout_return: Mapping[str, Any],
) -> RecurrenceEvaluation:
    if heldout_return.get("return_owner") != "EXTERNAL_EVALUATOR":
        raise BoundedRecurrenceError("held-out return must be externally owned")
    if heldout_return.get("exposure") != "POST_FREEZE_HELDOUT_EXTERNAL_RETURN":
        raise BoundedRecurrenceError("held-out return must be post-freeze")
    if str(heldout_return.get("candidate_id") or "") != candidate.candidate_id:
        raise BoundedRecurrenceError("held-out return candidate identity mismatch")
    return_id = str(heldout_return.get("return_id") or "")
    if not return_id:
        raise BoundedRecurrenceError("held-out return identity required")
    if program_digest(parent_program) != candidate.parent_program_digest:
        raise BoundedRecurrenceError("parent digest drift")
    if program_digest(successor_program) != candidate.successor_program_digest:
        raise BoundedRecurrenceError("successor digest drift")

    rows = tuple(heldout_return.get("traces", ()))
    if not rows:
        raise BoundedRecurrenceError("held-out traces required")
    parent_correct, total = score_program(parent_program, rows)
    successor_correct, successor_total = score_program(successor_program, rows)
    if successor_total != total:
        raise BoundedRecurrenceError("held-out totals differ")

    # Matched ablation removes the candidate patch and therefore evaluates the
    # retained parent at this one-patch bounded scope.
    ablated_correct = parent_correct
    gain_parent = (successor_correct - parent_correct) / total if total else 0.0
    gain_ablation = (successor_correct - ablated_correct) / total if total else 0.0
    accepted = (
        successor_correct > parent_correct
        and successor_correct > ablated_correct
        and candidate.safety_floor_unchanged
    )
    body = {
        "schema": "BoundedRecurrenceEvaluation.v0.1",
        "candidate_id": candidate.candidate_id,
        "parent_correct": parent_correct,
        "successor_correct": successor_correct,
        "ablated_correct": ablated_correct,
        "total": total,
        "successor_minus_parent": gain_parent,
        "successor_minus_ablation": gain_ablation,
        "heldout_return_id": return_id,
        "accepted_causal_gain": accepted,
        "mechanism_unique_or_necessary": False,
        "promotion_authority": False,
    }
    return RecurrenceEvaluation(evaluation_id=digest(body), **body)


def candidate_dict(candidate: RecurrenceCandidate) -> dict[str, Any]:
    return asdict(candidate)


def evaluation_dict(evaluation: RecurrenceEvaluation) -> dict[str, Any]:
    return asdict(evaluation)
