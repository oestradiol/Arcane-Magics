from __future__ import annotations

"""Bounded learner-owned research proposal synthesis for autonomous cycles.

The proposal is derived from the already-selected target and study object.
It may choose among a fixed set of read/test/audit operations. A state-owned
catalog may route a target to relevant admitted check IDs, but only the external
executor binds those IDs to executable commands.

Untrusted issue/PR text therefore may influence which already-admitted safe
check is relevant; it may not become shell, authority, arbitrary code-write
permission, promotion, merge, release, closure, or self-minted evidence.
"""

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from kernel.runtime.vmk2 import digest


SAFE_CHECK_IDS = (
    "AUDIT_AUTONOMY_MATRIX",
    "UNIT_AUTONOMY",
    "UNIT_INTERNAL_OSTAR",
    "UNIT_WORLD_INPUT_SECURITY",
    "UNIT_VMK2_TRUST",
    "FULL_UNIT_SUITE",
)

AUTONOMY_WRITABLE_PREFIXES = (
    "autonomy/problems/",
    "autonomy/cycles/",
    "autonomy/proposals/",
    "autonomy/evidence/",
    "kernel/development/AUTONOMOUS_LEARNING_STATE.json",
)


@dataclass(frozen=True)
class ResearchProposal:
    schema: str
    proposal_id: str
    cycle_id: str
    target_kind: str
    target_number: int
    study_method: str
    disposition: str
    hypotheses: tuple[str, ...]
    discriminator: str
    check_ids: tuple[str, ...]
    target_check_profiles: tuple[str, ...]
    target_check_ids: tuple[str, ...]
    target_relevance_grounded: bool
    writable_prefixes: tuple[str, ...]
    target_text_is_authority: bool
    external_return_required: bool
    arbitrary_code_write_authority: bool
    promotion_authority: bool


def _hidden_or_external_required(study: Mapping[str, Any]) -> bool:
    blockers = " ".join(str(x) for x in study.get("returned_blocker_sentences", ())).lower()
    signals = set(str(x).lower() for x in study.get("method_observed_signals", ()))
    return (
        "hidden" in blockers
        or "external return" in blockers
        or "waiting" in blockers
        or "await" in blockers
        or "hidden" in signals
    )


def _checks_for_method(method: str) -> tuple[str, ...]:
    table = {
        "DEPENDENCY_TRACE": ("AUDIT_AUTONOMY_MATRIX",),
        "DISCRIMINATOR_DESIGN": ("AUDIT_AUTONOMY_MATRIX", "UNIT_INTERNAL_OSTAR"),
        "REPRODUCTION": ("FULL_UNIT_SUITE",),
        "COMPARATOR_AUDIT": ("UNIT_AUTONOMY", "UNIT_INTERNAL_OSTAR"),
        "RETURN_BOUNDARY_AUDIT": (
            "UNIT_AUTONOMY",
            "UNIT_WORLD_INPUT_SECURITY",
            "AUDIT_AUTONOMY_MATRIX",
        ),
    }
    if method not in table:
        raise ValueError(f"unsupported autonomous study method: {method}")
    return table[method]


