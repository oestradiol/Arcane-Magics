from __future__ import annotations

"""Temporary O* teaching scaffold.

This module exists only to generate the prefrozen returned-decision surface from
which the generic learner induces a state-owned policy. Runtime use after
internalization is a test failure.
"""

from itertools import product
from typing import Any

FEATURES = tuple(f"f{i}" for i in range(8))


def teacher_decision(features: dict[str, bool]) -> str:
    external_access = features["f0"]
    contradiction_reachable = features["f1"]
    revision_reachable = features["f2"]
    action_authorized = features["f3"]
    evidence_sufficient = features["f4"]
    residual_unresolved = features["f5"]
    status_only_rejection = features["f6"]
    carrier_difference_consequential = features["f7"]

    if status_only_rejection and not carrier_difference_consequential:
        return "REOPEN"
    if not external_access:
        return "PROBE"
    if not contradiction_reachable:
        return "REOPEN"
    if not revision_reachable:
        return "REOPEN"
    if residual_unresolved and not evidence_sufficient:
        return "PROBE"
    if not action_authorized:
        return "WITHHOLD"
    if evidence_sufficient and not residual_unresolved:
        return "ACT"
    return "WITHHOLD"


def exhaustive_training_surface() -> list[dict[str, Any]]:
    rows = []
    for index, bits in enumerate(product((False, True), repeat=len(FEATURES))):
        features = dict(zip(FEATURES, bits))
        rows.append({
            "example_id": f"teacher-{index:03d}",
            "features": features,
            "decision": teacher_decision(features),
        })
    return rows
