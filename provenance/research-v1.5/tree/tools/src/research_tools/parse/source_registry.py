from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.sources import SourceEntry

ENTRY_RE = re.compile(r"^### (src-[a-z0-9-]+)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z /()'-]*): (.+)$")


def _clean_value(value: str) -> str:
    return value.strip().strip("`")


def parse_source_registry(path: Path) -> list[SourceEntry]:
    text = path.read_text(encoding="utf-8")
    matches = list(ENTRY_RE.finditer(text))
    entries: list[SourceEntry] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        fields: dict[str, str] = {}
        for line in block.splitlines():
            field_match = FIELD_RE.match(line.strip())
            if field_match:
                fields[field_match.group(1)] = _clean_value(field_match.group(2))
        entries.append(
            SourceEntry(
                source_id=match.group(1),
                citation=fields.get("Citation", ""),
                source_type=fields.get("Type", ""),
                role=fields.get("Role in SUF", ""),
                primary_link=fields.get("Primary link", ""),
                archive_link=fields.get("Archive link"),
                accessed_date=fields.get("Accessed"),
                verified_date=fields.get("Verified"),
                use_limit=fields.get("Use limit"),
            )
        )
    return entries


def source_registry_index(entries: list[SourceEntry]) -> dict[str, SourceEntry]:
    return {entry.source_id: entry for entry in entries}
