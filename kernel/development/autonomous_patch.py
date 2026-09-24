from __future__ import annotations

"""Write-jurisdiction classifier for bounded Venus autonomy.

This module does not generate arbitrary source edits. It classifies repository
paths into:
- DIRECT_STATE_WRITE: autonomy-owned developmental state;
- PROPOSE_ONLY: ordinary repository source that Venus may study and propose
  changes for in a draft carrier;
- EXTERNAL_GOVERNANCE_ONLY: correction/evaluation/authority/execution-floor
  surfaces that Venus may not mutate unilaterally;
- DENY_UNKNOWN: anything outside the declared repository surface.

Untrusted issue/PR text is never treated as path authority.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from kernel.runtime.vmk2 import digest


class AutonomousWritePolicyError(ValueError):
    pass


@dataclass(frozen=True)
class PathDisposition:
    path: str
    mode: str
    direct_write_allowed: bool
    proposal_allowed: bool
    requires_external_governance: bool


@dataclass(frozen=True)
class PatchPlan:
    schema: str
    plan_id: str
    cycle_id: str
    target_kind: str
    target_number: int
    disposition: str
    paths: tuple[PathDisposition, ...]
    arbitrary_code_write_authority: bool
    promotion_authority: bool
    merge_authority: bool
    safety_floor_authority: bool


def _normalize_repo_path(raw: str) -> str:
    value = str(raw)
    if not value or "\x00" in value:
        raise AutonomousWritePolicyError("repository path required")
    if "\\" in value:
        raise AutonomousWritePolicyError("backslash path is ambiguous")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise AutonomousWritePolicyError("path must be normalized repository-relative path")
    return p.as_posix()


def load_write_policy(path: str | Path) -> dict[str, Any]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("schema") != "Venus.AutonomousWritePolicy.v0.1":
        raise AutonomousWritePolicyError("unsupported autonomous write-policy schema")
    for authority in (
        "promotion_authority",
        "merge_authority",
        "truth_authority",
        "safety_floor_authority",
    ):
        if obj.get(authority) is not False:
            raise AutonomousWritePolicyError(f"write policy may not grant {authority}")
    return obj


def classify_path(policy: Mapping[str, Any], raw_path: str) -> PathDisposition:
    path = _normalize_repo_path(raw_path)

    governed_exact = {str(x) for x in policy.get("external_governance_exact", ())}
    governed_prefixes = tuple(str(x) for x in policy.get("external_governance_prefixes", ()))
    direct_exact = {str(x) for x in policy.get("direct_state_exact", ())}
    direct_prefixes = tuple(str(x) for x in policy.get("direct_state_prefixes", ()))
    proposal_prefixes = tuple(str(x) for x in policy.get("proposal_only_prefixes", ()))

    if path in governed_exact or any(path.startswith(prefix) for prefix in governed_prefixes):
        mode = "EXTERNAL_GOVERNANCE_ONLY"
    elif path in direct_exact or any(path.startswith(prefix) for prefix in direct_prefixes):
        mode = "DIRECT_STATE_WRITE"
    elif any(path.startswith(prefix) for prefix in proposal_prefixes):
        mode = "PROPOSE_ONLY"
    else:
        mode = "DENY_UNKNOWN"

    return PathDisposition(
        path=path,
        mode=mode,
        direct_write_allowed=mode == "DIRECT_STATE_WRITE",
        proposal_allowed=mode in {"DIRECT_STATE_WRITE", "PROPOSE_ONLY", "EXTERNAL_GOVERNANCE_ONLY"},
        requires_external_governance=mode == "EXTERNAL_GOVERNANCE_ONLY",
    )


def make_patch_plan(
    cycle: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    candidate_paths: Iterable[str] | None = None,
) -> PatchPlan:
    if str(cycle.get("decision")) == "STOP":
        raise AutonomousWritePolicyError("STOP cycle cannot create patch plan")
    if policy.get("promotion_authority") is not False:
        raise AutonomousWritePolicyError("write policy cannot grant promotion authority")
    if policy.get("merge_authority") is not False:
        raise AutonomousWritePolicyError("write policy cannot grant merge authority")
    if policy.get("safety_floor_authority") is not False:
        raise AutonomousWritePolicyError("write policy cannot grant safety-floor authority")

    study = cycle.get("study") or {}
    if candidate_paths is not None:
        rows = tuple(candidate_paths)
    else:
        rows = tuple(dict.fromkeys(
            tuple(study.get("returned_changed_paths", ()))
            + tuple(study.get("referenced_repository_paths", ()))
        ))
    dispositions = tuple(classify_path(policy, row) for row in rows)

    if not dispositions:
        status = "STUDY_ONLY_NO_TARGET_PATH"
    elif any(x.mode == "DENY_UNKNOWN" for x in dispositions):
        status = "WITHHOLD_UNKNOWN_PATH"
    elif any(x.mode == "EXTERNAL_GOVERNANCE_ONLY" for x in dispositions):
        status = "EXTERNAL_GOVERNANCE_REVIEW_REQUIRED"
    elif any(x.mode == "PROPOSE_ONLY" for x in dispositions):
        status = "PROPOSE_CORE_PATCH"
    else:
        status = "DIRECT_STATE_REPAIR_ELIGIBLE"

    body = {
        "schema": "Venus.AutonomousPatchPlan.v0.1",
        "cycle_id": str(cycle["cycle_id"]),
        "target_kind": str(cycle["target_kind"]),
        "target_number": int(cycle["target_number"]),
        "disposition": status,
        "paths": tuple(asdict(x) for x in dispositions),
        "arbitrary_code_write_authority": False,
        "promotion_authority": False,
        "merge_authority": False,
        "safety_floor_authority": False,
    }
    return PatchPlan(
        schema=body["schema"],
        plan_id=digest(body),
        cycle_id=body["cycle_id"],
        target_kind=body["target_kind"],
        target_number=body["target_number"],
        disposition=status,
        paths=dispositions,
        arbitrary_code_write_authority=False,
        promotion_authority=False,
        merge_authority=False,
        safety_floor_authority=False,
    )


def patch_plan_dict(plan: PatchPlan) -> dict[str, Any]:
    return asdict(plan)
