from __future__ import annotations

"""Bounded recompilation of U2-style unlabeled problem formation.

The input is a returned repository field, not a preselected target. Rows expose
only neutral structural incidence needed for the first bounded separator.
Titles and semantic problem-family labels are intentionally excluded.

This is not historical U2 journal recovery. It is a consequence-equivalent
recompilation candidate for one U2 function: form a research problem from
heterogeneous returned incidence before binding that problem to a Git carrier.
"""

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from kernel.runtime.vmk2 import digest
from kernel.development.autonomous_worker import WorkItem, _item_references


UNRESOLVED_MERGE_STATES = frozenset({
    "DIRTY",
    "BLOCKED",
    "CONFLICTING",
    "UNKNOWN",
    "UNSTABLE",
})


@dataclass(frozen=True)
class RepositoryIncidenceRow:
    stream_id: str
    carrier_kind: str
    open_state: bool
    draft: bool
    merge_state: str | None
    updated_at_present: bool
    changed_path_count: int
    reference_count: int
    unresolved_reference_count: int


@dataclass(frozen=True)
class ProblemRival:
    rival_id: str
    statement: str


@dataclass(frozen=True)
class ProblemResolution:
    problem_id: str
    disposition: str
    remaining_rival_ids: tuple[str, ...]
    external_return_consumed: bool
    promotion_authority: bool = False


@dataclass(frozen=True)
class FormedProblem:
    schema: str
    problem_id: str
    disposition: str
    source_stream_ids: tuple[str, ...]
    residual_coordinates: tuple[str, ...]
    rivals: tuple[ProblemRival, ...]
    discriminator: str | None
    external_return_required: bool
    carrier_binding_authority: bool
    promotion_authority: bool


def _stream_id(item: WorkItem) -> str:
    # Identity is provenance only. It is not a problem label and never appears
    # in the problem-selection score.
    return digest({"carrier_kind": item.kind, "number": item.number})


def snapshot_to_incidence(items: Iterable[WorkItem]) -> tuple[RepositoryIncidenceRow, ...]:
    rows = tuple(items)
    known_numbers = {item.number for item in rows}
    out: list[RepositoryIncidenceRow] = []
    for item in rows:
        refs = _item_references(item)
        unresolved = tuple(x for x in refs if x not in known_numbers)
        merge_state = (
            str(item.merge_state).upper()
            if item.merge_state is not None
            else None
        )
        out.append(RepositoryIncidenceRow(
            stream_id=_stream_id(item),
            carrier_kind=item.kind,
            open_state=item.state.upper() == "OPEN",
            draft=bool(item.draft),
            merge_state=merge_state,
            updated_at_present=bool(item.updated_at),
            changed_path_count=len(tuple(item.changed_paths)),
            reference_count=len(refs),
            unresolved_reference_count=len(unresolved),
        ))
    return tuple(out)


def _row_residuals(row: RepositoryIncidenceRow) -> tuple[str, ...]:
    residuals: list[str] = []

    # Returned PR state says the present local repository model cannot yet be
    # treated as a clean enactable continuation. This is a structural separator,
    # not a semantic defect-family label.
    if (
        row.carrier_kind == "PR"
        and row.open_state
        and (row.merge_state is None or row.merge_state in UNRESOLVED_MERGE_STATES)
    ):
        residuals.append("continuation_state_unresolved")

    # A returned reference points outside the present observed field. The local
    # snapshot therefore cannot close the dependency relation by itself.
    if row.unresolved_reference_count > 0:
        residuals.append("referenced_incidence_missing")

    # Missing provenance time prevents a later changed-state comparison.
    if row.open_state and not row.updated_at_present:
        residuals.append("change_order_unavailable")

    return tuple(residuals)


