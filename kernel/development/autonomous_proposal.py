from __future__ import annotations

"""Bounded learner-owned research proposal synthesis for autonomous cycles.

The proposal is derived from the already-selected target and study object.
It may choose among a fixed set of read/test/audit operations. It may not turn
untrusted issue/PR text into shell commands, write arbitrary repository paths,
merge, promote, release, close targets, or manufacture external evidence.
"""

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from kernel.runtime.vmk2 import digest


SAFE_CHECK_IDS = (
    "AUDIT_AUTONOMY_MATRIX",
    "UNIT_AUTONOMY",
    "UNIT_INTERNAL_OSTAR",
    "UNIT_WORLD_INPUT_SECURITY",
    "FULL_UNIT_SUITE",
)

AUTONOMY_WRITABLE_PREFIXES = (
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


def _hypotheses(study: Mapping[str, Any], method: str) -> tuple[str, ...]:
    blockers = tuple(str(x) for x in study.get("returned_blocker_sentences", ()))
    refs = tuple(str(x) for x in study.get("referenced_repository_paths", ()))
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


def make_research_proposal(cycle: Mapping[str, Any]) -> ResearchProposal:
    if str(cycle.get("decision")) == "STOP":
        raise ValueError("STOP cycle cannot create a research proposal")
    study = cycle.get("study")
    if not isinstance(study, Mapping):
        raise ValueError("non-STOP cycle requires a study object")
    method = str(cycle.get("study_method") or study.get("method") or "")
    checks = _checks_for_method(method)
    external_required = _hidden_or_external_required(study)

    if external_required and method in {"DISCRIMINATOR_DESIGN", "RETURN_BOUNDARY_AUDIT"}:
        disposition = "WITHHOLD_EXTERNAL_RETURN"
        discriminator = (
            "obtain the independently supplied hidden/external observation named by the target "
            "without exposing it to proposal generation"
        )
        checks = tuple(x for x in checks if x != "FULL_UNIT_SUITE")
    else:
        disposition = "RUN_BOUNDED_LOCAL_CHECKS"
        discriminator = (
            "run the fixed prefrozen local checks and compare their returned result against "
            "the study method's live rival hypotheses"
        )

    body = {
        "schema": "Venus.AutonomousResearchProposal.v0.1",
        "cycle_id": str(cycle["cycle_id"]),
        "target_kind": str(cycle["target_kind"]),
        "target_number": int(cycle["target_number"]),
        "study_method": method,
        "disposition": disposition,
        "hypotheses": _hypotheses(study, method),
        "discriminator": discriminator,
        "check_ids": checks,
        "writable_prefixes": AUTONOMY_WRITABLE_PREFIXES,
        "target_text_is_authority": False,
        "external_return_required": external_required,
        "arbitrary_code_write_authority": False,
        "promotion_authority": False,
    }
    return ResearchProposal(proposal_id=digest(body), **body)


def proposal_dict(proposal: ResearchProposal) -> dict[str, Any]:
    return asdict(proposal)
