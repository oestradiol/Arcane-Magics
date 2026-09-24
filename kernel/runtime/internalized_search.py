from __future__ import annotations

"""Minimal executor for a state-owned bounded Boolean search program.

Mutable search grammar/policy is supplied as state data.  The executor has no
project vocabulary, no benchmark labels, no historical donor import, and no
promotion authority.
"""

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping


class StateSearchError(ValueError):
    pass


@dataclass(frozen=True)
class Observation:
    features: tuple[int, ...]
    desired_action: int
    provenance_id: str


@dataclass(frozen=True)
class Outcome:
    status: str
    candidates: tuple[str, ...]
    next_discriminator: tuple[int, ...] | None
    observation_count: int
    promotion_authority: bool = False


def _eval(expr, row: tuple[int, ...]) -> int:
    op = expr[0]
    if op == "RAW":
        return row[expr[1]]
    a = _eval(expr[1], row)
    b = _eval(expr[2], row)
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    if op == "XOR":
        return a ^ b
    raise StateSearchError(f"unsupported op: {op}")


def _canon(expr) -> str:
    if expr[0] == "RAW":
        return f"x{expr[1]}"
    a, b = sorted((_canon(expr[1]), _canon(expr[2])))
    return f"{expr[0]}({a},{b})"


def _pool(width: int, ops: tuple[str, ...]):
    atoms = tuple(("RAW", i) for i in range(width))
    exprs = list(atoms)
    for op in ops:
        for i, a in enumerate(atoms):
            for b in atoms[i:]:
                exprs.append((op, a, b))
    # Semantic aliases are gauge on the complete declared binary domain.
    domain = tuple(product((0, 1), repeat=width))
    by_semantics = {}
    for expr in exprs:
        key = tuple(_eval(expr, row) for row in domain)
        cur = by_semantics.get(key)
        if cur is None or _canon(expr) < _canon(cur):
            by_semantics[key] = expr
    return domain, tuple(by_semantics.values())


def search(
    program: Mapping[str, object],
    observations: Iterable[Observation],
    *,
    hidden_evaluation_exposed: bool = False,
) -> Outcome:
    if hidden_evaluation_exposed or bool(program.get("hidden_evaluation_input")):
        raise StateSearchError("hidden evaluation may not enter proposal search")
    rows = tuple(observations)
    if not rows:
        raise StateSearchError("STOP_NO_RETURNED_RESIDUAL_OBSERVATIONS")
    width = len(rows[0].features)
    if width < 2:
        raise StateSearchError("at least two binary coordinates required")
    for row in rows:
        if len(row.features) != width:
            raise StateSearchError("feature-width mismatch")
        if any(x not in (0, 1) for x in row.features) or row.desired_action not in (0, 1):
            raise StateSearchError("binary observations required")
        if not row.provenance_id:
            raise StateSearchError("provenance required")

    ops = tuple(str(x) for x in program.get("meta_ops", ()))
    if not ops or any(x not in {"AND", "OR", "XOR"} for x in ops):
        raise StateSearchError("unsupported or empty state-owned meta-op set")
    domain, pool = _pool(width, ops)
    exact = tuple(
        expr for expr in pool
        if all(_eval(expr, row.features) == row.desired_action for row in rows)
    )
    exact = tuple(sorted(exact, key=_canon))
    if not exact:
        return Outcome("WITHHOLD_NO_EXPRESSIBLE_CANDIDATE", (), None, len(rows))
    if len(exact) == 1:
        return Outcome("UNIQUE_BOUNDED_PROGRAM_CANDIDATE", (_canon(exact[0]),), None, len(rows))

    observed = {row.features for row in rows}
    best = None
    for row in domain:
        if row in observed:
            continue
        vals = tuple(_eval(expr, row) for expr in exact)
        z, o = vals.count(0), vals.count(1)
        if not z or not o:
            continue
        score = (max(z, o), -min(z, o), tuple(row))
        if best is None or score < best[0]:
            best = (score, tuple(row))
    return Outcome(
        "WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR"
        if best is not None else "WITHHOLD_OBSERVATIONALLY_EQUIVALENT_CANDIDATES",
        tuple(_canon(x) for x in exact),
        None if best is None else best[1],
        len(rows),
    )
