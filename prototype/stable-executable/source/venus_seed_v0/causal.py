from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

class RelationStatus(str, Enum):
    PRESERVES='PRESERVES'
    FAILS_TO_PRESERVE='FAILS_TO_PRESERVE'
    UNDETERMINED='RELATION_UNDETERMINED'

class EpistemicStatus(str, Enum):
    LICENSE='LICENSE'
    REJECT='REJECT'
    UNDETERMINED='UNDETERMINED'

@dataclass(frozen=True)
class RelationEvidence:
    candidate: Any
    status: RelationStatus
    provenance_group: Hashable
    cross_fitted: bool = True

@dataclass
class TypedWarrantBridge:
    """Relation evidence is input to warrant, never warrant by nomenclature.

    This intentionally conservative reference rule is not a claim that DEV-019's learned
    bridge reduces to this implementation. It is a native law carrier: positive licensing
    requires clean cross-fitted support from independent provenance groups, while mixed,
    negative, non-cross-fitted or insufficiently recurrent support remains unresolved.
    """
    minimum_groups: int = 2

    def assess(self, candidate: Any, evidence: Iterable[RelationEvidence]) -> EpistemicStatus:
        rows=[e for e in evidence if e.candidate == candidate and e.cross_fitted]
        pos={e.provenance_group for e in rows if e.status is RelationStatus.PRESERVES}
        neg={e.provenance_group for e in rows if e.status is RelationStatus.FAILS_TO_PRESERVE}
        if neg and not pos:
            return EpistemicStatus.REJECT
        if not neg and len(pos) >= self.minimum_groups:
            return EpistemicStatus.LICENSE
        return EpistemicStatus.UNDETERMINED

    def authorize_binary(self, candidates: Sequence[Any], evidence: Iterable[RelationEvidence]):
        statuses={c:self.assess(c,evidence) for c in candidates}
        licensed=[c for c,s in statuses.items() if s is EpistemicStatus.LICENSE]
        return (licensed[0] if len(licensed)==1 else None), statuses

@dataclass(frozen=True)
class TrajectorySupport:
    candidate: Any
    changed: bool
    provenance_group: Hashable
    supports_candidate: bool


def recurrent_trajectory_support(candidate: Any, rows: Iterable[TrajectorySupport], *, minimum_groups: int=2) -> bool:
    groups={r.provenance_group for r in rows if r.candidate==candidate and r.changed and r.supports_candidate}
    return len(groups) >= minimum_groups

class CausalClassification(str, Enum):
    NECESSARY_AT_SCOPE='NECESSARY_AT_SCOPE'
    REDUNDANT_FOR_PERFORMANCE_AT_SCOPE='REDUNDANT_FOR_PERFORMANCE_AT_SCOPE'
    INTERACTION_DEPENDENT='INTERACTION_DEPENDENT'
    CONSTITUTIONALLY_REQUIRED='CONSTITUTIONALLY_REQUIRED'
    CLAIM_NECESSARY='CLAIM_NECESSARY'
    UNRESOLVED='UNRESOLVED'

@dataclass(frozen=True)
class InterventionComparison:
    intact: Any
    ablated: Any
    changed_condition: Any | None = None

    @property
    def effect(self) -> bool:
        return self.intact != self.ablated


def classify_component(*, intact: Any, ablated: Any, changed_condition: Any|None=None,
                       constitutional: bool=False, claim_required: bool=False) -> CausalClassification:
    if constitutional:
        return CausalClassification.CONSTITUTIONALLY_REQUIRED
    if claim_required and intact == ablated:
        return CausalClassification.CLAIM_NECESSARY
    if intact != ablated:
        return CausalClassification.NECESSARY_AT_SCOPE
    if changed_condition is not None and changed_condition != intact:
        return CausalClassification.INTERACTION_DEPENDENT
    return CausalClassification.REDUNDANT_FOR_PERFORMANCE_AT_SCOPE

@dataclass(frozen=True)
class ProbePlan:
    probe: Any | None
    worst_case_gain: int
    baseline_coverage: int
    simulated_coverages: Mapping[Any,int]


def choose_worst_case_improving_probe(
    probes: Iterable[Any], *, outcomes: Iterable[Any], baseline_coverage: int,
    simulate_coverage: Callable[[Any,Any],int]
) -> ProbePlan:
    """Truth-blind prospective query choice.

    The selector sees only simulated coverage for each possible return. It receives no
    actual return/evaluator truth. A probe is admissible only when every possible return
    strictly improves current authorized coverage.
    """
    best=None
    for p in probes:
        sims={o:int(simulate_coverage(p,o)) for o in outcomes}
        worst=min(sims.values()) if sims else baseline_coverage
        gain=worst-baseline_coverage
        if gain <= 0:
            continue
        key=(gain, sum(sims.values()), repr(p))
        if best is None or key > best[0]:
            best=(key,ProbePlan(p,gain,baseline_coverage,sims))
    return best[1] if best else ProbePlan(None,0,baseline_coverage,{})

@dataclass
class ExecutableKnowledge:
    """Verified returned consequence may install a learned executable relation.

    Source prose is never sufficient. Deletion is causal and leaves provenance history.
    """
    learned: dict[Hashable, Callable[[Any],Any]] = field(default_factory=dict)
    history: list[dict[str,Any]] = field(default_factory=list)

    def admit(self, key: Hashable, executable: Callable[[Any],Any], verification_cases: Sequence[tuple[Any,Any]], *, returned: bool):
        if not returned:
            self.history.append({'kind':'WITHHOLD','key':key,'reason':'no returned executable consequence'})
            return False
        if not verification_cases or not all(executable(x)==y for x,y in verification_cases):
            self.history.append({'kind':'REJECT','key':key,'reason':'executable counterexample'})
            return False
        self.learned[key]=executable
        self.history.append({'kind':'ADMIT','key':key,'verified_cases':len(verification_cases)})
        return True

    def predict(self, key: Hashable, x: Any):
        f=self.learned.get(key)
        return None if f is None else f(x)

    def delete(self, key: Hashable):
        existed=key in self.learned
        self.learned.pop(key,None)
        self.history.append({'kind':'DELETE','key':key,'existed':existed})
        return existed

@dataclass(frozen=True)
class CoordinateIntervention:
    coordinate: Hashable
    baseline: Any
    intervened: Any

    @property
    def consequential(self) -> bool:
        return self.baseline != self.intervened


def consequential_partition(interventions: Iterable[CoordinateIntervention]) -> frozenset[Hashable]:
    return frozenset(i.coordinate for i in interventions if i.consequential)


def trace_equivalent(left: Sequence[Any], right: Sequence[Any]) -> bool:
    """Reduction is licensed only for the declared enacted trace, not endpoint alone."""
    return tuple(left) == tuple(right)


def endpoint_equivalent(left: Sequence[Any], right: Sequence[Any]) -> bool:
    return bool(left) and bool(right) and left[-1] == right[-1]
