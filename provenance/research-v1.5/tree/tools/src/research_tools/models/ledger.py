from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str
    timestamp_or_date: str
    issuing_unit: str
    receiving_units: tuple[str, ...]
    action_type: str
    dependency_types: tuple[str, ...]
    implementation_markers: tuple[str, ...]
    public_information_markers: tuple[str, ...]
    source_citations: tuple[str, ...]
    confidence_note: str
    scale_tags: tuple[str, ...]

    @property
    def public_information_marked(self) -> bool:
        markers = {marker.lower() for marker in self.public_information_markers}
        return markers != {"none recorded"}

    @property
    def sigma3_tagged(self) -> bool:
        return "sigma3" in {tag.lower() for tag in self.scale_tags}
