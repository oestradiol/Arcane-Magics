from __future__ import annotations
from dataclasses import dataclass
from .runtime import OntogeneticVM

@dataclass
class SeedCandidate:
    """Minimal runtime composition. Heritage/evaluator ledgers are intentionally outside learner state."""
    vm: OntogeneticVM
    label: str = "IS0_SEED_CANDIDATE"
    @classmethod
    def boot(cls, journal_path=None, adapter=None):
        return cls(OntogeneticVM(journal_path=journal_path, adapter=adapter))
