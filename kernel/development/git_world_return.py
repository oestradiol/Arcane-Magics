from __future__ import annotations

"""Typed GitHub World request/return for prospective autonomous recurrence.

GitHub is treated as an external carrier/World interface. A request freezes one
problem-specific observation before the answer is known. A later repository/
workflow observation may satisfy it only when the source identity matches and
the observed World state changed after freeze.

Local execution receipts, reviewer prose, and learner-authored labels are not
accepted as World returns by this module.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Mapping

from kernel.runtime.vmk2 import digest


class GitWorldReturnError(ValueError):
    pass


@dataclass(frozen=True)
class GitCarrierSnapshot:
    carrier_kind: str
    carrier_number: int
    head_sha: str
    merge_state: str
    updated_at: str
    check_run_id: int | None
    check_status: str | None
    check_conclusion: str | None


@dataclass(frozen=True)
class GitWorldRequest:
    schema: str
    request_id: str
    problem_id: str
    source_stream_id: str
    discriminator: str
    carrier_kind: str
    carrier_number: int
    frozen_snapshot_digest: str
    frozen_head_sha: str
    frozen_merge_state: str
    frozen_updated_at: str
    frozen_check_run_id: int | None
    frozen_check_status: str | None
    accepted_observation_fields: tuple[str, ...]
    promotion_authority: bool = False


@dataclass(frozen=True)
class GitWorldReturn:
    schema: str
    return_id: str
    request_id: str
    problem_id: str
    source_id: str
    observed_snapshot_digest: str
    observed_at: str
    changed_fields: tuple[str, ...]
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    independent_world_observation: bool
    promotion_authority: bool = False


@dataclass(frozen=True)
class GitProblemResolution:
    schema: str
    resolution_id: str
    problem_id: str
    request_id: str
    return_id: str
    disposition: str
    remaining_rival_ids: tuple[str, ...]
    external_return_consumed: bool
    promotion_authority: bool = False


def _time(value: str) -> datetime:
    if not value:
        raise GitWorldReturnError("timestamp required")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def snapshot_dict(snapshot: GitCarrierSnapshot) -> dict[str, Any]:
    return asdict(snapshot)


def snapshot_digest(snapshot: GitCarrierSnapshot) -> str:
    return digest(snapshot_dict(snapshot))



def form_git_check_problem(snapshot: GitCarrierSnapshot) -> dict[str, Any]:
    """Form one neutral bounded problem from a nonterminal GitHub check state.

    The problem is defined from returned structural state only. It does not
    encode the later check conclusion.
    """
    if snapshot.carrier_kind.upper() != "PR":
        raise GitWorldReturnError("first bounded Git check problem supports PR carriers only")
    status = str(snapshot.check_status or "").lower()
    if status == "completed":
        body = {
            "schema": "Venus.GitCheckProblem.v0.1",
            "disposition": "STOP_NO_CONSEQUENTIAL_RESIDUAL",
            "source_stream_ids": (),
            "residual_coordinates": (),
            "discriminator": None,
            "rivals": (),
            "external_return_required": False,
            "carrier_binding_authority": False,
            "promotion_authority": False,
        }
        return {"problem_id": digest(body), **body}

    source_stream_id = digest({
        "carrier_kind": snapshot.carrier_kind.upper(),
        "carrier_number": int(snapshot.carrier_number),
    })
    rivals = (
        {
            "rival_id": "r0",
            "statement": "the unresolved continuation later terminates unsuccessfully",
        },
        {
            "rival_id": "r1",
            "statement": "the unresolved continuation is transient and later terminates successfully",
        },
    )
    body = {
        "schema": "Venus.GitCheckProblem.v0.1",
        "disposition": "FORMED_BOUNDED_PROBLEM",
        "source_stream_ids": (source_stream_id,),
        "residual_coordinates": ("check_state_nonterminal",),
        "discriminator": "OBSERVE_PR_CHECK_TERMINAL_STATE",
        "rivals": rivals,
        "external_return_required": True,
        "carrier_binding_authority": False,
        "promotion_authority": False,
    }
    return {"problem_id": digest(body), **body}


def freeze_git_world_request(
    *,
    problem: Mapping[str, Any],
    source_stream_id: str,
    snapshot: GitCarrierSnapshot,
) -> GitWorldRequest:
    if problem.get("disposition") != "FORMED_BOUNDED_PROBLEM":
        raise GitWorldReturnError("formed bounded problem required")
    problem_id = str(problem.get("problem_id") or "")
    discriminator = str(problem.get("discriminator") or "")
    sources = tuple(str(x) for x in problem.get("source_stream_ids", ()))
    if not problem_id or not discriminator:
        raise GitWorldReturnError("problem identity and discriminator required")
    if source_stream_id not in sources:
        raise GitWorldReturnError("request source is not a prefrozen problem source")
    if snapshot.carrier_kind.upper() != "PR":
        raise GitWorldReturnError("first bounded Git World adapter supports PR carriers only")
    _time(snapshot.updated_at)

    body = {
        "schema": "Venus.GitWorldRequest.v0.1",
        "problem_id": problem_id,
        "source_stream_id": source_stream_id,
        "discriminator": discriminator,
        "carrier_kind": snapshot.carrier_kind.upper(),
        "carrier_number": int(snapshot.carrier_number),
        "frozen_snapshot_digest": snapshot_digest(snapshot),
        "frozen_head_sha": snapshot.head_sha,
        "frozen_merge_state": snapshot.merge_state.upper(),
        "frozen_updated_at": snapshot.updated_at,
        "frozen_check_run_id": snapshot.check_run_id,
        "frozen_check_status": snapshot.check_status,
        "accepted_observation_fields": (
            "head_sha",
            "merge_state",
            "updated_at",
            "check_run_id",
            "check_status",
            "check_conclusion",
        ),
        "promotion_authority": False,
    }
    return GitWorldRequest(request_id=digest(body), **body)


def observe_git_world_return(
    request: GitWorldRequest,
    snapshot: GitCarrierSnapshot,
    *,
    observed_at: str,
) -> GitWorldReturn:
    if snapshot.carrier_kind.upper() != request.carrier_kind:
        raise GitWorldReturnError("carrier kind mismatch")
    if int(snapshot.carrier_number) != request.carrier_number:
        raise GitWorldReturnError("carrier number mismatch")
    observed_time = _time(observed_at)
    frozen_time = _time(request.frozen_updated_at)
    if observed_time <= frozen_time:
        raise GitWorldReturnError("World observation must be later than freeze")

    before = {
        "head_sha": request.frozen_head_sha,
        "merge_state": request.frozen_merge_state,
        "updated_at": request.frozen_updated_at,
        "check_run_id": request.frozen_check_run_id,
        "check_status": request.frozen_check_status,
        "check_conclusion": None,
    }
    after = {
        "head_sha": snapshot.head_sha,
        "merge_state": snapshot.merge_state.upper(),
        "updated_at": snapshot.updated_at,
        "check_run_id": snapshot.check_run_id,
        "check_status": snapshot.check_status,
        "check_conclusion": snapshot.check_conclusion,
    }
    changed = tuple(
        key for key in request.accepted_observation_fields
        if before.get(key) != after.get(key)
    )
    if not changed:
        raise GitWorldReturnError("same-state replay is not a fresh World return")

    body = {
        "schema": "Venus.GitWorldReturn.v0.1",
        "request_id": request.request_id,
        "problem_id": request.problem_id,
        "source_id": "GITHUB_REPOSITORY_STATE",
        "observed_snapshot_digest": snapshot_digest(snapshot),
        "observed_at": observed_at,
        "changed_fields": changed,
        "before": before,
        "after": after,
        "independent_world_observation": True,
        "promotion_authority": False,
    }
    return GitWorldReturn(return_id=digest(body), **body)


def resolve_continuation_problem(
    problem: Mapping[str, Any],
    request: GitWorldRequest,
    returned: GitWorldReturn,
) -> GitProblemResolution:
    if str(problem.get("problem_id") or "") != request.problem_id:
        raise GitWorldReturnError("problem/request identity mismatch")
    if returned.request_id != request.request_id or returned.problem_id != request.problem_id:
        raise GitWorldReturnError("return does not answer the frozen request")
    if returned.source_id != "GITHUB_REPOSITORY_STATE":
        raise GitWorldReturnError("only GitHub repository state may satisfy this request")
    if not returned.independent_world_observation:
        raise GitWorldReturnError("return is not independently observed World state")

    rival_ids = tuple(str(x.get("rival_id")) for x in problem.get("rivals", ()))
    discriminator = str(problem.get("discriminator") or "")
    after_status = str(returned.after.get("check_status") or "").lower()
    after_conclusion = str(returned.after.get("check_conclusion") or "").lower()
    after_merge = str(returned.after.get("merge_state") or "").upper()

    if discriminator == "OBSERVE_PR_CHECK_TERMINAL_STATE":
        if after_status != "completed":
            disposition = "WITHHOLD_CHANGED_BUT_NONTERMINAL"
            remaining = rival_ids
        elif after_conclusion == "success":
            disposition = "RETURN_REDUCED_RIVALS"
            remaining = ("r1",) if "r1" in rival_ids else rival_ids[:1]
        else:
            disposition = "RETURN_REDUCED_RIVALS"
            remaining = ("r0",) if "r0" in rival_ids else rival_ids[:1]
    elif discriminator == "REPRODUCE_OR_REFRESH_CONTINUATION_STATE":
        unresolved = {"DIRTY", "BLOCKED", "CONFLICTING", "UNKNOWN", "UNSTABLE"}
        if after_merge not in unresolved:
            disposition = "RETURN_REDUCED_RIVALS"
            remaining = ("r1",) if "r1" in rival_ids else rival_ids[:1]
        else:
            disposition = "WITHHOLD_CHANGED_BUT_UNRESOLVED"
            remaining = rival_ids
    else:
        disposition = "WITHHOLD_UNSUPPORTED_GIT_DISCRIMINATOR"
        remaining = rival_ids

    body = {
        "schema": "Venus.GitProblemResolution.v0.1",
        "problem_id": request.problem_id,
        "request_id": request.request_id,
        "return_id": returned.return_id,
        "disposition": disposition,
        "remaining_rival_ids": remaining,
        "external_return_consumed": True,
        "promotion_authority": False,
    }
    return GitProblemResolution(resolution_id=digest(body), **body)
