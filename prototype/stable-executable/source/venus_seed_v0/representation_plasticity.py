from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable, Sequence


@dataclass(frozen=True)
class PolynomialGrammar:
    """Bounded object grammar used to carry N2-GE's earned finite plasticity.

    The coefficient domain and the expansion rule are supplied interfaces. A change in
    max_degree is therefore object-grammar plasticity, not unrestricted meta-grammar invention.
    """
    max_degree: int
    coeff_values: tuple[int, ...] = (-3, -2, -1, 0, 1, 2, 3)

    @property
    def candidate_count(self) -> int:
        return len(self.coeff_values) ** (self.max_degree + 1)

    def coefficients(self):
        yield from product(self.coeff_values, repeat=self.max_degree + 1)

    def expand_one_degree(self) -> 'PolynomialGrammar':
        return PolynomialGrammar(self.max_degree + 1, self.coeff_values)


@dataclass(frozen=True)
class PolynomialSearchResult:
    winner: tuple[int, ...]
    score: tuple
    searched: int
    exact: bool
    exact_count: int
    runner_up: tuple[int, ...] | None


def eval_poly(coefficients: Sequence[int], x: int) -> int:
    return sum(int(c) * (int(x) ** i) for i, c in enumerate(coefficients))


def score_model(coefficients: Sequence[int], observations: Sequence[tuple[int, int]]) -> tuple:
    errors = [eval_poly(coefficients, x) - int(y) for x, y in observations]
    return (
        sum(e != 0 for e in errors),
        sum(abs(e) for e in errors),
        sum(abs(int(c)) for c in coefficients),
        sum(int(c) != 0 for c in coefficients),
        tuple(int(c) for c in coefficients),
    )


def search_polynomial(grammar: PolynomialGrammar, observations: Sequence[tuple[int, int]]) -> PolynomialSearchResult:
    rows = [(score_model(c, observations), tuple(int(x) for x in c)) for c in grammar.coefficients()]
    if not rows:
        raise ValueError('empty grammar')
    rows.sort(key=lambda z: z[0])
    score, winner = rows[0]
    return PolynomialSearchResult(
        winner=winner,
        score=score,
        searched=len(rows),
        exact=score[0] == 0,
        exact_count=sum(r[0][0] == 0 for r in rows),
        runner_up=rows[1][1] if len(rows) > 1 else None,
    )


def grammar_insufficient(grammar: PolynomialGrammar, observations: Sequence[tuple[int, int]]) -> bool:
    return not search_polynomial(grammar, observations).exact


def expand_after_certified_insufficiency(grammar: PolynomialGrammar, observations: Sequence[tuple[int, int]]) -> PolynomialGrammar:
    if not grammar_insufficient(grammar, observations):
        raise ValueError('expansion requires a certified insufficiency witness')
    return grammar.expand_one_degree()


def recompress_degree(coefficients: Sequence[int]) -> PolynomialGrammar:
    highest = 0
    for i, c in enumerate(coefficients):
        if int(c) != 0:
            highest = i
    return PolynomialGrammar(highest)


def predict(coefficients: Sequence[int], xs: Iterable[int]) -> tuple[int, ...]:
    return tuple(eval_poly(coefficients, int(x)) for x in xs)


def finite_differences(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    out = [tuple(int(v) for v in values)]
    while len(out[-1]) > 1:
        prev = out[-1]
        out.append(tuple(prev[i + 1] - prev[i] for i in range(len(prev) - 1)))
    return tuple(out)


def exact_degree_on_unit_grid(observations: Sequence[tuple[int, int]]) -> int:
    xs = [int(x) for x, _ in observations]
    if any(xs[i + 1] - xs[i] != 1 for i in range(len(xs) - 1)):
        raise ValueError('unit grid required')
    degree = 0
    for i, row in enumerate(finite_differences([y for _, y in observations])):
        if any(v != 0 for v in row):
            degree = i
    return degree


def _basis_value(name: str, x: int) -> int:
    if name == 'one': return 1
    if name == 'x': return int(x)
    if name in ('square', 'mul_xx'): return int(x) * int(x)
    if name == 'zero_cubic': return 0
    raise KeyError(name)


def search_basis(basis: Sequence[str], coeff_values: Sequence[int], observations: Sequence[tuple[int, int]]):
    rows = []
    for cs in product(tuple(coeff_values), repeat=len(basis)):
        errors = [sum(c * _basis_value(b, x) for c, b in zip(cs, basis)) - y for x, y in observations]
        score = (sum(e != 0 for e in errors), sum(abs(e) for e in errors), sum(abs(c) for c in cs), sum(c != 0 for c in cs), tuple(cs))
        rows.append((score, tuple(cs)))
    rows.sort(key=lambda z: z[0])
    score, winner = rows[0]
    return {'basis': tuple(basis), 'winner': winner, 'score': score, 'exact': score[0] == 0, 'searched': len(rows)}


def minimal_exact_bases(basis: Sequence[str], coeff_values: Sequence[int], observations: Sequence[tuple[int, int]]):
    for size in range(1, len(basis) + 1):
        exact = []
        for subset in combinations(tuple(basis), size):
            r = search_basis(subset, coeff_values, observations)
            if r['exact']:
                exact.append(r)
        if exact:
            return tuple(exact)
    return ()
