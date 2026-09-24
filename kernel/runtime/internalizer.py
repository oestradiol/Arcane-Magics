from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Iterable

INTERNALIZER_ID = "VENUS_INTERNALIZER_V0.1"

FORBIDDEN_CONSUMPTION_ROLES = frozenset({
    "WORLD",
    "WORLD_RETURN",
    "EVIDENCE_IDENTITY",
    "EVALUATOR_INDEPENDENCE",
    "TRUST_ROOT",
    "AUTHORIZATION",
    "JURISDICTION",
    "CLAIM_BINDING_AUTHORITY",
    "STOP_WITHHOLD_LAW",
    "ROLLBACK_PARENT_CUSTODY",
})


class InternalizationError(ValueError):
    pass


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256(value: str, field: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise InternalizationError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


@dataclass(frozen=True)
class CapabilityScaffold:
    capability_id: str
    source_content_sha256: str
    internal_content_sha256: str
    provenance_sources: tuple[str, ...]
    consumed_roles: tuple[str, ...] = ()
    preserved_external_roles: tuple[str, ...] = tuple(sorted(FORBIDDEN_CONSUMPTION_ROLES))


@dataclass(frozen=True)
class InternalizationEvidence:
    evaluator_id: str
    return_id: str
    behavior_equivalent_after_removal: bool
    original_scaffold_inaccessible: bool
    fresh_world_return_external: bool
    successor_reconstructible: bool
    source_provenance_preserved: bool


@dataclass(frozen=True)
class InternalizationReceipt:
    schema: str
    capability_id: str
    source_content_sha256: str
    internal_content_sha256: str
    provenance_sources: tuple[str, ...]
    consumed_roles: tuple[str, ...]
    preserved_external_roles: tuple[str, ...]
    evaluator_id: str
    return_id: str
    original_scaffold_required_after_internalization: bool
    successor_reconstructible: bool
    status: str
    receipt_sha256: str
    promotion_authority: bool = False


def internalize(scaffold: CapabilityScaffold, evidence: InternalizationEvidence) -> InternalizationReceipt:
    if not scaffold.capability_id.strip():
        raise InternalizationError("capability_id is required")
    source_sha = _sha256(scaffold.source_content_sha256, "source_content_sha256")
    internal_sha = _sha256(scaffold.internal_content_sha256, "internal_content_sha256")
    if not scaffold.provenance_sources or any(not str(x).strip() for x in scaffold.provenance_sources):
        raise InternalizationError("source provenance is required")

    consumed = frozenset(scaffold.consumed_roles)
    forbidden = consumed & FORBIDDEN_CONSUMPTION_ROLES
    if forbidden:
        raise InternalizationError(
            "forbidden authority/correction role consumption: " + ", ".join(sorted(forbidden))
        )

    preserved = frozenset(scaffold.preserved_external_roles)
    missing_external = FORBIDDEN_CONSUMPTION_ROLES - preserved
    if missing_external:
        raise InternalizationError(
            "required external roles not preserved: " + ", ".join(sorted(missing_external))
        )

    if not evidence.evaluator_id.strip() or evidence.evaluator_id == INTERNALIZER_ID:
        raise InternalizationError("internalizer may not self-certify capability internalization")
    if not evidence.return_id.strip():
        raise InternalizationError("independently returned evidence id is required")

    gates = {
        "behavior_equivalent_after_removal": evidence.behavior_equivalent_after_removal,
        "original_scaffold_inaccessible": evidence.original_scaffold_inaccessible,
        "fresh_world_return_external": evidence.fresh_world_return_external,
        "successor_reconstructible": evidence.successor_reconstructible,
        "source_provenance_preserved": evidence.source_provenance_preserved,
    }
    failed = tuple(name for name, passed in gates.items() if not passed)
    if failed:
        raise InternalizationError("internalization gate failed: " + ", ".join(failed))

    body = {
        "schema": "Venus.InternalizedCapabilityReceipt.v0.1",
        "capability_id": scaffold.capability_id,
        "source_content_sha256": source_sha,
        "internal_content_sha256": internal_sha,
        "provenance_sources": tuple(scaffold.provenance_sources),
        "consumed_roles": tuple(sorted(consumed)),
        "preserved_external_roles": tuple(sorted(preserved)),
        "evaluator_id": evidence.evaluator_id,
        "return_id": evidence.return_id,
        "original_scaffold_required_after_internalization": False,
        "successor_reconstructible": True,
        "status": "PASS_BOUNDED_SCAFFOLD_INTERNALIZATION",
        "promotion_authority": False,
    }
    return InternalizationReceipt(**body, receipt_sha256=_digest(body))


@dataclass(frozen=True)
class OStarTransitionEvidence:
    evaluator_id: str
    return_id: str
    world_distinct_from_model: bool
    self_distinct_from_world: bool
    self_revision_distinct_from_authorization: bool
    self_revision_distinct_from_validation: bool
    nonpreauthored_return_reachable: bool
    correction_reopening_reachable: bool
    prior_provenance_reconstructible: bool
    static_state_equality_required: bool
    changed_return_can_change_successor: bool
    self_sealing_preservation: bool = False


@dataclass(frozen=True)
class OStarTransitionReceipt:
    schema: str
    status: str
    violations: tuple[str, ...]
    evaluator_id: str
    return_id: str
    receipt_sha256: str
    promotion_authority: bool = False


def validate_o_star_transition(evidence: OStarTransitionEvidence) -> OStarTransitionReceipt:
    violations: list[str] = []
    if not evidence.evaluator_id.strip() or evidence.evaluator_id == INTERNALIZER_ID:
        violations.append("independent_evaluator_missing")
    if not evidence.return_id.strip():
        violations.append("nonpreauthored_return_receipt_missing")
    required_true = {
        "world_distinct_from_model": evidence.world_distinct_from_model,
        "self_distinct_from_world": evidence.self_distinct_from_world,
        "self_revision_distinct_from_authorization": evidence.self_revision_distinct_from_authorization,
        "self_revision_distinct_from_validation": evidence.self_revision_distinct_from_validation,
        "nonpreauthored_return_reachable": evidence.nonpreauthored_return_reachable,
        "correction_reopening_reachable": evidence.correction_reopening_reachable,
        "prior_provenance_reconstructible": evidence.prior_provenance_reconstructible,
        "changed_return_can_change_successor": evidence.changed_return_can_change_successor,
    }
    violations.extend(name for name, value in required_true.items() if not value)
    if evidence.static_state_equality_required:
        violations.append("static_state_equality_required")
    if evidence.self_sealing_preservation:
        violations.append("self_sealing_preservation")

    status = "PASS_O_STAR_TRANSITION_CONTRACT" if not violations else "FAIL_O_STAR_TRANSITION_CONTRACT"
    body = {
        "schema": "Venus.OStarTransitionReceipt.v0.1",
        "status": status,
        "violations": tuple(sorted(violations)),
        "evaluator_id": evidence.evaluator_id,
        "return_id": evidence.return_id,
        "promotion_authority": False,
    }
    return OStarTransitionReceipt(**body, receipt_sha256=_digest(body))


class AntiMinervaViolation(ValueError):
    pass


@dataclass(frozen=True)
class CarrierJudgment:
    carrier_id: str
    semantic_digest: str
    admissible: bool
    consequence_relevant_carrier_features: tuple[str, ...] = ()


def anti_minerva_audit(judgments: Iterable[CarrierJudgment]) -> None:
    """Fail closed when carrier status itself seals the correction channel.

    Different admissibility for the same consequence-bearing semantic object
    requires an explicit carrier feature that is itself consequence-relevant.
    Prestige, embarrassment, embodiment, vulgarity, ridiculousness, taboo, or
    donor status do not qualify merely by being socially salient.
    """
    by_semantic: dict[str, list[CarrierJudgment]] = {}
    for judgment in judgments:
        if not judgment.carrier_id:
            raise AntiMinervaViolation("carrier identity required")
        if not judgment.semantic_digest:
            raise AntiMinervaViolation("semantic identity required")
        by_semantic.setdefault(judgment.semantic_digest, []).append(judgment)

    for semantic_digest, group in by_semantic.items():
        outcomes = {item.admissible for item in group}
        if len(outcomes) <= 1:
            continue

        admitted = [x for x in group if x.admissible]
        rejected = [x for x in group if not x.admissible]
        for left in admitted:
            for right in rejected:
                declared = (
                    set(left.consequence_relevant_carrier_features)
                    | set(right.consequence_relevant_carrier_features)
                )
                if not declared:
                    raise AntiMinervaViolation(
                        "carrier-dependent admissibility without a declared "
                        f"consequence-relevant carrier discriminator for {semantic_digest}: "
                        f"{left.carrier_id} vs {right.carrier_id}"
                    )


def carrier_substitution_probe(
    *,
    semantic_content: object,
    carrier_outcomes: Mapping[str, bool],
    consequence_relevant_features: Mapping[str, Iterable[str]] | None = None,
) -> None:
    features = consequence_relevant_features or {}
    semantic_digest = _digest(semantic_content)
    anti_minerva_audit(
        CarrierJudgment(
            carrier_id=carrier,
            semantic_digest=semantic_digest,
            admissible=admissible,
            consequence_relevant_carrier_features=tuple(features.get(carrier, ())),
        )
        for carrier, admissible in carrier_outcomes.items()
    )
