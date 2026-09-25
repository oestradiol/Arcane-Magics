from __future__ import annotations

"""Typed external-return intake for live bounded recurrence candidates."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from kernel.development.autonomous_learning import (
    SELF_REVIEW_LOGINS,
    authorized_return_logins,
)
from kernel.runtime.bounded_recurrence import (
    BoundedRecurrenceError,
    author_candidate,
    candidate_dict,
)


TRAINING_PREFIX = "VENUS_RECURRENCE_TRAINING_V1:"
TRAINING_RE = re.compile(
    r"^VENUS_RECURRENCE_TRAINING_V1:\s*(\{.*\})\s*$",
    re.M,
)


class AutonomousRecurrenceError(ValueError):
    pass


def _review_login(review: Mapping[str, Any]) -> str:
    author = review.get("author") or {}
    return str(author.get("login") or "") if isinstance(author, Mapping) else ""


def _review_time(review: Mapping[str, Any]) -> str:
    return str(
        review.get("submittedAt")
        or review.get("submitted_at")
        or review.get("createdAt")
        or review.get("created_at")
        or ""
    )


def _review_body(review: Mapping[str, Any]) -> str:
    return str(review.get("body") or "")


def _fingerprint(
    *,
    carrier_kind: str,
    carrier_number: int,
    login: str,
    body: str,
    returned_at: str,
) -> str:
    raw = json.dumps({
        "carrier_kind": carrier_kind,
        "carrier_number": carrier_number,
        "login": login.lower(),
        "body": body,
        "returned_at": returned_at,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_catalog(path: str | Path) -> dict[str, Any]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("schema") != "Venus.AutonomousRecurrenceCatalog.v0.1":
        raise AutonomousRecurrenceError("unsupported recurrence catalog schema")
    for key in (
        "autonomy_may_add_programs",
        "autonomy_may_change_patch_ops",
        "autonomy_may_modify_return_authority",
        "promotion_authority",
        "merge_authority",
        "truth_authority",
    ):
        if obj.get(key) is not False:
            raise AutonomousRecurrenceError(f"catalog authority invariant violated: {key}")
    return obj


def _program_row(catalog: Mapping[str, Any], program_id: str) -> Mapping[str, Any]:
    rows = [x for x in catalog.get("programs", ()) if str(x.get("program_id")) == program_id]
    if len(rows) != 1:
        raise AutonomousRecurrenceError("program id is not uniquely allowlisted")
    return rows[0]


def _validate_trace(row: Mapping[str, Any], *, max_payload_fields: int) -> dict[str, Any]:
    payload = row.get("payload")
    if not isinstance(payload, Mapping):
        raise AutonomousRecurrenceError("recurrence trace payload must be an object")
    if len(payload) > max_payload_fields:
        raise AutonomousRecurrenceError("recurrence trace payload exceeds field limit")
    if not row.get("prior_state") or not row.get("action"):
        raise AutonomousRecurrenceError("trace state/action required")
    if row.get("expected_next_state") is not None and not isinstance(
        row.get("expected_next_state"), str
    ):
        raise AutonomousRecurrenceError("expected_next_state must be string or null")
    return {
        "trace_id": str(row.get("trace_id") or ""),
        "prior_state": str(row["prior_state"]),
        "action": str(row["action"]),
        "payload": dict(payload),
        "expect_success": bool(row.get("expect_success")),
        "expected_next_state": row.get("expected_next_state"),
        "provenance_id": str(row.get("provenance_id") or ""),
    }


def extract_training_returns(
    carriers: Iterable[Mapping[str, Any]],
    *,
    catalog: Mapping[str, Any],
    authorized_logins: Iterable[str] | None = None,
) -> tuple[dict[str, Any], ...]:
    authority = (
        authorized_return_logins()
        if authorized_logins is None
        else frozenset(str(x).strip().lower() for x in authorized_logins if str(x).strip())
    )
    if not authority or "*" in authority:
        raise AutonomousRecurrenceError("recurrence return authority must be explicit")
    if authority & SELF_REVIEW_LOGINS:
        raise AutonomousRecurrenceError("self-review identity cannot authorize recurrence return")

    out: list[dict[str, Any]] = []
    for carrier in carriers:
        carrier_kind = str(carrier.get("_carrier_kind") or "PR").upper()
        carrier_number = int(carrier.get("number", 0) or 0)
        returned_items = carrier.get("reviews") or carrier.get("comments") or ()
        for review in returned_items:
            login = _review_login(review).lower()
            if not login or login in SELF_REVIEW_LOGINS or login not in authority:
                continue
            returned_at = _review_time(review)
            if not returned_at:
                continue
            body = _review_body(review)
            matches = tuple(TRAINING_RE.finditer(body))
            for match in matches:
                try:
                    raw = json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
                if raw.get("schema") != "Venus.LiveRecurrenceTrainingReturn.v0.1":
                    continue
                problem_id = str(raw.get("problem_id") or "")
                program_id = str(raw.get("program_id") or "")
                if not problem_id or not program_id:
                    continue
                program = _program_row(catalog, program_id)
                max_traces = int(program.get("max_training_traces", 0) or 0)
                max_fields = int(program.get("max_payload_fields", 0) or 0)
                traces_in = tuple(raw.get("traces", ()))
                if not traces_in or len(traces_in) > max_traces:
                    continue
                try:
                    traces = tuple(
                        _validate_trace(row, max_payload_fields=max_fields)
                        for row in traces_in
                    )
                except AutonomousRecurrenceError:
                    continue
                if any(not row["provenance_id"] for row in traces):
                    continue
                fingerprint = _fingerprint(
                    carrier_kind=carrier_kind,
                    carrier_number=carrier_number,
                    login=login,
                    body=body,
                    returned_at=returned_at,
                )
                out.append({
                    "schema": raw["schema"],
                    "return_id": f"live-recurrence-return:{fingerprint}",
                    "return_owner": "EXTERNAL_EVALUATOR",
                    "exposure": "PUBLIC_DEVELOPMENT_RETURN",
                    "problem_id": problem_id,
                    "program_id": program_id,
                    "traces": list(traces),
                    "review_login": login,
                    "returned_at": returned_at,
                    "carrier_kind": carrier_kind,
                    "carrier_number": carrier_number,
                    "promotion_authority": False,
                })
    return tuple(out)


def make_live_candidate(
    *,
    problem: Mapping[str, Any],
    carriers: Iterable[Mapping[str, Any]],
    catalog: Mapping[str, Any],
    repository_root: str | Path,
    authorized_logins: Iterable[str] | None = None,
) -> dict[str, Any]:
    problem_id = str(problem.get("problem_id") or "")
    if problem.get("disposition") != "FORMED_BOUNDED_PROBLEM" or not problem_id:
        return {
            "schema": "Venus.LiveRecurrenceCandidateEnvelope.v0.1",
            "status": "NO_FORMED_PROBLEM",
            "generated": False,
            "promotion_authority": False,
        }

    eligible = tuple(
        row for row in extract_training_returns(
            carriers,
            catalog=catalog,
            authorized_logins=authorized_logins,
        )
        if row["problem_id"] == problem_id
    )
    if not eligible:
        return {
            "schema": "Venus.LiveRecurrenceCandidateEnvelope.v0.1",
            "status": "AWAITING_PROBLEM_SPECIFIC_EXTERNAL_RETURN",
            "generated": False,
            "problem_id": problem_id,
            "promotion_authority": False,
        }
    if len(eligible) != 1:
        return {
            "schema": "Venus.LiveRecurrenceCandidateEnvelope.v0.1",
            "status": "WITHHOLD_AMBIGUOUS_EXTERNAL_RETURNS",
            "generated": False,
            "problem_id": problem_id,
            "return_ids": sorted(row["return_id"] for row in eligible),
            "promotion_authority": False,
        }

    returned = eligible[0]
    program_row = _program_row(catalog, returned["program_id"])
    rel = Path(str(program_row["path"]))
    if rel.is_absolute() or ".." in rel.parts:
        raise AutonomousRecurrenceError("catalog program path must be repository-relative")
    root = Path(repository_root).resolve()
    path = (root / rel).resolve()
    if root not in path.parents:
        raise AutonomousRecurrenceError("catalog program path escapes repository")
    parent = json.loads(path.read_text(encoding="utf-8"))
    if str(parent.get("program_id")) != returned["program_id"]:
        raise AutonomousRecurrenceError("catalog/program identity mismatch")

    try:
        candidate, successor, search_status = author_candidate(
            problem=problem,
            parent_program=parent,
            training_return=returned,
            allowed_patch_ops=tuple(program_row.get("allowed_patch_ops", ())),
            author_id="venus-live-recurrence-search",
        )
    except BoundedRecurrenceError as exc:
        raise AutonomousRecurrenceError(str(exc)) from exc

    if candidate is None or successor is None:
        return {
            "schema": "Venus.LiveRecurrenceCandidateEnvelope.v0.1",
            "status": search_status,
            "generated": False,
            "problem_id": problem_id,
            "training_return_id": returned["return_id"],
            "promotion_authority": False,
        }
    return {
        "schema": "Venus.LiveRecurrenceCandidateEnvelope.v0.1",
        "status": "CANDIDATE_FROZEN_AWAITING_HELDOUT_RETURN",
        "generated": True,
        "problem_id": problem_id,
        "program_id": returned["program_id"],
        "program_path": str(rel),
        "candidate": candidate_dict(candidate),
        "successor_program": successor,
        "training_return_id": returned["return_id"],
        "external_reviewer": returned["review_login"],
        "returned_at": returned["returned_at"],
        "merge_authority": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
