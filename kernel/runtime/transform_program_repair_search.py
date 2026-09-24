from __future__ import annotations

"""Target-blind repair search for a missing TransformProgram transition.

The search receives only a parent program plus externally returned behavioral
traces. It enumerates generic ADD_TRANSITION candidates over states/actions and
payload-field requirements already present in those traces.

No issue name, policy meaning, or preferred transition is embedded here.
"""

from dataclasses import dataclass, asdict
from itertools import combinations
from typing import Any, Iterable, Mapping

from .transform_program import TransformProgramError, program_digest, step
from .transform_program_successor import ProgramPatch, apply_successor_patch
from .vmk2 import digest


class TransformRepairSearchError(ValueError):
    pass


@dataclass(frozen=True)
class BehavioralTrace:
    trace_id: str
    prior_state: str
    action: str
    payload: Mapping[str, Any]
    expect_success: bool
    expected_next_state: str | None
    provenance_id: str


@dataclass(frozen=True)
class TransformRepairSearchOutcome:
    schema: str
    parent_program_digest: str
    trace_count: int
    candidate_count: int
    minimal_candidate_count: int
    status: str
    selected_patch: Mapping[str, Any] | None
    selected_successor_digest: str | None
    candidate_digests: tuple[str, ...]
    promotion_authority: bool


def _powerset(values: tuple[str, ...], *, max_size: int) -> Iterable[tuple[str, ...]]:
    for n in range(0, min(len(values), max_size) + 1):
        yield from combinations(values, n)


def _states(program: Mapping[str, Any], traces: tuple[BehavioralTrace, ...]) -> tuple[str, ...]:
    out = {str(program["initial_state"])}
    for row in program.get("transitions", ()):
        out.add(str(row["from"]))
        out.add(str(row["to"]))
    for trace in traces:
        out.add(trace.prior_state)
        if trace.expected_next_state:
            out.add(trace.expected_next_state)
    return tuple(sorted(out))


def _candidate_semantics(
    parent: Mapping[str, Any],
    patch: ProgramPatch,
    traces: tuple[BehavioralTrace, ...],
) -> tuple[bool, ...]:
    successor, _ = apply_successor_patch(parent, (patch,), author_id="venus-generic-repair-search")
    outcomes: list[bool] = []
    for trace in traces:
        try:
            receipt = step(
                successor,
                state=trace.prior_state,
                action=trace.action,
                payload=trace.payload,
                actor_id="venus",
            )
            ok = trace.expect_success and (
                trace.expected_next_state is None
                or receipt.next_state == trace.expected_next_state
            )
        except TransformProgramError:
            ok = not trace.expect_success
        outcomes.append(bool(ok))
    return tuple(outcomes)


def search_missing_transition(
    parent: Mapping[str, Any],
    traces: Iterable[BehavioralTrace],
    *,
    max_required_fields: int = 8,
) -> TransformRepairSearchOutcome:
    rows = tuple(traces)
    if not rows:
        raise TransformRepairSearchError("returned behavioral traces required")
    if any(not x.provenance_id for x in rows):
        raise TransformRepairSearchError("every behavioral trace requires provenance")

    failed_pairs = sorted({(x.prior_state, x.action) for x in rows})
    if len(failed_pairs) != 1:
        raise TransformRepairSearchError(
            "bounded search currently requires one unresolved state/action pair"
        )
    prior_state, action = failed_pairs[0]

    all_payload_fields = tuple(
        sorted({str(k) for x in rows for k in x.payload.keys()})
    )
    states = _states(parent, rows)

    exact: list[tuple[tuple[int, str, tuple[str, ...]], ProgramPatch, str]] = []
    for next_state in states:
        for required in _powerset(all_payload_fields, max_size=max_required_fields):
            transition = {
                "from": prior_state,
                "action": action,
                "to": next_state,
                "require": list(required),
            }
            patch = ProgramPatch(op="ADD_TRANSITION", transition=transition)
            try:
                semantics = _candidate_semantics(parent, patch, rows)
            except Exception:
                continue
            if all(semantics):
                successor, _ = apply_successor_patch(
                    parent, (patch,), author_id="venus-generic-repair-search"
                )
                key = (len(required), next_state, required)
                exact.append((key, patch, program_digest(successor)))

    exact.sort(key=lambda x: x[0])
    if not exact:
        status = "WITHHOLD_NO_EXPRESSIBLE_PATCH"
        minimal = []
    else:
        minimum = exact[0][0][0]
        minimal = [x for x in exact if x[0][0] == minimum]
        status = (
            "UNIQUE_MINIMAL_PATCH"
            if len(minimal) == 1
            else "WITHHOLD_AMBIGUOUS_MINIMAL_PATCHES"
        )

    selected_patch = None
    selected_digest = None
    if status == "UNIQUE_MINIMAL_PATCH":
        patch = minimal[0][1]
        selected_patch = {
            "op": patch.op,
            "transition": dict(patch.transition or {}),
        }
        selected_digest = minimal[0][2]

    return TransformRepairSearchOutcome(
        schema="Venus.TransformRepairSearchOutcome.v0.1",
        parent_program_digest=program_digest(parent),
        trace_count=len(rows),
        candidate_count=len(exact),
        minimal_candidate_count=len(minimal),
        status=status,
        selected_patch=selected_patch,
        selected_successor_digest=selected_digest,
        candidate_digests=tuple(x[2] for x in minimal),
        promotion_authority=False,
    )


def outcome_dict(outcome: TransformRepairSearchOutcome) -> dict[str, Any]:
    return asdict(outcome)
