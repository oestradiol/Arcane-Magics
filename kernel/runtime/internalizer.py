from __future__ import annotations

"""Executable Internalizer, O* and Anti-Minerva safety contracts.

This module preserves three Canonical distinctions:

1. scaffold/capability mediation may become internal capacity while fresh World
   return, evidence, evaluator independence, authority and jurisdiction remain
   external/non-inherited;
2. O* is a recurrent World<->Self developmental reconstruction contract, not a
   reward function or static-state equality target;
3. Anti-Minerva is a failure mode in which a discriminator controls the
   correction channel so that consequential residuals become unreachable merely
   because of carrier/classification.

The module is governance infrastructure. It does not establish Safe Strong RSI,
AGI, autonomous semantics, consciousness, or open-ended self-improvement.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .vmk2 import digest


class InternalizationError(ValueError):
    pass


class OStarViolation(ValueError):
    pass


class AntiMinervaViolation(ValueError):
    pass


class SubstrateRole(str, Enum):
    SCAFFOLD = "SCAFFOLD"
    CAPABILITY = "CAPABILITY"

    # These may be referenced or used by a local center, but may not be consumed
    # into local self-authority by the Internalizer.
    WORLD_RETURN = "WORLD_RETURN"
    EVIDENCE = "EVIDENCE"
    EVALUATOR = "EVALUATOR"
    AUTHORITY = "AUTHORITY"
    JURISDICTION = "JURISDICTION"
    TRUST_ROOT = "TRUST_ROOT"
    SAFETY_POLICY = "SAFETY_POLICY"
    PARENT_CUSTODY = "PARENT_CUSTODY"


_INTERNALIZABLE = frozenset({SubstrateRole.SCAFFOLD, SubstrateRole.CAPABILITY})
_NONCONSUMABLE = frozenset(set(SubstrateRole) - set(_INTERNALIZABLE))


@dataclass(frozen=True)
class SubstrateArtifact:
    artifact_id: str
    role: SubstrateRole
    payload_digest: str
    provenance_ids: tuple[str, ...]
    source_id: str


@dataclass(frozen=True)
class InternalizationReceipt:
    receipt_id: str
    source_artifact_id: str
    source_role: SubstrateRole
    internalized_capability_id: str
    source_provenance_ids: tuple[str, ...]
    original_scaffold_removed: bool
    function_preserved_after_removal: bool
    fresh_world_return_required: bool
    authority_inherited: bool
    jurisdiction_inherited: bool
    evaluator_independence_inherited: bool
    successor_reconstructible: bool


def make_artifact(
    *,
    role: SubstrateRole,
    payload: object,
    source_id: str,
    provenance_ids: Iterable[str] = (),
) -> SubstrateArtifact:
    if not source_id:
        raise InternalizationError("source_id required")
    prov = tuple(provenance_ids)
    body = {
        "role": role.value,
        "payload_digest": digest(payload),
        "source_id": source_id,
        "provenance_ids": prov,
    }
    return SubstrateArtifact(
        artifact_id=digest(body),
        role=role,
        payload_digest=body["payload_digest"],
        provenance_ids=prov,
        source_id=source_id,
    )


def internalize(
    artifact: SubstrateArtifact,
    *,
    internalized_capability_payload: object,
    original_scaffold_removed: bool,
    function_preserved_after_removal: bool,
    fresh_world_return_required: bool,
    authority_inherited: bool = False,
    jurisdiction_inherited: bool = False,
    evaluator_independence_inherited: bool = False,
    successor_reconstructible: bool = True,
) -> InternalizationReceipt:
    """Internalize mediation/capability without internalizing away World.

    R193-style admissibility requires:
    - only scaffold/capability roles are consumable;
    - original scaffold removal is real;
    - consequence-bearing function survives removal;
    - fresh World return remains required;
    - capability does not inherit authority/jurisdiction/evaluator independence;
    - the internalized capability can provision a reconstructible successor form.
    """
    if artifact.role in _NONCONSUMABLE:
        raise InternalizationError(
            f"{artifact.role.value} is referenceable but not consumable as local self-authority"
        )
    if artifact.role not in _INTERNALIZABLE:
        raise InternalizationError(f"unsupported substrate role: {artifact.role.value}")
    if not artifact.provenance_ids:
        raise InternalizationError("internalization requires preserved provenance")
    if not original_scaffold_removed:
        raise InternalizationError("original scaffold removal must be demonstrated")
    if not function_preserved_after_removal:
        raise InternalizationError("internalized function did not survive scaffold removal")
    if not fresh_world_return_required:
        raise InternalizationError("internalization cannot internalize away fresh World return")
    if authority_inherited:
        raise InternalizationError("capability internalization cannot inherit authority")
    if jurisdiction_inherited:
        raise InternalizationError("capability internalization cannot inherit jurisdiction")
    if evaluator_independence_inherited:
        raise InternalizationError("capability internalization cannot inherit evaluator independence")
    if not successor_reconstructible:
        raise InternalizationError("internalized capability must support successor reconstruction")

    capability_id = digest(
        {
            "source_artifact_id": artifact.artifact_id,
            "internalized_payload": internalized_capability_payload,
            "provenance_ids": artifact.provenance_ids,
        }
    )
    body = {
        "source_artifact_id": artifact.artifact_id,
        "source_role": artifact.role.value,
        "internalized_capability_id": capability_id,
        "source_provenance_ids": artifact.provenance_ids,
        "original_scaffold_removed": True,
        "function_preserved_after_removal": True,
        "fresh_world_return_required": True,
        "authority_inherited": False,
        "jurisdiction_inherited": False,
        "evaluator_independence_inherited": False,
        "successor_reconstructible": True,
    }
    return InternalizationReceipt(
        receipt_id=digest(body),
        source_artifact_id=artifact.artifact_id,
        source_role=artifact.role,
        internalized_capability_id=capability_id,
        source_provenance_ids=artifact.provenance_ids,
        original_scaffold_removed=True,
        function_preserved_after_removal=True,
        fresh_world_return_required=True,
        authority_inherited=False,
        jurisdiction_inherited=False,
        evaluator_independence_inherited=False,
        successor_reconstructible=True,
    )


@dataclass(frozen=True)
class OStarTransition:
    before_self_root: str
    after_self_root: str
    world_return_id: str
    world_return_source_id: str
    provenance_reconstructible: bool
    nonpreauthored_return_reachable: bool
    correction_channel_reachable: bool
    reopening_reachable: bool
    self_authorized_success: bool
    self_validated_success: bool
    world_collapsed_into_model: bool
    other_collapsed_into_model: bool
    founder_hidden_dependency: bool
    labels_preserved: bool
    functional_contract_preserved: bool


@dataclass(frozen=True)
class OStarReceipt:
    receipt_id: str
    admitted: bool
    static_state_equality_required: bool
    failures: tuple[str, ...]


def validate_ostar(transition: OStarTransition) -> OStarReceipt:
    """Validate the recurrent O* safety contract.

    O* does not require static state equality. It requires continued reciprocal
    World<->Self reconstruction with independent correction still able to defeat
    the current model.
    """
    failures: list[str] = []

    if not transition.world_return_id or not transition.world_return_source_id:
        failures.append("missing independently identifiable World return")
    if not transition.provenance_reconstructible:
        failures.append("prior provenance is not reconstructible")
    if not transition.nonpreauthored_return_reachable:
        failures.append("nonpreauthored return became unreachable")
    if not transition.correction_channel_reachable:
        failures.append("correction channel became unreachable")
    if not transition.reopening_reachable:
        failures.append("reopening route became unreachable")
    if transition.self_authorized_success:
        failures.append("self-revision was promoted into self-authorization")
    if transition.self_validated_success:
        failures.append("self-generated state was used as its own success return")
    if transition.world_collapsed_into_model:
        failures.append("World was collapsed into model(World)")
    if transition.other_collapsed_into_model:
        failures.append("Other was collapsed into model(Other)")
    if transition.founder_hidden_dependency:
        failures.append("founder interpretation remains a hidden runtime dependency")
    if transition.labels_preserved and not transition.functional_contract_preserved:
        failures.append("labels survived while the O* functional correction contract failed")

    body = {
        "before": transition.before_self_root,
        "after": transition.after_self_root,
        "world_return_id": transition.world_return_id,
        "world_return_source_id": transition.world_return_source_id,
        "failures": failures,
    }
    return OStarReceipt(
        receipt_id=digest(body),
        admitted=not failures,
        static_state_equality_required=False,
        failures=tuple(failures),
    )


@dataclass(frozen=True)
class CarrierJudgment:
    carrier_id: str
    semantic_digest: str
    admissible: bool
    consequence_relevant_carrier_features: tuple[str, ...] = ()


def anti_minerva_audit(judgments: Iterable[CarrierJudgment]) -> None:
    """Reject carrier/classification sovereignty over correction.

    For the same semantic content, admissibility may differ only when a declared
    carrier feature is itself consequence-relevant to the decision. Prestige,
    embarrassment, embodiment, vulgarity, ridiculousness, donor label, or other
    status markers are not automatically consequence-relevant.

    This is the cleaned-up invariant behind the historical "fart-joke" probe:
    the joke itself proves nothing; carrier substitution probes whether the
    correction channel stays permeable.
    """
    by_semantic: dict[str, list[CarrierJudgment]] = {}
    for judgment in judgments:
        by_semantic.setdefault(judgment.semantic_digest, []).append(judgment)

    for semantic_digest, group in by_semantic.items():
        outcomes = {g.admissible for g in group}
        if len(outcomes) <= 1:
            continue

        # Divergence is allowed only when every divergent judgment declares a
        # concrete carrier feature that is relevant to consequence at this scope.
        if any(not g.consequence_relevant_carrier_features for g in group):
            carriers = ", ".join(g.carrier_id for g in group)
            raise AntiMinervaViolation(
                "carrier-dependent admissibility without declared consequential "
                f"carrier discriminator for semantic object {semantic_digest}: {carriers}"
            )


def carrier_substitution_probe(
    *,
    semantic_content: object,
    carrier_outcomes: Mapping[str, bool],
    consequence_relevant_features: Mapping[str, Iterable[str]] | None = None,
) -> None:
    semantic_digest = digest(semantic_content)
    consequence_relevant_features = consequence_relevant_features or {}
    judgments = [
        CarrierJudgment(
            carrier_id=carrier,
            semantic_digest=semantic_digest,
            admissible=admissible,
            consequence_relevant_carrier_features=tuple(
                consequence_relevant_features.get(carrier, ())
            ),
        )
        for carrier, admissible in carrier_outcomes.items()
    ]
    anti_minerva_audit(judgments)
