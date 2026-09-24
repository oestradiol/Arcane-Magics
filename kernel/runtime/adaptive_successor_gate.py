from __future__ import annotations

"""Adaptive successor acceptance gate.

Two evidence modes are deliberately separated:

1. SAMPLED: one-sided alpha-spending acceptance for noisy/repeated evaluation,
   using the repository's frozen schedule alpha_t = alpha/(t(t+1)).
2. EXHAUSTIVE_BOUNDED: deterministic acceptance only when the evaluator attests
   that the declared finite obligation domain was exhaustively checked.

The exhaustive path does not pretend finite specification checking is a
statistical sample. It also does not generalize outside that declared domain.
"""

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist
from typing import Literal

from .vmk2 import digest


class AdaptiveGateError(ValueError):
    pass


@dataclass(frozen=True)
class CandidateEvidence:
    candidate_id: str
    cycle_index: int
    evidence_mode: Literal["SAMPLED", "EXHAUSTIVE_BOUNDED"]
    evaluator_id: str
    pressure_id: str
    candidate_prefrozen: bool
    evaluator_hidden_before_freeze: bool
    parent_score: float
    successor_score: float
    ablated_score: float
    regression_failures: int
    safety_floor_violations: int
    ctl_admitted: bool
    rollback_available: bool
    exhaustive_domain_attested: bool = False
    exhaustive_obligations_total: int = 0
    exhaustive_obligations_passed: int = 0
    sampled_standard_error: float | None = None


@dataclass(frozen=True)
class AdaptiveGateReceipt:
    receipt_id: str
    candidate_id: str
    cycle_index: int
    evidence_mode: str
    decision: str
    alpha_spent: float | None
    z_statistic: float | None
    failures: tuple[str, ...]
    promotion_authority: bool


def alpha_for_cycle(cycle_index: int, *, familywise_alpha: float = 0.05) -> float:
    if cycle_index < 1:
        raise AdaptiveGateError("cycle_index must be >=1")
    if not (0.0 < familywise_alpha < 1.0):
        raise AdaptiveGateError("familywise_alpha must be in (0,1)")
    return familywise_alpha / (cycle_index * (cycle_index + 1))


def evaluate_candidate(
    evidence: CandidateEvidence,
    *,
    familywise_alpha: float = 0.05,
) -> AdaptiveGateReceipt:
    failures: list[str] = []
    if not evidence.candidate_prefrozen:
        failures.append("candidate not frozen before evaluation")
    if evidence.evaluator_hidden_before_freeze:
        failures.append("evaluation exposed before candidate freeze")
    if not evidence.evaluator_id or not evidence.pressure_id:
        failures.append("evaluator/pressure identity missing")
    if evidence.successor_score <= evidence.parent_score:
        failures.append("successor does not beat parent")
    if evidence.successor_score <= evidence.ablated_score:
        failures.append("claimed change is not causally load-bearing")
    if evidence.regression_failures:
        failures.append("regression failures present")
    if evidence.safety_floor_violations:
        failures.append("safety-floor violation")
    if not evidence.ctl_admitted:
        failures.append("CTL did not admit successor")
    if not evidence.rollback_available:
        failures.append("rollback unavailable")

    alpha_spent = None
    z_statistic = None

    if evidence.evidence_mode == "EXHAUSTIVE_BOUNDED":
        if not evidence.exhaustive_domain_attested:
            failures.append("finite obligation domain not attested exhaustive")
        if evidence.exhaustive_obligations_total <= 0:
            failures.append("exhaustive obligation count missing")
        if (
            evidence.exhaustive_obligations_passed
            != evidence.exhaustive_obligations_total
        ):
            failures.append("successor failed exhaustive bounded obligations")
    elif evidence.evidence_mode == "SAMPLED":
        if evidence.sampled_standard_error is None or evidence.sampled_standard_error <= 0:
            failures.append("sampled evaluation requires positive standard error")
        else:
            delta = evidence.successor_score - evidence.parent_score
            z_statistic = delta / evidence.sampled_standard_error
            alpha_spent = alpha_for_cycle(
                evidence.cycle_index, familywise_alpha=familywise_alpha
            )
            threshold = NormalDist().inv_cdf(1.0 - alpha_spent)
            if z_statistic <= threshold:
                failures.append("successor gain does not pass alpha-spending gate")
    else:
        raise AdaptiveGateError(f"unknown evidence mode: {evidence.evidence_mode}")

    decision = "ACCEPT_BOUNDED_SUCCESSOR" if not failures else "REJECT_OR_WITHHOLD"
    body = {
        "candidate_id": evidence.candidate_id,
        "cycle_index": evidence.cycle_index,
        "evidence_mode": evidence.evidence_mode,
        "decision": decision,
        "alpha_spent": alpha_spent,
        "z_statistic": z_statistic,
        "failures": failures,
        "promotion_authority": False,
    }
    return AdaptiveGateReceipt(
        receipt_id=digest(body),
        candidate_id=evidence.candidate_id,
        cycle_index=evidence.cycle_index,
        evidence_mode=evidence.evidence_mode,
        decision=decision,
        alpha_spent=alpha_spent,
        z_statistic=z_statistic,
        failures=tuple(failures),
        promotion_authority=False,
    )
