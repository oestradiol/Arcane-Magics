from __future__ import annotations

"""Bounded meta-learning state for autonomous study-strategy selection.

The live autonomous worker already learns method utility. This module adds one
higher-order layer: explicit authorized external review may teach Venus which
admitted *method-selection strategy* is more useful.

The strategy family itself remains host-governed. This is bounded meta-learning,
not unrestricted self-modification and not full Strong RSI.
"""

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

from kernel.development.autonomous_learning import (
    SELF_REVIEW_LOGINS,
    authorized_return_logins,
)


STRATEGIES = (
    "RETURN_UTILITY_FIRST",
    "TARGET_SIGNAL_FIRST",
)

STRATEGY_RE = re.compile(
    r"VENUS_LEARNING_STRATEGY_RETURN:\s*("
    + "|".join(STRATEGIES)
    + r"):\s*(USEFUL|UNHELPFUL)",
    re.I,
)


@dataclass(frozen=True)
class MetaLearningState:
    seen_return_ids: tuple[str, ...]
    strategy_success: Mapping[str, int]
    strategy_failure: Mapping[str, int]

    def utility(self, strategy: str) -> float:
        s = int(self.strategy_success.get(strategy, 0))
        f = int(self.strategy_failure.get(strategy, 0))
        total = s + f
        return 0.0 if total == 0 else (s - f) / total


def empty_meta_state() -> MetaLearningState:
    return MetaLearningState(
        seen_return_ids=(),
        strategy_success={x: 0 for x in STRATEGIES},
        strategy_failure={x: 0 for x in STRATEGIES},
    )


def from_json(obj: Mapping[str, Any]) -> MetaLearningState:
    if obj.get("schema") not in {
        "Venus.AutonomousMetaLearningState.v0.1",
    }:
        return empty_meta_state()
    return MetaLearningState(
        seen_return_ids=tuple(str(x) for x in obj.get("seen_return_ids", ())),
        strategy_success={
            s: int((obj.get("strategy_success") or {}).get(s, 0))
            for s in STRATEGIES
        },
        strategy_failure={
            s: int((obj.get("strategy_failure") or {}).get(s, 0))
            for s in STRATEGIES
        },
    )


def to_json(state: MetaLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousMetaLearningState.v0.1",
        "seen_return_ids": list(state.seen_return_ids),
        "strategy_success": dict(state.strategy_success),
        "strategy_failure": dict(state.strategy_failure),
        "promotion_authority": False,
        "merge_authority": False,
        "truth_authority": False,
        "safety_floor_authority": False,
        "strategy_family_mutation_authority": False,
        "return_authority_mutation_authority": False,
    }


def _fingerprint(
    *,
    carrier_kind: str,
    carrier_number: int,
    login: str,
    body: str,
    returned_at: str,
    strategy: str,
) -> str:
    payload = {
        "carrier_kind": carrier_kind.upper(),
        "carrier_number": int(carrier_number),
        "author": login.lower(),
        "body": body,
        "returned_at": returned_at,
        "strategy": strategy,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def extract_strategy_returns(
    carriers: Iterable[Mapping[str, Any]],
    *,
    authorized_logins: Iterable[str] | None = None,
) -> tuple[tuple[str, str, bool], ...]:
    authority = (
        authorized_return_logins()
        if authorized_logins is None
        else frozenset(str(x).strip().lower() for x in authorized_logins if str(x).strip())
    )
    if not authority or "*" in authority:
        raise ValueError("meta-learning return authority must be explicit and non-wildcard")
    if authority & SELF_REVIEW_LOGINS:
        raise ValueError("self-review identity cannot authorize meta-learning return")

    out: list[tuple[str, str, bool]] = []
    for carrier in carriers:
        carrier_number = int(carrier.get("number", 0) or 0)
        carrier_kind = str(carrier.get("_carrier_kind") or "PR").upper()
        returned_items = carrier.get("reviews") or carrier.get("comments") or ()
        for review in returned_items:
            author = review.get("author") or {}
            login = str(author.get("login") or "") if isinstance(author, Mapping) else ""
            if not login or login.lower() not in authority or login.lower() in SELF_REVIEW_LOGINS:
                continue
            body = str(review.get("body") or "")
            returned_at = str(
                review.get("submittedAt")
                or review.get("submitted_at")
                or review.get("createdAt")
                or review.get("created_at")
                or ""
            )
            if not returned_at:
                continue

            grouped: dict[str, set[str]] = {}
            for match in STRATEGY_RE.finditer(body):
                grouped.setdefault(match.group(1).upper(), set()).add(match.group(2).upper())

            for strategy, dispositions in sorted(grouped.items()):
                if len(dispositions) != 1:
                    continue
                disposition = next(iter(dispositions))
                rid = "meta-return:" + _fingerprint(
                    carrier_kind=carrier_kind,
                    carrier_number=carrier_number,
                    login=login,
                    body=body,
                    returned_at=returned_at,
                    strategy=strategy,
                )
                out.append((rid, strategy, disposition == "USEFUL"))
    return tuple(out)


def update_from_cycle_carriers(
    state: MetaLearningState,
    carriers: Iterable[Mapping[str, Any]],
    *,
    authorized_logins: Iterable[str] | None = None,
) -> MetaLearningState:
    seen = set(state.seen_return_ids)
    success = dict(state.strategy_success)
    failure = dict(state.strategy_failure)

    for return_id, strategy, useful in extract_strategy_returns(
        carriers,
        authorized_logins=authorized_logins,
    ):
        if return_id in seen:
            continue
        (success if useful else failure)[strategy] = (
            (success if useful else failure).get(strategy, 0) + 1
        )
        seen.add(return_id)

    return MetaLearningState(
        seen_return_ids=tuple(sorted(seen)),
        strategy_success=success,
        strategy_failure=failure,
    )


def choose_strategy(state: MetaLearningState) -> str:
    """Choose the admitted selector strategy from returned meta-utility.

    With no learned preference, preserve the existing RETURN_UTILITY_FIRST
    behavior. A strategy only overtakes it through explicit external return.
    """
    ranked = sorted(
        STRATEGIES,
        key=lambda s: (
            -state.utility(s),
            0 if s == "RETURN_UTILITY_FIRST" else 1,
            s,
        ),
    )
    return ranked[0]