def _target_surface(cycle: Mapping[str, Any], study: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    title = str(cycle.get("target_title") or "").lower()
    refs = tuple(str(x).lower() for x in study.get("referenced_repository_paths", ()))
    return title, refs


def _target_checks(
    cycle: Mapping[str, Any],
    study: Mapping[str, Any],
    catalog: Mapping[str, Any] | None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if catalog is None:
        return (), ()
    if catalog.get("promotion_authority") is not False:
        raise ValueError("target-check catalog may not grant promotion authority")
    if catalog.get("arbitrary_command_authority") is not False:
        raise ValueError("target-check catalog may not grant arbitrary command authority")

    title, refs = _target_surface(cycle, study)
    matched: list[tuple[int, str, tuple[str, ...]]] = []
    for profile in catalog.get("profiles", ()):
        profile_id = str(profile.get("profile_id") or "")
        title_terms = tuple(str(x).lower() for x in profile.get("match_title_terms", ()))
        path_prefixes = tuple(
            str(x).lower() for x in profile.get("match_repository_path_prefixes", ())
        )
        title_match = bool(title_terms) and all(term in title for term in title_terms)
        path_match = bool(path_prefixes) and any(
            ref.startswith(prefix)
            for ref in refs
            for prefix in path_prefixes
        )
        if not (title_match or path_match):
            continue
        check_ids = tuple(str(x) for x in profile.get("check_ids", ()))
        unknown = tuple(x for x in check_ids if x not in SAFE_CHECK_IDS)
        if unknown:
            raise ValueError(
                "target-check catalog references unadmitted check ids: "
                + ", ".join(unknown)
            )
        matched.append((len(title_terms) + len(path_prefixes), profile_id, check_ids))

    if not matched:
        return (), ()

    best_score = max(x[0] for x in matched)
    best = sorted(x for x in matched if x[0] == best_score)
    profiles = tuple(x[1] for x in best)
    checks: list[str] = []
    for _, _, ids in best:
        for check_id in ids:
            if check_id not in checks:
                checks.append(check_id)
    return profiles, tuple(checks)


def _hypotheses(study: Mapping[str, Any], method: str) -> tuple[str, ...]:
    if method == "DEPENDENCY_TRACE":
        return (
            "the target remains unresolved because one or more explicit dependencies are still blocking",
            "the apparent blocker is incidental and the smallest implicated dependency lies elsewhere",
        )
    if method == "DISCRIMINATOR_DESIGN":
        return (
            "the live rival dispositions remain observationally separable by a prospective returned observation",
            "the current evidence is insufficient to distinguish the live rivals without a fresh external return",
        )
    if method == "REPRODUCTION":
        return (
            "the target's smallest executable claim reproduces under the current admitted repository state",
            "the executable claim fails or differs, localizing a returned implementation residual",
        )
    if method == "COMPARATOR_AUDIT":
        return (
            "the Venus-specific mechanism contributes a causal consequence beyond its matched ablation/substitute",
            "a simpler mature substitute explains the same consequence at the declared scope",
        )
    return (
        "the current proposal/receipt path preserves independent return and authority noncollapse",
        "one boundary is being laundered from local execution into return, authorization, or validation",
    )


def make_research_proposal(
    cycle: Mapping[str, Any],
    *,
    check_catalog: Mapping[str, Any] | None = None,
) -> ResearchProposal:
    if str(cycle.get("decision")) == "STOP":
        raise ValueError("STOP cycle cannot create a research proposal")
    study = cycle.get("study")
    if not isinstance(study, Mapping):
        raise ValueError("non-STOP cycle requires a study object")

    method = str(cycle.get("study_method") or study.get("method") or "")
    method_checks = _checks_for_method(method)
    target_profiles, target_checks = _target_checks(cycle, study, check_catalog)
    checks = tuple(dict.fromkeys(method_checks + target_checks))
    external_required = _hidden_or_external_required(study)
    target_grounded = bool(target_checks)

    if external_required and method in {"DISCRIMINATOR_DESIGN", "RETURN_BOUNDARY_AUDIT"}:
        disposition = "WITHHOLD_EXTERNAL_RETURN"
        discriminator = (
            "obtain the independently supplied hidden/external observation named by the target "
            "without exposing it to proposal generation"
        )
    elif check_catalog is not None and not target_grounded:
        disposition = "WITHHOLD_NO_TARGET_RELEVANT_LOCAL_CHECK"
        discriminator = (
            "retain the target obligation and acquire or reconstruct an admitted target-relevant "
            "check profile before treating generic process checks as evidence about the target"
        )
    else:
        disposition = "RUN_BOUNDED_LOCAL_CHECKS"
        discriminator = (
            "run the fixed prefrozen local checks, including the state-selected target-relevant "
            "profile where available, and compare returned results against the live rival hypotheses"
        )

    body = {
        "schema": "Venus.AutonomousResearchProposal.v0.2",
        "cycle_id": str(cycle["cycle_id"]),
        "target_kind": str(cycle["target_kind"]),
        "target_number": int(cycle["target_number"]),
        "study_method": method,
        "disposition": disposition,
        "hypotheses": _hypotheses(study, method),
        "discriminator": discriminator,
        "check_ids": checks,
        "target_check_profiles": target_profiles,
        "target_check_ids": target_checks,
        "target_relevance_grounded": target_grounded,
        "writable_prefixes": AUTONOMY_WRITABLE_PREFIXES,
        "target_text_is_authority": False,
        "external_return_required": external_required,
        "arbitrary_code_write_authority": False,
        "promotion_authority": False,
    }
    return ResearchProposal(proposal_id=digest(body), **body)


def proposal_dict(proposal: ResearchProposal) -> dict[str, Any]:
    return asdict(proposal)
