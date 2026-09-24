from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence

BitRow = tuple[int, ...]


@dataclass(frozen=True)
class BoolExpr:
    op: str
    args: tuple['BoolExpr', ...] = ()
    index: int | None = None

    @staticmethod
    def atom(index: int) -> 'BoolExpr':
        return BoolExpr('ATOM', (), index)

    def eval(self, row: BitRow) -> int:
        if self.op == 'ATOM':
            if self.index is None:
                raise ValueError('ATOM missing index')
            return int(bool(row[self.index]))
        if len(self.args) != 2:
            raise ValueError(f'{self.op} expects two arguments')
        a = self.args[0].eval(row)
        b = self.args[1].eval(row)
        if self.op == 'AND':
            return a & b
        if self.op == 'OR':
            return a | b
        if self.op == 'XOR':
            return a ^ b
        raise ValueError(f'unknown op {self.op}')

    @property
    def nodes(self) -> int:
        return 1 + sum(a.nodes for a in self.args)

    @property
    def depth(self) -> int:
        return 0 if not self.args else 1 + max(a.depth for a in self.args)

    def canonical(self) -> str:
        if self.op == 'ATOM':
            return f'x{self.index}'
        left, right = self.args
        # Current meta-ops are commutative; sort only as a syntax canonicalizer.
        parts = sorted((left.canonical(), right.canonical()))
        return f'{self.op}({parts[0]},{parts[1]})'


@dataclass(frozen=True)
class ObjectGrammar:
    basis: tuple[BoolExpr, ...]
    stage: int = 0


@dataclass(frozen=True)
class ExpansionResult:
    prior: ObjectGrammar
    raw_successor: tuple[BoolExpr, ...]
    raw_added_count: int
    semantic_classes: int
    gauge_duplicates: int
    meta_ops: tuple[str, ...]


@dataclass(frozen=True)
class SearchResult:
    winner: BoolExpr
    train_error: int
    zero_error_count: int
    searched: int
    minimum_nodes: int | None


def bit_domain(width: int) -> tuple[BitRow, ...]:
    return tuple(tuple(int(v) for v in row) for row in product((0, 1), repeat=width))


def truth_table(expr: BoolExpr, rows: Sequence[BitRow]) -> tuple[int, ...]:
    return tuple(expr.eval(r) for r in rows)


def dedupe_semantics(exprs: Iterable[BoolExpr], rows: Sequence[BitRow]) -> tuple[BoolExpr, ...]:
    best: dict[tuple[int, ...], BoolExpr] = {}
    for e in exprs:
        sig = truth_table(e, rows)
        old = best.get(sig)
        if old is None or (e.nodes, e.depth, e.canonical()) < (old.nodes, old.depth, old.canonical()):
            best[sig] = e
    return tuple(sorted(best.values(), key=lambda e: (e.nodes, e.depth, e.canonical())))


def generic_expand_once(grammar: ObjectGrammar, atoms: Sequence[BoolExpr], *, meta_ops: Sequence[str], domain_rows: Sequence[BitRow]) -> ExpansionResult:
    """Expand syntax generically after an insufficiency witness.

    No target labels enter this function. It composes every currently retained basis
    expression with every atomic interface feature using the declared meta-operator set.
    """
    meta_ops = tuple(meta_ops)
    raw = list(grammar.basis)
    prior_canon = {e.canonical() for e in grammar.basis}
    for left in grammar.basis:
        for right in atoms:
            for op in meta_ops:
                raw.append(BoolExpr(op, (left, right)))
                raw.append(BoolExpr(op, (right, left)))
    raw_unique_syntax = {e.canonical(): e for e in raw}
    raw_tuple = tuple(sorted(raw_unique_syntax.values(), key=lambda e: (e.nodes, e.depth, e.canonical())))
    semantic = dedupe_semantics(raw_tuple, domain_rows)
    added = sum(1 for e in raw_tuple if e.canonical() not in prior_canon)
    return ExpansionResult(
        prior=grammar,
        raw_successor=raw_tuple,
        raw_added_count=added,
        semantic_classes=len(semantic),
        gauge_duplicates=len(raw_tuple) - len(semantic),
        meta_ops=meta_ops,
    )


def errors(expr: BoolExpr, observations: Sequence[tuple[BitRow, int]]) -> int:
    return sum(int(expr.eval(x) != int(y)) for x, y in observations)


def exhaustive_select(exprs: Sequence[BoolExpr], observations: Sequence[tuple[BitRow, int]]) -> SearchResult:
    if not exprs:
        raise ValueError('empty grammar')
    scored = [(errors(e, observations), e.nodes, e.depth, e.canonical(), e) for e in exprs]
    scored.sort(key=lambda z: z[:4])
    best_err = scored[0][0]
    zero = [z for z in scored if z[0] == 0]
    return SearchResult(
        winner=scored[0][4],
        train_error=best_err,
        zero_error_count=len(zero),
        searched=len(scored),
        minimum_nodes=min((z[1] for z in zero), default=None),
    )


def grammar_insufficient(grammar: ObjectGrammar, observations: Sequence[tuple[BitRow, int]]) -> bool:
    return exhaustive_select(grammar.basis, observations).train_error > 0


def recompress_to_atoms_plus_winner(atoms: Sequence[BoolExpr], winner: BoolExpr, *, domain_rows: Sequence[BitRow], next_stage: int) -> ObjectGrammar:
    # Semantic dedupe is target-label-free; it uses only executable behavior on admitted inputs.
    retained = dedupe_semantics(tuple(atoms) + (winner,), domain_rows)
    return ObjectGrammar(retained, stage=next_stage)


def semantic_member(expr: BoolExpr, grammar: ObjectGrammar, rows: Sequence[BitRow]) -> bool:
    sig = truth_table(expr, rows)
    return any(truth_table(e, rows) == sig for e in grammar.basis)


def matched_alias_expansion(grammar: ObjectGrammar, *, added_count: int) -> tuple[BoolExpr, ...]:
    """Return a syntax-size-matched useless expansion with no new executable semantics.

    Since BoolExpr canonical syntax cannot carry inert wrappers, this control returns repeated
    executable aliases as an explicit multiset. Search count is matched; semantic capacity is not.
    """
    if not grammar.basis:
        return ()
    out = list(grammar.basis)
    for i in range(added_count):
        out.append(grammar.basis[i % len(grammar.basis)])
    return tuple(out)


def expression_dependencies(expr: BoolExpr) -> tuple[int, ...]:
    if expr.op == 'ATOM':
        return (int(expr.index),)
    vals = set()
    for a in expr.args:
        vals.update(expression_dependencies(a))
    return tuple(sorted(vals))


def target_chain() -> tuple[BoolExpr, ...]:
    x = [BoolExpr.atom(i) for i in range(6)]
    t1 = BoolExpr('XOR', (x[0], x[1]))
    t2 = BoolExpr('AND', (t1, x[2]))
    t3 = BoolExpr('OR', (t2, x[3]))
    return (t1, t2, t3)


def xnor_target() -> Callable[[BitRow], int]:
    return lambda row: 1 ^ (int(bool(row[0])) ^ int(bool(row[1])))
