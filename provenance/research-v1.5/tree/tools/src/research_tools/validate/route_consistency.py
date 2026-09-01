from __future__ import annotations

from pathlib import Path

from research_tools.config import SIGMA1_UNITS
from research_tools.models.ledger import LedgerEvent
from research_tools.models.reports import ValidationResult
from research_tools.models.sources import SourceEntry
from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.reports.nz_summary import (
    compare_nz_summary_to_docs,
    compute_nz_window_summaries,
    compute_route_summary,
)
from research_tools.reports.nz_taiwan_summary import compare_nz_taiwan_summary_to_docs
from research_tools.reports.taiwan_summary import compare_taiwan_summary_to_docs


def _validate_event_schema(
    route_name: str,
    events: list[LedgerEvent],
    source_index: dict[str, SourceEntry],
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    seen_ids: set[str] = set()
    valid_units = set(SIGMA1_UNITS)
    for event in events:
        if event.event_id in seen_ids:
            results.append(
                ValidationResult(
                    check_name=f"{route_name}-event-schema",
                    status="fail",
                    message="Duplicate event id.",
                    path=event.event_id,
                    found=event.event_id,
                )
            )
        seen_ids.add(event.event_id)
        if event.issuing_unit not in valid_units:
            results.append(
                ValidationResult(
                    check_name=f"{route_name}-event-schema",
                    status="fail",
                    message="Unknown issuing unit.",
                    path=event.event_id,
                    expected="known sigma1 unit",
                    found=event.issuing_unit,
                )
            )
        for receiver in event.receiving_units:
            if receiver not in valid_units:
                results.append(
                    ValidationResult(
                        check_name=f"{route_name}-event-schema",
                        status="fail",
                        message="Unknown receiving unit.",
                        path=event.event_id,
                        expected="known sigma1 unit",
                        found=receiver,
                    )
                )
        for field_name, value in (
            ("timestamp_or_date", event.timestamp_or_date),
            ("action_type", event.action_type),
            ("confidence_note", event.confidence_note),
        ):
            if not value:
                results.append(
                    ValidationResult(
                        check_name=f"{route_name}-event-schema",
                        status="fail",
                        message=f"Missing required field: {field_name}.",
                        path=event.event_id,
                        expected=field_name,
                        found="missing",
                    )
                )
        for source_id in event.source_citations:
            if source_id not in source_index:
                results.append(
                    ValidationResult(
                        check_name=f"{route_name}-event-schema",
                        status="fail",
                        message="Event references an unknown source id.",
                        path=event.event_id,
                        expected="known source id",
                        found=source_id,
                    )
                )
    if not results:
        results.append(
            ValidationResult(
                check_name=f"{route_name}-event-schema",
                status="pass",
                message="Ledger schema and source references validated.",
            )
        )
    return results


def validate_nz_route(
    route_root: Path,
    source_index: dict[str, SourceEntry],
) -> list[ValidationResult]:
    events = parse_nz_ledger(route_root / "event-ledger-seed.md")
    results = _validate_event_schema("nz", events, source_index)
    summary = compute_route_summary("nz", events)
    windows = compute_nz_window_summaries(events)
    results.extend(
        compare_nz_summary_to_docs(
            summary=summary,
            window_summary=windows["Main perturbation interval"],
            comparator_b_summary=windows["Comparator B"],
            project_status_path=route_root.parents[3] / "docs" / "project-status.md",
            i_summary_path=route_root / "first-pass-i-summary.md",
            seed_readout_path=route_root / "first-pass-seed-readout.md",
            window_comparison_path=route_root / "first-pass-window-comparison.md",
            sensitivity_note_path=route_root / "first-pass-sensitivity-and-null-note.md",
        )
    )
    return results


def validate_taiwan_route(
    route_root: Path,
    source_index: dict[str, SourceEntry],
) -> list[ValidationResult]:
    taiwan_events = parse_taiwan_ledger(route_root / "taiwan-event-ledger-seed.md")
    results = _validate_event_schema("taiwan", taiwan_events, source_index)
    nz_events = parse_nz_ledger(route_root / "event-ledger-seed.md")
    nz_summary = compute_route_summary("nz", nz_events)
    taiwan_summary = compute_route_summary("taiwan", taiwan_events)
    results.extend(
        compare_nz_taiwan_summary_to_docs(
            nz_summary=nz_summary,
            taiwan_summary=taiwan_summary,
            comparison_note_path=route_root / "first-nz-taiwan-comparison-note.md",
        )
    )
    results.extend(
        compare_taiwan_summary_to_docs(
            summary=taiwan_summary,
            ledger_path=route_root / "taiwan-event-ledger-seed.md",
            evidence_map_path=route_root / "taiwan-chapter-evidence-map.md",
            table_plan_path=route_root / "taiwan-chapter-table-and-figure-plan.md",
        )
    )
    return results


def validate_australia_route(
    route_root: Path,
    source_index: dict[str, SourceEntry],
) -> list[ValidationResult]:
    from research_tools.parse.australia_ledger import parse_australia_ledger
    from research_tools.reports.australia_summary import (
        compare_australia_summary_to_docs,
        compute_route_summary,
    )

    australia_events = parse_australia_ledger(route_root / "australia-event-ledger-seed.md")
    results = _validate_event_schema("australia", australia_events, source_index)
    summary = compute_route_summary("australia", australia_events)
    results.extend(
        compare_australia_summary_to_docs(
            summary=summary,
            ledger_path=route_root / "australia-event-ledger-seed.md",
            events=australia_events,
        )
    )
    return results
