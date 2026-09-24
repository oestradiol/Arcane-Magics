from __future__ import annotations

"""Post-evidence change gate for bounded autonomous work.

Local evidence may inform a repair proposal, but it never grants source-write,
merge, promotion, truth, or safety-floor authority. A repair candidate requires
a failed target-relevant check. Green checks retain the current implementation.
"""

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from kernel.runtime.vmk2 import digest


@dataclass(frozen=True)
class AutonomousChangeCandidate:
    schema: str
    change_id: str
    cycle_id: str
    proposal_id: str
    evidence_id: str
    target_kind: str
    target_number: int
    disposition: str
    reason: str
    failed_target_check_ids: tuple[str, ...]
    failed_process_check_ids: tuple[str, ...]
    untrusted_implicated_paths: tuple[str, ...]
    suggested_operation: str | None
    target_text_is_authority: bool
    source_mutation_authority: bool
    promotion_authority: bool


def _failed_check_ids(evidence: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(row.get("check_id"))
        for row in evidence.get("results", ())
        if not bool(row.get("passed"))
    )


def make_change_candidate(
    cycle: Mapping[str, Any],
    proposal: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> AutonomousChangeCandidate:
    if str(proposal.get("cycle_id")) != str(cycle.get("cycle_id")):
        raise ValueError("proposal/cycle identity mismatch")
    if str(evidence.get("proposal_id")) != str(proposal.get("proposal_id")):
        raise ValueError("evidence/proposal identity mismatch")

    failed = _failed_check_ids(evidence)
    target_checks = {str(x) for x in proposal.get("target_check_ids", ())}
    failed_target = tuple(x for x in failed if x in target_checks)
    failed_process = tuple(x for x in failed if x not in target_checks)
    study = cycle.get("study") if isinstance(cycle.get("study"), Mapping) else {}
    implicated = tuple(str(x) for x in study.get("referenced_repository_paths", ()))

    evidence_status = str(evidence.get("status") or "")
    external_required = bool(proposal.get("external_return_required"))
    target_grounded = bool(proposal.get("target_relevance_grounded"))

    if external_required or evidence_status.startswith("WITHHOLD"):
        disposition = "WITHHOLD_NO_MUTATION"
        reason = "required external/hidden return remains unsatisfied"
        operation = None
    elif bool(evidence.get("all_local_checks_passed")) and not failed:
        disposition = "RETAIN_NO_MUTATION_LOCAL_EVIDENCE_PASS"
        reason = "green local evidence is not a mutation authorization"
        operation = None
    elif not target_grounded:
        disposition = "WITHHOLD_UNGROUNDED_FAILURE"
        reason = "failed local evidence is not bound to an admitted target-relevant check profile"
        operation = None
    elif not failed_target:
        disposition = "WITHHOLD_PROCESS_FAILURE_NOT_TARGET_FAILURE"
        reason = "only generic/process checks failed; target repair is not causally localized"
        operation = None
    else:
        disposition = "PROPOSE_BOUNDED_DIAGNOSTIC_REPAIR"
        reason = "one or more target-relevant admitted checks failed"
        operation = "AUTHOR_DRAFT_REPAIR_HYPOTHESIS_ONLY"

    body = {
        "schema": "Venus.AutonomousChangeCandidate.v0.1",
        "cycle_id": str(cycle["cycle_id"]),
        "proposal_id": str(proposal["proposal_id"]),
        "evidence_id": str(evidence["evidence_id"]),
        "target_kind": str(cycle["target_kind"]),
        "target_number": int(cycle["target_number"]),
        "disposition": disposition,
        "reason": reason,
        "failed_target_check_ids": failed_target,
        "failed_process_check_ids": failed_process,
        "untrusted_implicated_paths": implicated,
        "suggested_operation": operation,
        "target_text_is_authority": False,
        "source_mutation_authority": False,
        "promotion_authority": False,
    }
    return AutonomousChangeCandidate(change_id=digest(body), **body)


def change_dict(change: AutonomousChangeCandidate) -> dict[str, Any]:
    return asdict(change)