def form_problem(
    rows: Iterable[RepositoryIncidenceRow],
    *,
    history_grammar_available: bool = True,
    reference_closure_available: bool = True,
) -> FormedProblem:
    """Form one bounded problem from returned incidence without a target label."""
    candidates: list[tuple[tuple[int, int, str], RepositoryIncidenceRow, tuple[str, ...]]] = []
    for row in rows:
        residuals = _row_residuals(row)
        if not residuals:
            continue

        # Prefer rows with more independent separating coordinates. Tie-break
        # content-addressedly rather than by issue/PR number or title.
        key = (
            -len(residuals),
            0 if "continuation_state_unresolved" in residuals else 1,
            row.stream_id,
        )
        candidates.append((key, row, residuals))

    if not candidates:
        body = {
            "schema": "Venus.RecompiledProblemFormation.v0.2",
            "disposition": "STOP_NO_CONSEQUENTIAL_RESIDUAL",
            "source_stream_ids": (),
            "residual_coordinates": (),
            "rivals": (),
            "discriminator": None,
            "external_return_required": False,
            "carrier_binding_authority": False,
            "promotion_authority": False,
        }
        return FormedProblem(problem_id=digest(body), **body)

    _, row, residuals = sorted(candidates, key=lambda x: x[0])[0]

    if (
        "referenced_incidence_missing" in residuals
        and not reference_closure_available
    ):
        body = {
            "schema": "Venus.RecompiledProblemFormation.v0.2",
            "disposition": "WITHHOLD_NO_REFERENCE_CLOSURE",
            "source_stream_ids": (row.stream_id,),
            "residual_coordinates": residuals,
            "rivals": (),
            "discriminator": None,
            "external_return_required": True,
            "carrier_binding_authority": False,
            "promotion_authority": False,
        }
        return FormedProblem(problem_id=digest(body), **body)

    if (
        "change_order_unavailable" in residuals
        and not history_grammar_available
    ):
        body = {
            "schema": "Venus.RecompiledProblemFormation.v0.2",
            "disposition": "WITHHOLD_NO_HISTORY_GRAMMAR",
            "source_stream_ids": (row.stream_id,),
            "residual_coordinates": residuals,
            "rivals": (),
            "discriminator": None,
            "external_return_required": True,
            "carrier_binding_authority": False,
            "promotion_authority": False,
        }
        return FormedProblem(problem_id=digest(body), **body)

    rivals: tuple[ProblemRival, ...]
    discriminator: str
    external_required: bool

    if "continuation_state_unresolved" in residuals:
        rivals = (
            ProblemRival(
                "r0",
                "the returned continuation state reflects a locally reproducible repository incompatibility",
            ),
            ProblemRival(
                "r1",
                "the returned continuation state is incomplete/stale and requires a fresh repository return",
            ),
        )
        discriminator = "REPRODUCE_OR_REFRESH_CONTINUATION_STATE"
        external_required = row.merge_state in {None, "UNKNOWN"}
    elif "referenced_incidence_missing" in residuals:
        rivals = (
            ProblemRival(
                "r0",
                "the missing referenced incidence is a consequential dependency",
            ),
            ProblemRival(
                "r1",
                "the missing reference is non-consequential/stale context",
            ),
        )
        discriminator = "RESOLVE_REFERENCED_INCIDENCE"
        external_required = True
    else:
        rivals = (
            ProblemRival(
                "r0",
                "changed-state ordering is required to determine whether reopening is licensed",
            ),
            ProblemRival(
                "r1",
                "the current observation is sufficient without historical ordering",
            ),
        )
        discriminator = "OBTAIN_ORDERED_RETURN"
        external_required = True

    rival_dicts = tuple(asdict(x) for x in rivals)
    body = {
        "schema": "Venus.RecompiledProblemFormation.v0.1",
        "disposition": "FORMED_BOUNDED_PROBLEM",
        "source_stream_ids": (row.stream_id,),
        "residual_coordinates": residuals,
        "rivals": rival_dicts,
        "discriminator": discriminator,
        "external_return_required": external_required,
        "carrier_binding_authority": False,
        "promotion_authority": False,
    }
    return FormedProblem(
        schema=body["schema"],
        problem_id=digest(body),
        disposition=body["disposition"],
        source_stream_ids=body["source_stream_ids"],
        residual_coordinates=body["residual_coordinates"],
        rivals=rivals,
        discriminator=body["discriminator"],
        external_return_required=body["external_return_required"],
        carrier_binding_authority=False,
        promotion_authority=False,
    )


