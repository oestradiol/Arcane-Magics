from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

class LineageStatus(str, Enum):
    VALID='VALID'
    INVALID='INVALID'
    SUPERSEDED='SUPERSEDED'
    NONCONTROLLING='NONCONTROLLING'

@dataclass(frozen=True)
class EvidenceLineage:
    """Validity of an evidence lineage is distinct from its scientific verdict."""
    id: str
    expected_records: int | None = None
    observed_records: int | None = None
    status: LineageStatus = LineageStatus.VALID
    reason: str = ''
    parent_ids: tuple[str,...] = ()

    @property
    def complete(self) -> bool:
        return (self.expected_records is None or self.observed_records is None
                or self.expected_records == self.observed_records)

    @property
    def claim_eligible(self) -> bool:
        return self.status is LineageStatus.VALID and self.complete

    @classmethod
    def from_record_count(cls, id: str, expected: int, observed: int, *, reason: str='') -> 'EvidenceLineage':
        status = LineageStatus.VALID if expected == observed else LineageStatus.INVALID
        why = reason or ('' if status is LineageStatus.VALID else f'record-count mismatch: expected={expected}, observed={observed}')
        return cls(id, expected, observed, status, why)

@dataclass(frozen=True)
class CostComparison:
    baseline_total: float
    candidate_total: float
    relative_saving: float
    threshold: float
    passes: bool

@dataclass(frozen=True)
class MeasurementLedger:
    """Complete-cost accounting: a claim is unavailable until every declared component is measured."""
    required_components: tuple[str,...]
    values: Mapping[str,float]

    @property
    def complete(self) -> bool:
        return all(k in self.values for k in self.required_components)

    def total(self) -> float:
        if not self.complete:
            missing=[k for k in self.required_components if k not in self.values]
            raise ValueError(f'incomplete measurement ledger; missing={missing}')
        return sum(float(self.values[k]) for k in self.required_components)

    def compare(self, other:'MeasurementLedger', *, minimum_relative_saving: float=0.0) -> CostComparison:
        baseline=self.total(); candidate=other.total()
        saving=0.0 if baseline == 0 else (baseline-candidate)/baseline
        return CostComparison(baseline,candidate,saving,minimum_relative_saving,saving >= minimum_relative_saving)
