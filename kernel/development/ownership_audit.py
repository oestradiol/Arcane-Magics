from __future__ import annotations

"""Generic ownership audit reconstructed from the earned EDU13 distinction.

The audit does not rank domains or issues. It separates:
- learner-owned functions;
- host-owned but internalizable scaffolds;
- externally governed boundaries that must remain external.

If more than one host-owned internalizable function remains, selection WITHHOLDS
unless returned causal evidence supplies a unique discriminator.
"""

from dataclasses import dataclass
from typing import Iterable, Mapping


class OwnershipAuditError(ValueError):
    pass


@dataclass(frozen=True)
class FunctionOwnership:
    function_id: str
    owner: str
    internalizable: bool
    external_boundary: bool
    provenance_id: str


@dataclass(frozen=True)
class CausalReturn:
    function_id: str
    ablation_changes_behavior: bool
    returned_gain_if_internalized: float | None
    provenance_id: str


@dataclass(frozen=True)
class OwnershipAuditOutcome:
    status: str
    candidate_ids: tuple[str, ...]
    selected_target_id: str | None
    selection_basis: str
    promotion_authority: bool


def select_internalization_target(
    functions: Iterable[FunctionOwnership],
    *,
    causal_returns: Iterable[CausalReturn] = (),
) -> OwnershipAuditOutcome:
    rows = tuple(functions)
    if not rows:
        raise OwnershipAuditError("ownership inventory required")
    if any(not x.function_id or not x.provenance_id for x in rows):
        raise OwnershipAuditError("function ownership rows require identity and provenance")

    candidates = tuple(
        sorted(
            x.function_id
            for x in rows
            if x.owner == "HOST_SCAFFOLD"
            and x.internalizable
            and not x.external_boundary
        )
    )
    if not candidates:
        return OwnershipAuditOutcome(
            status="STOP_NO_INTERNALIZABLE_HOST_SCAFFOLD",
            candidate_ids=(),
            selected_target_id=None,
            selection_basis="ownership-audit",
            promotion_authority=False,
        )
    if len(candidates) == 1:
        return OwnershipAuditOutcome(
            status="UNIQUE_INTERNALIZATION_TARGET",
            candidate_ids=candidates,
            selected_target_id=candidates[0],
            selection_basis="ownership-audit",
            promotion_authority=False,
        )

    returns = {
        x.function_id: x
        for x in causal_returns
        if x.function_id in candidates and x.provenance_id
    }
    scored: list[tuple[float, str]] = []
    for cid in candidates:
        ret = returns.get(cid)
        if ret is None or not ret.ablation_changes_behavior:
            continue
        gain = ret.returned_gain_if_internalized
        if gain is None:
            continue
        scored.append((float(gain), cid))

    if not scored:
        return OwnershipAuditOutcome(
            status="WITHHOLD_MULTIPLE_INTERNALIZATION_TARGETS",
            candidate_ids=candidates,
            selected_target_id=None,
            selection_basis="need-returned-causal-discriminator",
            promotion_authority=False,
        )

    scored.sort(key=lambda x: (-x[0], x[1]))
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return OwnershipAuditOutcome(
            status="WITHHOLD_CAUSAL_TIE",
            candidate_ids=candidates,
            selected_target_id=None,
            selection_basis="returned-causal-evidence-tied",
            promotion_authority=False,
        )

    return OwnershipAuditOutcome(
        status="SELECTED_BY_RETURNED_CAUSAL_EVIDENCE",
        candidate_ids=candidates,
        selected_target_id=scored[0][1],
        selection_basis="returned-causal-evidence",
        promotion_authority=False,
    )