def problem_dict(problem: FormedProblem) -> Mapping[str, Any]:
    return {
        "schema": problem.schema,
        "problem_id": problem.problem_id,
        "disposition": problem.disposition,
        "source_stream_ids": list(problem.source_stream_ids),
        "residual_coordinates": list(problem.residual_coordinates),
        "rivals": [asdict(x) for x in problem.rivals],
        "discriminator": problem.discriminator,
        "external_return_required": problem.external_return_required,
        "carrier_binding_authority": problem.carrier_binding_authority,
        "promotion_authority": problem.promotion_authority,
    }


def bind_problem_to_carriers(
    problem: FormedProblem,
    items: Iterable[WorkItem],
) -> tuple[tuple[str, int], ...]:
    """Map a formed problem back onto possible Git carriers.

    Carrier identity is consulted only after problem formation. A STOP problem
    binds nothing. Missing/ambiguous source streams fail closed rather than
    falling back to the old global target ranking.
    """
    if problem.disposition == "STOP_NO_CONSEQUENTIAL_RESIDUAL":
        return ()
    wanted = set(problem.source_stream_ids)
    matches = tuple(
        (item.kind, item.number)
        for item in items
        if _stream_id(item) in wanted
    )
    if len(matches) != len(wanted):
        return ()
    return tuple(sorted(set(matches)))


def resolve_problem(
    problem: FormedProblem,
    *,
    returned_rival_id: str | None = None,
) -> ProblemResolution:
    """Consume an independently supplied discriminator return.

    The learner may not reduce externally unresolved rivals by local execution.
    """
    rival_ids = tuple(x.rival_id for x in problem.rivals)
    if problem.disposition != "FORMED_BOUNDED_PROBLEM":
        return ProblemResolution(
            problem_id=problem.problem_id,
            disposition=problem.disposition,
            remaining_rival_ids=rival_ids,
            external_return_consumed=False,
            promotion_authority=False,
        )
    if problem.external_return_required and returned_rival_id is None:
        return ProblemResolution(
            problem_id=problem.problem_id,
            disposition="WITHHOLD_EXTERNAL_RETURN",
            remaining_rival_ids=rival_ids,
            external_return_consumed=False,
            promotion_authority=False,
        )
    if returned_rival_id is not None:
        if returned_rival_id not in rival_ids:
            raise ValueError("returned rival id is not one of the prefrozen live rivals")
        return ProblemResolution(
            problem_id=problem.problem_id,
            disposition="RETURN_REDUCED_RIVALS",
            remaining_rival_ids=(returned_rival_id,),
            external_return_consumed=True,
            promotion_authority=False,
        )
    return ProblemResolution(
        problem_id=problem.problem_id,
        disposition="LOCAL_DISCRIMINATOR_AVAILABLE",
        remaining_rival_ids=rival_ids,
        external_return_consumed=False,
        promotion_authority=False,
    )


def exhaustive_problem_scan(
    rows: Iterable[RepositoryIncidenceRow],
) -> tuple[str, tuple[str, ...]] | None:
    """Mature ordinary comparator: exhaustively enumerate structural residuals.

    Matching the developmental problem former mature-reduces algorithmic
    novelty; it does not erase the ordering/ownership result.
    """
    candidates: list[tuple[tuple[int, int, str], str, tuple[str, ...]]] = []
    for row in rows:
        residuals = _row_residuals(row)
        if not residuals:
            continue
        key = (
            -len(residuals),
            0 if "continuation_state_unresolved" in residuals else 1,
            row.stream_id,
        )
        candidates.append((key, row.stream_id, residuals))
    if not candidates:
        return None
    _, stream_id, residuals = sorted(candidates, key=lambda x: x[0])[0]
    return stream_id, residuals
