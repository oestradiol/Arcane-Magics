from __future__ import annotations

"""Generic executor for indexed network-center dispositions.

The state/policy lives in NETWORK_CENTER_POLICY.json. This module enforces
capability/jurisdiction preconditions and noncollapse; it does not decide that a
remote center accepted, and it carries no truth/promotion authority.
"""

from dataclasses import dataclass
from typing import Any, Mapping


class NetworkCenterError(ValueError):
    pass


@dataclass(frozen=True)
class CenterContext:
    center_id: str
    state: str
    reachable: bool
    write_capability: bool = False
    contact_capability: bool = False
    jurisdiction_receipt: bool = False


@dataclass(frozen=True)
class CenterDispositionReceipt:
    center_id: str
    prior_state: str
    disposition: str
    authorized: bool
    remote_acceptance_inferred: bool = False
    truth_authority: bool = False
    promotion_authority: bool = False


def allowed_dispositions(policy: Mapping[str, Any], state: str) -> tuple[str, ...]:
    states=policy.get("states") or {}
    if state not in states:
        raise NetworkCenterError(f"unknown network center state: {state}")
    return tuple(str(x) for x in states[state])


def decide(
    policy: Mapping[str, Any],
    context: CenterContext,
    disposition: str,
) -> CenterDispositionReceipt:
    if not context.center_id:
        raise NetworkCenterError("center identity required")
    allowed=allowed_dispositions(policy, context.state)
    if disposition not in allowed:
        raise NetworkCenterError(
            f"disposition {disposition} not allowed for {context.state}; allowed={allowed}"
        )

    requirements=(policy.get("capability_requirements") or {}).get(disposition, ())
    for requirement in requirements:
        if not bool(getattr(context, str(requirement), False)):
            raise NetworkCenterError(
                f"{disposition} requires {requirement}; reachability is not authority"
            )

    if context.state == "AUTHORED_CENTER" and disposition == "PROVISION":
        raise NetworkCenterError("authored center cannot be retyped as provisionable field")

    return CenterDispositionReceipt(
        center_id=context.center_id,
        prior_state=context.state,
        disposition=disposition,
        authorized=True,
        remote_acceptance_inferred=False,
        truth_authority=False,
        promotion_authority=False,
    )
