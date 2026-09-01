"""Generic ledger parser with route-specific configurations.

Consolidates the 90% duplicate code from nz_ledger.py, taiwan_ledger.py,
and australia_ledger.py into a single generic parser with route configs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from research_tools.models.ledger import LedgerEvent

# Standard patterns used across all ledger formats
SECTION_RE = re.compile(r"^### `([^`]+)`\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- `([^`]+)`: (.+)$")
SOURCE_ID_RE = re.compile(r"(src-[A-Za-z0-9-]+)")


def _clean_value(value: str) -> str:
    return value.strip().strip("`")


def _split_semicolon_field(value: str) -> tuple[str, ...]:
    items = []
    for piece in value.split(";"):
        cleaned = _clean_value(piece)
        if cleaned:
            items.append(cleaned)
    return tuple(items)


def _extract_source_ids(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(SOURCE_ID_RE.findall(value)))


@dataclass(frozen=True)
class RouteConfig:
    """Configuration for parsing a route's ledger.

    Attributes:
        prefix: Event ID prefix to filter (e.g., "nz-", "tw-", "au-")
        section_pattern: Optional custom section regex pattern
    """

    prefix: str
    section_pattern: re.Pattern | None = None


# Route configurations
ROUTE_CONFIGS = {
    "nz": RouteConfig(prefix="nz-"),
    "taiwan": RouteConfig(prefix="tw-"),
    "australia": RouteConfig(prefix="au-"),
}


def parse_ledger(path: Path, route: str | RouteConfig) -> list[LedgerEvent]:
    """Parse a ledger file for any route.

    Args:
        path: Path to the ledger markdown file
        route: Either a route name ("nz", "taiwan", "australia") or a RouteConfig

    Returns:
        List of LedgerEvent objects
    """
    if isinstance(route, str):
        config = ROUTE_CONFIGS[route]
    else:
        config = route

    section_re = config.section_pattern or SECTION_RE
    prefix = config.prefix

    text = path.read_text(encoding="utf-8")
    matches = list(section_re.finditer(text))
    events: list[LedgerEvent] = []

    for index, match in enumerate(matches):
        event_id = match.group(1)
        if not event_id.startswith(prefix):
            continue

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]

        fields: dict[str, str] = {}
        for line in block.splitlines():
            field_match = FIELD_RE.match(line.strip())
            if field_match:
                fields[field_match.group(1)] = field_match.group(2).strip()

        events.append(
            LedgerEvent(
                event_id=event_id,
                timestamp_or_date=_clean_value(fields.get("timestamp_or_date", "")),
                issuing_unit=_clean_value(fields.get("issuing_unit", "")),
                receiving_units=_split_semicolon_field(fields.get("receiving_units", "")),
                action_type=_clean_value(fields.get("action_type", "")),
                dependency_types=_split_semicolon_field(fields.get("dependency_type", "")),
                implementation_markers=_split_semicolon_field(fields.get("implementation_marker", "")),
                public_information_markers=_split_semicolon_field(fields.get("public_information_marker", "")),
                source_citations=_extract_source_ids(fields.get("source_citation", "")),
                confidence_note=_clean_value(fields.get("confidence_note", "")),
                scale_tags=_split_semicolon_field(fields.get("scale_tag", "")),
            )
        )

    return events


# Backward-compatible wrappers
def parse_nz_ledger(path: Path) -> list[LedgerEvent]:
    """Parse New Zealand ledger."""
    return parse_ledger(path, "nz")


def parse_taiwan_ledger(path: Path) -> list[LedgerEvent]:
    """Parse Taiwan ledger."""
    return parse_ledger(path, "taiwan")


def parse_australia_ledger(path: Path) -> list[LedgerEvent]:
    """Parse Australia ledger."""
    return parse_ledger(path, "australia")
