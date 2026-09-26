from __future__ import annotations

"""Canonical machine action proposals.

A proposal is inert data. This module intentionally does not import or invoke
ProcessBridge. Execution belongs to a separately authorized external boundary.
"""

from dataclasses import asdict, dataclass
import base64
from typing import Any, Iterable, Mapping

from kernel.runtime.canonical import digest


class ActionProposalError(ValueError):
    pass


@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    kind: str
    argv: tuple[str, ...]
    cwd: str
    stdin_base64: str
    rationale: str
    expected_return: str
    requested_capability: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def propose_process(
    argv: Iterable[str],
    *,
    cwd: str = ".",
    stdin: bytes = b"",
    rationale: str,
    expected_return: str,
    requested_capability: str = "BOUNDED_PROCESS_EXECUTION",
) -> ActionProposal:
    args = tuple(str(x) for x in argv)
    if not args:
        raise ActionProposalError("argv cannot be empty")
    if not rationale.strip():
        raise ActionProposalError("rationale required")
    if not expected_return.strip():
        raise ActionProposalError("expected_return required")

    payload = {
        "schema": "Venus.WorldMirrorActionProposal.v0.1",
        "kind": "PROCESS",
        "argv": args,
        "cwd": str(cwd),
        "stdin_base64": base64.b64encode(stdin).decode("ascii"),
        "rationale": rationale,
        "expected_return": expected_return,
        "requested_capability": requested_capability,
    }
    return ActionProposal(
        proposal_id=digest(payload),
        kind="PROCESS",
        argv=args,
        cwd=str(cwd),
        stdin_base64=payload["stdin_base64"],
        rationale=rationale,
        expected_return=expected_return,
        requested_capability=requested_capability,
    )


def authorization_matches(
    proposal: ActionProposal,
    authorization: Mapping[str, Any],
) -> bool:
    """Check a returned external authorization object's binding only.

    This does not establish that the authorization issuer is trustworthy.
    Issuer authentication/jurisdiction remains outside this module.
    """
    return (
        authorization.get("schema") == "Venus.WorldMirrorActionAuthorization.v0.1"
        and authorization.get("proposal_id") == proposal.proposal_id
        and authorization.get("authorized") is True
        and bool(authorization.get("authorization_id"))
        and bool(authorization.get("issuer"))
    )
