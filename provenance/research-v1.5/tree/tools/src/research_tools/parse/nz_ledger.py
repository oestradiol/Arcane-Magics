"""New Zealand ledger parser (wrapper around generic ledger parser)."""

from __future__ import annotations

from pathlib import Path

from research_tools.models.ledger import LedgerEvent
from research_tools.parse.ledger import parse_ledger


def parse_nz_ledger(path: Path) -> list[LedgerEvent]:
    """Parse New Zealand ledger."""
    return parse_ledger(path, "nz")
