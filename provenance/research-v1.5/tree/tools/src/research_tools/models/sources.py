from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceEntry:
    source_id: str
    citation: str
    source_type: str
    role: str
    primary_link: str
    archive_link: str | None
    accessed_date: str | None
    verified_date: str | None
    use_limit: str | None

    @property
    def reference_date(self) -> str | None:
        return self.accessed_date or self.verified_date

    @property
    def is_doi_primary(self) -> bool:
        return "doi.org/" in self.primary_link

    @property
    def requires_archive(self) -> bool:
        return not self.is_doi_primary
