from __future__ import annotations

from research_tools.config import ARCHIVE_WILDCARD_MARKERS, NATIVE_FIXED_ARCHIVE_PREFIXES
from research_tools.models.reports import ValidationResult
from research_tools.models.sources import SourceEntry


def validate_archive_links(entries: list[SourceEntry]) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    for entry in entries:
        if entry.requires_archive and not entry.archive_link:
            results.append(
                ValidationResult(
                    check_name="archive-link",
                    status="fail",
                    message="Non-DOI source is missing an archive link.",
                    path=entry.source_id,
                    expected="archive link",
                    found="missing",
                )
            )
            continue
        if not entry.archive_link:
            continue
        if any(marker in entry.archive_link for marker in ARCHIVE_WILDCARD_MARKERS):
            results.append(
                ValidationResult(
                    check_name="archive-link",
                    status="fail",
                    message="Archive link uses a wildcard or save endpoint.",
                    path=entry.source_id,
                    expected="fixed archive URL",
                    found=entry.archive_link,
                )
            )
            continue
        if not (
            entry.archive_link.startswith("https://web.archive.org/web/")
            or entry.archive_link.startswith("https://archive.org/")
            or any(
                entry.archive_link.startswith(prefix)
                for prefix in NATIVE_FIXED_ARCHIVE_PREFIXES
            )
        ):
            results.append(
                ValidationResult(
                    check_name="archive-link",
                    status="fail",
                    message="Archive link is not a recognized fixed archive surface.",
                    path=entry.source_id,
                    expected=(
                        "Wayback fixed capture, archive.org item, "
                        "or approved source-native archive"
                    ),
                    found=entry.archive_link,
                )
            )
    if not results:
        results.append(
            ValidationResult(
                check_name="archive-link",
                status="pass",
                message="All current archive links are fixed-form and valid by policy.",
            )
        )
    return results
