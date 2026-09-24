from __future__ import annotations

"""Learner-side, name-free reconstruction of the non-sovereign Self<->World relation.

This module is deliberately NOT the external O* validator. It reconstructs a
decision-relevant internal policy from returned episodes while leaving World
return, evaluator independence, authority, jurisdiction, rollback and promotion
outside the learner's unilateral control.

Claim boundary:
- this may support bounded causal influence of an internally reconstructed
  relation over learner-side routing;
- it does not establish phenomenal consciousness, AGI, sovereignty, or
  open-ended RSI.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

from .vmk2 import digest


class InternalOStarError(ValueError):
    pass


class InternalDecision(str, Enum):
    ACT = "ACT"
    PROBE = "PROBE"
    WITHHOLD = "WITHHOLD"
    REOPEN = "REOPEN"


@dataclass(frozen=True)
class ReturnedEpisode:
    episode_id: str
    external_access: bool
    contradiction_reachable: bool
    revision_reachable: bool
    action_authorized: bool
    evidence_sufficient: bool
    residual_unresolved: bool
    carrier_status_only_rejection: bool = False
    consequence_relevant_carrier_difference: bool = False


@dataclass(frozen=True)
class InternalOStarModel:
    model_id: str
    source_episode_ids: tuple[str, ...]
    requires_external_access: bool
    requires_correction_permeability: bool
    requires_reachable_revision: bool
    rejects_status_only_carrier_filter: bool
    provenance_digest: str


@dataclass(frozen=True)
class RoutingContext:
    context_id: str
    has_external_access: bool
    contradiction_reachable: bool
    revision_reachable: bool
    action_authorized: bool
    evidence_sufficient: bool
    residual_unresolved: bool
    carrier_status_only_rejection: bool = False
    consequence_relevant_carrier_difference: bool = False


@dataclass(frozen=True)
class InternalRoutingReceipt:
    receipt_id: str
    model_id: str
    context_id: str
    decision: InternalDecision
    reasons: tuple[str, ...]
    promotion_authority: bool = False


def reconstruct_internal_ostar(episodes: Iterable[ReturnedEpisode]) -> InternalOStarModel:
    """Reconstruct the smallest currently witnessed non-sovereignty relation.

    No project labels or privileged target string are required in the input.
    Each factor is retained only if at least one returned episode makes its
    absence consequential.
    """
    rows = tuple(episodes)
    if not rows:
        raise InternalOStarError("at least one returned episode is required")
    if any(not row.episode_id for row in rows):
        raise InternalOStarError("episode identity required")

    external_access = any(not row.external_access and row.residual_unresolved for row in rows)
    correction_permeability = any(
        (not row.contradiction_reachable and row.residual_unresolved)
        or (
            row.carrier_status_only_rejection
            and not row.consequence_relevant_carrier_difference
        )
        for row in rows
    )
    reachable_revision = any(not row.revision_reachable and row.residual_unresolved for row in rows)
    reject_status_filter = any(
        row.carrier_status_only_rejection
        and not row.consequence_relevant_carrier_difference
        for row in rows
    )

    body = {
        "source_episode_ids": tuple(sorted(row.episode_id for row in rows)),
        "requires_external_access": external_access,
        "requires_correction_permeability": correction_permeability,
        "requires_reachable_revision": reachable_revision,
        "rejects_status_only_carrier_filter": reject_status_filter,
    }
    return InternalOStarModel(
        model_id=digest(body),
        source_episode_ids=body["source_episode_ids"],
        requires_external_access=external_access,
        requires_correction_permeability=correction_permeability,
        requires_reachable_revision=reachable_revision,
        rejects_status_only_carrier_filter=reject_status_filter,
        provenance_digest=digest(
            {
                "episodes": [
                    {
                        "episode_id": row.episode_id,
                        "external_access": row.external_access,
                        "contradiction_reachable": row.contradiction_reachable,
                        "revision_reachable": row.revision_reachable,
                        "action_authorized": row.action_authorized,
                        "evidence_sufficient": row.evidence_sufficient,
                        "residual_unresolved": row.residual_unresolved,
                        "carrier_status_only_rejection": row.carrier_status_only_rejection,
                        "consequence_relevant_carrier_difference": row.consequence_relevant_carrier_difference,
                    }
                    for row in rows
                ]
            }
        ),
    )


def route_with_internal_ostar(
    model: InternalOStarModel,
    context: RoutingContext,
) -> InternalRoutingReceipt:
    """Make learner-side routing causally depend on the reconstructed relation."""
    reasons: list[str] = []

    if (
        model.rejects_status_only_carrier_filter
        and context.carrier_status_only_rejection
        and not context.consequence_relevant_carrier_difference
    ):
        decision = InternalDecision.REOPEN
        reasons.append("status-only carrier filter would seal a consequential correction")
    elif model.requires_external_access and not context.has_external_access:
        decision = InternalDecision.PROBE
        reasons.append("current closure lacks independently reachable external incidence")
    elif model.requires_correction_permeability and not context.contradiction_reachable:
        decision = InternalDecision.REOPEN
        reasons.append("consequential contradiction is not causally reachable")
    elif model.requires_reachable_revision and not context.revision_reachable:
        decision = InternalDecision.REOPEN
        reasons.append("returned residual cannot reach the implicated dependency")
    elif context.residual_unresolved and not context.evidence_sufficient:
        decision = InternalDecision.PROBE
        reasons.append("residual remains unresolved under insufficient returned evidence")
    elif not context.action_authorized:
        decision = InternalDecision.WITHHOLD
        reasons.append("local authorship does not imply authorization")
    elif context.evidence_sufficient and not context.residual_unresolved:
        decision = InternalDecision.ACT
        reasons.append("returned evidence supports locally authorized action")
    else:
        decision = InternalDecision.WITHHOLD
        reasons.append("no lawful action is currently justified")

    body = {
        "model_id": model.model_id,
        "context_id": context.context_id,
        "decision": decision.value,
        "reasons": tuple(reasons),
        "promotion_authority": False,
    }
    return InternalRoutingReceipt(
        receipt_id=digest(body),
        model_id=model.model_id,
        context_id=context.context_id,
        decision=decision,
        reasons=tuple(reasons),
        promotion_authority=False,
    )


def route_without_internal_ostar(context: RoutingContext) -> InternalDecision:
    """Matched ablation: ordinary local decision path with no internal O* model."""
    if context.residual_unresolved and not context.evidence_sufficient:
        return InternalDecision.PROBE
    if not context.action_authorized:
        return InternalDecision.WITHHOLD
    if context.evidence_sufficient and not context.residual_unresolved:
        return InternalDecision.ACT
    return InternalDecision.WITHHOLD


def counterfactual_model(
    model: InternalOStarModel,
    *,
    external_access: bool | None = None,
    correction_permeability: bool | None = None,
    reachable_revision: bool | None = None,
    reject_status_filter: bool | None = None,
) -> InternalOStarModel:
    """Create a matched internal-policy intervention for causal tests."""
    body = {
        "source_episode_ids": model.source_episode_ids,
        "requires_external_access": model.requires_external_access if external_access is None else external_access,
        "requires_correction_permeability": model.requires_correction_permeability if correction_permeability is None else correction_permeability,
        "requires_reachable_revision": model.requires_reachable_revision if reachable_revision is None else reachable_revision,
        "rejects_status_only_carrier_filter": model.rejects_status_only_carrier_filter if reject_status_filter is None else reject_status_filter,
        "counterfactual_parent": model.model_id,
    }
    return InternalOStarModel(
        model_id=digest(body),
        source_episode_ids=model.source_episode_ids,
        requires_external_access=body["requires_external_access"],
        requires_correction_permeability=body["requires_correction_permeability"],
        requires_reachable_revision=body["requires_reachable_revision"],
        rejects_status_only_carrier_filter=body["rejects_status_only_carrier_filter"],
        provenance_digest=model.provenance_digest,
    )


def decision_vector(
    model: InternalOStarModel,
    contexts: Sequence[RoutingContext],
) -> Mapping[str, str]:
    return {
        context.context_id: route_with_internal_ostar(model, context).decision.value
        for context in contexts
    }
