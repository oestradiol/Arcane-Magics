from __future__ import annotations

"""Neutral relation-feature adapter for learner-side residual search.

This module deliberately contains no EDU17R1 target vocabulary and no target
admission rule. It maps provenance-bearing relation observations onto a bounded
binary coordinate vector derived from already admitted U4/WorldMirror structure.

Meaning of the coordinates is generic:

x0  source coordinates present
x1  source provenance present
x2  explicit neutral relation operator present
x3  left/right endpoints present
x4  typed relation instance present
x5  independently returned evidence bound

The learner/search machinery receives only these coordinates plus returned
desired actions supplied by an external discriminator/evaluator.
"""

from dataclasses import dataclass
from typing import Any, Mapping


class RelationFeatureError(ValueError):
    pass


@dataclass(frozen=True)
class RelationObservation:
    source_start: int | None
    source_end: int | None
    provenance_ids: tuple[str, ...]
    operator: str | None
    left_endpoint: str | None
    right_endpoint: str | None
    typed_relation_id: str | None
    return_id: str | None


NEUTRAL_OPERATORS = frozenset({"NEQ", "NOFLOW", "ARROW"})


def relation_features(obs: RelationObservation) -> tuple[int, ...]:
    coords_present = (
        isinstance(obs.source_start, int)
        and isinstance(obs.source_end, int)
        and obs.source_start >= 0
        and obs.source_end >= obs.source_start
    )
    provenance_present = bool(obs.provenance_ids)
    operator_present = obs.operator in NEUTRAL_OPERATORS
    endpoints_present = bool(
        obs.left_endpoint and obs.left_endpoint.strip()
        and obs.right_endpoint and obs.right_endpoint.strip()
    )
    typed_relation_present = bool(obs.typed_relation_id)
    independent_return_present = bool(obs.return_id)

    return tuple(
        int(v)
        for v in (
            coords_present,
            provenance_present,
            operator_present,
            endpoints_present,
            typed_relation_present,
            independent_return_present,
        )
    )


def observation_from_mapping(value: Mapping[str, Any]) -> RelationObservation:
    return RelationObservation(
        source_start=value.get("source_start"),
        source_end=value.get("source_end"),
        provenance_ids=tuple(str(x) for x in value.get("provenance_ids", ()) if str(x)),
        operator=value.get("operator"),
        left_endpoint=value.get("left_endpoint"),
        right_endpoint=value.get("right_endpoint"),
        typed_relation_id=value.get("typed_relation_id"),
        return_id=value.get("return_id"),
    )
