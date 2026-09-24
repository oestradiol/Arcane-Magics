from __future__ import annotations

"""Deterministic repository study over one learner-selected GitHub target.

This is not a truth oracle or patch generator. It turns the external target
snapshot plus the frozen autonomous cycle into a bounded study receipt that can
be externally reviewed before stronger action.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from kernel.runtime.vmk2 import digest


@dataclass(frozen=True)
class StudyReceipt:
    schema: str
    study_id: str
    target_kind: str
    target_number: int
    disposition: str
    observations: tuple[str, ...]
    changed_files: tuple[str, ...]
    failed_checks: tuple[str, ...]
    pending_checks: tuple[str, ...]
    review_states: tuple[str, ...]
    related_paths: tuple[str, ...]
    next_discriminators: tuple[str, ...]
    source_digest: str
    promotion_authority: bool = False
    merge_authority: bool = False


def _checks(target: Mapping[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    failed, pending = [], []
    for row in target.get("statusCheckRollup") or ():
        if not isinstance(row, Mapping):
            continue
        name = str(row.get("name") or row.get("context") or row.get("workflowName") or "unnamed")
        conclusion = str(row.get("conclusion") or "").upper()
        status = str(row.get("status") or "").upper()
        if conclusion in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            failed.append(name)
        elif status in {"QUEUED", "IN_PROGRESS", "PENDING"}:
            pending.append(name)
    return tuple(sorted(set(failed))), tuple(sorted(set(pending)))


def study_target(
    *,
    cycle: Mapping[str, Any],
    target: Mapping[str, Any],
) -> StudyReceipt:
    kind = str(cycle.get("target_kind") or "").upper()
    number = int(cycle.get("target_number"))
    if kind not in {"ISSUE", "PR"}:
        raise ValueError("study requires ISSUE or PR target")

    failed, pending = _checks(target)
    changed_files = tuple(sorted(
        str(x.get("path") or x.get("filename"))
        for x in (target.get("files") or ())
        if isinstance(x, Mapping) and (x.get("path") or x.get("filename"))
    ))
    review_states = tuple(sorted(set(
        str(x.get("state") or "").upper()
        for x in (target.get("reviews") or ())
        if isinstance(x, Mapping) and x.get("state")
    )))
    related = tuple(str(x) for x in cycle.get("related_paths", ()))

    observations: list[str] = []
    discriminators: list[str] = []

    if kind == "PR":
        merge_state = str(target.get("mergeStateStatus") or "").upper()
        if merge_state in {"DIRTY", "BLOCKED", "CONFLICTING"}:
            observations.append("PR merge state reports an unresolved structural conflict")
            discriminators.append("identify whether conflict is mechanical or changes claim-bearing semantics")
        if failed:
            observations.append("external CI contains failing checks")
            discriminators.append("localize each failed check to the smallest implicated dependency before repair")
        if pending:
            observations.append("external CI return is still pending")
            discriminators.append("wait for pending checks before treating the current candidate as evaluated")
        if "CHANGES_REQUESTED" in review_states:
            observations.append("external review requested changes")
            discriminators.append("bind requested changes to exact review evidence before successor authorship")
        if not failed and not pending and merge_state not in {"DIRTY", "BLOCKED", "CONFLICTING"}:
            observations.append("no mechanical failure is visible in the current PR snapshot")
            discriminators.append("review claim/evidence/provenance scope before any merge recommendation")
    else:
        body = str(target.get("body") or "")
        comments = target.get("comments") or ()
        labels = target.get("labels") or ()
        observations.append(f"issue body captured ({len(body)} characters)")
        observations.append(f"issue has {len(comments)} returned comments and {len(labels)} labels in snapshot")
        discriminators.extend((
            "reconstruct the issue's current live disposition from authority-bearing repository state",
            "identify the smallest unresolved causal distinction rather than restating the issue title",
            "identify whether the next evidence can be produced locally or requires independent World return",
        ))

    if related:
        observations.append(f"{len(related)} repository paths were selected for local reconstruction")

    if failed:
        disposition = "REPAIR_RETURNED_FAILURE"
    elif pending:
        disposition = "WAIT_EXTERNAL_RETURN"
    elif kind == "PR" and str(target.get("mergeStateStatus") or "").upper() in {"DIRTY", "BLOCKED", "CONFLICTING"}:
        disposition = "REOPEN_STRUCTURAL_CONFLICT"
    else:
        disposition = "PROBE"

    source = {
        "cycle_id": cycle.get("cycle_id"),
        "target_kind": kind,
        "target_number": number,
        "target": target,
        "related_paths": related,
    }
    body = {
        "schema": "Venus.AutonomousTargetStudy.v0.1",
        "target_kind": kind,
        "target_number": number,
        "disposition": disposition,
        "observations": tuple(observations),
        "changed_files": changed_files,
        "failed_checks": failed,
        "pending_checks": pending,
        "review_states": review_states,
        "related_paths": related,
        "next_discriminators": tuple(discriminators),
        "source_digest": digest(source),
        "promotion_authority": False,
        "merge_authority": False,
    }
    return StudyReceipt(study_id=digest(body), **body)
