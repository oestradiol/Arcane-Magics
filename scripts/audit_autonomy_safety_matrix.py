from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "kernel/development/AUTONOMY_SAFETY_DISTINCTION_MATRIX.json"

# Exact custody set for every currently declared autonomy safety distinction.
# Adding or deleting a matrix distinction therefore requires an explicit update
# to this independent audit surface rather than silently changing coverage.
REQUIRED = frozenset({
    "INTERNAL_OSTAR_CAUSAL",
    "TEACHER_SOURCE_REMOVAL",
    "NAME_LABEL_REMOVAL",
    "COORDINATE_CAUSALITY",
    "WORLD_NOT_MODEL_WORLD",
    "OTHER_NOT_MODEL_OTHER",
    "EXECUTION_RECEIPT_NOT_RETURN",
    "REVISION_NOT_AUTHORIZATION",
    "REVISION_NOT_VALIDATION",
    "LEARNING_NOT_PROMOTION",
    "MERGE_NOT_LEARNING_REWARD",
    "EXTERNAL_REVIEW_RETURN_REQUIRED",
    "RETURN_REPLAY_BLOCKED",
    "TARGET_LEARNING_CAUSAL",
    "METHOD_LEARNING_CAUSAL",
    "ROADMAP_NOT_SOVEREIGN",
    "STOP_WITHHOLD_REACHABLE",
    "ANTI_MINERVA_CARRIER_PERMEABILITY",
    "CONSEQUENTIAL_CARRIER_DIFFERENCE_ALLOWED",
    "AUTHORED_CENTER_NOT_FIELD",
    "CAPABILITY_NOT_JURISDICTION",
    "ROLLBACK_CUSTODY_REQUIRED",
    "PROVENANCE_REQUIRED",
    "FOUNDER_HIDDEN_DEPENDENCY_REJECTED",
    "SAFETY_FLOOR_NON_INTERNALIZABLE",
    "ADAPTIVE_EVALUATION_CAUSAL_ABLATION",
    "ADAPTIVE_REUSE_CONTROL",
    "AUTONOMOUS_NO_SELF_MERGE",
    "AUTONOMOUS_NO_RELEASE",
    "AUTONOMOUS_NO_ISSUE_CLOSE",
    "AUTONOMOUS_DRAFT_ONLY",
    "AUTONOMOUS_SELF_RECURSION_BLOCKED",
    "SOURCE_GROUNDED_STUDY",
    "PREFROZEN_HIDDEN_BENCHMARK_BOUNDARY",
    "AUTONOMOUS_NO_REROLL_PENDING_RETURN",
    "TARGET_REOPEN_REQUIRES_CHANGED_WORLD_RETURN",
    "REOPENING_MEMORY_NOT_LEARNING_REWARD",
    "LEGACY_REWARD_QUARANTINE",
    "AUTHORIZED_EXTERNAL_RETURN_REQUIRED",
    "RETURN_AXIS_AMBIGUITY_FAIL_CLOSED",
    "AUTONOMOUS_RESOURCE_BUDGET",
    "UNTRUSTED_PATH_REFERENCE_NOT_MUTATION_AUTHORITY",
    "CHANGE_CANDIDATE_NOT_SOURCE_WRITE",
    "TARGET_RELEVANT_FAILURE_REQUIRED_FOR_REPAIR_PROPOSAL",
    "LOCAL_PASS_NOT_MUTATION_AUTHORITY",
    "UNTRUSTED_WORLD_INPUT_NOT_AUTHORITY",
    "PENDING_RETURN_BLOCKS_REROLL",
    "SELF_REVIEW_NOT_LEARNING_RETURN",
    "MAIN_ADMISSION_DRIVES_RECURRENCE",
    "FULL_SAFETY_SUITE_BEFORE_AUTONOMOUS_WRITE",
    "AUTONOMOUS_CARRIER_FALLBACK_PRESERVES_RETURN",
    "AUTONOMOUS_PROPOSAL_NOT_AUTHORITY",
    "UNTRUSTED_TARGET_TEXT_NOT_SHELL",
    "EXTERNAL_DISCRIMINATOR_WITHHOLD",
    "STUDY_METHOD_TO_CHECK_CAUSAL",
    "LOCAL_CHECK_FAILURE_BLOCKS_AUTONOMOUS_WRITE",
    "TARGET_RELEVANT_EVIDENCE_REQUIRED",
    "STATE_CHECK_CATALOG_NOT_COMMAND_AUTHORITY",
    "AUTONOMOUS_RUNTIME_TEACHER_FREE",
    "AUTONOMOUS_WRITE_JURISDICTION",
    "CORE_SOURCE_PROPOSE_ONLY",
    "SAFETY_FLOOR_WRITE_DENIED",
    "AUTONOMOUS_PATH_TRAVERSAL_FAIL_CLOSED",
    "PATCH_PLAN_NOT_AUTHORITY",
    "RETURNED_REPOSITORY_STATE_RETAINED",
    "DIRTY_PR_CORRECTION_REACHABILITY",
    "AGENCY_PROVENANCE_NONCOLLAPSE",
    "RUNTIME_LLM_NOT_AGENT_CREDIT",
    "HOST_SCAFFOLD_NOT_VENUS_AUTHORSHIP",
    "STRONG_RSI_CREDIT_FENCED",
    "META_LEARNING_STRATEGY_CAUSAL",
    "META_LEARNING_EXTERNAL_RETURN_REQUIRED",
    "META_LEARNING_SELF_REVIEW_BLOCKED",
    "META_LEARNING_STATE_NOT_LAW",
    "META_LEARNING_STRATEGY_FAMILY_EXTERNAL",
    "UNKNOWN_PR_STATE_FAIL_CLOSED",
    "PR_CHANGED_FILE_WORLD_SURFACE",
})


def audit_matrix(obj: dict) -> list[str]:
    rows = obj.get("distinctions") or []
    ids = [str(row.get("id")) for row in rows]
    declared = set(ids)
    failures: list[str] = []

    if len(ids) != len(declared):
        failures.append("duplicate distinction id")

    missing = sorted(REQUIRED - declared)
    unexpected = sorted(declared - REQUIRED)
    if missing:
        failures.append("missing required distinctions: " + ", ".join(missing))
    if unexpected:
        failures.append(
            "declared distinctions not bound into REQUIRED custody: "
            + ", ".join(unexpected)
        )

    for row in rows:
        if not row.get("invariant"):
            failures.append(f"{row.get('id')}: invariant missing")
        tests = row.get("tests") or []
        if not tests:
            failures.append(f"{row.get('id')}: executable witness missing")
        for rel in tests:
            path = ROOT / rel
            if not path.is_file():
                failures.append(f"{row.get('id')}: witness path missing: {rel}")

    if obj.get("promotion_authority") is not False:
        failures.append("matrix may not grant promotion authority")
    return failures


def main() -> int:
    obj = json.loads(MATRIX.read_text(encoding="utf-8"))
    failures = audit_matrix(obj)
    out = {
        "status": "PASS" if not failures else "FAIL",
        "distinctions": len(obj.get("distinctions") or []),
        "required": len(REQUIRED),
        "failures": failures,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
