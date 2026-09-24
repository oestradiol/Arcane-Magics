from __future__ import annotations
from pathlib import Path
from .heritage import HeritageRegistry, ConservationGate
from .seed_candidate import SeedCandidate

class IntegrationHarness:
    def __init__(self, ledger_path):
        self.ledger_path=Path(ledger_path)
        self.registry=HeritageRegistry.load(self.ledger_path)
    def boot_seed(self, **kwargs): return SeedCandidate.boot(**kwargs)
    def conservation_status(self): return ConservationGate(self.registry).evaluate()
    def assert_m6_locked(self):
        s=self.conservation_status()
        if s['m6_unlocked']: raise AssertionError('IS0 must not unlock M6 before IS1')
        return s
