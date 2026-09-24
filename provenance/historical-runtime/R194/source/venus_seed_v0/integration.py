from __future__ import annotations
from pathlib import Path
from .heritage import HeritageRegistry,ConservationGate

def is1_gate(ledger_path):
    return ConservationGate(HeritageRegistry.load(ledger_path)).evaluate()
def require_m6_unlocked(ledger_path):
    result=is1_gate(ledger_path)
    if not result["m6_unlocked"]: raise RuntimeError(f"M6_BLOCKED: {len(result['failures'])} conservation obligations incomplete")
    return True
