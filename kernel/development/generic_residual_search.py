from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence

BitRow = tuple[int, ...]
META_OPS = ("AND", "OR", "XOR")
VERSION = "GENERIC_RESIDUAL_PROGRAM_SEARCH_V0.1"


class GenericSearchError(ValueError):
    pass


@dataclass(frozen=True)
class BoolProgram:
    op: str
    left: int
    right: int | None = None

    def eval(self, row: BitRow) -> int:
        if self.op == "ATOM":
            return int(bool(row[self.left]))
        if self.right is None:
            raise GenericSearchError(f"{self.op} requires right operand")
        a = int(bool(row[self.left]))
        b = int(bool(row[self.right]))
        if self.op == "AND":
            return a & b
        if self.op == "OR":
            return a | b
        if self.op == "XOR":
            return a ^ b
        raise GenericSearchError(f"unknown op {self.op!r}")

    @property
    def nodes(self) -> int:
        return 1 if self.op == "ATOM" else 3

    @property
    def depth(self) -> int:
        return 0 if self.op == "ATOM" else 1

    def canonical(self) -> str:
        if self.op == "ATOM":
            return f"x{self.left}"
        assert self.right is not None
        a, b = sorted((self.left, self.right))
        return f"{self.op}(x{a},x{b})"


@dataclass(frozen=True)
class ResidualObservation:
    features: BitRow
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
    next_discriminator: BitRow | None
    hidden_evaluation_exposed: bool
    promotion_authority: bool = False


def bit_domain(width: int) -> tuple[BitRow, ...]:
    if width < 2:
        raise GenericSearchError("generic search requires at least two feature coordinates")
    return tuple(tuple(int(v) for v in row) for row in product((0, 1), repeat=width))


def truth_table(program: BoolProgram, rows: Sequence[BitRow]) -> tuple[int, ...]:
    return tuple(program.eval(row) for row in rows)


def candidate_pool(width: int) -> tuple[BoolProgram, ...]:
    """One bounded target-label-free expansion from atomic coordinates.

    This is the internalized functional image of the R194 generic expansion at
    stage zero. It contains no task-family, issue, semantic-label, or expected
    repair branch.
    """
    domain = bit_domain(width)
    raw: list[BoolProgram] = [BoolProgram("ATOM", i) for i in range(width)]
    for left in range(width):
        for right in range(width):
            for op in META_OPS:
                raw.append(BoolProgram(op, left, right))

    best: dict[tuple[int, ...], BoolProgram] = {}
    for program in raw:
        signature = truth_table(program, domain)
        old = best.get(signature)
        rank = (program.nodes, program.depth, program.canonical())
        if old is None or rank < (old.nodes, old.depth, old.canonical()):
            best[signature] = program
    return tuple(sorted(best.values(), key=lambda p: (p.nodes, p.depth, p.canonical())))


def _normalize(observations: Iterable[ResidualObservation]) -> tuple[ResidualObservation, ...]:
    rows = tuple(observations)
    if not rows:
        raise GenericSearchError("STOP_NO_RETURNED_RESIDUAL_OBSERVATIONS")
    width = len(rows[0].features)
    bit_domain(width)
    seen: set[BitRow] = set()
    for row in rows:
        if len(row.features) != width:
            raise GenericSearchError("feature-width mismatch")
        if any(bit not in (0, 1) for bit in row.features):
            raise GenericSearchError("features must be binary")
        if row.desired_action not in (0, 1):
            raise GenericSearchError("desired_action must be binary")
        if not row.provenance_id.strip():
            raise GenericSearchError("returned observation requires provenance")
        if row.features in seen:
            raise GenericSearchError("duplicate feature row is not a fresh discriminator")
        seen.add(row.features)
    return rows


def _next_discriminator(
    exact: Sequence[BoolProgram],
    observed: set[BitRow],
    domain: Sequence[BitRow],
) -> BitRow | None:
    best: tuple[tuple[int, int, BitRow], BitRow] | None = None
    for row in domain:
        if row in observed:
            continue
        outputs = tuple(program.eval(row) for program in exact)
        zeros, ones = outputs.count(0), outputs.count(1)
        if zeros == 0 or ones == 0:
            continue
        # Prefer the most balanced partition; then deterministic row order.
        score = (max(zeros, ones), -min(zeros, ones), row)
        if best is None or score < best[0]:
            best = (score, row)
    return None if best is None else best[1]


def search(
    observations: Iterable[ResidualObservation],
    *,
    hidden_evaluation_exposed: bool = False,
) -> SearchOutcome:
    if hidden_evaluation_exposed:
        raise GenericSearchError("hidden evaluation may not enter learner-side proposal search")

    rows = _normalize(observations)
    width = len(rows[0].features)
    domain = bit_domain(width)
    candidates = candidate_pool(width)
    exact = tuple(
        p for p in candidates
        if all(p.eval(row.features) == row.desired_action for row in rows)
    )
    exact = tuple(sorted(exact, key=lambda p: (p.nodes, p.depth, p.canonical())))

    if not exact:
        return SearchOutcome(
            "Venus.GenericResidualSearchOutcome.v0.1",
            VERSION,
            "WITHHOLD_NO_EXPRESSIBLE_CANDIDATE",
            len(rows),
            width,
            (),
            None,
            None,
            False,
        )

    minimum = min((p.nodes, p.depth) for p in exact)
    names = tuple(p.canonical() for p in exact)
    if len(exact) == 1:
        return SearchOutcome(
            "Venus.GenericResidualSearchOutcome.v0.1",
            VERSION,
            "UNIQUE_BOUNDED_PROGRAM_CANDIDATE",
            len(rows),
            width,
            names,
            minimum,
            None,
            False,
        )

    discriminator = _next_discriminator(exact, {row.features for row in rows}, domain)
    return SearchOutcome(
        "Venus.GenericResidualSearchOutcome.v0.1",
        VERSION,
        (
            "WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR"
            if discriminator is not None
            else "WITHHOLD_OBSERVATIONALLY_EQUIVALENT_CANDIDATES"
        ),
        len(rows),
        width,
        names,
        minimum,
        discriminator,
        False,
    )
