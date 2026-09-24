from __future__ import annotations

"""Compatibility facade for the state-owned generic residual-search capability.

The mutable search grammar and ambiguity policy live in
GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json.  Runtime execution is supplied
by kernel.runtime.internalized_search, which is project-blind and contains no
historical donor import or issue-specific semantic table.

This module preserves the admitted v0.1 public API so existing developmental
audits do not need to depend on the storage representation.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from kernel.runtime.internalized_search import (
    Observation as _Observation,
    StateSearchError,
    search as _state_search,
    semantic_signatures as _semantic_signatures,
)

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "kernel/development/GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json"
VERSION = "GENERIC_RESIDUAL_PROGRAM_SEARCH_V0.1"
GenericSearchError = StateSearchError


@dataclass(frozen=True)
class ResidualObservation:
    features: tuple[int, ...]
    desired_action: int
    provenance_id: str


@dataclass(frozen=True)
class SearchOutcome:
    schema: str
    version: str
    status: str
    observation_count: int
    feature_count: int
    exact_semantic_candidates: tuple[str, ...]
    minimal_complexity: tuple[int, int] | None
    next_discriminator: tuple[int, ...] | None
    hidden_evaluation_exposed: bool
    promotion_authority: bool = False


def load_state_program() -> dict:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state.get("schema") != "Venus.InternalizedBooleanSearchProgram.v0.1":
        raise GenericSearchError("wrong state-owned generic-search schema")
    program = state.get("program")
    if not isinstance(program, dict):
        raise GenericSearchError("missing state-owned generic-search program")
    return program


def semantic_signatures(width: int) -> frozenset[tuple[int, ...]]:
    return _semantic_signatures(load_state_program(), width)


def _complexity(name: str) -> tuple[int, int]:
    # v0.1 grammar is atoms or one binary operation over atoms.
    return (1, 0) if name.startswith("x") else (3, 1)


def search(
    observations: Iterable[ResidualObservation],
    *,
    hidden_evaluation_exposed: bool = False,
) -> SearchOutcome:
    rows = tuple(observations)
    internal_rows = tuple(
        _Observation(
            features=tuple(row.features),
            desired_action=row.desired_action,
            provenance_id=row.provenance_id,
        )
        for row in rows
    )
    out = _state_search(
        load_state_program(),
        internal_rows,
        hidden_evaluation_exposed=hidden_evaluation_exposed,
    )
    width = len(rows[0].features) if rows else 0
    minimum = (
        None
        if not out.candidates
        else min(_complexity(name) for name in out.candidates)
    )
    return SearchOutcome(
        schema="Venus.GenericResidualSearchOutcome.v0.1",
        version=VERSION,
        status=out.status,
        observation_count=out.observation_count,
        feature_count=width,
        exact_semantic_candidates=out.candidates,
        minimal_complexity=minimum,
        next_discriminator=out.next_discriminator,
        hidden_evaluation_exposed=False,
        promotion_authority=False,
    )
