from __future__ import annotations

from research_tools.models.reports import ValidationResult
from research_tools.models.sources import SourceEntry


def validate_source_registry(entries: list[SourceEntry]) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    seen_ids: set[str] = set()
    for entry in entries:
        if entry.source_id in seen_ids:
            results.append(
                ValidationResult(
                    check_name="source-registry",
                    status="fail",
                    message="Duplicate source id.",
                    path=entry.source_id,
                    found=entry.source_id,
                )
            )
        seen_ids.add(entry.source_id)
        for field_name, value in (
            ("citation", entry.citation),
            ("source_type", entry.source_type),
            ("role", entry.role),
            ("primary_link", entry.primary_link),
        ):
            if not value:
                results.append(
                    ValidationResult(
                        check_name="source-registry",
                        status="fail",
                        message=f"Missing required source field: {field_name}.",
                        path=entry.source_id,
                        expected=field_name,
                        found="missing",
                    )
                )
        if not entry.reference_date:
            results.append(
                ValidationResult(
                    check_name="source-registry",
                    status="fail",
                    message="Source is missing both Accessed and Verified dates.",
                    path=entry.source_id,
                    expected="Accessed or Verified date",
                    found="missing",
                )
            )
    if not results:
        results.append(
            ValidationResult(
                check_name="source-registry",
                status="pass",
                message="Source registry shape validated successfully.",
            )
        )
    return results
