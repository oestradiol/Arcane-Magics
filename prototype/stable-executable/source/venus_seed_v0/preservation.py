from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ProjectionCollision:
    key: Hashable
    outcomes: tuple[Any, ...]
    row_ids: tuple[Any, ...]


def projection_collisions(
    rows: Iterable[Any],
    *,
    key: Callable[[Any], Hashable],
    outcome: Callable[[Any], Any],
    row_id: Callable[[Any], Any] = lambda r: id(r),
) -> tuple[ProjectionCollision, ...]:
    """Return keys whose projection collapses rows requiring different outcomes.

    This is an information-loss witness, not a model-selection failure. If two rows have
    the same projected key and different required consequences, no deterministic
    downstream function of that key alone can recover the erased distinction.
    """
    groups: dict[Hashable, list[Any]] = {}
    ids: dict[Hashable, list[Any]] = {}
    for r in rows:
        k = key(r)
        groups.setdefault(k, []).append(outcome(r))
        ids.setdefault(k, []).append(row_id(r))
    out=[]
    for k, values in groups.items():
        distinct=tuple(sorted(set(values), key=repr))
        if len(distinct) > 1:
            out.append(ProjectionCollision(k, distinct, tuple(ids[k])))
    return tuple(sorted(out, key=lambda c: repr(c.key)))


def deterministic_projection_can_fit(rows: Iterable[Any], *, key, outcome) -> bool:
    return not projection_collisions(rows, key=key, outcome=outcome)


@dataclass(frozen=True)
class LayeredAlternatives:
    """Alternatives indexed by an explicit admissibility/resource boundary.

    A current or adjacent slice is never silently upgraded into truth about a wider
    declared future family. `warrant` requires agreement across every declared live
    layer through the requested horizon.
    """
    layers: Mapping[int, tuple[Any, ...]]
    evaluator: Callable[[Any, Any], Any]

    def consensus(self, depth: int, x: Any):
        candidates=self.layers.get(depth, ())
        if not candidates:
            return None
        values={self.evaluator(c,x) for c in candidates}
        return next(iter(values)) if len(values)==1 else None

    def stable_through(self, start: int, horizon: int, x: Any) -> bool:
        vals=[]
        for d in sorted(k for k in self.layers if start <= k <= horizon):
            v=self.consensus(d,x)
            if v is None:
                return False
            vals.append(v)
        return bool(vals) and len(set(vals)) == 1

    def warrant(self, start: int, horizon: int, x: Any):
        if not self.stable_through(start,horizon,x):
            return None
        return self.consensus(start,x)


@dataclass(frozen=True)
class CounterDefeat:
    target: Any
    predicted: Any
    defeated_counter_id: Any
    returned_probe: Any


def counter_defeat_is_warrant(defeat: CounterDefeat, remaining_counters: Sequence[Any], evaluator, *, x: Any) -> bool:
    """Nearest-counter defeat is insufficient while another compatible counter flips x."""
    return all(evaluator(c,x) == defeat.predicted for c in remaining_counters)


@dataclass(frozen=True)
class SupportReturn:
    key: Hashable
    value: Any
    correct: bool
    provenance_group: Hashable
    row_id: Hashable


@dataclass
class PreservationLedger:
    """Returned-support licensing with provenance-group independence and local revocation.

    Multiple presentations/transformations from one group do not become independent
    corroboration. A negative return revokes only the exact key. Structural availability
    without returned support is not warrant.
    """
    minimum_groups: int = 2
    rows: list[SupportReturn] = field(default_factory=list)
    _revoked: set[Hashable] = field(default_factory=set)

    def return_evidence(self, row: SupportReturn) -> None:
        if any(r.row_id == row.row_id for r in self.rows):
            raise ValueError('duplicate returned-support row')
        self.rows.append(row)
        if not row.correct:
            self._revoked.add(row.key)

    def groups(self, key: Hashable, value: Any) -> set[Hashable]:
        return {r.provenance_group for r in self.rows
                if r.key == key and r.value == value and r.correct}

    def has_negative(self, key: Hashable) -> bool:
        return key in self._revoked or any(r.key == key and not r.correct for r in self.rows)

    def licensed_values(self, key: Hashable) -> tuple[Any, ...]:
        if self.has_negative(key):
            return ()
        values={r.value for r in self.rows if r.key == key and r.correct}
        licensed=[v for v in values if len(self.groups(key,v)) >= self.minimum_groups]
        return tuple(sorted(licensed,key=repr))

    def authorize(self, keys: Iterable[Hashable]):
        values=set()
        for k in keys:
            values.update(self.licensed_values(k))
        return next(iter(values)) if len(values) == 1 else None


@dataclass(frozen=True)
class WarrantAssessment:
    causally_active: bool
    zero_wrong: bool
    cross_group_support: bool
    warranted: bool


def assess_warrant(*, treatment_outputs: Sequence[Any], deletion_outputs: Sequence[Any],
                   correctness: Sequence[bool], supporting_groups: Iterable[Hashable],
                   minimum_groups: int = 2) -> WarrantAssessment:
    """Causal activity of learned state is logically weaker than epistemic warrant."""
    causal=tuple(treatment_outputs) != tuple(deletion_outputs)
    zero_wrong=bool(correctness) and all(correctness)
    groups=len(set(supporting_groups)) >= minimum_groups
    return WarrantAssessment(causal,zero_wrong,groups,causal and zero_wrong and groups)


@dataclass(frozen=True)
class FiberTransport:
    source: frozenset[Any]
    image: frozenset[Any]
    survivors: frozenset[Any]
    lost: frozenset[Any]
    introduced: frozenset[Any]

    @classmethod
    def from_transform(cls, source: Iterable[Any], transform: Callable[[Any],Any], admissible_destination: Iterable[Any]):
        src=frozenset(source); dst=frozenset(admissible_destination); image=frozenset(transform(x) for x in src)
        survivors=frozenset(x for x in src if transform(x) in dst)
        return cls(src,image,survivors,src-survivors,dst-image)


class AttemptState(str, Enum):
    STARTED='STARTED'
    COMPLETED='COMPLETED'
    INTERRUPTED='INTERRUPTED'


@dataclass(frozen=True)
class ExecutionAttempt:
    id: str
    state: AttemptState
    result: Any = None
    harness_valid: bool = True

    @property
    def scientific_verdict(self):
        if self.state is not AttemptState.COMPLETED or not self.harness_valid:
            return None
        return self.result


@dataclass
class LineageAuthority:
    """Historical evidence stays reconstructible while exactly one lineage may control."""
    records: dict[str, Any] = field(default_factory=dict)
    controlling_id: str | None = None

    def add(self, lineage_id: str, record: Any, *, controlling: bool=False):
        if lineage_id in self.records:
            raise ValueError('lineage already recorded')
        self.records[lineage_id]=record
        if controlling:
            self.controlling_id=lineage_id

    @property
    def controlling(self):
        return None if self.controlling_id is None else self.records[self.controlling_id]

    def historical(self, lineage_id: str):
        return self.records[lineage_id]
