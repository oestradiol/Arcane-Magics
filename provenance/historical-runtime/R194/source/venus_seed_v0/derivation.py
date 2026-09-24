from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Any, Callable, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class FiniteGrammar:
    """Researcher-supplied finite search grammar.

    The grammar is an admitted search interface, not a claim that the world has these axes.
    """
    axes: tuple[str, ...]
    domains: Mapping[str, tuple[Any, ...]]

    def programs(self):
        for values in product(*(self.domains[a] for a in self.axes)):
            yield tuple(values)

    @property
    def size(self) -> int:
        n=1
        for a in self.axes:
            n *= len(self.domains[a])
        return n


@dataclass(frozen=True)
class DerivationResult:
    winner: tuple[Any, ...]
    objective: tuple[Any, ...]
    searched: int
    unique: bool
    runner_up: tuple[Any, ...] | None
    state_id: str | None = None
    parent_policy_supplied: bool = False


def derive_exhaustively(grammar: FiniteGrammar, objective: Callable[[tuple[Any, ...]], Sequence[Any]], *, state_id: str|None=None) -> DerivationResult:
    rows=[]
    for p in grammar.programs():
        rows.append((tuple(objective(p)), p))
    if not rows:
        raise ValueError('empty grammar')
    rows.sort(key=lambda z:(z[0],z[1]))
    winner_obj,winner=rows[0]
    unique=len(rows)==1 or winner_obj < rows[1][0]
    return DerivationResult(winner,winner_obj,len(rows),unique,rows[1][1] if len(rows)>1 else None,state_id,False)


def rederive_across_states(grammar: FiniteGrammar, states: Iterable[Any], objective_for_state: Callable[[Any],Callable[[tuple[Any,...]],Sequence[Any]]]):
    """Each state receives a fresh full search. No parent vector enters this interface."""
    out=[]
    for i,state in enumerate(states):
        sid=str(state.get('id',i)) if isinstance(state,dict) else str(i)
        out.append(derive_exhaustively(grammar,objective_for_state(state),state_id=sid))
    return tuple(out)


def normalized_text(value: Any) -> str:
    return str(value).lower().replace(' ','').replace('-','').replace('_','')


def vocabulary_firewall(values: Iterable[Any], banned: Iterable[str]) -> tuple[str,...]:
    text='\n'.join(normalized_text(v) for v in values)
    leaks=[]
    for token in banned:
        t=normalized_text(token)
        if t and t in text:
            leaks.append(token)
    return tuple(leaks)


@dataclass(frozen=True)
class PolicyRevisionResult:
    parent: tuple[Any, ...]
    successor: tuple[Any, ...]
    parent_objective: tuple[Any, ...]
    successor_objective: tuple[Any, ...]
    parent_invalidated: bool
    searched: int


def revise_policy_if_consequence_invalidates(
    grammar: FiniteGrammar,
    parent: Sequence[Any],
    objective: Callable[[tuple[Any, ...]], Sequence[Any]],
) -> PolicyRevisionResult:
    """Re-run the admitted finite derivation when returned consequence defeats the parent.

    This changes a policy inside the supplied grammar. It is intentionally not a grammar
    expansion operator and therefore cannot satisfy N2-GE meta-grammar revision by itself.
    """
    p = tuple(parent)
    parent_obj = tuple(objective(p))
    derived = derive_exhaustively(grammar, objective)
    successor_obj = tuple(derived.objective)
    return PolicyRevisionResult(
        parent=p,
        successor=tuple(derived.winner),
        parent_objective=parent_obj,
        successor_objective=successor_obj,
        parent_invalidated=successor_obj < parent_obj and tuple(derived.winner) != p,
        searched=derived.searched,
    )
